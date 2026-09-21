import { append, clear, h } from './dom.js';
import { inline } from './markup.js';
import { createRunner } from './runner.js';
import { createStore, PLAYGROUND } from './storage.js';
import { createSnippet, createWorkbench, engineStatus, providedFiles } from './workbench.js';
import { highlight } from './highlight.js';

const CALLOUT_LABELS = { tip: 'Tip: ', warn: 'Watch out: ', sec: 'Security lens: ' };

const main = document.getElementById('main');
const sidebar = document.getElementById('sidebar');
const menuToggle = document.getElementById('menu-toggle');
const engineSlot = document.getElementById('engine-slot');
const footerSlot = document.getElementById('footer-slot');
const skipLink = document.getElementById('skip-link');

const PLAYGROUND_STARTER = `# Welcome to the Playground!
# Write any Python here and press Run (or Ctrl+Enter).

name = "world"
print(f"Hello, {name}!")
`;

let lessons = [];
let byId = new Map();
let store = null;
let runner = null;
let cleanups = [];
let firstRender = true;

// ---------------------------------------------------------------- data

async function loadLessons() {
  // Relative to this file (not the site root) so the app works from a sub-path like /repo-name/.
  const response = await fetch(new URL('../data/lessons.json', import.meta.url), { credentials: 'omit' });
  if (!response.ok) throw new Error(`lessons.json: HTTP ${response.status}`);
  const data = await response.json();
  if (!data || !Array.isArray(data.lessons) || data.lessons.length === 0) throw new Error('lessons.json has an unexpected shape');
  for (const lesson of data.lessons) {
    const valid =
      typeof lesson.id === 'string' && /^[a-z0-9-]+$/.test(lesson.id) &&
      typeof lesson.title === 'string' && typeof lesson.summary === 'string' &&
      Array.isArray(lesson.blocks) && lesson.exercise && typeof lesson.exercise.check === 'string';
    if (!valid) throw new Error('lessons.json contains an invalid lesson');
  }
  return data.lessons;
}

// ---------------------------------------------------------------- routing

