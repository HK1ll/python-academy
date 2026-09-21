import { h } from './dom.js';
import { INDENT, autoCloseAction, dedentLines, indentLines, lineOfOffset, newLineEdit, pairBackspaceEdit, toggleComment } from './editing.js';
import { highlight } from './highlight.js';

const MODIFIER_KEYS = new Set(['Shift', 'Control', 'Alt', 'Meta']);

/**
 * A code editor made of one real <textarea> (what the learner types into, so undo, selection, IME and
 * screen readers all just work) layered over a syntax-highlighted copy of its text, with a line-number gutter.
 * Gutter, highlight layer and textarea live in ONE scrolling box, so they can never drift out of alignment.
 * All text is inserted via DOM nodes (textContent), never as HTML.
 */
export function createEditor({ value = '', label = 'Python code', describedBy, maxLength = 50_000, getSettings, onRun, onRunSelection } = {}) {
  const settings = () => ({ fontSize: 15, autoClose: true, ...(getSettings?.() ?? {}) });

  const textarea = h('textarea', {
    class: 'editor',
    spellcheck: 'false',
    autocomplete: 'off',
    autocapitalize: 'off',
    autocorrect: 'off',
    wrap: 'off',
    'aria-label': label,
    'aria-describedby': describedBy,
  });
  textarea.maxLength = maxLength;

  const code = h('code');
  const pre = h('pre', { class: 'hl', 'aria-hidden': 'true' }, code);
  const band = h('div', { class: 'error-band', hidden: true });
  const layers = h('div', { class: 'layers' }, pre, band, textarea);
  const gutter = h('div', { class: 'gutter', 'aria-hidden': 'true' });
  const scroller = h('div', { class: 'code-scroll' }, gutter, layers);
  const element = h('div', { class: 'code-editor' }, scroller);

  // ---- rendering -----------------------------------------------------------------------
  let renderedLines = 0;
  let errorLine = null;

  function metrics() {
    const style = getComputedStyle(pre);
    const size = parseFloat(style.fontSize) || 15;
    return { lineHeight: parseFloat(style.lineHeight) || size * 1.55, paddingTop: parseFloat(style.paddingTop) || 0 };
  }

  function applyMark() {
    for (const marked of gutter.querySelectorAll('.err')) marked.classList.remove('err');
    const row = errorLine ? gutter.children[errorLine - 1] : null;
    if (!row) {
      band.hidden = true;
      return;
    }
    row.classList.add('err');
    const { lineHeight, paddingTop } = metrics();
    band.style.top = `${paddingTop + (errorLine - 1) * lineHeight}px`;
    band.style.height = `${lineHeight}px`;
    band.hidden = false;
  }

  function refresh() {
    const text = textarea.value;
    code.replaceChildren(highlight(`${text}\n`)); // the extra newline keeps the last (empty) line's height
    const lines = text.split('\n').length;
    if (lines !== renderedLines) {
      renderedLines = lines;
      gutter.replaceChildren(...Array.from({ length: lines }, (_, index) => h('span', null, String(index + 1))));
      if (errorLine) applyMark();
    }
  }

  // Setting `textarea.value` from code (not from typing) must also refresh the layers.
  const nativeValue = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value');
  Object.defineProperty(textarea, 'value', {
    configurable: true,
    get() {
      return nativeValue.get.call(this);
    },
    set(next) {
      nativeValue.set.call(this, next);
      refresh();
    },
  });

  function clearError() {
    if (errorLine === null) return;
    errorLine = null;
    applyMark();
  }

  textarea.addEventListener('input', () => {
    clearError(); // the marked line may no longer be where the mistake is
    refresh();
  });

  // ---- editing commands --------------------------------------------------------------------
  function applyEdit(edit) {
    textarea.focus();
    textarea.setSelectionRange(edit.from, edit.to);
    // execCommand keeps the browser's undo history intact; fall back if it is unavailable.
    if (!document.execCommand('insertText', false, edit.insert)) {
      textarea.setRangeText(edit.insert, edit.from, edit.to, 'end');
      textarea.dispatchEvent(new Event('input', { bubbles: true }));
    }
    textarea.setSelectionRange(edit.selStart, edit.selEnd);
  }

  let tabMovesFocus = false; // Esc then Tab lets keyboard users leave the editor
  textarea.addEventListener('blur', () => {
    tabMovesFocus = false;
  });
  textarea.addEventListener('keydown', (event) => {
    if (event.isComposing || event.defaultPrevented) return;
    if (MODIFIER_KEYS.has(event.key)) return; // pressing Shift for Shift+Tab must not cancel Esc
    const { selectionStart: start, selectionEnd: end } = textarea;
    const text = textarea.value;
    const modifier = event.ctrlKey || event.metaKey;

    if (event.key === 'Escape') {
      tabMovesFocus = true;
      return;
    }
    if (modifier && event.key === 'Enter') {
      event.preventDefault();
      (event.shiftKey ? onRunSelection : onRun)?.();
      return;
    }
    if (modifier && event.key === '/') {
      const edit = toggleComment(text, start, end);
      if (edit) {
        event.preventDefault();
        applyEdit(edit);
      }
      return;
    }
    if (event.key === 'Tab' && !tabMovesFocus) {
      event.preventDefault();
      if (event.shiftKey) applyEdit(dedentLines(text, start, end));
      else if (start !== end && text.slice(start, end).includes('\n')) applyEdit(indentLines(text, start, end));
      else applyEdit({ from: start, to: end, insert: INDENT, selStart: start + INDENT.length, selEnd: start + INDENT.length });
      return;
    }
    if (event.key === 'Enter' && !event.shiftKey && !event.altKey && !modifier) {
      event.preventDefault();
      applyEdit(newLineEdit(text, start, end));
      return;
    }
    if (!modifier && !event.altKey && settings().autoClose) {
      if (event.key === 'Backspace') {
        const edit = pairBackspaceEdit(text, start, end);
        if (edit) {
          event.preventDefault();
          applyEdit(edit);
          return;
        }
      } else if (event.key.length === 1) {
        const action = autoCloseAction(text, start, end, event.key);
        if (action?.skip) {
          event.preventDefault();
          textarea.setSelectionRange(start + 1, start + 1);
          return;
        }
        if (action?.edit) {
          event.preventDefault();
          applyEdit(action.edit);
          return;
        }
      }
    }
    tabMovesFocus = false;
  });

  textarea.value = value;

  return {
    element,
    textarea,
    refresh,
    focus: () => textarea.focus(),
    applySettings({ fontSize }) {
      scroller.style.setProperty('--editor-size', `${fontSize}px`);
      if (errorLine) applyMark();
    },
    /** The selected text and the 1-based line it starts on. */
    getSelection() {
      const { selectionStart: start, selectionEnd: end } = textarea;
      return { text: textarea.value.slice(start, end), startLine: lineOfOffset(textarea.value, start) };
    },
    /** Highlight a line (1-based) and, by default, scroll it into view. */
    markError(line, { reveal = true } = {}) {
      errorLine = Number.isInteger(line) && line >= 1 ? line : null;
      applyMark();
      if (errorLine && reveal) {
        const { lineHeight, paddingTop } = metrics();
        const top = paddingTop + (errorLine - 1) * lineHeight;
        if (top < scroller.scrollTop || top + lineHeight > scroller.scrollTop + scroller.clientHeight) {
          scroller.scrollTop = Math.max(0, top - scroller.clientHeight / 3);
        }
      }
    },
    clearError,
  };
}
