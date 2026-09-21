import { clear, h } from './dom.js';
import { downloadTextFile, safeFileName } from './download.js';
import { MAX_CODE_CHARS, MAX_NAME_CHARS } from './storage.js';
import { createWorkbench } from './workbench.js';

const NEW_SNIPPET = '# New snippet: write some Python and press Run (Ctrl+Enter)\n';
const FIRST_SNIPPET = `# Welcome to the Playground!
# Write any Python here and press Run (or Ctrl+Enter).
# Your snippets are saved in this browser. Try the examples on the left too.

name = "world"
print(f"Hello, {name}!")
`;
const MAX_FILE_BYTES = 200_000;

let examplesPromise = null;
/** The example gallery, fetched once. Resolves to { categories, examples } (empty if it can't be loaded). */
function loadExamples() {
  examplesPromise ??= fetch(new URL('../data/examples.json', import.meta.url), { credentials: 'omit' })
    .then((response) => (response.ok ? response.json() : Promise.reject(new Error(`HTTP ${response.status}`))))
    .then((data) => {
      const valid = data && Array.isArray(data.categories) && Array.isArray(data.examples);
      if (!valid) throw new Error('unexpected shape');
      const examples = data.examples.filter((e) => e && typeof e.id === 'string' && typeof e.title === 'string' && typeof e.code === 'string' && typeof e.category === 'string');
      return { categories: data.categories.filter((c) => typeof c === 'string'), examples };
    })
    .catch(() => ({ categories: [], examples: [] }));
  return examplesPromise;
}

const relativeTime = new Intl.RelativeTimeFormat(undefined, { numeric: 'auto' });
/** "just now", "5 minutes ago", "yesterday"… */
function timeAgo(timestamp) {
  const seconds = Math.round((timestamp - Date.now()) / 1000);
  const steps = [['day', 86_400], ['hour', 3_600], ['minute', 60]];
  for (const [unit, size] of steps) {
    if (Math.abs(seconds) >= size) return relativeTime.format(Math.round(seconds / size), unit);
  }
  return 'just now';
}

