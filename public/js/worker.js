// Runs Python (Pyodide/WebAssembly) off the main thread. A Web Worker has no DOM, no
// cookies and no localStorage, and the page CSP restricts it to same-origin requests
// with no eval, so learner code is confined to a sandbox on the learner's own machine.
import { loadPyodide } from '../vendor/pyodide/pyodide.mjs';

const LIMITS = { code: 100_000, stdin: 20_000, check: 50_000, files: 10, fileChars: 20_000 };
const FILE_NAME = /^[A-Za-z0-9_][A-Za-z0-9_.-]{0,39}$/;
let runUser = null;

const ready = (async () => {
  const pyodide = await loadPyodide({ indexURL: new URL('../vendor/pyodide/', import.meta.url).href });
  const response = await fetch(new URL('../py/harness.py', import.meta.url), { credentials: 'omit' });
  if (!response.ok) throw new Error(`Could not load the Python runner (${response.status})`);
  const scope = pyodide.globals.get('dict')();
  pyodide.runPython(await response.text(), { globals: scope });
  scope.get('lock_down')();
  runUser = scope.get('run_user');
  postMessage({ type: 'ready' });
})().catch((error) => {
  postMessage({ type: 'fatal', message: String(error?.message ?? error) });
});

function validFiles(files) {
  if (files === null) return true;
  if (typeof files !== 'object' || Array.isArray(files)) return false;
  const entries = Object.entries(files);
  return (
    entries.length <= LIMITS.files &&
    entries.every(([name, text]) => FILE_NAME.test(name) && typeof text === 'string' && text.length <= LIMITS.fileChars)
  );
}

function isValid(msg) {
  return (
    msg &&
    msg.type === 'run' &&
    Number.isSafeInteger(msg.id) &&
    typeof msg.code === 'string' && msg.code.length <= LIMITS.code &&
    typeof msg.stdin === 'string' && msg.stdin.length <= LIMITS.stdin &&
    (msg.check === null || (typeof msg.check === 'string' && msg.check.length <= LIMITS.check)) &&
    validFiles(msg.files)
  );
}

self.addEventListener('message', async (event) => {
  const msg = event.data;
  if (!isValid(msg)) return;
  await ready;
  if (!runUser) return;
  const emit = (stream, text) => postMessage({ type: 'output', id: msg.id, stream: String(stream), text: String(text) });
  try {
    const result = JSON.parse(runUser(msg.code, msg.stdin, msg.check, emit, JSON.stringify(msg.files ?? {})));
    postMessage({ type: 'done', id: msg.id, status: result.status, error: result.error, check: result.check });
  } catch (error) {
    postMessage({ type: 'done', id: msg.id, status: 'error', error: String(error?.message ?? error), check: null });
  }
});
