# Python Academy

An interactive web app for learning Python: 32 lessons in five sections (basics; modules and
files; object-oriented programming; intermediate Python with generators and decorators;
and programming for security: hashing, regular expressions, encoding, integrity, time-based
detection and a final Log Analyzer project), runnable examples, auto-checked exercises and
a free Playground. Python runs **inside the learner's browser**
(Pyodide/WebAssembly in a Web Worker), so there is no server that executes code.

## Run it

```powershell
python server.py            # http://localhost:8000
python server.py --port 9000
```

Only Python 3.10+ is needed to serve it (standard library only). Nothing to install.

## Security design

| Threat | Mitigation |
| --- | --- |
| Remote code execution via learner code | No server-side execution at all. Code runs in a Web Worker (no DOM, cookies or localStorage) on the learner's own machine. |
| XSS | The app never uses `innerHTML`/`eval`. All text (lessons, program output, saved code) is inserted as text nodes. CSP: `script-src 'self' 'wasm-unsafe-eval'` (no inline scripts, no `unsafe-eval`), `style-src 'self'`, `default-src 'none'`, plus **Trusted Types** enforced with a single allowed policy. |
| Third-party / supply-chain compromise | Zero CDNs and zero runtime npm dependencies. Pyodide 314.0.7 (npm `pyodide`, sha512 `0YvXxEhf…D2R1A==`) is vendored and its SHA-256 hashes are in `public/vendor/pyodide/SHA256SUMS.txt`; `server.py` refuses to start if any file differs. |
| Path traversal / info leaks | Only files under `public/`, allow-listed extensions, strict URL character allowlist, symlink-escape check, no dotfiles, no directory listings, no version banner. |
| DNS rebinding | `Host` header must be `localhost`/`127.0.0.1`/`[::1]` or a name given with `--allowed-host`. |
| Clickjacking / MIME sniffing / referrer leaks | `frame-ancestors 'none'`, `X-Frame-Options`, `nosniff`, `Referrer-Policy: no-referrer`, COOP/CORP, restrictive `Permissions-Policy`. |
| Infinite loops and print-bombs | Programs are killed after 10 s (20 s for checks) by terminating the worker; output is capped at 200,000 characters. |
| Tampered browser storage | Saved progress is schema-validated on load (known lesson ids, size limits) and only ever rendered as text. |
| Malicious progress-backup file | Import checks the app id, schema version and size (2 MB max), keeps only known lesson ids, real calendar dates and sane counts, only merges (never deletes progress or overwrites saved code), and shows everything as text. Covered by unit tests. |
| Slow-connection abuse | 15 s socket timeout; only `GET`/`HEAD` are accepted. |
| Data collection | No accounts, cookies, analytics or network calls after load. Progress lives in `localStorage` and can be erased from the footer. |

**What "secure" means here, honestly:** there is no login, database or user data to
steal, which removes most of the attack surface by design. Nothing is ever *100 %*
secure, so read the limits below.

### Known limits
- Learner code runs on the learner's own device; a malicious program can burn CPU/RAM in
  their tab until the timeout, but cannot touch the page, the site or their files.
- The browser build of Python has no OpenSSL, so `hashlib.pbkdf2_hmac` and `scrypt` are
  unavailable there. The password-hashing lesson uses a clearly labelled teaching model and
  shows the real `pbkdf2_hmac` call as display-only code.
- `import js` is blocked inside Python as defence in depth, but that is not the security
  boundary. The boundary is the browser's Worker sandbox plus the CSP.
- The Edge/Chrome console shows one blocked `TrustedScriptURL` message from Pyodide's
  own startup probe (`importScripts("data:…")`). It is caught by Pyodide and harmless.
- `server.py` is fine for local use and small deployments. For the public internet put
  it behind a TLS reverse proxy (Caddy/nginx) with rate limiting, start it with
  `--host 127.0.0.1 --allowed-host your.domain`, and keep the same response headers if
  you serve `public/` from another host (see `SECURITY_HEADERS` in `server.py`).

## Hosting on GitHub Pages

The app is fully static, so GitHub Pages can host it for free. `.github/workflows/pages.yml`
runs the tests and then publishes only `public/` on every push to `main`.

1. Install Git and the GitHub CLI (once), then restart the terminal:
   `winget install --id Git.Git -e` and `winget install --id GitHub.cli -e`
