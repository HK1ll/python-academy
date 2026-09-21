/** Save text as a file through the browser's normal download flow (no server involved). */
export function downloadTextFile(filename, text, mime = 'text/plain') {
  const url = URL.createObjectURL(new Blob([text], { type: `${mime};charset=utf-8` }));
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 10_000);
}

/** A file name made only of letters, digits, dot, dash and underscore (no paths, no odd characters). */
export function safeFileName(name, fallback = 'snippet') {
  const cleaned = String(name ?? '')
    .normalize('NFKD')
    .replace(/[^A-Za-z0-9._-]+/g, '-')
    .replace(/^[.-]+|[.-]+$/g, '')
    .slice(0, 50)
    .replace(/[.-]+$/g, '');
  return cleaned || fallback;
}
