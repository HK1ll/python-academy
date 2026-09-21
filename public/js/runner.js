// Main-thread controller for the Python worker. Runs one program at a time, enforces
// a wall-clock timeout by terminating the worker (the only reliable way to stop an
// infinite loop), and transparently starts a fresh worker afterwards.

// The CSP enforces Trusted Types for scripts and allows exactly one policy name, so the
// only URL that can ever be handed to `new Worker()` is our own same-origin worker file.
const WORKER_URL = new URL('./worker.js', import.meta.url).href;
const workerPolicy = globalThis.trustedTypes?.createPolicy('python-academy-worker', {
  createScriptURL(url) {
    if (new URL(url, location.href).href !== WORKER_URL) throw new TypeError('Blocked worker URL');
    return WORKER_URL;
  },
});

function createWorker() {
  return new Worker(workerPolicy ? workerPolicy.createScriptURL(WORKER_URL) : WORKER_URL, { type: 'module' });
}

export function createRunner() {
  const listeners = new Set();
  let worker = null;
  let state = 'loading'; // loading | ready | running | restarting | error
  let detail = '';
  let current = null;
  let sequence = 0;
  let ready = Promise.resolve();

  function setState(next, message = '') {
    state = next;
    detail = message;
    for (const listener of listeners) listener(state, detail);
  }

  function spawn(restarting) {
    setState(restarting ? 'restarting' : 'loading');
    const instance = createWorker();
    worker = instance;
    ready = new Promise((resolve, reject) => {
      instance.addEventListener('message', (event) => {
        if (instance !== worker) return;
        const msg = event.data;
        if (!msg || typeof msg.type !== 'string') return;
        if (msg.type === 'ready') {
          setState('ready');
          resolve();
        } else if (msg.type === 'fatal') {
          setState('error', String(msg.message));
          reject(new Error(String(msg.message)));
        } else if (msg.type === 'output') {
          if (current && msg.id === current.id && typeof msg.text === 'string') {
            current.onOutput?.(msg.stream === 'stderr' ? 'stderr' : 'stdout', msg.text);
          }
        } else if (msg.type === 'done') {
          if (current && msg.id === current.id) finish({ status: msg.status, error: msg.error, check: msg.check });
        }
      });
      instance.addEventListener('error', (event) => {
        if (instance !== worker) return;
        setState('error', event.message || 'The Python worker failed to start.');
        reject(new Error(event.message || 'worker error'));
      });
    });
    ready.catch(() => {}); // failures are surfaced through state and run()
  }

  function finish(result) {
    if (!current) return;
    const { resolve, timer } = current;
    clearTimeout(timer);
    current = null;
    if (state === 'running') setState('ready');
    resolve(result);
  }

  function restart() {
    worker?.terminate();
    spawn(true);
  }

  spawn(false);

  return {
    get state() {
      return state;
    },
    get detail() {
      return detail;
    },
    get busy() {
      return current !== null;
    },
    subscribe(listener) {
      listeners.add(listener);
      listener(state, detail);
      return () => listeners.delete(listener);
    },
    async run({ code, stdin = '', check = null, files = null, onOutput, timeoutMs = 10_000 }) {
      if (current) throw new Error('Python is already running a program.');
      const id = ++sequence;
      const marker = { id };
      current = marker; // reserve the slot while the engine finishes loading
      try {
        await ready;
      } catch (error) {
        current = null;
        throw error;
      }
      return new Promise((resolve) => {
        marker.onOutput = onOutput;
        marker.resolve = resolve;
        marker.timer = setTimeout(() => {
          finish({ status: 'timeout', error: `Stopped after ${timeoutMs / 1000} seconds.`, check: null });
          restart();
        }, timeoutMs);
        setState('running');
        worker.postMessage({ type: 'run', id, code, stdin, check, files });
      });
    },
    stop() {
      if (!current || !current.resolve) return;
      finish({ status: 'stopped', error: null, check: null });
      restart();
    },
  };
}