function parseRoute() {
  const hash = location.hash.replace(/^#/, '');
  if (hash === '/playground') return { name: 'playground' };
  const match = /^\/lesson\/([a-z0-9-]+)$/.exec(hash);
  if (match && byId.has(match[1])) return { name: 'lesson', id: match[1] };
  return { name: 'home' };
}

function render() {
  for (const cleanup of cleanups.splice(0)) cleanup();
  const route = parseRoute();
  clear(main);
  let title = 'Python Academy';
  if (route.name === 'lesson') {
    const lesson = byId.get(route.id);
    title = `${lesson.title} · Python Academy`;
    main.append(lessonView(lesson));
  } else if (route.name === 'playground') {
    title = 'Playground · Python Academy';
    main.append(playgroundView());
  } else {
    main.append(homeView());
  }
  document.title = title;
  renderNav(route);
  sidebar.dataset.open = 'false';
  menuToggle.setAttribute('aria-expanded', 'false');
  if (!firstRender) {
    window.scrollTo(0, 0);
    main.querySelector('h1')?.focus({ preventScroll: true });
  }
  firstRender = false;
}

function goToPlayground(code) {
  store.saveCode(PLAYGROUND, code);
  if (location.hash === '#/playground') render();
  else location.hash = '#/playground';
}

// ---------------------------------------------------------------- navigation

function renderNav(route) {
  const done = store.completedCount();
  clear(sidebar);
  append(
    sidebar,
    h('p', { class: 'nav-progress' }, `${done} of ${lessons.length} lessons complete`),
    h('progress', { max: lessons.length, value: done, 'aria-label': 'Lessons completed' }),
    h(
      'ol',
      { class: 'lesson-list' },
      lessons.map((lesson) =>
        h(
          'li',
          null,
          h(
            'a',
            { href: `#/lesson/${lesson.id}`, 'aria-current': route.name === 'lesson' && route.id === lesson.id ? 'page' : null },
            h('span', { class: 'check', 'aria-hidden': 'true' }, store.isComplete(lesson.id) ? '✓' : ''),
            h('span', null, lesson.title),
            store.isComplete(lesson.id) ? h('span', { class: 'sr-only' }, '(completed)') : null,
          ),
        ),
      ),
    ),
    h('a', { class: 'nav-link', href: '#/playground', 'aria-current': route.name === 'playground' ? 'page' : null }, '⚡ Playground'),
  );
}

// ---------------------------------------------------------------- views

function homeView() {
  const done = store.completedCount();
  const next = lessons.find((l) => !store.isComplete(l.id));
  const startLabel = done === 0 ? 'Start with lesson 1' : next ? `Continue: ${next.title}` : 'Review lesson 1';
  const startTarget = next ?? lessons[0];

  return h(
    'div',
    { class: 'home' },
    h(
      'section',
      { class: 'hero' },
      h('h1', { tabindex: '-1' }, 'Learn Python by writing it'),
      h('p', { class: 'lead' }, 'Short lessons, real code and instant feedback. Everything runs privately in your browser: no sign-up, no installs, nothing uploaded.'),
      h('div', { class: 'row' }, h('a', { class: 'btn primary large', href: `#/lesson/${startTarget.id}` }, startLabel), h('a', { class: 'btn large', href: '#/playground' }, 'Open the Playground')),
      done === lessons.length ? h('p', { class: 'success-note' }, '🎉 You finished every lesson. Keep building in the Playground!') : null,
    ),
    h(
      'section',
      { 'aria-labelledby': 'lessons-title' },
      h('h2', { id: 'lessons-title' }, 'Lessons'),
      h(
        'ol',
        { class: 'card-grid' },
        lessons.map((lesson, index) =>
          h(
            'li',
            null,
            h(
              'a',
              { class: 'card lesson-card', href: `#/lesson/${lesson.id}` },
              h('span', { class: 'num', 'aria-hidden': 'true' }, store.isComplete(lesson.id) ? '✓' : String(index + 1)),
              h('span', { class: 'card-title' }, lesson.title),
              h('span', { class: 'muted' }, lesson.summary),
              store.isComplete(lesson.id) ? h('span', { class: 'sr-only' }, 'Completed') : null,
            ),
          ),
        ),
      ),
    ),
    h(
      'section',
      { class: 'card trust', 'aria-labelledby': 'safe-title' },
      h('h2', { id: 'safe-title' }, 'Built to be safe'),
      h(
        'ul',
        null,
        h('li', null, h('strong', null, 'Your code never leaves your device.'), ' Python runs inside a sandboxed Web Worker in your browser (WebAssembly). There is no server that executes code.'),
        h('li', null, h('strong', null, 'No accounts, cookies or tracking.'), ' Progress is saved only in this browser and can be erased any time from the footer.'),
        h('li', null, h('strong', null, 'Nothing third-party.'), ' A strict Content-Security-Policy blocks inline scripts and any outside resources; Python itself is served from this site and integrity-checked.'),
        h('li', null, h('strong', null, 'Runaway programs are stopped.'), ' Infinite loops end after 10 seconds and huge outputs are capped.'),
      ),
    ),
  );
}

function renderBlock(block) {
  switch (block.type) {
    case 'p':
      return h('p', null, ...inline(block.text));
    case 'h':
      return h('h3', null, block.text);
    case 'list':
      return h('ul', null, block.items.map((item) => h('li', null, ...inline(item))));
    case 'tip':
    case 'warn':
    case 'sec':
      return h('aside', { class: `callout ${block.type}` }, h('strong', null, CALLOUT_LABELS[block.type]), ...inline(block.text));
    case 'codeonly':
      return h(
        'figure',
        { class: 'snippet static' },
        h('pre', { class: 'code', tabindex: '0' }, h('code', null, highlight(block.text))),
        h('figcaption', { class: 'muted small' }, 'Example only: this one is not run in the app.'),
      );
    case 'output':
      return h('figure', { class: 'expected' }, h('figcaption', null, 'Output'), h('pre', { class: 'console', tabindex: '0' }, block.text));
    case 'code':
      return createSnippet({ runner, code: block.text, onOpenInPlayground: goToPlayground, cleanups });
    default:
      return null;
  }
}

function lessonView(lesson) {
  const index = lessons.indexOf(lesson);
  const previous = lessons[index - 1];
  const next = lessons[index + 1];
  const badge = h('span', { class: 'badge', hidden: !store.isComplete(lesson.id) }, '✓ Completed');
  const nextSlot = h('div', { class: 'next-cta' });

  function updateNextCta() {
    clear(nextSlot);
    if (!store.isComplete(lesson.id)) return;
    append(nextSlot, next ? h('a', { class: 'btn primary', href: `#/lesson/${next.id}` }, `Next lesson: ${next.title} →`) : h('a', { class: 'btn primary', href: '#/playground' }, 'Finished! Open the Playground →'));
  }
  updateNextCta();

  const bench = createWorkbench({
    runner,
    store,
    storageKey: lesson.id,
    starter: lesson.exercise.starter,
    stdin: lesson.exercise.stdin ?? '',
    exercise: lesson.exercise,
    cleanups,
    onPass() {
      badge.hidden = false;
      updateNextCta();
      renderNav({ name: 'lesson', id: lesson.id });
    },
  });

  return h(
    'div',
    { class: 'lesson' },
    h('header', { class: 'lesson-head' }, h('p', { class: 'kicker' }, `Lesson ${index + 1} of ${lessons.length}`), h('h1', { tabindex: '-1' }, lesson.title), h('p', { class: 'lead' }, lesson.summary), badge),
    h(
      'div',
      { class: 'lesson-grid' },
      h(
        'article',
        { class: 'lesson-body' },
        lesson.blocks.map(renderBlock),
        h(
          'nav',
          { class: 'pager', 'aria-label': 'Lesson navigation' },
          previous ? h('a', { class: 'btn ghost', href: `#/lesson/${previous.id}` }, `← ${previous.title}`) : h('span'),
          next ? h('a', { class: 'btn ghost', href: `#/lesson/${next.id}` }, `${next.title} →`) : h('span'),
        ),
      ),
      h('aside', { class: 'task', 'aria-labelledby': 'task-title' }, h('h2', { id: 'task-title' }, 'Your turn'), h('p', { class: 'prompt' }, ...inline(lesson.exercise.prompt)), providedFiles(lesson.exercise.files), bench.element, nextSlot),
    ),
  );
}

function playgroundView() {
  const bench = createWorkbench({ runner, store, storageKey: PLAYGROUND, starter: PLAYGROUND_STARTER, cleanups });
  return h(
    'div',
    { class: 'playground' },
    h('header', { class: 'lesson-head' }, h('p', { class: 'kicker' }, 'Free practice'), h('h1', { tabindex: '-1' }, 'Playground'), h('p', { class: 'lead' }, 'Experiment freely. Your code is saved in this browser and runs only on your device. Files your program creates exist only while it runs.')),
    bench.element,
  );
}

// ---------------------------------------------------------------- footer & chrome

function setupChrome() {
  const [status] = engineStatus(runner);
  engineSlot.append(status);

  let armed = 0;
  const resetButton = h('button', { type: 'button', class: 'btn ghost small' }, 'Erase my progress');
  resetButton.addEventListener('click', () => {
    if (!armed) {
      resetButton.textContent = 'Click again to confirm';
      armed = window.setTimeout(() => {
        armed = 0;
        resetButton.textContent = 'Erase my progress';
      }, 4000);
      return;
    }
    clearTimeout(armed);
    armed = 0;
    resetButton.textContent = 'Erase my progress';
    store.clearAll();
    if (location.hash && location.hash !== '#/') location.hash = '#/';
    else render();
  });
  footerSlot.append(resetButton);

  menuToggle.addEventListener('click', () => {
    const open = sidebar.dataset.open !== 'true';
    sidebar.dataset.open = String(open);
    menuToggle.setAttribute('aria-expanded', String(open));
  });
  skipLink.addEventListener('click', (event) => {
    event.preventDefault();
    main.focus();
  });
}

// ---------------------------------------------------------------- boot

// Clickjacking defence for hosts that can't send frame-ancestors / X-Frame-Options (e.g. GitHub Pages).
function isFramed() {
  try {
    return window.top !== window.self;
  } catch {
    return true;
  }
}

async function boot() {
  if (isFramed()) {
    clear(main);
    main.append(h('div', { class: 'card' }, h('h1', { tabindex: '-1' }, 'Open this page directly'), h('p', null, 'For your safety, Python Academy does not run inside frames on other sites. Open its address in its own browser tab.')));
    return;
  }
  try {
    lessons = await loadLessons();
  } catch (error) {
    clear(main);
    main.append(h('div', { class: 'card' }, h('h1', { tabindex: '-1' }, 'Could not load the lessons'), h('p', null, String(error.message))));
    return;
  }
  byId = new Map(lessons.map((lesson) => [lesson.id, lesson]));
  store = createStore(lessons.map((lesson) => lesson.id));
  runner = createRunner();
  setupChrome();
  window.addEventListener('hashchange', render);
  render();
}

boot();
