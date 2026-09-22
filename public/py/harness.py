"""Runs learner code inside the Pyodide Web Worker.

Kept as a plain Python file (no Pyodide imports) so it can be unit-tested with CPython.
"""
import builtins
import json
import linecache
import logging
import os
import re
import shutil
import sys
import tempfile
import time
import traceback

OUTPUT_LIMIT = 200_000  # characters per run; protects the page from print-bombs
FLUSH_CHARS = 4096
FLUSH_SECONDS = 0.1
FILENAME = "<your code>"

MAX_SEED_FILES = 10
MAX_SEED_FILE_CHARS = 20_000
SEED_NAME = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,39}")


class _Workdir:
    """A private temporary working directory for one run.

    Learner programs can create/read files freely (Pyodide's filesystem lives in memory,
    never on the visitor's disk), but nothing may leak from one run into the next: the
    directory, any modules imported from it and the sys.path entry are all removed on exit.
    Optional `files` (name -> text) are created first, e.g. data for an exercise.
    """

    def __init__(self, files=None):
        self._files = files or {}
        self.path = None
        self._previous_cwd = None

    def __enter__(self):
        if len(self._files) > MAX_SEED_FILES:
            raise ValueError("too many provided files")
        for name, content in self._files.items():
            if not SEED_NAME.fullmatch(name) or not isinstance(content, str) or len(content) > MAX_SEED_FILE_CHARS:
                raise ValueError(f"invalid provided file: {name!r}")
        self._previous_cwd = os.getcwd()
        self.path = os.path.realpath(tempfile.mkdtemp(prefix="academy-"))
        for name, content in self._files.items():
            with open(os.path.join(self.path, name), "w", encoding="utf-8", newline="\n") as handle:
                handle.write(content)
        os.chdir(self.path)
        sys.path.insert(0, self.path)
        return self

    def __exit__(self, *exc_info):
        try:
            os.chdir(self._previous_cwd)
        except OSError:
            pass
        if self.path in sys.path:
            sys.path.remove(self.path)
        sys.path_importer_cache.pop(self.path, None)
        prefix = self.path + os.sep
        for name, module in list(sys.modules.items()):
            try:
                origin = getattr(module, "__file__", None)
                if origin and os.path.realpath(origin).startswith(prefix):
                    del sys.modules[name]
            except Exception:  # noqa: BLE001 - exotic module objects must not break cleanup
                continue
        shutil.rmtree(self.path, ignore_errors=True)
        return False


class OutputLimitExceeded(BaseException):
    """A BaseException so a learner's `except Exception:` cannot swallow it."""


class _Channel:
    """Buffers writes from stdout/stderr and forwards them, in order, to emit(stream, text)."""

    def __init__(self, emit):
        self._emit = emit
        self._parts = []
        self._size = 0
        self._total = 0
        self._last = time.monotonic()
        self.stdout_text = []

    def write(self, stream, text):
        if not isinstance(text, str):
            raise TypeError(f"write() argument must be str, not {type(text).__name__}")
        if not text:
            return 0
        self._total += len(text)
        if self._total > OUTPUT_LIMIT:
            self.flush()
            raise OutputLimitExceeded
        if stream == "stdout":
            self.stdout_text.append(text)
        self._parts.append((stream, text))
        self._size += len(text)
        if self._size >= FLUSH_CHARS or time.monotonic() - self._last >= FLUSH_SECONDS:
            self.flush()
        return len(text)

    def flush(self):
        parts, self._parts, self._size = self._parts, [], 0
        self._last = time.monotonic()
        if self._emit is None:
            return
        current, buffer = None, []
        for stream, text in parts:
            if stream != current and buffer:
                self._emit(current, "".join(buffer))
                buffer = []
            current = stream
            buffer.append(text)
        if buffer:
            self._emit(current, "".join(buffer))


class _Stream:
    encoding = "utf-8"
    errors = "strict"

    def __init__(self, channel, name):
        self._channel = channel
        self._name = name

    def write(self, text):
        return self._channel.write(self._name, text)

    def flush(self):
        self._channel.flush()

    def isatty(self):
        return False

    def writable(self):
        return True


class _Silent:
    def write(self, text):
        return len(text)

    def flush(self):
        pass

    def isatty(self):
        return False


