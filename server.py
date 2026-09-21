#!/usr/bin/env python3
"""Hardened static file server for Python Academy (standard library only).

The app is 100% static: learner code runs in the visitor's browser (Pyodide in a
Web Worker), so this server never executes, stores or accepts user data.
Its job is to serve ``public/`` with strict security headers and nothing else.

    python server.py                       # http://127.0.0.1:8000
    python server.py --port 9000
    python server.py --host 0.0.0.0 --allowed-host learn.example.com   # behind a TLS proxy
"""
from __future__ import annotations

import argparse
import hashlib
import http.server
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ROOT = (BASE_DIR / "public").resolve()
VENDOR_SUMS = ROOT / "vendor" / "pyodide" / "SHA256SUMS.txt"

# 'wasm-unsafe-eval' is required to compile WebAssembly (Pyodide) and nothing more:
# no 'unsafe-inline', no 'unsafe-eval', no third-party origins.
CSP = "; ".join(
    [
        "default-src 'none'",
        "script-src 'self' 'wasm-unsafe-eval'",
        "style-src 'self'",
        "img-src 'self'",
        "font-src 'self'",
        "connect-src 'self'",
        "worker-src 'self'",
        "base-uri 'none'",
        "form-action 'none'",
        "frame-ancestors 'none'",
        "object-src 'none'",
        "require-trusted-types-for 'script'",
        "trusted-types python-academy-worker",  # the one policy js/runner.js creates
    ]
)

SECURITY_HEADERS = {
    "Content-Security-Policy": CSP,
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
    "Permissions-Policy": (
        "accelerometer=(), camera=(), display-capture=(), geolocation=(), gyroscope=(), "
        "microphone=(), midi=(), payment=(), usb=(), serial=(), bluetooth=(), interest-cohort=()"
    ),
    # Only honoured by browsers when received over HTTPS (i.e. behind a TLS proxy).
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
}

# Explicit allowlist: anything with another extension is a 404, so stray files
# (backups, source maps, dotfiles) can never be served by accident.
MIME_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".mjs": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".wasm": "application/wasm",
    ".zip": "application/zip",
    ".svg": "image/svg+xml",
    ".py": "text/plain; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
}

# Raw request paths may only contain these characters. Percent-escapes, backslashes,
# colons (NTFS alternate data streams) and NUL bytes are rejected before touching disk.
SAFE_PATH = re.compile(r"/[A-Za-z0-9._/-]*")
LOOPBACK_HOSTS = frozenset({"localhost", "127.0.0.1", "[::1]"})
CHUNK = 64 * 1024


def resolve_static(raw_target: str) -> tuple[Path, str] | None:
    """Map a request target to (file, content-type) inside ROOT, or None."""
    path = raw_target.split("?", 1)[0].split("#", 1)[0]
    if path.endswith("/"):
        path += "index.html"
    if not SAFE_PATH.fullmatch(path):
        return None
    parts = path.split("/")[1:]
    if any(p in ("", ".", "..") or p.startswith(".") for p in parts):
        return None
    try:
        resolved = ROOT.joinpath(*parts).resolve(strict=True)
    except (OSError, RuntimeError, ValueError):
        return None
    # Re-check after resolving so symlinks/junctions cannot point outside ROOT.
    if not resolved.is_file() or not resolved.is_relative_to(ROOT):
        return None
    content_type = MIME_TYPES.get(resolved.suffix.lower())
    if content_type is None:
        return None
    return resolved, content_type


def cache_control(path: Path) -> str:
    # Vendored Pyodide is pinned and hash-verified, so it can be cached hard.
    if path.is_relative_to(ROOT / "vendor"):
        return "public, max-age=604800, immutable"
    return "no-cache"


def host_of(header: str) -> str:
    """Hostname part of a Host header (port stripped, IPv6 literals kept bracketed)."""
    header = header.strip().lower()
    if header.startswith("["):
        return header[: header.find("]") + 1] if "]" in header else header
    return header.split(":", 1)[0]