/** The Playground: a personal library of saved snippets, an examples gallery and the editor. */
export function playgroundView({ runner, store, cleanups, notice = null }) {
  let paneCleanups = [];
  let bench = null;
  let activeId = ensureActive();

  const runPaneCleanups = () => {
    for (const cleanup of paneCleanups.splice(0)) cleanup();
  };
  cleanups.push(runPaneCleanups);

  function ensureActive() {
    let id = store.activeSnippetId();
    if (!id) id = store.snippets()[0]?.id ?? store.createSnippet({ name: 'My first snippet', code: FIRST_SNIPPET })?.id;
    if (id) store.setActiveSnippet(id);
    return id;
  }

  // ---- notices -----------------------------------------------------------------------------
  const noticeBox = h('p', { class: 'pg-notice', role: 'status', hidden: true });
  function showNotice(kind, text) {
    noticeBox.hidden = !text;
    noticeBox.dataset.kind = kind;
    noticeBox.textContent = text ?? '';
  }
  const limitMessage = () => `You have ${store.maxSnippets} snippets, the maximum. Delete some to make room.`;

  // ---- snippet list & examples ----------------------------------------------------------------
  const snippetList = h('ul', { class: 'snippet-list' });
  const examplesSlot = h('div', { class: 'examples' }, h('p', { class: 'muted small' }, 'Loading examples…'));

  function renderList() {
    clear(snippetList);
    for (const snippet of store.snippets()) {
      snippetList.append(
        h(
          'li',
          null,
          h(
            'button',
            { type: 'button', class: 'snippet-item', 'aria-current': snippet.id === activeId ? 'true' : null, onclick: () => openSnippet(snippet.id) },
            h('span', { class: 'snippet-item-name' }, snippet.name),
            h('span', { class: 'muted small' }, `edited ${timeAgo(snippet.updated)}`),
          ),
        ),
      );
    }
  }

  async function renderExamples() {
    const { categories, examples } = await loadExamples();
    clear(examplesSlot);
    if (examples.length === 0) {
      examplesSlot.append(h('p', { class: 'muted small' }, 'The examples could not be loaded.'));
      return;
    }
    for (const category of categories) {
      const inCategory = examples.filter((example) => example.category === category);
      if (inCategory.length === 0) continue;
      examplesSlot.append(
        h('h3', { class: 'example-category' }, category),
        h(
          'ul',
          { class: 'example-list' },
          inCategory.map((example) =>
            h(
              'li',
              null,
              h('button', { type: 'button', class: 'example-item', title: example.description, onclick: () => openExample(example) }, h('span', { class: 'example-title' }, example.title), h('span', { class: 'muted small' }, example.description)),
            ),
          ),
        ),
      );
    }
  }

  // ---- the open snippet ------------------------------------------------------------------------
  const nameInput = h('input', { type: 'text', class: 'snippet-name', 'aria-label': 'Snippet name', spellcheck: 'false', autocomplete: 'off' });
  nameInput.maxLength = MAX_NAME_CHARS;
  nameInput.addEventListener('change', () => {
    const updated = store.updateSnippet(activeId, { name: nameInput.value });
    if (updated) nameInput.value = updated.name;
    renderList();
  });
  nameInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') nameInput.blur();
  });

  const paneSlot = h('div', { class: 'pg-pane' });

  function renderPane() {
    runPaneCleanups();
    const snippet = store.snippet(activeId);
    if (!snippet) {
      clear(paneSlot);
      return;
    }
    const id = snippet.id; // captured: later saves must go to THIS snippet even after switching
    nameInput.value = snippet.name;
    bench = createWorkbench({
      runner,
      store,
      storageKey: 'playground',
      starter: '',
      features: { selectionRun: true, reset: false },
      cleanups: paneCleanups,
      persist: {
        load: () => store.snippet(id)?.code ?? '',
        save: (code) => {
          store.updateSnippet(id, { code });
        },
        loadStdin: () => store.snippet(id)?.stdin ?? '',
        saveStdin: (text) => {
          store.updateSnippet(id, { stdin: text });
        },
      },
    });
    clear(paneSlot);
    paneSlot.append(bench.element);
  }

  function openSnippet(id) {
    runPaneCleanups(); // saves pending edits to the snippet we are leaving
    activeId = id;
    store.setActiveSnippet(id);
    showNotice('info', null);
    sideEl.dataset.open = 'false';
    toggleButton.setAttribute('aria-expanded', 'false');
    renderList();
    renderPane();
  }

  function openNew(options) {
    runPaneCleanups();
    const created = store.createSnippet(options);
    if (!created) {
      showNotice('error', limitMessage());
      renderPane();
      return null;
    }
    openSnippet(created.id);
    bench?.focus();
    return created;
  }

  const openExample = (example) => openNew({ name: example.title, code: example.code, stdin: example.stdin ?? '' });

  // ---- snippet actions ------------------------------------------------------------------------------
  let deleteTimer = 0;
  const deleteButton = h('button', { type: 'button', class: 'btn ghost small', onclick: askDelete }, 'Delete');
  function askDelete() {
    if (!deleteTimer) {
      deleteButton.textContent = 'Click again to delete';
      deleteTimer = window.setTimeout(resetDeleteButton, 4000);
      return;
    }
    resetDeleteButton();
    runPaneCleanups();
    const next = store.deleteSnippet(activeId);
    if (next) {
      openSnippet(next);
    } else {
      activeId = null;
      openNew({ name: 'My first snippet', code: FIRST_SNIPPET });
    }
    showNotice('info', 'Snippet deleted.');
  }
  function resetDeleteButton() {
    clearTimeout(deleteTimer);
    deleteTimer = 0;
    deleteButton.textContent = 'Delete';
  }
  cleanups.push(() => clearTimeout(deleteTimer));

  function duplicate() {
    runPaneCleanups();
    const copy = store.duplicateSnippet(activeId);
    if (!copy) {
      showNotice('error', limitMessage());
      renderPane();
      return;
    }
    openSnippet(copy.id);
  }

  function download() {
    const name = safeFileName(nameInput.value);
    downloadTextFile(`${name}.py`, bench?.editor.value ?? '', 'text/x-python');
    showNotice('info', `Saved as ${name}.py in your downloads.`);
  }

  const fileInput = h('input', { type: 'file', accept: '.py,text/x-python,text/plain', class: 'sr-only', tabindex: '-1', 'aria-label': 'Open a Python file' });
  fileInput.addEventListener('change', async () => {
    const file = fileInput.files?.[0];
    fileInput.value = '';
    if (!file) return;
    if (file.size > MAX_FILE_BYTES) {
      showNotice('error', `"${file.name.slice(0, 40)}" is too large. The limit is ${MAX_CODE_CHARS.toLocaleString()} characters.`);
      return;
    }
    const text = await file.text();
    if (text.includes(' ')) {
      showNotice('error', 'That does not look like a text file.');
    } else if (text.length > MAX_CODE_CHARS) {
      showNotice('error', `That file is too large. The limit is ${MAX_CODE_CHARS.toLocaleString()} characters.`);
    } else if (openNew({ name: file.name.replace(/\.py$/i, '') || 'Opened file', code: text })) {
      showNotice('info', `Opened "${file.name.slice(0, 40)}" as a new snippet.`);
    }
  });

  const snippetBar = h(
    'div',
    { class: 'snippet-bar' },
    h('label', { class: 'sr-only', for: 'snippet-name' }, 'Snippet name'),
    nameInput,
    h('div', { class: 'row snippet-actions-row' }, h('button', { type: 'button', class: 'btn ghost small', onclick: duplicate }, 'Duplicate'), h('button', { type: 'button', class: 'btn ghost small', onclick: () => fileInput.click() }, 'Open .py file'), h('button', { type: 'button', class: 'btn ghost small', onclick: download }, 'Download .py'), deleteButton, fileInput),
  );
  nameInput.id = 'snippet-name';

  // ---- layout ------------------------------------------------------------------------------------------
  const toggleButton = h('button', { type: 'button', class: 'btn ghost pg-side-toggle', 'aria-expanded': 'false', 'aria-controls': 'pg-side', onclick: toggleSide }, '☰ Snippets & examples');
  const sideEl = h(
    'aside',
    { class: 'pg-side', id: 'pg-side', 'data-open': 'false', 'aria-label': 'Snippets and examples' },
    h('div', { class: 'pg-side-head' }, h('h2', null, 'My snippets'), h('button', { type: 'button', class: 'btn small primary', onclick: () => openNew({ name: 'Untitled snippet', code: NEW_SNIPPET }) }, '+ New')),
    snippetList,
    h('h2', { class: 'pg-examples-title' }, 'Examples'),
    h('p', { class: 'muted small' }, 'Click one to open it as a new snippet. Your own work is never overwritten.'),
    examplesSlot,
  );
  function toggleSide() {
    const open = sideEl.dataset.open !== 'true';
    sideEl.dataset.open = String(open);
    toggleButton.setAttribute('aria-expanded', String(open));
  }

  const view = h(
    'div',
    { class: 'playground' },
    h('header', { class: 'lesson-head' }, h('p', { class: 'kicker' }, 'Free practice'), h('h1', { tabindex: '-1' }, 'Playground'), h('p', { class: 'lead' }, 'Experiment freely. Snippets are saved in this browser and run only on your device. Files your program creates exist only while it runs.')),
    noticeBox,
    h('div', { class: 'pg-layout' }, sideEl, h('div', { class: 'pg-main' }, toggleButton, snippetBar, paneSlot)),
  );

  if (notice) showNotice('error', notice);
  renderList();
  renderPane();
  renderExamples();
  return view;
}
