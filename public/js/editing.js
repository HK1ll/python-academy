// Pure text-editing helpers for the code editor. They take the text and the selection and return an
// "edit": replace text[from:to] with `insert`, then select [selStart, selEnd] in the NEW text.
// No DOM access, so they are unit-tested under Node (tests/js/editing.test.mjs).

export const INDENT = '    ';
const PAIRS = { '(': ')', '[': ']', '{': '}', '"': '"', "'": "'" };
const CLOSERS = new Set([')', ']', '}', '"', "'"]);

const lineStartOf = (text, offset) => (offset === 0 ? 0 : text.lastIndexOf('\n', offset - 1) + 1);

/** Offsets [start, end) of the whole lines touched by a selection (end excludes the final newline). */
export function selectedLines(text, selStart, selEnd) {
  const start = lineStartOf(text, selStart);
  // A selection that ends exactly at the start of a line does not include that line.
  const point = selEnd > selStart && text[selEnd - 1] === '\n' ? selEnd - 1 : selEnd;
  const newline = text.indexOf('\n', point);
  return { start, end: newline === -1 ? text.length : newline };
}

/** 1-based line number of a character offset. */
export function lineOfOffset(text, offset) {
  return text.slice(0, offset).split('\n').length;
}

export function indentLines(text, selStart, selEnd) {
  const { start, end } = selectedLines(text, selStart, selEnd);
  const insert = text
    .slice(start, end)
    .split('\n')
    .map((line) => (line.length ? INDENT + line : line))
    .join('\n');
  return { from: start, to: end, insert, selStart: start, selEnd: start + insert.length };
}

export function dedentLines(text, selStart, selEnd) {
  const { start, end } = selectedLines(text, selStart, selEnd);
  let removedFromFirst = 0;
  const insert = text
    .slice(start, end)
    .split('\n')
    .map((line, index) => {
      const lead = /^( {1,4}|\t)/.exec(line);
      const removed = lead ? lead[0].length : 0;
      if (index === 0) removedFromFirst = removed;
      return line.slice(removed);
    })
    .join('\n');
  if (selStart === selEnd) {
    const caret = Math.max(start, selStart - removedFromFirst);
    return { from: start, to: end, insert, selStart: caret, selEnd: caret };
  }
  return { from: start, to: end, insert, selStart: start, selEnd: start + insert.length };
}

/** Comment (or uncomment) the selected lines with "# ". Returns null when there is nothing to toggle. */
export function toggleComment(text, selStart, selEnd) {
  const { start, end } = selectedLines(text, selStart, selEnd);
  const lines = text.slice(start, end).split('\n');
  const code = lines.filter((line) => line.trim());
  if (code.length === 0) return null;
  let changed;
  if (code.every((line) => /^\s*#/.test(line))) {
    changed = lines.map((line) => line.replace(/^(\s*)# ?/, '$1'));
  } else {
    const column = Math.min(...code.map((line) => /^ */.exec(line)[0].length));
    changed = lines.map((line) => (line.trim() ? `${line.slice(0, column)}# ${line.slice(column)}` : line));
  }
  const insert = changed.join('\n');
  if (selStart === selEnd) {
    const caret = Math.min(Math.max(start, selStart + insert.length - (end - start)), start + insert.length);
    return { from: start, to: end, insert, selStart: caret, selEnd: caret };
  }
  return { from: start, to: end, insert, selStart: start, selEnd: start + insert.length };
}

/** What pressing Enter should do: keep the indentation, indent after a trailing ":", and open bracket pairs. */
export function newLineEdit(text, selStart, selEnd) {
  const start = lineStartOf(text, selStart);
  const before = text.slice(start, selStart);
  const base = /^[ \t]*/.exec(before)[0];
  const opensBlock = before.trimEnd().endsWith(':') && !/^\s*#/.test(before);
  const previous = text[selStart - 1];
  const next = text[selEnd];
  if (selStart === selEnd && previous in PAIRS && PAIRS[previous] === next && '([{'.includes(previous)) {
    const inner = `\n${base}${INDENT}`;
    return { from: selStart, to: selEnd, insert: `${inner}\n${base}`, selStart: selStart + inner.length, selEnd: selStart + inner.length };
  }
  const insert = `\n${opensBlock ? base + INDENT : base}`;
  return { from: selStart, to: selEnd, insert, selStart: selStart + insert.length, selEnd: selStart + insert.length };
}

/**
 * Auto-closing of brackets and quotes when `key` is typed.
 * Returns { skip: true } to step over an existing closer, { edit } to insert a pair (or wrap a selection),
 * or null to let the browser type the key normally.
 */
export function autoCloseAction(text, selStart, selEnd, key) {
  const next = text[selEnd] ?? '';
  const previous = selStart > 0 ? text[selStart - 1] : '';
  if (selStart === selEnd && CLOSERS.has(key) && next === key) return { skip: true };
  if (!(key in PAIRS)) return null;
  const close = PAIRS[key];
  if (selStart !== selEnd) {
    const wrapped = key + text.slice(selStart, selEnd) + close;
    return { edit: { from: selStart, to: selEnd, insert: wrapped, selStart: selStart + 1, selEnd: selEnd + 1 } };
  }
  if (key === '"' || key === "'") {
    if (/\w/.test(previous) || /\w/.test(next)) return null; // an apostrophe inside a word, or a quote after text
    if (previous === key && text[selStart - 2] === key) return null; // typing a triple quote
  } else if (next && !/[\s)\]}.,;:]/.test(next)) {
    return null;
  }
  return { edit: { from: selStart, to: selStart, insert: key + close, selStart: selStart + 1, selEnd: selStart + 1 } };
}

/** Backspace between an empty pair, like ( | ), removes both characters. */
export function pairBackspaceEdit(text, selStart, selEnd) {
  if (selStart !== selEnd || selStart === 0) return null;
  if (PAIRS[text[selStart - 1]] !== text[selStart] || text[selStart] === undefined) return null;
  return { from: selStart - 1, to: selStart + 1, insert: '', selStart: selStart - 1, selEnd: selStart - 1 };
}

/** Remove the indentation shared by every non-empty line (used when running just a selected block). */
export function dedentBlock(text) {
  const lines = text.split('\n');
  const filled = lines.filter((line) => line.trim());
  if (filled.length === 0) return text;
  const shared = Math.min(...filled.map((line) => /^[ \t]*/.exec(line)[0].length));
  return lines.map((line) => line.slice(Math.min(shared, /^[ \t]*/.exec(line)[0].length))).join('\n');
}

/** The line number of the last frame in the learner's own code from a Python traceback, or null. */
export function parseErrorLine(errorText) {
  let line = null;
  for (const match of String(errorText ?? '').matchAll(/File "<your code>", line (\d+)/g)) line = Number(match[1]);
  return line;
}