class Handler(http.server.BaseHTTPRequestHandler):
    server_version = "PythonAcademy"  # no Python/OS version is advertised
    protocol_version = "HTTP/1.1"
    timeout = 15  # drop idle/slow connections (slowloris)
    allowed_hosts: frozenset[str] = LOOPBACK_HOSTS
    error_message_format = (
        "<!doctype html><meta charset=utf-8><title>%(code)d</title><p>%(code)d %(message)s</p>"
    )

    def version_string(self) -> str:
        return self.server_version

    def end_headers(self) -> None:
        # Applied to every response, including error pages.
        for name, value in SECURITY_HEADERS.items():
            self.send_header(name, value)
        super().end_headers()

    def do_GET(self) -> None:
        self._serve(send_body=True)

    def do_HEAD(self) -> None:
        self._serve(send_body=False)

    def _method_not_allowed(self) -> None:
        self.send_response(405, "Method Not Allowed")
        self.send_header("Allow", "GET, HEAD")
        self.send_header("Content-Length", "0")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True

    do_POST = do_PUT = do_DELETE = do_PATCH = do_OPTIONS = _method_not_allowed

    def _serve(self, send_body: bool) -> None:
        # Reject unexpected Host headers: defeats DNS-rebinding attacks on a local server.
        host = self.headers.get("Host")
        if not host or host_of(host) not in self.allowed_hosts:
            self.send_error(403, "Forbidden")
            return

        found = resolve_static(self.path)
        if found is None:
            self.send_error(404, "Not Found")
            return
        path, content_type = found

        try:
            with path.open("rb") as fh:
                size = path.stat().st_size
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(size))
                self.send_header("Cache-Control", cache_control(path))
                self.end_headers()
                if send_body:
                    while chunk := fh.read(CHUNK):
                        self.wfile.write(chunk)
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            self.close_connection = True

    def log_message(self, format: str, *args) -> None:  # noqa: A002 - stdlib signature
        sys.stderr.write("%s - %s\n" % (self.address_string(), format % args))


def verify_vendor_files() -> list[str]:
    """Compare vendored Pyodide files against SHA256SUMS.txt; return problems."""
    problems: list[str] = []
    try:
        lines = VENDOR_SUMS.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [f"cannot read {VENDOR_SUMS.name}: {exc}"]
    listed = set()
    for line in filter(None, (ln.strip() for ln in lines)):
        digest, _, name = line.partition("  ")
        listed.add(name)
        target = VENDOR_SUMS.parent / name
        try:
            actual = hashlib.sha256(target.read_bytes()).hexdigest()
        except OSError:
            problems.append(f"missing vendored file: {name}")
            continue
        if actual != digest:
            problems.append(f"hash mismatch: {name}")
    for extra in VENDOR_SUMS.parent.iterdir():
        if extra.is_file() and extra.name != VENDOR_SUMS.name and extra.name not in listed:
            problems.append(f"unlisted file in vendor directory: {extra.name}")
    return problems


def make_server(host: str, port: int, extra_hosts: tuple[str, ...] = ()) -> http.server.ThreadingHTTPServer:
    allowed = set(LOOPBACK_HOSTS) | {h.strip().lower() for h in extra_hosts if h.strip()}
    handler = type("BoundHandler", (Handler,), {"allowed_hosts": frozenset(allowed)})
    server = http.server.ThreadingHTTPServer((host, port), handler)
    server.daemon_threads = True
    return server


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--host", default="127.0.0.1", help="interface to bind (default: 127.0.0.1, local only)")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument(
        "--allowed-host",
        action="append",
        default=[],
        metavar="HOSTNAME",
        help="extra Host header hostname to accept (repeatable), e.g. your public domain",
    )
    args = parser.parse_args()

    problems = verify_vendor_files()
    if problems:
        print("Refusing to start: vendored Pyodide failed integrity verification:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    server = make_server(args.host, args.port, tuple(args.allowed_host))
    shown = "localhost" if args.host in ("127.0.0.1", "0.0.0.0") else args.host
    print(f"Python Academy running at http://{shown}:{server.server_address[1]}/  (Ctrl+C to stop)")
    if args.host not in ("127.0.0.1", "localhost", "::1"):
        print(
            "WARNING: bound to a non-loopback interface. Put this behind an HTTPS reverse proxy "
            "(Caddy/nginx) and add rate limiting before exposing it to the internet.",
            file=sys.stderr,
        )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
