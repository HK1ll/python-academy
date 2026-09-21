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
const PLAYGROUND = 'playground';
const DATE_PATTERN = /^(\d{4})-(\d{2})-(\d{2})$/;

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

export function createStore(lessonIds, { today = localToday } = {}) {
  const known = new Set(lessonIds);
  const codeKeys = new Set([...lessonIds, PLAYGROUND]);
  let state = emptyState();

  function emptyState() {
    return { completed: {}, attempts: {}, days: [], code: {} };
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

  return {
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

    /** A plain object safe to serialise as a backup file. */
    exportData() {
      return { app: APP_ID, version: SCHEMA_VERSION, exportedOn: today(), ...structuredClone(state) };
    },

    /**
     * Merge a backup file into the current progress, keeping the most progress from both sides:
     * completions are unioned (earliest date wins), attempt counts take the larger value, activity days
     * are unioned and saved code is only added where this browser has none. Throws Error(message) on bad input.
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
      const result = { lessonsAdded: 0, draftsAdded: 0 };

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
}

export { MAX_CODE_CHARS, PLAYGROUND };
