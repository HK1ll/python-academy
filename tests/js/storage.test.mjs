// Run with: node --test tests/js/storage.test.mjs
// storage.js only touches localStorage inside try/catch, so it works (in memory) under Node.
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { computeStreak, createStore } from '../../public/js/storage.js';

const IDS = ['alpha', 'beta', 'gamma'];
const makeStore = (today = '2026-09-21') => createStore(IDS, { today: () => today });

test('completing a lesson records the date once and counts it', () => {
  const store = makeStore('2026-09-21');
  assert.equal(store.completedCount(), 0);
  store.markComplete('alpha');
  assert.equal(store.isComplete('alpha'), true);
  assert.equal(store.completedAt('alpha'), '2026-09-21');
  const later = createStore(IDS, { today: () => '2026-10-01' });
  later.importData(JSON.stringify(store.exportData()));
  later.markComplete('alpha'); // already complete: the original date must not move
  assert.equal(later.completedAt('alpha'), '2026-09-21');
  assert.equal(later.completedCount(), 1);
});

test('unknown lesson ids are ignored everywhere', () => {
  const store = makeStore();
  store.markComplete('nope');
  store.recordAttempt('nope');
  store.saveCode('nope', 'x = 1');
  assert.equal(store.completedCount(), 0);
  assert.equal(store.totalAttempts(), 0);
  assert.equal(store.getCode('nope'), undefined);
  assert.equal(store.isComplete('constructor'), false, 'inherited object keys must not look like lessons');
  assert.equal(store.isComplete('__proto__'), false);
});

test('attempts accumulate per lesson', () => {
  const store = makeStore();
  store.recordAttempt('alpha');
  store.recordAttempt('alpha');
  store.recordAttempt('beta');
  assert.equal(store.attempts('alpha'), 2);
  assert.equal(store.attempts('gamma'), 0);
  assert.equal(store.totalAttempts(), 3);
});

test('code drafts: playground allowed, size capped', () => {
  const store = makeStore();
  store.saveCode('playground', 'print(1)');
  assert.equal(store.getCode('playground'), 'print(1)');
  store.saveCode('alpha', 'x'.repeat(60_000));
  assert.equal(store.getCode('alpha').length, 50_000);
});

test('streak: consecutive days, gaps, and a streak that survives until a day is missed', () => {
  assert.deepEqual(computeStreak([], '2026-09-21'), { current: 0, longest: 0, activeDays: 0 });
  assert.deepEqual(computeStreak(['2026-09-19', '2026-09-20', '2026-09-21'], '2026-09-21'), { current: 3, longest: 3, activeDays: 3 });
  assert.equal(computeStreak(['2026-09-19', '2026-09-20'], '2026-09-21').current, 2, 'yesterday still counts: today is not over');
  assert.equal(computeStreak(['2026-09-18', '2026-09-19'], '2026-09-21').current, 0, 'a fully missed day breaks it');
  const gappy = computeStreak(['2026-09-01', '2026-09-02', '2026-09-03', '2026-09-10', '2026-09-11'], '2026-09-11');
  assert.deepEqual(gappy, { current: 2, longest: 3, activeDays: 5 });
  assert.equal(computeStreak(['2026-09-21', '2026-09-21'], '2026-09-21').activeDays, 1, 'duplicates collapse');
});

test('streak is stable across month, year and daylight-saving boundaries', () => {
  assert.equal(computeStreak(['2026-12-30', '2026-12-31', '2027-01-01'], '2027-01-01').current, 3);
  assert.equal(computeStreak(['2028-02-28', '2028-02-29', '2028-03-01'], '2028-03-01').current, 3, 'leap day');
  assert.equal(computeStreak(['2026-03-28', '2026-03-29', '2026-03-30'], '2026-03-30').current, 3, 'DST change weekend');
  assert.equal(computeStreak(['2026-10-24', '2026-10-25', '2026-10-26'], '2026-10-26').current, 3, 'DST change weekend');
});

test('recording activity adds each day once', () => {
  let day = '2026-09-20';
  const store = createStore(IDS, { today: () => day });
  store.recordActivity();
  store.recordActivity();
  day = '2026-09-21';
  store.recordActivity();
  assert.deepEqual(store.streak(), { current: 2, longest: 2, activeDays: 2 });
});

test('export -> import round trip on a fresh browser restores everything', () => {
  const a = makeStore('2026-09-21');
  a.markComplete('alpha');
  a.recordAttempt('beta');
  a.saveCode('beta', 'print("draft")');
  const backup = JSON.stringify(a.exportData());

  const b = makeStore('2026-09-22');
  const result = b.importData(backup);
  assert.deepEqual(result, { lessonsAdded: 1, draftsAdded: 1 });
  assert.equal(b.isComplete('alpha'), true);
  assert.equal(b.completedAt('alpha'), '2026-09-21');
  assert.equal(b.attempts('beta'), 1);
  assert.equal(b.getCode('beta'), 'print("draft")');
  assert.equal(b.streak().activeDays, 1);
});

