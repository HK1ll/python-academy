import { h } from './dom.js';

// Minimal Python syntax highlighter. Builds <span> elements with textContent only.
const KEYWORDS = new Set([
  'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
  'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not',
  'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield', 'True', 'False', 'None',
]);
const BUILTINS = new Set([
  'print', 'len', 'range', 'int', 'str', 'float', 'bool', 'list', 'dict', 'set', 'tuple', 'input',
  'type', 'sum', 'min', 'max', 'sorted', 'abs', 'round', 'enumerate', 'zip', 'isinstance', 'open',
  'reversed', 'map', 'filter', 'any', 'all', 'super', 'self',
]);

// Capture groups: 1 comment, 2 string (with optional prefix, unterminated allowed), 3 number, 4 identifier.
const TOKEN =
  /(#[^\n]*)|((?:[rRbBfFuU]{0,2})(?:"""[\s\S]*?(?:"""|$)|'''[\s\S]*?(?:'''|$)|"(?:\\.|[^"\\\n])*(?:"|$)|'(?:\\.|[^'\\\n])*(?:'|$)))|(\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b)|(\b[A-Za-z_]\w*\b)/g;

export function highlight(source) {
  const nodes = [];
  let last = 0;
  let previousWord = '';
  for (const match of source.matchAll(TOKEN)) {
    if (match.index > last) nodes.push(source.slice(last, match.index));
    const [text, comment, string, number, word] = match;
    let cls = null;
    if (comment) cls = 'tok-comment';
    else if (string) cls = 'tok-string';
    else if (number) cls = 'tok-number';
    else if (word) {
      if (KEYWORDS.has(word)) cls = 'tok-keyword';
      else if (previousWord === 'def' || previousWord === 'class') cls = 'tok-def';
      else if (BUILTINS.has(word)) cls = 'tok-builtin';
      previousWord = word;
    }
    nodes.push(cls ? h('span', { class: cls }, text) : text);
    last = match.index + text.length;
  }
  if (last < source.length) nodes.push(source.slice(last));
  const fragment = document.createDocumentFragment();
  for (const node of nodes) fragment.append(node);
  return fragment;
}
