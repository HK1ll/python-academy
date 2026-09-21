import { append, clear, h } from './dom.js';
import { highlight } from './highlight.js';
import { inline } from './markup.js';
import { MAX_CODE_CHARS } from './storage.js';

const INDENT = '    ';
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

/** Code editor + run/check controls + output console. */
export function createWorkbench({ runner, store, storageKey, starter, stdin = '', exercise = null, onPass, cleanups }) {
  const editorId = `editor-${storageKey}`;
  const saved = store.getCode(storageKey);
  const editor = h('textarea', {
    id: editorId,
    class: 'editor',
    spellcheck: 'false',
    autocomplete: 'off',
    autocapitalize: 'off',
    autocorrect: 'off',
    wrap: 'off',
    'aria-describedby': `${editorId}-help`,
  });
  editor.value = saved ?? starter;
  editor.maxLength = MAX_CODE_CHARS;

  const stdinBox = h('textarea', { class: 'stdin', rows: '3', spellcheck: 'false', 'aria-label': 'Input for input() calls, one line per call' });
  stdinBox.value = stdin;
  stdinBox.maxLength = 20_000;

  const output = h('pre', { class: 'console', role: 'log', 'aria-live': 'polite', 'aria-label': 'Program output', tabindex: '0' });
  const feedback = h('div', { class: 'feedback', role: 'status', hidden: true });

  const runButton = h('button', { type: 'button', class: 'btn primary', onclick: () => execute(false) }, '▶ Run');
  const checkButton = exercise ? h('button', { type: 'button', class: 'btn success', onclick: () => execute(true) }, '✓ Check answer') : null;
  const stopButton = h('button', { type: 'button', class: 'btn', hidden: true, onclick: () => runner.stop() }, '■ Stop');
  const resetButton = h('button', { type: 'button', class: 'btn ghost', onclick: reset }, '↺ Reset');

  function showFeedback(kind, ...content) {
    feedback.hidden = false;
    feedback.dataset.kind = kind;
    clear(feedback);
    append(feedback, content);
  }

  function setRunning(running) {
    for (const button of [runButton, checkButton]) if (button) button.disabled = running;
    stopButton.hidden = !running;
    editor.readOnly = running;
  }

  function appendOutput(stream, text) {
    const node = document.createTextNode(text);
    if (stream === 'stderr') output.append(h('span', { class: 'stderr' }, node));
    else output.append(node);
    output.scrollTop = output.scrollHeight;
  }

  async function execute(withCheck) {
    if (runner.busy) return;
    clear(output);
    feedback.hidden = true;
    setRunning(true);
    try {
      const result = await runner.run({
        code: editor.value,
        stdin: stdinBox.value,
        check: withCheck ? exercise.check : null,
        files: exercise?.files ?? null,
        timeoutMs: withCheck ? CHECK_TIMEOUT_MS : RUN_TIMEOUT_MS,
        onOutput: appendOutput,
      });
      renderResult(result, withCheck);
    } catch (error) {
      showFeedback('error', `Python could not run: ${error.message}. Reload the page to try again.`);
    } finally {
      setRunning(false);
    }
  }

  function renderResult(result, withCheck) {
    if (result.status === 'timeout') {
      showFeedback('error', h('strong', null, 'Stopped. '), 'Your program ran for more than ', `${(withCheck ? CHECK_TIMEOUT_MS : RUN_TIMEOUT_MS) / 1000}`, ' seconds. Is there a loop that never ends?');
    } else if (result.status === 'stopped') {
      showFeedback('info', 'Stopped.');
    } else if (result.status === 'error') {
      showFeedback('error', h('strong', null, 'Your program stopped with an error. '), 'Read the last line of the message above: it says what went wrong, and the line above it shows where.');
    } else if (withCheck && result.check) {
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

  function reset() {
    editor.value = starter;
    stdinBox.value = stdin;
    store.saveCode(storageKey, editor.value);
    clear(output);
    feedback.hidden = true;
    editor.focus();
  }

  // --- editor ergonomics -------------------------------------------------------------
  let tabMovesFocus = false; // Esc then Tab lets keyboard users leave the editor
  let saveTimer = 0;
  editor.addEventListener('input', () => {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(() => store.saveCode(storageKey, editor.value), 400);
  });
  cleanups.push(() => {
    clearTimeout(saveTimer);
    store.saveCode(storageKey, editor.value);
  });
  editor.addEventListener('blur', () => {
    tabMovesFocus = false;
  });
  editor.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      tabMovesFocus = true;
    } else if (event.key === 'Tab' && !tabMovesFocus) {
      event.preventDefault();
      if (event.shiftKey) dedent();
      else insert(INDENT);
    } else if (event.key === 'Enter' && !event.ctrlKey && !event.metaKey && !event.shiftKey) {
      event.preventDefault();
      insert('\n' + nextIndent());
    } else if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      execute(false);
    } else {
      tabMovesFocus = false;
    }
  });

  function insert(text) {
    editor.focus();
    // execCommand keeps the browser's undo stack intact; fall back if unsupported.
    if (!document.execCommand('insertText', false, text)) {
      editor.setRangeText(text, editor.selectionStart, editor.selectionEnd, 'end');
      editor.dispatchEvent(new Event('input'));
    }
  }

  function currentLine() {
    const start = editor.value.lastIndexOf('\n', editor.selectionStart - 1) + 1;
    return { start, text: editor.value.slice(start, editor.selectionStart) };
  }

  function nextIndent() {
    const { text } = currentLine();
    const base = /^ */.exec(text)[0];
    return text.trimEnd().endsWith(':') ? base + INDENT : base;
  }

  function dedent() {
    const { start } = currentLine();
    const lead = /^ {1,4}/.exec(editor.value.slice(start));
    if (!lead) return;
    const caret = editor.selectionStart;
    editor.setRangeText('', start, start + lead[0].length, 'preserve');
    editor.setSelectionRange(Math.max(start, caret - lead[0].length), Math.max(start, caret - lead[0].length));
    editor.dispatchEvent(new Event('input'));
  }

  // --- optional exercise helpers -----------------------------------------------------
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

  const element = h(
    'section',
    { class: 'workbench', 'aria-label': 'Code editor' },
    h('div', { class: 'toolbar' }, runButton, checkButton, stopButton, resetButton),
    h('label', { class: 'sr-only', for: editorId }, 'Python code'),
    editor,
    h('p', { id: `${editorId}-help`, class: 'muted small' }, 'Tab indents · Esc then Tab leaves the editor · Ctrl+Enter runs'),
    h('details', { class: 'stdin-wrap', open: stdin ? true : null }, h('summary', null, 'Input for input()'), h('p', { class: 'muted small' }, 'One line per input() call.'), stdinBox),
    h('h3', { class: 'console-title' }, 'Output'),
    output,
    feedback,
    helpers,
  );

  return { element, editor, load(code) { editor.value = code; store.saveCode(storageKey, code); } };
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
