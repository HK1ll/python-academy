// Progress and draft code live only in this browser's localStorage. Everything read back
// (from storage OR from an imported backup file) is validated: shape, known lesson ids,
// value ranges and sizes. It is only ever rendered as text, never as HTML.

const KEY = 'python-academy:v1'; // same key as before, so progress saved by older versions is kept
const APP_ID = 'python-academy';
const SCHEMA_VERSION = 2;
const MAX_CODE_CHARS = 50_000;
const MAX_ATTEMPTS = 100_000;
const MAX_DAYS = 400;
const MAX_IMPORT_CHARS = 2_000_000;
const MAX_STDIN_CHARS = 20_000;
const MAX_SNIPPETS = 100;
const MAX_NAME_CHARS = 60;
const PLAYGROUND = 'playground';
const DATE_PATTERN = /^(\d{4})-(\d{2})-(\d{2})$/;
const SNIPPET_ID = /^[a-z0-9]{8}$/;
const DEFAULT_SETTINGS = Object.freeze({ fontSize: 15, autoClose: true });
const FONT_SIZE_RANGE = [11, 24];

function randomId() {
  const bytes = new Uint8Array(8);
  if (globalThis.crypto?.getRandomValues) globalThis.crypto.getRandomValues(bytes);
  else for (let i = 0; i < bytes.length; i++) bytes[i] = Math.floor(Math.random() * 256);
  return Array.from(bytes, (byte) => (byte % 36).toString(36)).join('');
}

function sanitizeSettings(raw) {
  const fontSize = raw && Number.isSafeInteger(raw.fontSize) && raw.fontSize >= FONT_SIZE_RANGE[0] && raw.fontSize <= FONT_SIZE_RANGE[1] ? raw.fontSize : DEFAULT_SETTINGS.fontSize;
  const autoClose = raw && typeof raw.autoClose === 'boolean' ? raw.autoClose : DEFAULT_SETTINGS.autoClose;
  return { fontSize, autoClose };
}

/** Apply a settings patch, ignoring any field whose value is invalid (the current value stays). */
function mergeSettings(current, patch) {
  const next = { ...current };
  if (patch && Number.isSafeInteger(patch.fontSize) && patch.fontSize >= FONT_SIZE_RANGE[0] && patch.fontSize <= FONT_SIZE_RANGE[1]) next.fontSize = patch.fontSize;
  if (patch && typeof patch.autoClose === 'boolean') next.autoClose = patch.autoClose;
  return next;
}

function cleanName(value) {
  const name = typeof value === 'string' ? value.replace(/\s+/g, ' ').trim().slice(0, MAX_NAME_CHARS) : '';
  return name || 'Untitled';
}

const pad = (n) => String(n).padStart(2, '0');

/** Today's date in the learner's own time zone, as YYYY-MM-DD. */
export function localToday() {
  const now = new Date();
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
}

function isValidDay(value) {
  if (typeof value !== 'string') return false;
  const match = DATE_PATTERN.exec(value);
  if (!match) return false;
  const [year, month, day] = [Number(match[1]), Number(match[2]), Number(match[3])];
  const date = new Date(Date.UTC(year, month - 1, day));
  return date.getUTCFullYear() === year && date.getUTCMonth() === month - 1 && date.getUTCDate() === day;
}

/** Whole days since 1970 for a YYYY-MM-DD string (UTC maths, so daylight saving can't skew it). */
function dayNumber(value) {
  const [year, month, day] = value.split('-').map(Number);
  return Math.round(Date.UTC(year, month - 1, day) / 86_400_000);
}

