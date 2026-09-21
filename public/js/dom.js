// Safe DOM construction. The app never assigns to innerHTML/outerHTML or uses
// insertAdjacentHTML: every piece of text (lessons, learner output, stored code)
// goes in as a text node, so it can never be interpreted as markup.

const PLAIN_ATTRS = new Set([
  'class', 'id', 'type', 'role', 'title', 'for', 'name', 'rows', 'cols', 'placeholder',
  'disabled', 'hidden', 'tabindex', 'spellcheck', 'autocomplete', 'autocapitalize',
  'autocorrect', 'open', 'value', 'min', 'max', 'wrap', 'lang', 'href', 'readonly',
]);

export function h(tag, props, ...children) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(props ?? {})) {
    if (value == null || value === false) continue;
    if (key.startsWith('on')) {
      if (typeof value !== 'function') throw new TypeError(`${key} must be a function`);
      el.addEventListener(key.slice(2), value);
    } else if (key.startsWith('aria-') || key.startsWith('data-') || PLAIN_ATTRS.has(key)) {
      // Only in-app hash links are allowed as hrefs (blocks javascript:, data:, external URLs).
      if (key === 'href' && !/^#\//.test(String(value))) throw new Error(`Blocked href: ${value}`);
      el.setAttribute(key, value === true ? '' : String(value));
    } else {
      throw new Error(`Attribute not allowed: ${key}`);
    }
  }
  append(el, ...children);
  return el;
}

export function append(parent, ...children) {
  for (const child of children.flat(Infinity)) {
    if (child == null || child === false) continue;
    parent.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return parent;
}

export function clear(node) {
  node.replaceChildren();
  return node;
}
