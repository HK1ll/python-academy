import { append, clear, h } from './dom.js';
import { dedentBlock, parseErrorLine } from './editing.js';
import { createEditor } from './editor.js';
import { highlight } from './highlight.js';
import { inline } from './markup.js';
import { MAX_CODE_CHARS } from './storage.js';

const RUN_TIMEOUT_MS = 10_000;
const CHECK_TIMEOUT_MS = 20_000;

const STATUS_TEXT = {
  loading: 'Loading Python…',
  restarting: 'Restarting Python…',
  ready: 'Python ready',
  running: 'Running…',
  error: 'Python failed to load',
};

/** Live indicator showing the state of the Python engine. Returns [element, unsubscribe]. */
export function engineStatus(runner) {
  const dot = h('span', { class: 'dot', 'aria-hidden': 'true' });
  const label = h('span', null, STATUS_TEXT.loading);
  const el = h('span', { class: 'engine', role: 'status', 'data-state': 'loading' }, dot, label);
  const off = runner.subscribe((state, detail) => {
    el.dataset.state = state;
    label.textContent = state === 'error' && detail ? `${STATUS_TEXT.error}: ${detail}` : STATUS_TEXT[state];
  });
  return [el, off];
}

/** Shows the read-only files an exercise provides (they exist while the program runs). */
export function providedFiles(files) {
  const entries = Object.entries(files ?? {});
  if (entries.length === 0) return null;
  return h(
    'details',
    { class: 'provided-files', open: true },
    h('summary', null, `Provided ${entries.length === 1 ? 'file' : 'files'}: `, entries.map(([name]) => h('code', null, name))),
    entries.map(([name, text]) => h('figure', { class: 'provided-file' }, h('figcaption', null, name), h('pre', { class: 'code', tabindex: '0' }, text))),
  );
}

function formatSeconds(milliseconds) {
  const seconds = milliseconds / 1000;
  return seconds < 10 ? `${seconds.toFixed(2)} s` : `${seconds.toFixed(1)} s`;
}

/**
 * Code editor + run/check controls + output console. Used by lessons (with an exercise) and by the Playground.
 *  - `persist` optionally replaces the default per-lesson autosave: { load(), save(code), loadStdin?(), saveStdin?(text) }
 *  - `features`: { selectionRun: show "Run selection", reset: show "Reset" (needs `starter`) }
 */