/** Current and longest run of consecutive active days. A streak stays alive until a full day is missed. */
export function computeStreak(days, today) {
  const numbers = [...new Set(days.filter(isValidDay).map(dayNumber))].sort((a, b) => a - b);
  let longest = 0;
  let run = 0;
  for (let i = 0; i < numbers.length; i++) {
    run = i > 0 && numbers[i] === numbers[i - 1] + 1 ? run + 1 : 1;
    longest = Math.max(longest, run);
  }
  let current = 0;
  const last = numbers[numbers.length - 1];
  const now = dayNumber(today);
  if (last !== undefined && (last === now || last === now - 1)) {
    current = 1;
    for (let i = numbers.length - 1; i > 0 && numbers[i] === numbers[i - 1] + 1; i--) current++;
  }
  return { current, longest, activeDays: numbers.length };
}

export function createStore(lessonIds, { today = localToday, now = Date.now } = {}) {
  const known = new Set(lessonIds);
  const codeKeys = new Set([...lessonIds, PLAYGROUND]);
  let state = emptyState();

  function emptyState() {
    return { completed: {}, attempts: {}, days: [], code: {}, snippets: [], activeSnippet: null, settings: { ...DEFAULT_SETTINGS } };
  }

  /** A valid snippet, or null. Ids, names and sizes are all re-checked, whatever their source. */
  function sanitizeSnippet(raw) {
    if (!raw || typeof raw !== 'object' || typeof raw.id !== 'string' || !SNIPPET_ID.test(raw.id)) return null;
    if (typeof raw.code !== 'string' || raw.code.length > MAX_CODE_CHARS) return null;
    const stamp = (value) => (Number.isSafeInteger(value) && value > 0 ? value : now());
    return {
      id: raw.id,
      name: cleanName(raw.name),
      code: raw.code,
      stdin: typeof raw.stdin === 'string' && raw.stdin.length <= MAX_STDIN_CHARS ? raw.stdin : '',
      created: stamp(raw.created),
      updated: stamp(raw.updated),
    };
  }

  function sanitize(data) {
    const clean = emptyState();
    if (!data || typeof data !== 'object' || Array.isArray(data)) return clean;

    if (data.completed && typeof data.completed === 'object' && !Array.isArray(data.completed)) {
      for (const id of known) {
        const entry = data.completed[id];
        if (entry === true) clean.completed[id] = { at: null }; // saved by the first version of the app
        else if (entry && typeof entry === 'object') clean.completed[id] = { at: isValidDay(entry.at) ? entry.at : null };
      }
    }
    if (data.attempts && typeof data.attempts === 'object' && !Array.isArray(data.attempts)) {
      for (const id of known) {
        const count = data.attempts[id];
        if (Number.isSafeInteger(count) && count > 0) clean.attempts[id] = Math.min(count, MAX_ATTEMPTS);
      }
    }
    if (Array.isArray(data.days)) {
      clean.days = [...new Set(data.days.filter(isValidDay))].sort().slice(-MAX_DAYS);
    }
    if (data.code && typeof data.code === 'object' && !Array.isArray(data.code)) {
      for (const id of codeKeys) {
        const value = data.code[id];
        if (typeof value === 'string' && value.length <= MAX_CODE_CHARS) clean.code[id] = value;
      }
    }
    if (Array.isArray(data.snippets)) {
      const seen = new Set();
      for (const raw of data.snippets) {
        const snippet = sanitizeSnippet(raw);
        if (snippet && !seen.has(snippet.id) && seen.size < MAX_SNIPPETS) {
          seen.add(snippet.id);
          clean.snippets.push(snippet);
        }
      }
    }
    if (typeof data.activeSnippet === 'string' && clean.snippets.some((s) => s.id === data.activeSnippet)) clean.activeSnippet = data.activeSnippet;
    clean.settings = sanitizeSettings(data.settings);
    return clean;
  }

  try {
    const raw = localStorage.getItem(KEY);
    if (raw && raw.length < 5_000_000) state = sanitize(JSON.parse(raw));
  } catch {
    // Storage blocked or corrupt: continue with in-memory state.
  }

  function persist() {
    try {
      localStorage.setItem(KEY, JSON.stringify({ version: SCHEMA_VERSION, ...state }));
    } catch {
      // Quota exceeded or blocked: progress simply won't survive a reload.
    }
  }

  function recordActivity() {
    const day = today();
    if (state.days[state.days.length - 1] === day) return false;
    if (!state.days.includes(day)) state.days = [...state.days, day].sort().slice(-MAX_DAYS);
    return true;
  }

  const findSnippet = (id) => state.snippets.find((snippet) => snippet.id === id);
  const uniqueId = () => {
    const taken = new Set(state.snippets.map((snippet) => snippet.id));
    for (;;) {
      const id = randomId();
      if (!taken.has(id)) return id;
    }
  };
  const newestFirst = (a, b) => b.created - a.created || a.id.localeCompare(b.id);

  // Progress made before snippets existed: the single playground scratchpad becomes the first snippet.
  if (state.snippets.length === 0 && typeof state.code[PLAYGROUND] === 'string' && state.code[PLAYGROUND].trim()) {
    const migrated = sanitizeSnippet({ id: uniqueId(), name: 'My first snippet', code: state.code[PLAYGROUND], stdin: '', created: now(), updated: now() });
    if (migrated) {
      state.snippets.push(migrated);
      state.activeSnippet = migrated.id;
      persist();
    }
  }

  const api = {
    today,
    isComplete: (id) => Object.hasOwn(state.completed, id),
    completedAt: (id) => state.completed[id]?.at ?? null,
    completedCount: () => Object.keys(state.completed).length,
    attempts: (id) => state.attempts[id] ?? 0,
    totalAttempts: () => Object.values(state.attempts).reduce((sum, n) => sum + n, 0),
    streak: () => computeStreak(state.days, today()),

    markComplete(id) {
      if (!known.has(id)) return;
      if (!state.completed[id]) state.completed[id] = { at: today() };
      recordActivity();
      persist();
    },
    /** Called whenever the learner presses Check on a lesson exercise. */
    recordAttempt(id) {
      if (!known.has(id)) return;
      state.attempts[id] = Math.min((state.attempts[id] ?? 0) + 1, MAX_ATTEMPTS);
      recordActivity();
      persist();
    },
    /** Called when the learner runs any code (lesson, snippet or playground). */
    recordActivity() {
      if (recordActivity()) persist();
    },

    getCode: (id) => (codeKeys.has(id) ? state.code[id] : undefined),
    saveCode(id, code) {
      if (!codeKeys.has(id) || typeof code !== 'string') return;
      state.code[id] = code.slice(0, MAX_CODE_CHARS);
      persist();
    },

    // ---- editor settings ------------------------------------------------------------------
    settings: () => ({ ...state.settings }),
    updateSettings(patch) {
      state.settings = mergeSettings(state.settings, patch);
      persist();
      return { ...state.settings };
    },

    // ---- Playground snippets ---------------------------------------------------------------
    /** Newest first. Copies, so callers can't change stored data by accident. */
    snippets: () => [...state.snippets].sort(newestFirst).map((snippet) => ({ ...snippet })),
    snippet: (id) => {
      const found = findSnippet(id);
      return found ? { ...found } : undefined;
    },
    snippetCount: () => state.snippets.length,
    maxSnippets: MAX_SNIPPETS,
    activeSnippetId: () => (state.activeSnippet && findSnippet(state.activeSnippet) ? state.activeSnippet : null),
    setActiveSnippet(id) {
      if (!findSnippet(id)) return;
      state.activeSnippet = id;
      persist();
    },
    /** Returns the new snippet, or null when the limit is reached. */
    createSnippet({ name = 'Untitled', code = '', stdin = '' } = {}) {
      if (state.snippets.length >= MAX_SNIPPETS) return null;
      const snippet = sanitizeSnippet({ id: uniqueId(), name, code: String(code).slice(0, MAX_CODE_CHARS), stdin: String(stdin).slice(0, MAX_STDIN_CHARS), created: now(), updated: now() });
      if (!snippet) return null;
      state.snippets.push(snippet);
      persist();
      return { ...snippet };
    },
    updateSnippet(id, patch) {
      const snippet = findSnippet(id);
      if (!snippet || !patch || typeof patch !== 'object') return undefined;
      if ('name' in patch) snippet.name = cleanName(patch.name);
      if (typeof patch.code === 'string') snippet.code = patch.code.slice(0, MAX_CODE_CHARS);
      if (typeof patch.stdin === 'string') snippet.stdin = patch.stdin.slice(0, MAX_STDIN_CHARS);
      snippet.updated = now();
      persist();
      return { ...snippet };
    },
    duplicateSnippet(id) {
      const original = findSnippet(id);
      if (!original) return null;
      const name = `${original.name.slice(0, MAX_NAME_CHARS - 7)} (copy)`;
      return api.createSnippet({ name, code: original.code, stdin: original.stdin });
    },
    /** Deletes a snippet and returns the id that should be active afterwards (or null if none are left). */
    deleteSnippet(id) {
      if (!findSnippet(id)) return api.activeSnippetId();
      state.snippets = state.snippets.filter((snippet) => snippet.id !== id);
      if (state.activeSnippet === id) state.activeSnippet = [...state.snippets].sort(newestFirst)[0]?.id ?? null;
      persist();
      return api.activeSnippetId();
    },

    /** A plain object safe to serialise as a backup file (settings and the active snippet stay on this device). */
    exportData() {
      const { completed, attempts, days, code, snippets } = structuredClone(state);
      return { app: APP_ID, version: SCHEMA_VERSION, exportedOn: today(), completed, attempts, days, code, snippets };
    },

    /**
     * Merge a backup file into the current progress, keeping the most progress from both sides:
     * completions are unioned (earliest date wins), attempt counts take the larger value, activity days
     * are unioned, and saved code and snippets are only added where this browser has none. Throws Error(message) on bad input.
     */
    importData(text) {
      if (typeof text !== 'string' || text.length > MAX_IMPORT_CHARS) throw new Error('That file is too large to be a progress backup.');
      let data;
      try {
        data = JSON.parse(text);
      } catch {
        throw new Error('That file is not valid JSON.');
      }
      if (!data || typeof data !== 'object' || data.app !== APP_ID) throw new Error('That is not a Python Academy progress file.');
      if (!Number.isSafeInteger(data.version) || data.version < 1 || data.version > SCHEMA_VERSION) {
        throw new Error('That backup was made by a newer version of the app.');
      }
      const incoming = sanitize(data);
      const result = { lessonsAdded: 0, draftsAdded: 0, snippetsAdded: 0 };

      for (const [id, entry] of Object.entries(incoming.completed)) {
        const mine = state.completed[id];
        if (!mine) {
          state.completed[id] = entry;
          result.lessonsAdded++;
        } else if (entry.at && (!mine.at || entry.at < mine.at)) {
          mine.at = entry.at;
        }
      }
      for (const [id, count] of Object.entries(incoming.attempts)) {
        state.attempts[id] = Math.max(state.attempts[id] ?? 0, count);
      }
      state.days = [...new Set([...state.days, ...incoming.days])].sort().slice(-MAX_DAYS);
      for (const [id, code] of Object.entries(incoming.code)) {
        if (state.code[id] === undefined) {
          state.code[id] = code;
          result.draftsAdded++;
        }
      }
      for (const snippet of incoming.snippets) {
        if (state.snippets.length >= MAX_SNIPPETS) break;
        if (findSnippet(snippet.id)) continue; // never overwrite a snippet that already exists here
        state.snippets.push(snippet);
        result.snippetsAdded++;
      }
      persist();
      return result;
    },

    clearAll() {
      state = emptyState();
      try {
        localStorage.removeItem(KEY);
      } catch {
        // ignore
      }
    },
  };
  return api;
}

export { MAX_CODE_CHARS, MAX_NAME_CHARS, MAX_STDIN_CHARS, PLAYGROUND };
