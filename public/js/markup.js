import { h } from './dom.js';

// Tiny inline formatter for lesson text: `code` and **bold**. Produces DOM nodes only.
const INLINE = /(`[^`]+`|\*\*[^*]+\*\*)/;

export function inline(text) {
  return String(text)
    .split(INLINE)
    .filter(Boolean)
    .map((part) => {
      if (part.length > 2 && part.startsWith('`') && part.endsWith('`')) return h('code', null, part.slice(1, -1));
      if (part.length > 4 && part.startsWith('**') && part.endsWith('**')) return h('strong', null, part.slice(2, -2));
      return part;
    });
}