def _make_input(lines, channel, echo):
    remaining = iter(lines)

    def fake_input(prompt=""):
        if prompt:
            channel.write("stdout", str(prompt))
        try:
            line = next(remaining)
        except StopIteration:
            raise EOFError(
                "No input left. Type more lines into the Input box, one line per input() call."
            ) from None
        if echo:  # mimic a terminal, where the typed answer appears on screen
            channel.write("stdout", line + "\n")
        return line

    return fake_input


def _format_error(exc):
    if isinstance(exc, SyntaxError) and exc.filename == FILENAME:
        return "".join(traceback.format_exception_only(type(exc), exc))
    tb = exc.__traceback__
    while tb is not None and tb.tb_frame.f_code.co_filename != FILENAME:
        tb = tb.tb_next  # hide the harness's own frames from the learner
    return "".join(traceback.format_exception(type(exc), exc, tb))


def _execute(code, stdin_lines, channel, echo):
    """Run learner code in a fresh namespace. Returns (namespace, error_text | None)."""
    linecache.cache[FILENAME] = (len(code), None, code.splitlines(True), FILENAME)
    namespace = {"__name__": "__main__"}
    saved = sys.stdout, sys.stderr, builtins.input
    sys.stdout = _Stream(channel, "stdout")
    sys.stderr = _Stream(channel, "stderr")
    builtins.input = _make_input(stdin_lines, channel, echo)
    # The `logging` module is a singleton that survives between runs (only the namespace is
    # fresh). Without this, a learner's logging.basicConfig() would only ever take effect on
    # the first run, and later runs would try to write through a stream object from a run
    # that already ended.
    logging.root.handlers.clear()
    logging.root.setLevel(logging.WARNING)
    error = None
    try:
        exec(compile(code, FILENAME, "exec"), namespace)
    except SystemExit:
        pass
    except OutputLimitExceeded:
        error = f"Output limit reached: your program printed more than {OUTPUT_LIMIT:,} characters, so it was stopped."
    except BaseException as exc:  # noqa: BLE001 - learner code may raise anything
        error = _format_error(exc)
    finally:
        sys.stdout, sys.stderr, builtins.input = saved
        try:
            channel.flush()
        except OutputLimitExceeded:
            pass
    return namespace, error


def _rerun(code, stdin_text, files):
    """Used by exercise checks: run the learner's program again (fresh folder) with other input."""
    channel = _Channel(None)
    with _Workdir(files):
        _, error = _execute(code, stdin_text.splitlines(), channel, echo=False)
    if error:
        last_line = error.strip().splitlines()[-1]
        raise AssertionError(f"Your program crashed when the input was {stdin_text!r}: {last_line}")
    return "".join(channel.stdout_text)


def _run_check(check, code, namespace, output_text, files):
    scope = dict(namespace)
    scope.update(_output=output_text, _code=code, run_again=lambda stdin="": _rerun(code, stdin, files))
    saved = sys.stdout, sys.stderr, builtins.input
    sys.stdout = sys.stderr = _Silent()
    builtins.input = _make_input([], _Channel(None), echo=False)
    try:
        exec(compile(check, "<check>", "exec"), scope)
        return {"passed": True, "message": "All checks passed."}
    except AssertionError as exc:
        return {"passed": False, "message": str(exc) or "That isn't quite right yet."}
    except BaseException as exc:  # noqa: BLE001 - e.g. NameError when a variable is missing
        return {"passed": False, "message": f"{type(exc).__name__}: {exc}"}
    finally:
        sys.stdout, sys.stderr, builtins.input = saved


def run_user(code, stdin_text, check, emit, files_json="{}"):
    """Entry point called from worker.js. Returns a JSON string describing the outcome.

    `files_json` is a JSON object of name -> text created in the run's private folder first.
    The folder stays alive while the exercise check runs, so checks can inspect files
    the learner's program wrote.
    """
    files = json.loads(files_json or "{}")
    channel = _Channel(emit)
    result = {"status": "ok", "error": None, "check": None}
    with _Workdir(files):
        namespace, error = _execute(code, stdin_text.splitlines(), channel, echo=True)
        if error:
            result.update(status="error", error=error)
            emit("stderr", error if error.endswith("\n") else error + "\n")
        elif check:
            result["check"] = _run_check(check, code, namespace, "".join(channel.stdout_text), files)
    return json.dumps(result)


def lock_down():
    """Defence in depth: stop learner code importing the JS bridge from inside the worker.

    The real boundary is the browser's Worker sandbox plus the page's CSP (no DOM, no
    cookies or localStorage, same-origin-only network, no eval); this just removes the
    obvious doors.
    """
    for name in ("js", "pyodide_js"):
        sys.modules[name] = None
