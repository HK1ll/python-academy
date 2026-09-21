// Run with: node --test tests/js/snippets.test.mjs
// Playground snippets and editor settings, including persistence, migration and hostile stored data.
import assert from 'node:assert/strict';
import { beforeEach, test } from 'node:test';

// A tiny in-memory localStorage so persistence and reloading can be tested under Node.
const backing = new Map();
globalThis.localStorage = {
  getItem: (key) => (backing.has(key) ? backing.get(key) : null),
  setItem: (key, value) => void backing.set(key, String(value)),
  removeItem: (key) => void backing.delete(key),
};
const { createStore } = await import('../../public/js/storage.js');

const KEY = 'python-academy:v1';
const IDS = ['alpha', 'beta'];
let clock;
const makeStore = () => createStore(IDS, { today: () => '2026-09-21', now: () => ++clock });
beforeEach(() => {
  backing.clear();
  clock = 1_000_000;
});

test('create: ids are 8 lowercase alphanumerics, unique, newest first', () => {
  const store = makeStore();
  const a = store.createSnippet({ name: 'First', code: 'print(1)' });
  const b = store.createSnippet({ name: 'Second' });
  assert.match(a.id, /^[a-z0-9]{8}$/);
  assert.notEqual(a.id, b.id);
  assert.deepEqual(store.snippets().map((s) => s.name), ['Second', 'First'], 'newest first');
  assert.equal(store.snippet(a.id).code, 'print(1)');
  assert.equal(store.snippetCount(), 2);
});

test('names are trimmed, whitespace-collapsed, capped at 60 and never empty', () => {
  const store = makeStore();
  assert.equal(store.createSnippet({ name: '   a    b   ' }).name, 'a b');
  assert.equal(store.createSnippet({ name: 'x'.repeat(200) }).name.length, 60);
  assert.equal(store.createSnippet({ name: '   ' }).name, 'Untitled');
  assert.equal(store.createSnippet({ name: 42 }).name, 'Untitled');
  assert.equal(store.createSnippet({}).name, 'Untitled');
  const html = store.createSnippet({ name: '<img src=x onerror=alert(1)>' });
  assert.equal(html.name, '<img src=x onerror=alert(1)>', 'stored verbatim as text: it is only ever displayed via textContent');
});

test('returned snippets are copies: editing them does not change the store', () => {
  const store = makeStore();
  const made = store.createSnippet({ name: 'Keep', code: 'a' });
  made.code = 'HACKED';
  store.snippets()[0].name = 'HACKED';
  store.snippet(made.id).code = 'HACKED';
  assert.equal(store.snippet(made.id).code, 'a');
  assert.equal(store.snippet(made.id).name, 'Keep');
});

test('update changes only known fields, caps sizes and bumps the updated time', () => {
  const store = makeStore();
  const made = store.createSnippet({ name: 'N', code: 'a', stdin: 'x' });
  const updated = store.updateSnippet(made.id, { name: '  Renamed  ', code: 'b'.repeat(60_000), stdin: 's'.repeat(30_000), id: 'evilevil', created: 1 });
  assert.equal(updated.name, 'Renamed');
  assert.equal(updated.code.length, 50_000);
  assert.equal(updated.stdin.length, 20_000);
  assert.equal(updated.id, made.id, 'the id cannot be changed');
  assert.equal(updated.created, made.created, 'the creation time cannot be changed');
  assert.ok(updated.updated > made.updated);
  assert.equal(store.updateSnippet('nonexistent', { name: 'x' }), undefined);
  assert.equal(store.updateSnippet(made.id, null), undefined);
  assert.equal(store.updateSnippet(made.id, { code: 12345 }).code.length, 50_000, 'a non-string code value is ignored');
});

test('duplicate copies the content with a "(copy)" name that still fits the limit', () => {
  const store = makeStore();
  const original = store.createSnippet({ name: 'x'.repeat(60), code: 'print(1)', stdin: '5' });
  const copy = store.duplicateSnippet(original.id);
  assert.notEqual(copy.id, original.id);
  assert.equal(copy.code, 'print(1)');
  assert.equal(copy.stdin, '5');
  assert.ok(copy.name.endsWith(' (copy)') && copy.name.length <= 60, copy.name);
  assert.equal(store.duplicateSnippet('nope'), null);
  store.updateSnippet(copy.id, { code: 'changed' });
  assert.equal(store.snippet(original.id).code, 'print(1)', 'the copy is independent');
});