2. Publish (in this folder; set your name/email with `git config` first if Git asks):

   ```powershell
   git init -b main
   git add .
   git commit -m "Python Academy"
   gh auth login
   gh repo create python-academy --public --source . --push
   ```
3. On GitHub: **Settings → Pages → Build and deployment → Source: GitHub Actions**, then re-run
   the workflow (Actions tab). The site appears at `https://<your-username>.github.io/python-academy/`.

Pages cannot send custom HTTP headers, so on Pages the app relies on the CSP `<meta>` tag in
`index.html` (kept identical to the header in `server.py` by a test) and a frame guard in
`app.js`. Compared with `server.py` you lose: `frame-ancestors`/`X-Frame-Options` (the frame guard
covers it), COOP/CORP/`Permissions-Policy`, and the CSP on the Web Worker script itself (a worker
gets its CSP from its own response headers). The learner's code is still confined to the
worker sandbox and the page CSP still blocks injected scripts and outside requests. If you want
the full header set on a free host, use Cloudflare Pages or Netlify with a `_headers` file built
from `SECURITY_HEADERS` in `server.py`.

## Project layout

```
server.py            hardened static server (+ vendored-file integrity check)
build.py             validates content/lessons.py -> public/data/lessons.json
content/lessons.py   all lesson text, exercises, solutions and checks
public/              everything that is served
  js/                app, runner (main thread), worker (Pyodide), workbench, storage, ...
  py/harness.py      runs learner code, captures output, evaluates exercise checks
  vendor/pyodide/    pinned, hash-verified Pyodide
tests/               unittest suites (lessons, harness, server security)
```

## Adding or editing lessons

1. Edit `content/lessons.py` (block types: `p`, `h`, `list`, `tip`, `warn`, `sec` = "Security
   lens" callout, `code` = runnable snippet, `example` = display-only code, `output`).
   Exercises may also list `files` (name -> text) that exist in the program's private folder.
2. Exercise `check` code runs after the learner's program. It can use their variables,
   `_output` (what was printed), `_code`, and `run_again("stdin text")` to re-run the
   program on other input. Use `assert cond, "friendly message"`.
3. `python build.py` to regenerate `public/data/lessons.json`.
4. `python -m unittest discover -s tests` verifies every solution passes its check,
   every starter fails it, and every `output` block matches what the code really prints.

## Tests

```powershell
python -m unittest discover -s tests -v      # lessons, harness, server hardening, vendored files
node --test tests/js/*.test.mjs              # storage, snippets, editor text-editing logic, file names
```

## Playground

The Playground (`#/playground`) is a personal workspace:

- **Saved snippets**: create, rename, duplicate and delete as many as you like (up to 100). Each
  keeps its own code and its own `input()` text. Lessons open their examples as a *new* snippet,
  so your own work is never overwritten. Snippets are included in progress backups.
- **Examples gallery**: 16 runnable examples (basics, text and data, files, classes, security).
  `content/examples.py` is the source; a test runs every one of them.
- **Editor**: line numbers, syntax highlighting, auto-closing brackets and quotes, smart Enter,
  Tab/Shift+Tab (also on several lines), `Ctrl+/` to comment, adjustable text size, and the
  failing line highlighted in red after an error.
- **Run controls**: `Ctrl+Enter` runs everything, `Ctrl+Shift+Enter` runs only the selection.
  Output shows run time and has Copy and Clear.
- **Files**: open a `.py` file (text only, up to 50,000 characters) or download a snippet as `.py`.

The editor is a real `<textarea>` layered over a highlighted copy of its text inside a single
scrolling box, so the layers cannot drift apart. All text is inserted with `textContent`, never HTML.

## Progress tracking

The **My progress** page (`#/progress`) shows completion overall and per topic, a day streak, active
days, answer attempts, and the status, attempts and completion date of every lesson. Progress is
stored only in the browser; **Export progress** saves a JSON backup and **Import progress** merges
one back in, so it can move between devices with no account.

## License

The project's own code and lessons are licensed under the **Apache License 2.0** (see
`LICENSE`). The bundled Pyodide runtime in `public/vendor/pyodide/` is a separate work under
the Mozilla Public License 2.0 (see `THIRD_PARTY_NOTICES.md`).
