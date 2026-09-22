"""Verifies lesson content and the execution harness using plain CPython."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

import build  # noqa: E402

spec = importlib.util.spec_from_file_location("harness", BASE / "public" / "py" / "harness.py")
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)

LESSONS = build.build()


def run(code, stdin="", check=None, files=None):
    chunks = []
    emit = lambda stream, text: chunks.append((stream, text))  # noqa: E731
    result = json.loads(harness.run_user(code, stdin, check, emit, json.dumps(files or {})))
    return result, "".join(t for s, t in chunks if s == "stdout"), "".join(t for s, t in chunks if s == "stderr")


class LessonContent(unittest.TestCase):
    def test_generated_json_is_up_to_date(self):
        on_disk = (BASE / "public" / "data" / "lessons.json").read_text(encoding="utf-8")
        self.assertEqual(on_disk, build.render(), "run `python build.py`")

    def test_solutions_pass_and_starters_fail(self):
        for lesson in LESSONS:
            ex = lesson["exercise"]
            with self.subTest(lesson=lesson["id"], part="solution"):
                result, _, err = run(ex["solution"], ex.get("stdin", ""), ex["check"], ex.get("files"))
                self.assertEqual(result["status"], "ok", err)
                self.assertTrue(result["check"]["passed"], result["check"]["message"])
            with self.subTest(lesson=lesson["id"], part="starter"):
                result, _, _ = run(ex["starter"], ex.get("stdin", ""), ex["check"], ex.get("files"))
                passed = result["status"] == "ok" and result["check"]["passed"]
                self.assertFalse(passed, "the untouched starter code must not pass its own check")

    def test_sections_list_every_lesson_once_in_order(self):
        data = json.loads((BASE / "public" / "data" / "lessons.json").read_text(encoding="utf-8"))
        ids = [lesson["id"] for lesson in data["lessons"]]
        self.assertEqual([i for section in data["sections"] for i in section["ids"]], ids)
        self.assertTrue(all(section["title"].strip() for section in data["sections"]))

    def test_display_only_examples_are_valid_python(self):
        found = 0
        for lesson in LESSONS:
            for block in lesson["blocks"]:
                if block["type"] == "codeonly":
                    found += 1
                    with self.subTest(lesson=lesson["id"]):
                        compile(block["text"], "<example>", "exec")
        self.assertGreater(found, 0)

    def test_pbkdf2_example_really_works_where_openssl_exists(self):
        # The lesson shows hashlib.pbkdf2_hmac (not runnable in the browser build); prove the shown call is right.
        import hashlib

        key = hashlib.pbkdf2_hmac("sha256", b"hunter2", b"0" * 16, 600_000)
        self.assertEqual(len(key), 32)

    def test_static_output_blocks_match_reality(self):
        for lesson in LESSONS:
            blocks = lesson["blocks"]
            for before, after in zip(blocks, blocks[1:]):
                if before["type"] == "code" and after["type"] == "output":
                    if after["text"].startswith("Traceback"):
                        continue  # error demos: exact caret lines vary by Python version
                    with self.subTest(lesson=lesson["id"], code=before["text"][:40]):
                        result, out, err = run(before["text"])
                        self.assertEqual(result["status"], "ok", err)
                        self.assertEqual(out.rstrip("\n"), after["text"])


class PlaygroundExamples(unittest.TestCase):
    def test_generated_examples_json_is_up_to_date(self):
        on_disk = (BASE / "public" / "data" / "examples.json").read_text(encoding="utf-8")
        self.assertEqual(on_disk, build.render_examples(), "run `python build.py`")

    def test_every_example_runs_and_prints_something(self):
        examples = build.build_examples()
        self.assertGreaterEqual(len(examples), 10)
        for example in examples:
            with self.subTest(example=example["id"]):
                result, out, err = run(example["code"], example.get("stdin", ""))
                self.assertEqual(result["status"], "ok", err)
                self.assertTrue(out.strip(), "an example must print something so learners see it working")

    def test_examples_cover_every_category(self):
        used = {example["category"] for example in build.build_examples()}
        self.assertEqual(used, set(build.CATEGORIES))

    def test_guessing_game_example_is_deterministic(self):
        example = next(e for e in build.build_examples() if e["id"] == "guessing-game")
        _, out, _ = run(example["code"], example["stdin"])
        self.assertIn("You got it in 4 tries!", out)


class HarnessBehaviour(unittest.TestCase):
    def test_print_and_input_echo(self):
        result, out, _ = run('name = input("Name? ")\nprint("Hi", name)', "Ada")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(out, "Name? Ada\nHi Ada\n")

    def test_missing_input_gives_friendly_error(self):
        result, _, err = run("input()")
        self.assertEqual(result["status"], "error")
        self.assertIn("Input box", err)

    def test_runtime_error_traceback_hides_harness_frames(self):
        result, _, err = run("x = 1\nprint(1 / 0)")
        self.assertEqual(result["status"], "error")
        self.assertIn("ZeroDivisionError", err)
        self.assertIn('File "<your code>", line 2', err)
        self.assertNotIn("harness.py", err)

    def test_syntax_error_is_reported(self):
        result, _, err = run("if True print(1)")
        self.assertEqual(result["status"], "error")
        self.assertIn("SyntaxError", err)

    def test_system_exit_is_not_an_error(self):
        result, out, _ = run('print("a")\nraise SystemExit\nprint("b")')
        self.assertEqual(result["status"], "ok")
        self.assertEqual(out, "a\n")

    def test_output_limit_cannot_be_swallowed(self):
        code = "while True:\n    try:\n        print('x' * 1000)\n    except Exception:\n        pass\n"
        result, out, err = run(code)
        self.assertEqual(result["status"], "error")
        self.assertIn("Output limit", err)
        self.assertLessEqual(len(out), harness.OUTPUT_LIMIT)

    def test_streams_restored_after_run(self):
        before = sys.stdout, sys.stderr
        import builtins

        original_input = builtins.input
        run("print(1)")
        run("raise ValueError")
        self.assertEqual((sys.stdout, sys.stderr), before)
        self.assertIs(builtins.input, original_input)

    def test_state_does_not_leak_between_runs(self):
        run("secret = 42")
        result, _, err = run("print(secret)")
        self.assertEqual(result["status"], "error")
        self.assertIn("NameError", err)

    def test_check_failure_message_and_missing_name(self):
        result, _, _ = run("x = 1", check='assert x == 2, "x should be 2"')
        self.assertEqual(result["check"], {"passed": False, "message": "x should be 2"})
        result, _, _ = run("x = 1", check="assert y == 2")
        self.assertFalse(result["check"]["passed"])
        self.assertIn("NameError", result["check"]["message"])

    def test_check_output_from_user_functions_is_silenced(self):
        code = 'def f():\n    print("noisy")\n    return 1\n'
        result, out, _ = run(code, check="assert f() == 1")
        self.assertTrue(result["check"]["passed"])
        self.assertEqual(out, "")

    def test_files_written_by_a_run_do_not_leak_into_the_next_run(self):
        run('open("secret.txt", "w").close()\nprint(open("secret.txt").read() == "")')
        result, out, err = run('import os\nprint(os.path.exists("secret.txt"))')
        self.assertEqual(out.strip(), "False", err)

    def test_workdir_is_cleaned_up_and_state_restored(self):
        import os

        cwd, path = os.getcwd(), list(sys.path)
        _, out, _ = run('import os\nprint(os.getcwd())\nopen("a.txt", "w").write("x")')
        workdir = out.strip()
        self.assertFalse(os.path.exists(workdir), "temporary folder should be deleted")
        self.assertEqual(os.getcwd(), cwd)
        self.assertEqual(sys.path, path)
        run("import os\nos.chdir('..')")  # learner wandering off must not break restoration
        self.assertEqual(os.getcwd(), cwd)

    def test_modules_created_by_a_run_are_purged(self):
        code = 'open("tmpmod.py", "w").write("VALUE = 1\\n")\nimport tmpmod\nprint(tmpmod.VALUE)'
        result, out, err = run(code)
        self.assertEqual(out.strip(), "1", err)
        self.assertNotIn("tmpmod", sys.modules)

    def test_provided_files_exist_and_are_validated(self):
        _, out, err = run('print(open("data.txt").read().strip())', files={"data.txt": "hello\n"})
        self.assertEqual(out.strip(), "hello", err)
        for bad in ({"../evil.txt": "x"}, {"a/b.txt": "x"}, {".hidden": "x"}, {"ok.txt": 5}):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    run("print(1)", files=bad)
        with self.assertRaises(ValueError):
            run("print(1)", files={f"f{i}.txt": "x" for i in range(11)})

    def test_check_can_inspect_files_the_program_wrote(self):
        result, _, _ = run('open("out.txt", "w").write("hi")', check='assert open("out.txt").read() == "hi"')
        self.assertTrue(result["check"]["passed"], result["check"])

    def test_logging_state_resets_between_runs(self):
        code = 'import logging, sys\nlogging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stdout)\nlogging.info("hi")\n'
        _, out1, _ = run(code)
        _, out2, _ = run(code)
        self.assertIn("INFO: hi", out1)
        self.assertIn("INFO: hi", out2, "a second run must not be silenced by the first run's logging handler")

    def test_run_again_uses_fresh_input(self):
        code = "print(int(input()) * 2)"
        result, _, _ = run(code, "1", check='assert run_again("21").strip() == "42"')
        self.assertTrue(result["check"]["passed"], result["check"])


if __name__ == "__main__":
    unittest.main()