test('delete: the newest remaining snippet becomes active; deleting the last leaves none', () => {
  const store = makeStore();
  const a = store.createSnippet({ name: 'A' });
  const b = store.createSnippet({ name: 'B' });
  const c = store.createSnippet({ name: 'C' });
  store.setActiveSnippet(c.id);
  assert.equal(store.deleteSnippet(c.id), b.id, 'B is the newest of what is left');
  assert.equal(store.activeSnippetId(), b.id);
  assert.equal(store.deleteSnippet(a.id), b.id, 'deleting a non-active snippet keeps the active one');
  assert.equal(store.deleteSnippet('nope'), b.id);
  assert.equal(store.deleteSnippet(b.id), null);
  assert.equal(store.snippetCount(), 0);
  assert.equal(store.activeSnippetId(), null);
});

test('setActiveSnippet ignores unknown ids', () => {
  const store = makeStore();
  const a = store.createSnippet({ name: 'A' });
  store.setActiveSnippet(a.id);
  store.setActiveSnippet('zzzzzzzz');
  store.setActiveSnippet(undefined);
  assert.equal(store.activeSnippetId(), a.id);
});

test('the snippet limit is enforced for create and duplicate', () => {
  const store = makeStore();
  const first = store.createSnippet({ name: 'first' });
  for (let i = 1; i < store.maxSnippets; i++) assert.ok(store.createSnippet({ name: `s${i}` }));
  assert.equal(store.snippetCount(), store.maxSnippets);
  assert.equal(store.createSnippet({ name: 'one too many' }), null);
  assert.equal(store.duplicateSnippet(first.id), null);
  store.deleteSnippet(first.id);
  assert.ok(store.createSnippet({ name: 'fits again' }));
});

test('snippets and the active snippet survive a reload', () => {
  const store = makeStore();
  const a = store.createSnippet({ name: 'Persisted', code: 'print("hi")', stdin: '7' });
  store.setActiveSnippet(a.id);
  const reloaded = makeStore();
  assert.deepEqual(reloaded.snippet(a.id), store.snippet(a.id));
  assert.equal(reloaded.activeSnippetId(), a.id);
});

test('the old single playground scratchpad migrates into a first snippet, once', () => {
  backing.set(KEY, JSON.stringify({ version: 2, completed: {}, attempts: {}, days: [], code: { playground: 'print("my old work")' } }));
  const store = makeStore();
  assert.equal(store.snippetCount(), 1);
  const [migrated] = store.snippets();
  assert.equal(migrated.name, 'My first snippet');
  assert.equal(migrated.code, 'print("my old work")');
  assert.equal(store.activeSnippetId(), migrated.id);
  const again = makeStore();
  assert.equal(again.snippetCount(), 1, 'reloading must not migrate a second time');
  assert.equal(again.snippets()[0].id, migrated.id);
});

test('an empty old scratchpad is not migrated', () => {
  backing.set(KEY, JSON.stringify({ version: 2, code: { playground: '   \n' } }));
  assert.equal(makeStore().snippetCount(), 0);
});

test('stored snippets are re-validated on load: bad ids, sizes, duplicates and types are dropped', () => {
  const good = { id: 'goodgood', name: 'Good', code: 'ok', stdin: '', created: 5, updated: 6 };
  const tooMany = Array.from({ length: 150 }, (_, i) => ({ id: `n${String(i).padStart(7, '0')}`, name: `n${i}`, code: '', created: i + 1 }));
  backing.set(KEY, JSON.stringify({
    version: 2,
    snippets: [
      good,
      { ...good, name: 'duplicate id' },
      { id: '../etc/passwd', name: 'path', code: 'x' },
      { id: 'UPPERCAS', name: 'caps', code: 'x' },
      { id: 'short', name: 'short', code: 'x' },
      { id: 'bigbigbi', name: 'big', code: 'x'.repeat(50_001) },
      { id: 'nocodeco', name: 'no code' },
      { id: 'numnumnu', name: 'num', code: 42 },
      null, 7, 'string', [],
      ...tooMany,
    ],
    activeSnippet: 'gone1234',
    settings: { fontSize: 999, autoClose: 'yes' },
  }));
  const store = makeStore();
  assert.equal(store.snippetCount(), 100, 'capped at the maximum');
  assert.equal(store.snippet('goodgood').name, 'Good', 'the first of two duplicate ids wins');
  for (const bad of ['../etc/passwd', 'UPPERCAS', 'short', 'bigbigbi', 'nocodeco', 'numnumnu']) assert.equal(store.snippet(bad), undefined, `${bad} must be dropped`);
  assert.equal(store.activeSnippetId(), null, 'an active id that does not exist is ignored');
  assert.deepEqual(store.settings(), { fontSize: 15, autoClose: true }, 'invalid settings fall back to defaults');
});

