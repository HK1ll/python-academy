// Run with: node --test tests/js/download.test.mjs
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { safeFileName } from '../../public/js/download.js';

test('safeFileName keeps simple names and turns spaces into dashes', () => {
  assert.equal(safeFileName('my snippet'), 'my-snippet');
  assert.equal(safeFileName('FizzBuzz_v2'), 'FizzBuzz_v2');
  assert.equal(safeFileName('a.b-c_d'), 'a.b-c_d');
});

test('safeFileName removes path tricks and odd characters', () => {
  assert.equal(safeFileName('../../etc/passwd'), 'etc-passwd');
  assert.equal(safeFileName('C:\\Windows\\System32'), 'C-Windows-System32');
  assert.equal(safeFileName('a/b\\c:d*e?f"g<h>i|j'), 'a-b-c-d-e-f-g-h-i-j');
  assert.equal(safeFileName('<script>alert(1)</script>'), 'script-alert-1-script');
  assert.equal(safeFileName('.hidden'), 'hidden');
  assert.equal(safeFileName('name.'), 'name');
});

test('safeFileName falls back when nothing usable is left', () => {
  assert.equal(safeFileName(''), 'snippet');
  assert.equal(safeFileName('   '), 'snippet');
  assert.equal(safeFileName('???'), 'snippet');
  assert.equal(safeFileName(null), 'snippet');
  assert.equal(safeFileName(undefined, 'x'), 'x');
  assert.equal(safeFileName('日本語'), 'snippet');
});

test('safeFileName folds accents and caps the length', () => {
  assert.equal(safeFileName('café'), 'cafe');
  const long = safeFileName('a'.repeat(300));
  assert.equal(long.length, 50);
  assert.equal(safeFileName(`${'a'.repeat(49)}-tail`).endsWith('-'), false, 'no dangling separator after truncation');
});
