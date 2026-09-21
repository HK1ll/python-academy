import { h } from './dom.js';

const dateFormat = new Intl.DateTimeFormat(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
const MAX_IMPORT_BYTES = 2_000_000;

/** 'YYYY-MM-DD' (a day in the learner's own time zone) as readable text. */
export function formatDay(day) {
  const [year, month, date] = day.split('-').map(Number);
  return dateFormat.format(new Date(year, month - 1, date));
}

/** done | started | todo, for one lesson. "Started" means they pressed Check or edited the starter code. */
export function lessonStatus(lesson, store) {
  if (store.isComplete(lesson.id)) return 'done';
  const draft = store.getCode(lesson.id);
  if (store.attempts(lesson.id) > 0 || (draft !== undefined && draft !== lesson.exercise.starter)) return 'started';
  return 'todo';
}

const STATUS_LABEL = { done: 'Completed', started: 'In progress', todo: 'Not started' };

function pluralise(count, one, many) {
  return count === 1 ? one : many;
}

function statCard(label, value, note) {
  return h('div', { class: 'stat' }, h('span', { class: 'stat-label' }, label), h('span', { class: 'stat-value' }, value), h('span', { class: 'muted small' }, note));
}

function downloadBackup(store) {
  const json = JSON.stringify(store.exportData(), null, 2);
  const url = URL.createObjectURL(new Blob([json], { type: 'application/json' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = `python-academy-progress-${store.today()}.json`;
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 10_000);
}

/** The Progress page. `onChange` re-renders the app after an import so every view updates. */
export function progressView({ lessons, sections, store, onChange }) {
  const total = lessons.length;
  const done = store.completedCount();
  const percent = Math.round((100 * done) / total);
  const streak = store.streak();
  const byId = new Map(lessons.map((lesson) => [lesson.id, lesson]));
  const next = lessons.find((lesson) => !store.isComplete(lesson.id));

  // ---- summary cards ------------------------------------------------------------------
  const summary = h(
    'div',
    { class: 'stat-grid' },
    h(
      'div',
      { class: 'stat stat-wide' },
      h('span', { class: 'stat-label' }, 'Course completed'),
      h('span', { class: 'stat-value' }, `${done} of ${total} lessons`, h('span', { class: 'stat-percent' }, ` · ${percent}%`)),
      h('progress', { max: total, value: done, 'aria-label': `${done} of ${total} lessons completed` }),
      next
        ? h('a', { class: 'btn primary', href: `#/lesson/${next.id}` }, `${done === 0 ? 'Start' : 'Continue'}: ${next.title}`)
        : h('p', { class: 'success-note' }, '🎉 You completed every lesson!'),
    ),
    statCard('Day streak', String(streak.current), `${pluralise(streak.current, 'day', 'days')} in a row · best ${streak.longest}`),
    statCard('Active days', String(streak.activeDays), 'days you practised'),
    statCard('Answer attempts', String(store.totalAttempts()), 'times you pressed Check'),
  );

  // ---- per-section breakdown ------------------------------------------------------------
  const sectionRows = sections.map((section) => {
    const finished = section.ids.filter((id) => store.isComplete(id)).length;
    return h(
      'li',
      { class: 'section-row' },
      h('span', { class: 'section-name' }, section.title),
      h('span', { class: 'muted' }, `${finished} / ${section.ids.length}`),
      h('progress', { max: section.ids.length, value: finished, 'aria-label': `${section.title}: ${finished} of ${section.ids.length} lessons completed` }),
    );
  });

  // ---- every lesson -----------------------------------------------------------------------
  let number = 0;
  const bodyRows = sections.flatMap((section) => [
    h('tr', { class: 'group-row' }, h('th', { scope: 'rowgroup', colspan: '5' }, section.title)),
    ...section.ids.map((id) => {
      const lesson = byId.get(id);
      const status = lessonStatus(lesson, store);
      const attempts = store.attempts(id);
      const date = store.completedAt(id);
      number += 1;
      return h(
        'tr',
        null,
        h('td', { class: 'num-cell' }, String(number)),
        h('td', null, h('a', { href: `#/lesson/${id}` }, lesson.title)),
        h('td', null, h('span', { class: `pill ${status}` }, STATUS_LABEL[status])),
        h('td', null, attempts > 0 ? String(attempts) : '–'),
        h('td', null, date ? formatDay(date) : status === 'done' ? 'earlier' : '–'),
      );
    }),
  ]);
  const table = h(
    'div',
    { class: 'table-wrap' },
    h(
      'table',
      { class: 'progress-table' },
      h('caption', { class: 'sr-only' }, 'Your progress in every lesson'),
      h('thead', null, h('tr', null, h('th', { scope: 'col' }, '#'), h('th', { scope: 'col' }, 'Lesson'), h('th', { scope: 'col' }, 'Status'), h('th', { scope: 'col' }, 'Attempts'), h('th', { scope: 'col' }, 'Completed'))),
      h('tbody', null, bodyRows),
    ),
  );

  // ---- backup: export / import -------------------------------------------------------------
  const message = h('p', { class: 'backup-message', role: 'status', hidden: true });
  const showMessage = (kind, text) => {
    message.hidden = false;
    message.dataset.kind = kind;
    message.textContent = text;
  };
  const fileInput = h('input', { type: 'file', accept: 'application/json,.json', class: 'sr-only', id: 'import-file', tabindex: '-1' });
  fileInput.addEventListener('change', async () => {
    const file = fileInput.files?.[0];
    fileInput.value = '';
    if (!file) return;
    if (file.size > MAX_IMPORT_BYTES) {
      showMessage('error', 'That file is too large to be a progress backup.');
      return;
    }
    try {
      const result = store.importData(await file.text());
      onChange(); // re-renders the page, so the message is shown again below
      const summaryText = `Imported: ${result.lessonsAdded} ${pluralise(result.lessonsAdded, 'new completed lesson', 'new completed lessons')} and ${result.draftsAdded} saved ${pluralise(result.draftsAdded, 'draft', 'drafts')} added.`;
      const fresh = document.getElementById('backup-message');
      if (fresh) {
        fresh.hidden = false;
        fresh.dataset.kind = 'success';
        fresh.textContent = summaryText;
      }
    } catch (error) {
      showMessage('error', String(error.message));
    }
  });
  message.id = 'backup-message';

  const backup = h(
    'section',
    { class: 'card backup', 'aria-labelledby': 'backup-title' },
    h('h2', { id: 'backup-title' }, 'Back up or move your progress'),
    h('p', null, 'There are no accounts: your progress is stored only in this browser. Save a backup file to keep it safe, or to continue on another device.'),
    h(
      'div',
      { class: 'row' },
      h('button', { type: 'button', class: 'btn primary', onclick: () => downloadBackup(store) }, '⬇ Export progress'),
      h('button', { type: 'button', class: 'btn', onclick: () => fileInput.click() }, '⬆ Import progress'),
      fileInput,
    ),
    message,
    h('p', { class: 'muted small' }, 'Importing merges the file with what you already have: it never deletes progress or overwrites your saved code.'),
  );

  const view = h(
    'div',
    { class: 'progress-page' },
    h('header', { class: 'lesson-head' }, h('p', { class: 'kicker' }, 'Your journey'), h('h1', { tabindex: '-1' }, 'My progress'), h('p', { class: 'lead' }, 'Everything here is calculated on your device and never leaves it.')),
    summary,
    h('section', { 'aria-labelledby': 'sections-title' }, h('h2', { id: 'sections-title' }, 'By topic'), h('ul', { class: 'section-list' }, sectionRows)),
    h('section', { 'aria-labelledby': 'lessons-table-title' }, h('h2', { id: 'lessons-table-title' }, 'All lessons'), table),
    backup,
  );
  return view;
}