test('import merges: keeps the most progress and never overwrites local drafts', () => {
  const local = makeStore('2026-09-25');
  local.markComplete('alpha'); // completed 2026-09-25 here
  local.recordAttempt('alpha');
  local.recordAttempt('alpha');
  local.saveCode('beta', 'LOCAL');

  const other = makeStore('2026-09-10');
  other.markComplete('alpha'); // completed earlier on another device
  other.markComplete('gamma');
  other.recordAttempt('alpha');
  other.saveCode('beta', 'REMOTE');
  other.saveCode('gamma', 'REMOTE-GAMMA');

  const result = local.importData(JSON.stringify(other.exportData()));
  assert.deepEqual(result, { lessonsAdded: 1, draftsAdded: 1 });
  assert.equal(local.completedAt('alpha'), '2026-09-10', 'earliest completion date wins');
  assert.equal(local.isComplete('gamma'), true);
  assert.equal(local.attempts('alpha'), 2, 'larger attempt count wins');
  assert.equal(local.getCode('beta'), 'LOCAL', 'local draft must not be overwritten');
  assert.equal(local.getCode('gamma'), 'REMOTE-GAMMA');
  assert.equal(local.streak().activeDays, 2);
});

test('import rejects anything that is not a valid Python Academy backup', () => {
  const store = makeStore();
  const reject = (input, pattern) => assert.throws(() => store.importData(input), pattern);
  reject('not json {', /not valid JSON/);
  reject('[]', /not a Python Academy/);
  reject('null', /not a Python Academy/);
  reject('"just a string"', /not a Python Academy/);
  reject(JSON.stringify({ app: 'something-else', version: 2 }), /not a Python Academy/);
  reject(JSON.stringify({ app: 'python-academy', version: 99 }), /newer version/);
  reject(JSON.stringify({ app: 'python-academy', version: 'two' }), /newer version/);
  reject(JSON.stringify({ app: 'python-academy' }), /newer version/);
  reject('x'.repeat(2_000_001), /too large/);
  reject(42, /too large/);
  assert.equal(store.completedCount(), 0, 'a rejected import must not change anything');
});

test('import sanitises hostile or malformed content instead of trusting it', () => {
  const store = makeStore();
  const hostile = {
    app: 'python-academy',
    version: 2,
    completed: { alpha: { at: '<script>alert(1)</script>' }, beta: 'yes', gamma: { at: '2026-02-30' }, evil: { at: '2026-01-01' }, __proto__: { alpha: true } },
    attempts: { alpha: -5, beta: 1.5, gamma: '7', evil: 3, constructor: 9 },
    days: ['2026-09-21', 'nonsense', 42, null, '2026-13-01', '2026-09-21'],
    code: { alpha: 'ok', evil: 'x', beta: 12345, playground: 'p'.repeat(50_001) },
  };
  const result = store.importData(JSON.stringify(hostile));
  assert.equal(store.isComplete('alpha'), true);
  assert.equal(store.completedAt('alpha'), null, 'a non-date string must be dropped, never stored');
  assert.equal(store.isComplete('beta'), false, 'only true / {at} entries count as complete');
  assert.equal(store.isComplete('gamma'), true);
  assert.equal(store.completedAt('gamma'), null, '2026-02-30 is not a real date');
  assert.equal(store.isComplete('evil'), false, 'unknown lesson ids are dropped');
  assert.equal(store.totalAttempts(), 0, 'negative, fractional, string and unknown attempt counts are dropped');
  assert.deepEqual(store.streak(), { current: 1, longest: 1, activeDays: 1 }, 'only the one real date (today) survives');
  assert.equal(store.getCode('alpha'), 'ok');
  assert.equal(store.getCode('playground'), undefined, 'oversized drafts are dropped');
  assert.equal(store.getCode('beta'), undefined);
  assert.deepEqual(result, { lessonsAdded: 2, draftsAdded: 1 });
  assert.equal(Object.keys(store.exportData().completed).sort().join(), 'alpha,gamma');
});

test('backups from the first version of the app (completed: true) still import', () => {
  const store = makeStore();
  const old = { app: 'python-academy', version: 1, completed: { alpha: true, beta: true }, code: { alpha: 'print(1)' } };
  assert.deepEqual(store.importData(JSON.stringify(old)), { lessonsAdded: 2, draftsAdded: 1 });
  assert.equal(store.completedAt('alpha'), null, 'old data has no completion date');
});

test('clearAll wipes progress', () => {
  const store = makeStore();
  store.markComplete('alpha');
  store.recordAttempt('alpha');
  store.saveCode('alpha', 'x');
  store.clearAll();
  assert.equal(store.completedCount(), 0);
  assert.equal(store.totalAttempts(), 0);
  assert.equal(store.getCode('alpha'), undefined);
  assert.equal(store.streak().activeDays, 0);
});
