// Run with: node --test tests/js/editing.test.mjs
import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  INDENT,
  autoCloseAction,
  dedentBlock,
  dedentLines,
  indentLines,
  lineOfOffset,
  newLineEdit,
  pairBackspaceEdit,
  parseErrorLine,
  selectedLines,
  toggleComment,
} from '../../public/js/editing.js';

/** Apply an edit the way the editor does, so tests can compare resulting text and selection. */
function apply(text, edit) {
  return { text: text.slice(0, edit.from) + edit.insert + text.slice(edit.to), selStart: edit.selStart, selEnd: edit.selEnd };
}

test('selectedLines covers whole lines and ignores a trailing line start', () => {
  const text = 'aaa\nbbb\nccc';
  assert.deepEqual(selectedLines(text, 5, 5), { start: 4, end: 7 }, 'caret inside line 2');
  assert.deepEqual(selectedLines(text, 1, 6), { start: 0, end: 7 }, 'selection across lines 1-2');
  assert.deepEqual(selectedLines(text, 0, 4), { start: 0, end: 3 }, 'selection ending right after a newline excludes the next line');
  assert.deepEqual(selectedLines('\nx', 0, 0), { start: 0, end: 0 }, 'caret on a leading empty line');
  assert.deepEqual(selectedLines('abc', 3, 3), { start: 0, end: 3 }, 'caret at the very end');
});

test('lineOfOffset is 1-based', () => {
  assert.equal(lineOfOffset('a\nb\nc', 0), 1);
  assert.equal(lineOfOffset('a\nb\nc', 2), 2);
  assert.equal(lineOfOffset('a\nb\nc', 4), 3);
});

test('indent and dedent whole blocks, leaving empty lines alone', () => {
  const text = 'if x:\n    a\n\n    b';
  const indented = apply(text, indentLines(text, 0, text.length));
  assert.equal(indented.text, `${INDENT}if x:\n${INDENT}    a\n\n${INDENT}    b`);
  const back = apply(indented.text, dedentLines(indented.text, indented.selStart, indented.selEnd));
  assert.equal(back.text, text, 'dedent undoes indent');
});

test('dedent removes at most one indent level, tabs included, and moves a lone caret with the text', () => {
  assert.equal(apply('        x', dedentLines('        x', 8, 8)).text, '    x');
  assert.equal(apply('\tx', dedentLines('\tx', 2, 2)).text, 'x');
  assert.equal(apply('  x', dedentLines('  x', 3, 3)).text, 'x', 'only two spaces available');
  assert.equal(apply('x', dedentLines('x', 1, 1)).text, 'x', 'nothing to remove');
  const moved = apply('    x', dedentLines('    x', 5, 5));
  assert.equal(moved.selStart, 1, 'caret follows the text');
});

test('toggleComment comments at the shared indentation and uncomments again', () => {
  const text = 'def f():\n    a = 1\n\n    b = 2';
  const on = apply(text, toggleComment(text, 0, text.length));
  assert.equal(on.text, '# def f():\n#     a = 1\n\n#     b = 2', 'shared column is 0 because the def line starts at column 0');
  const off = apply(on.text, toggleComment(on.text, on.selStart, on.selEnd));
  assert.equal(off.text, text);

  const inner = '    a = 1\n    b = 2';
  assert.equal(apply(inner, toggleComment(inner, 0, inner.length)).text, '    # a = 1\n    # b = 2', 'comment after the shared indent');
});

test('toggleComment: mixed selection comments everything, blank selection does nothing', () => {
  const mixed = '# done\nprint(1)';
  assert.equal(apply(mixed, toggleComment(mixed, 0, mixed.length)).text, '# # done\n# print(1)');
  assert.equal(toggleComment('\n\n', 0, 2), null);
  const single = 'x = 1';
  const edit = toggleComment(single, 2, 2);
  assert.equal(apply(single, edit).text, '# x = 1');
  assert.equal(edit.selStart, 4, 'a lone caret moves right with the inserted "# "');
});

test('newLineEdit keeps indentation, adds a level after a colon, ignores colons in comments', () => {
  const at = (text, caret = text.length) => apply(text, newLineEdit(text, caret, caret));
  assert.equal(at('    x = 1').text, '    x = 1\n    ');
  assert.equal(at('if ready:').text, 'if ready:\n    ');
  assert.equal(at('    for i in r:').text, '    for i in r:\n        ');
  assert.equal(at('# note:').text, '# note:\n', 'a comment ending in ":" does not open a block');
  assert.equal(at('x = {"a": 1}').text, 'x = {"a": 1}\n', 'a closing brace is not a block opener');
  const result = at('if ready:');
  assert.equal(result.selStart, 'if ready:\n    '.length, 'caret lands after the new indentation');
});