export function createWorkbench({ runner, store, storageKey, starter = '', stdin = '', exercise = null, onPass, cleanups, features = {}, persist = null }) {
  const { selectionRun = false, reset: canReset = true } = features;
  const saver = persist ?? { load: () => store.getCode(storageKey), save: (code) => store.saveCode(storageKey, code) };
  const editorId = `editor-${storageKey}`;

  const ed = createEditor({
    value: saver.load() ?? starter,
    describedBy: `${editorId}-help`,
    maxLength: MAX_CODE_CHARS,
    getSettings: () => store.settings(),
    onRun: () => execute(false),
    onRunSelection: () => selectionRun && execute(false, true),
  });
  const editor = ed.textarea;
  editor.id = editorId;
  ed.applySettings(store.settings());

  const stdinBox = h('textarea', { class: 'stdin', rows: '3', spellcheck: 'false', 'aria-label': 'Input for input() calls, one line per call' });
  stdinBox.value = saver.loadStdin ? saver.loadStdin() : stdin;
  stdinBox.maxLength = 20_000;
  const stdinWrap = h('details', { class: 'stdin-wrap', open: stdinBox.value ? true : null }, h('summary', null, 'Input for input()'), h('p', { class: 'muted small' }, 'One line per input() call.'), stdinBox);

  const output = h('pre', { class: 'console', role: 'log', 'aria-live': 'polite', 'aria-label': 'Program output', tabindex: '0' });
  const runInfo = h('span', { class: 'run-info muted small', role: 'status' });
  const feedback = h('div', { class: 'feedback', role: 'status', hidden: true });

  const runButton = h('button', { type: 'button', class: 'btn primary', title: 'Run the program (Ctrl+Enter)', onclick: () => execute(false) }, '▶ Run');
  const selectionButton = selectionRun ? h('button', { type: 'button', class: 'btn', title: 'Run only the selected code (Ctrl+Shift+Enter)', onclick: () => execute(false, true) }, 'Run selection') : null;
  const checkButton = exercise ? h('button', { type: 'button', class: 'btn success', onclick: () => execute(true) }, '✓ Check answer') : null;
  const stopButton = h('button', { type: 'button', class: 'btn', hidden: true, onclick: () => runner.stop() }, '■ Stop');
  const resetButton = canReset ? h('button', { type: 'button', class: 'btn ghost', onclick: reset }, '↺ Reset') : null;
  const smallerButton = h('button', { type: 'button', class: 'btn ghost small', 'aria-label': 'Smaller text', title: 'Smaller text', onclick: () => changeFontSize(-1) }, 'A−');
  const largerButton = h('button', { type: 'button', class: 'btn ghost small', 'aria-label': 'Larger text', title: 'Larger text', onclick: () => changeFontSize(1) }, 'A+');

  function changeFontSize(delta) {
    const { fontSize } = store.updateSettings({ fontSize: store.settings().fontSize + delta });
    ed.applySettings({ fontSize });
  }

  function showFeedback(kind, ...content) {
    feedback.hidden = false;
    feedback.dataset.kind = kind;
    clear(feedback);
    append(feedback, content);
  }

  function setRunning(running) {
    for (const button of [runButton, selectionButton, checkButton]) if (button) button.disabled = running;
    stopButton.hidden = !running;
    editor.readOnly = running;
  }

  function appendOutput(stream, text) {
    const node = document.createTextNode(text);
    if (stream === 'stderr') output.append(h('span', { class: 'stderr' }, node));
    else output.append(node);
    output.scrollTop = output.scrollHeight;
  }

  function clearOutput() {
    clear(output);
    feedback.hidden = true;
    runInfo.textContent = '';
    ed.clearError();
  }

  async function copyOutput() {
    const text = output.textContent;
    if (!text) {
      runInfo.textContent = 'Nothing to copy yet';
      return;
    }
    try {
      await navigator.clipboard.writeText(text);
      runInfo.textContent = 'Output copied';
    } catch {
      runInfo.textContent = 'Copying is blocked here: select the output and press Ctrl+C';
    }
  }

  async function execute(withCheck, selectionOnly = false) {
    if (runner.busy) {
      stopButton.hidden = false;
      showFeedback('info', 'Python is still busy with a previous run. It stops by itself after at most 10 seconds, or press Stop.');
      return;
    }
    let code = editor.value;
    let lineOffset = 0;
    if (selectionOnly) {
      const selected = ed.getSelection();
      if (!selected.text.trim()) {
        showFeedback('info', 'Select some code in the editor first, then choose "Run selection".');
        return;
      }
      code = dedentBlock(selected.text);
      lineOffset = selected.startLine - 1;
    }
    if (withCheck && exercise) store.recordAttempt(storageKey);
    else store.recordActivity();
    clearOutput();
    setRunning(true);
    const started = performance.now();
    try {
      const result = await runner.run({
        code,
        stdin: stdinBox.value,
        check: withCheck ? exercise.check : null,
        files: exercise?.files ?? null,
        timeoutMs: withCheck ? CHECK_TIMEOUT_MS : RUN_TIMEOUT_MS,
        onOutput: appendOutput,
      });
      renderResult(result, withCheck, lineOffset, performance.now() - started, selectionOnly);
    } catch (error) {
      showFeedback('error', `Python could not run: ${error.message}. Reload the page to try again.`);
    } finally {
      setRunning(false);
    }
  }

  function renderResult(result, withCheck, lineOffset, elapsed, selectionOnly) {
    const took = formatSeconds(elapsed);
    if (result.status === 'timeout') {
      runInfo.textContent = `⏱ Stopped after ${took}`;
      showFeedback('error', h('strong', null, 'Stopped. '), 'Your program ran for more than ', `${(withCheck ? CHECK_TIMEOUT_MS : RUN_TIMEOUT_MS) / 1000}`, ' seconds. Is there a loop that never ends?');
    } else if (result.status === 'stopped') {
      runInfo.textContent = 'Stopped';
      showFeedback('info', 'Stopped.');
    } else if (result.status === 'error') {
      runInfo.textContent = `✗ Error after ${took}`;
      if (/No input left/.test(result.error ?? '')) {
        stdinWrap.open = true;
        stdinBox.focus();
        showFeedback('info', h('strong', null, 'Your program is asking for input. '), 'Type the answers into the Input box (one line per input() call), then run it again.');
        return;
      }
      const line = parseErrorLine(result.error);
      if (line !== null) ed.markError(line + lineOffset);
      showFeedback(
        'error',
        h('strong', null, 'Your program stopped with an error. '),
        line !== null ? `Line ${line + lineOffset} is highlighted in the editor${selectionOnly ? ' (counting from the top of the whole file)' : ''}. ` : '',
        'Read the last line of the message above: it says what went wrong.',
      );
    } else {
      runInfo.textContent = `✓ Finished in ${took}`;
      if (withCheck && result.check) {
        if (result.check.passed) {
          store.markComplete(storageKey);
          showFeedback('success', h('strong', null, '🎉 Correct! '), 'Nice work: exercise complete.');
          onPass?.();
        } else {
          showFeedback('warn', h('strong', null, 'Not quite yet. '), String(result.check.message));
        }
      } else if (!output.hasChildNodes()) {
        showFeedback('info', 'Your program ran successfully but printed nothing. Use print() to show a value.');
      }
    }
  }

  function reset() {
    editor.value = starter;
    stdinBox.value = stdin;
    scheduleSave();
    clearOutput();
    editor.focus();
  }

  // ---- autosave -------------------------------------------------------------------------
  let saveTimer = 0;
  let dirty = false; // only save when the learner actually changed something (viewing must not bump "edited")
  const flush = () => {
    clearTimeout(saveTimer);
    if (!dirty) return;
    dirty = false;
    saver.save(editor.value);
    saver.saveStdin?.(stdinBox.value);
  };
  const scheduleSave = () => {
    dirty = true;
    clearTimeout(saveTimer);
    saveTimer = setTimeout(flush, 400);
  };
  editor.addEventListener('input', scheduleSave);
  stdinBox.addEventListener('input', scheduleSave);
  cleanups.push(flush);

  // If a run started elsewhere (e.g. before switching snippets) ends, don't leave a stale Stop button behind.
  cleanups.push(
    runner.subscribe(() => {
      if (!runner.busy) stopButton.hidden = true;
    }),
  );

  // ---- optional exercise helpers ----------------------------------------------------------
  let helpers = null;
  if (exercise) {
    const hintBox = h('p', { class: 'hint', hidden: true }, h('strong', null, 'Hint: '), ...inline(exercise.hint));
    const solutionBox = h('div', { class: 'solution', hidden: true }, h('p', null, 'One possible solution. Try to understand every line:'), h('pre', { class: 'code' }, h('code', null, highlight(exercise.solution))));
    const hintButton = h('button', { type: 'button', class: 'btn ghost small', 'aria-expanded': 'false', onclick: () => toggle(hintBox, hintButton) }, 'Need a hint?');
    const solutionButton = h('button', { type: 'button', class: 'btn ghost small', 'aria-expanded': 'false', onclick: () => toggle(solutionBox, solutionButton) }, 'Show solution');
    helpers = h('div', { class: 'helpers' }, h('div', { class: 'row' }, hintButton, solutionButton), hintBox, solutionBox);
  }

  function toggle(box, button) {
    box.hidden = !box.hidden;
    button.setAttribute('aria-expanded', String(!box.hidden));
  }

  // ---- editor options & shortcuts ------------------------------------------------------------
  const autoCloseBox = h('input', { type: 'checkbox', id: `${editorId}-autoclose` });
  autoCloseBox.checked = store.settings().autoClose;
  autoCloseBox.addEventListener('change', () => store.updateSettings({ autoClose: autoCloseBox.checked }));
  const options = h(
    'details',
    { class: 'editor-options' },
    h('summary', null, 'Editor options & shortcuts'),
    h('label', { class: 'check-option', for: `${editorId}-autoclose` }, autoCloseBox, ' Auto-close brackets and quotes'),
    h(
      'ul',
      { class: 'shortcut-list' },
      h('li', null, h('kbd', null, 'Ctrl'), '+', h('kbd', null, 'Enter'), ' run the program'),
      selectionRun ? h('li', null, h('kbd', null, 'Ctrl'), '+', h('kbd', null, 'Shift'), '+', h('kbd', null, 'Enter'), ' run only the selected code') : null,
      h('li', null, h('kbd', null, 'Tab'), ' / ', h('kbd', null, 'Shift'), '+', h('kbd', null, 'Tab'), ' indent / dedent (also several selected lines)'),
      h('li', null, h('kbd', null, 'Ctrl'), '+', h('kbd', null, '/'), ' comment or uncomment the selected lines'),
      h('li', null, h('kbd', null, 'Esc'), ' then ', h('kbd', null, 'Tab'), ' move to the next control (the editor otherwise keeps Tab)'),
    ),
  );

  const element = h(
    'section',
    { class: 'workbench', 'aria-label': 'Code editor' },
    h('div', { class: 'toolbar' }, runButton, selectionButton, checkButton, stopButton, resetButton, h('span', { class: 'grow' }), smallerButton, largerButton),
    h('label', { class: 'sr-only', for: editorId }, 'Python code'),
    ed.element,
    h('p', { id: `${editorId}-help`, class: 'muted small' }, 'Tab indents · Esc then Tab leaves the editor · Ctrl+Enter runs'),
    options,
    stdinWrap,
    h('div', { class: 'console-head' }, h('h3', { class: 'console-title' }, 'Output'), runInfo, h('span', { class: 'grow' }), h('button', { type: 'button', class: 'btn ghost small', onclick: copyOutput }, 'Copy'), h('button', { type: 'button', class: 'btn ghost small', onclick: clearOutput }, 'Clear')),
    output,
    feedback,
    helpers,
  );

  return {
    element,
    editor,
    focus: () => ed.focus(),
    load(code) {
      editor.value = code;
      scheduleSave();
    },
  };
}

