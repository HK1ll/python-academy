// Progress and draft code live only in this browser's localStorage. Everything read
// back is validated (shape, known ids, size) because storage can be edited by anyone
// with access to the browser, and it is only ever rendered as text, never as HTML.

const KEY = 'python-academy:v1';
const MAX_CODE_CHARS = 50_000;
const PLAYGROUND = 'playground';

export function createStore(lessonIds) {
  const known = new Set(lessonIds);
  const codeKeys = new Set([...lessonIds, PLAYGROUND]);
  let state = { completed: {}, code: {} };

  try {
    const raw = localStorage.getItem(KEY);
    if (raw && raw.length < 5_000_000) state = sanitize(JSON.parse(raw));
  } catch {
    // Storage blocked/corrupt: continue with in-memory state.
  }

  function sanitize(data) {
    const clean = { completed: {}, code: {} };
    if (!data || typeof data !== 'object' || Array.isArray(data)) return clean;
    if (data.completed && typeof data.completed === 'object') {
      for (const id of known) if (data.completed[id] === true) clean.completed[id] = true;
    }
    if (data.code && typeof data.code === 'object') {
      for (const id of codeKeys) {
        const value = data.code[id];
        if (typeof value === 'string' && value.length <= MAX_CODE_CHARS) clean.code[id] = value;
      }
    }
    return clean;
  }

  function persist() {
    try {
      localStorage.setItem(KEY, JSON.stringify(state));
    } catch {
      // Quota exceeded or blocked: progress simply won't survive a reload.
    }
  }

  return {
    isComplete: (id) => state.completed[id] === true,
    completedCount: () => Object.keys(state.completed).length,
    markComplete(id) {
      if (!known.has(id)) return;
      state.completed[id] = true;
      persist();
    },
    getCode: (id) => (codeKeys.has(id) ? state.code[id] : undefined),
    saveCode(id, code) {
      if (!codeKeys.has(id) || typeof code !== 'string') return;
      state.code[id] = code.slice(0, MAX_CODE_CHARS);
      persist();
    },
    clearAll() {
      state = { completed: {}, code: {} };
      try {
        localStorage.removeItem(KEY);
      } catch {
        // ignore
      }
    },
  };
}

export { MAX_CODE_CHARS, PLAYGROUND };