test('newLineEdit opens a bracket pair onto three lines', () => {
  const text = 'call()';
  const result = apply(text, newLineEdit(text, 5, 5));
  assert.equal(result.text, 'call(\n    \n)');
  assert.equal(result.selStart, 'call(\n    '.length, 'caret is on the indented middle line');
  const inner = apply('    items = []', newLineEdit('    items = []', 13, 13));
  assert.equal(inner.text, '    items = [\n        \n    ]', 'the inner line is indented one level deeper than the opening line');
});

test('autoCloseAction pairs brackets only in sensible places', () => {
  const auto = (text, caret, key) => autoCloseAction(text, caret, caret, key);
  assert.equal(apply('', auto('', 0, '(').edit).text, '()');
  assert.equal(apply('', auto('', 0, '[').edit).selStart, 1, 'caret between the pair');
  assert.equal(apply('x = ', auto('x = ', 4, '{').edit).text, 'x = {}');
  assert.equal(auto('foo', 2, '('), null, 'no pair when typing before more text');
  assert.ok(auto('foo)', 3, '('), 'pair is fine right before a closer');
});

test('autoCloseAction quotes: pair at word boundaries, not inside words or for triple quotes', () => {
  const auto = (text, caret, key) => autoCloseAction(text, caret, caret, key);
  assert.equal(apply('x = ', auto('x = ', 4, '"').edit).text, 'x = ""');
  assert.equal(auto("don", 3, "'"), null, "an apostrophe in \"don't\" is not a quote");
  assert.equal(auto('print', 5, '"'), null, 'no auto-quote glued to a word');
  assert.equal(auto('""', 2, '"'), null, 'typing the third quote of """ is left alone');
  assert.deepEqual(auto('""', 1, '"'), { skip: true }, 'typing the closing quote steps over it');
});

test('autoCloseAction steps over closers and wraps selections', () => {
  assert.deepEqual(autoCloseAction('f()', 2, 2, ')'), { skip: true });
  assert.equal(autoCloseAction('f()', 1, 1, ')'), null, 'no closer ahead, type normally');
  const wrapped = apply('say hello', autoCloseAction('say hello', 4, 9, '"').edit);
  assert.equal(wrapped.text, 'say "hello"');
  assert.deepEqual([wrapped.selStart, wrapped.selEnd], [5, 10], 'the wrapped text stays selected');
  assert.equal(autoCloseAction('abc', 1, 1, 'x'), null);
});

test('pairBackspaceEdit removes both halves of an empty pair only', () => {
  assert.equal(apply('f()', pairBackspaceEdit('f()', 2, 2)).text, 'f');
  assert.equal(apply('x = ""', pairBackspaceEdit('x = ""', 5, 5)).text, 'x = ');
  assert.equal(pairBackspaceEdit('f(x)', 3, 3), null, 'pair is not empty');
  assert.equal(pairBackspaceEdit('f()', 2, 3), null, 'a selection is deleted normally');
  assert.equal(pairBackspaceEdit('(', 0, 0), null);
  assert.equal(pairBackspaceEdit('(', 1, 1), null, 'nothing after the caret');
});

test('dedentBlock strips only the shared indentation', () => {
  assert.equal(dedentBlock('    a\n      b\n\n    c'), 'a\n  b\n\nc');
  assert.equal(dedentBlock('a\n  b'), 'a\n  b');
  assert.equal(dedentBlock('   \n  '), '   \n  ', 'all-blank text is left alone');
});

test('parseErrorLine finds the last line in the learner code, or null', () => {
  const traceback = 'Traceback (most recent call last):\n  File "<your code>", line 7, in <module>\n    main()\n  File "<your code>", line 3, in main\n    1 / 0\nZeroDivisionError: division by zero\n';
  assert.equal(parseErrorLine(traceback), 3, 'the innermost frame in the learner code');
  assert.equal(parseErrorLine('  File "<your code>", line 12\n    if x\n        ^\nSyntaxError: expected \':\''), 12);
  assert.equal(parseErrorLine('ValueError: no location'), null);
  assert.equal(parseErrorLine(null), null);
  assert.equal(parseErrorLine('File "/lib/python/json.py", line 5'), null, 'library frames are ignored');
});