test('corrupt stored JSON does not crash the store', () => {
  backing.set(KEY, '{not json');
  const store = makeStore();
  assert.equal(store.snippetCount(), 0);
  assert.ok(store.createSnippet({ name: 'still works' }));
});

test('settings: valid changes stick, invalid values are ignored, everything persists', () => {
  const store = makeStore();
  assert.deepEqual(store.settings(), { fontSize: 15, autoClose: true });
  assert.deepEqual(store.updateSettings({ fontSize: 18, autoClose: false }), { fontSize: 18, autoClose: false });
  for (const bad of [5, 99, 15.5, '20', NaN, null, undefined, {}]) {
    assert.equal(store.updateSettings({ fontSize: bad }).fontSize, 18, `fontSize ${String(bad)} must be ignored`);
  }
  assert.equal(store.updateSettings({ autoClose: 'no' }).autoClose, false, 'a non-boolean is ignored');
  assert.equal(store.updateSettings(null).fontSize, 18);
  assert.deepEqual(makeStore().settings(), { fontSize: 18, autoClose: false });
  const copy = store.settings();
  copy.fontSize = 24;
  assert.equal(store.settings().fontSize, 18, 'settings() returns a copy');
});

test('export includes snippets but keeps settings and the active snippet on this device', () => {
  const store = makeStore();
  const a = store.createSnippet({ name: 'Shared', code: 'print(1)' });
  store.setActiveSnippet(a.id);
  store.updateSettings({ fontSize: 20 });
  const backup = store.exportData();
  assert.equal(backup.snippets.length, 1);
  assert.equal(backup.snippets[0].name, 'Shared');
  assert.equal('settings' in backup, false);
  assert.equal('activeSnippet' in backup, false);
});

test('import adds new snippets, never overwrites existing ones, and respects the limit', () => {
  const source = makeStore();
  const shared = source.createSnippet({ name: 'Shared', code: 'REMOTE' });
  source.createSnippet({ name: 'Only remote', code: 'x' });
  const backup = JSON.stringify(source.exportData());

  backing.clear();
  const local = makeStore();
  local.createSnippet({ name: 'Local only', code: 'LOCAL' });
  const result = local.importData(backup);
  assert.equal(result.snippetsAdded, 2);
  assert.equal(local.snippetCount(), 3);

  // Same id already exists locally with different content: the local one wins.
  local.updateSnippet(shared.id, { code: 'EDITED LOCALLY' });
  const again = local.importData(backup);
  assert.equal(again.snippetsAdded, 0, 'importing the same backup twice adds nothing');
  assert.equal(local.snippet(shared.id).code, 'EDITED LOCALLY');
});

test('import sanitises hostile snippets and honours the cap', () => {
  const store = makeStore();
  const hostile = {
    app: 'python-academy',
    version: 2,
    snippets: [
      { id: 'goodgood', name: 'Fine', code: 'ok' },
      { id: '<script>', name: 'bad id', code: 'x' },
      { id: 'hugehuge', name: 'huge', code: 'x'.repeat(60_000) },
      { id: 'wrongtyp', name: 'typed', code: { evil: true } },
    ],
    settings: { fontSize: 24 },
    activeSnippet: 'goodgood',
  };
  const result = store.importData(JSON.stringify(hostile));
  assert.equal(result.snippetsAdded, 1);
  assert.deepEqual(store.snippets().map((s) => s.id), ['goodgood']);
  assert.equal(store.settings().fontSize, 15, 'imported settings are ignored');
  assert.equal(store.activeSnippetId(), null, 'an imported active snippet is ignored');

  backing.clear(); // start from an empty browser so the count below is exact
  const full = makeStore();
  for (let i = 0; i < 99; i++) full.createSnippet({ name: `s${i}` });
  assert.equal(full.snippetCount(), 99);
  const many = { app: 'python-academy', version: 2, snippets: Array.from({ length: 5 }, (_, i) => ({ id: `import0${i}xx`.slice(0, 8), name: 'i', code: '' })) };
  assert.equal(new Set(many.snippets.map((s) => s.id)).size, 5, 'five distinct valid ids');
  assert.equal(full.importData(JSON.stringify(many)).snippetsAdded, 1, 'only one slot was free');
  assert.equal(full.snippetCount(), 100);
});

test('clearAll removes snippets and settings too', () => {
  const store = makeStore();
  store.createSnippet({ name: 'Gone' });
  store.updateSettings({ fontSize: 20 });
  store.clearAll();
  assert.equal(store.snippetCount(), 0);
  assert.deepEqual(store.settings(), { fontSize: 15, autoClose: true });
  assert.equal(backing.has(KEY), false);
});