/** Read-only highlighted code sample with its own Run button and inline output. */
export function createSnippet({ runner, code, onOpenInPlayground, cleanups }) {
  const output = h('pre', { class: 'console snippet-output', role: 'log', 'aria-live': 'polite', hidden: true });
  const runButton = h('button', { type: 'button', class: 'btn small primary', onclick: run }, '▶ Run');
  const playButton = h('button', { type: 'button', class: 'btn small ghost', onclick: () => onOpenInPlayground(code) }, 'Edit in Playground');

  const off = runner.subscribe(() => {
    runButton.disabled = runner.busy;
  });
  cleanups.push(off);

  async function run() {
    if (runner.busy) return;
    output.hidden = false;
    clear(output);
    try {
      await runner.run({
        code,
        timeoutMs: RUN_TIMEOUT_MS,
        onOutput: (stream, text) => {
          output.append(stream === 'stderr' ? h('span', { class: 'stderr' }, text) : document.createTextNode(text));
        },
      });
    } catch (error) {
      output.append(h('span', { class: 'stderr' }, `Python could not run: ${error.message}`));
    }
  }

  return h(
    'figure',
    { class: 'snippet' },
    h('pre', { class: 'code', tabindex: '0' }, h('code', null, highlight(code))),
    h('div', { class: 'snippet-actions' }, runButton, playButton),
    output,
  );
}
