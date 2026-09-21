"""Security tests for server.py: headers, path traversal, methods, Host validation, integrity."""
import http.client
import socket
import sys
import threading
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

import server  # noqa: E402


class ServerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = server.make_server("127.0.0.1", 0, extra_hosts=("learn.example.com",))
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def request(self, method, path, headers=None, host="localhost"):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        try:
            conn.putrequest(method, path, skip_host=True, skip_accept_encoding=True)
            if host is not None:
                conn.putheader("Host", host)
            for key, value in (headers or {}).items():
                conn.putheader(key, value)
            conn.endheaders()
            response = conn.getresponse()
            return response.status, {k.lower(): v for k, v in response.getheaders()}, response.read()
        finally:
            conn.close()


class Headers(ServerTestCase):
    def test_every_response_has_security_headers(self):
        for path in ("/", "/js/app.js", "/nope", "/vendor/pyodide/pyodide.asm.wasm"):
            with self.subTest(path=path):
                status, headers, _ = self.request("GET", path)
                self.assertIn(status, (200, 404))
                for name in server.SECURITY_HEADERS:
                    self.assertIn(name.lower(), headers, f"{name} missing on {path}")
                self.assertEqual(headers["x-content-type-options"], "nosniff")

    def test_csp_is_strict(self):
        _, headers, _ = self.request("GET", "/")
        csp = headers["content-security-policy"]
        self.assertIn("default-src 'none'", csp)
        self.assertIn("frame-ancestors 'none'", csp)
        self.assertIn("script-src 'self' 'wasm-unsafe-eval'", csp)
        self.assertNotIn("unsafe-inline", csp)
        self.assertNotIn("'unsafe-eval'", csp)
        self.assertIn("require-trusted-types-for 'script'", csp)
        self.assertIn("trusted-types python-academy-worker", csp)
        self.assertNotIn("http:", csp)
        self.assertNotIn("*", csp)

    def test_html_uses_no_inline_script_or_style(self):
        _, _, body = self.request("GET", "/")
        text = body.decode().lower()
        self.assertNotIn("<style", text)
        self.assertNotIn(" style=", text)
        self.assertNotIn(" onclick=", text)
        self.assertNotRegex(text, r"<script(?![^>]*\bsrc=)")

    def test_no_server_version_leak(self):
        _, headers, _ = self.request("GET", "/")
        self.assertEqual(headers["server"], "PythonAcademy")

    def test_content_types(self):
        expectations = {
            "/": "text/html",
            "/js/app.js": "text/javascript",
            "/css/style.css": "text/css",
            "/data/lessons.json": "application/json",
            "/vendor/pyodide/pyodide.asm.wasm": "application/wasm",
            "/py/harness.py": "text/plain",
        }
        for path, expected in expectations.items():
            with self.subTest(path=path):
                status, headers, _ = self.request("GET", path)
                self.assertEqual(status, 200)
                self.assertTrue(headers["content-type"].startswith(expected), headers["content-type"])


class PathHandling(ServerTestCase):
    def test_traversal_and_odd_paths_are_rejected(self):
        bad = [
            "/../server.py",
            "/../../Windows/win.ini",
            "/..%2fserver.py",
            "/%2e%2e/server.py",
            "/js/../../server.py",
            "/js/%2e%2e/%2e%2e/server.py",
            "/js\\..\\..\\server.py",
            "/index.html::$DATA",
            "/index.html%00.txt",
            "/.git/config",
            "/js/.hidden",
            "//etc/passwd",
            "/js//app.js",
            "http://evil.example/index.html",
            "/vendor/pyodide/SHA256SUMS.txt.bak",
            "/js",  # directory without trailing slash
            "/nul",
            "/CON",
        ]
        for path in bad:
            with self.subTest(path=path):
                try:
                    status, _, body = self.request("GET", path)
                except (http.client.HTTPException, ConnectionError, socket.timeout):
                    continue  # connection refused/closed is also a rejection
                self.assertIn(status, (400, 403, 404), f"{path} -> {status}")
                self.assertNotIn(b"import http.server", body)

    def test_source_files_outside_public_are_not_reachable(self):
        for path in ("/server.py", "/build.py", "/content/lessons.py", "/tests/test_server.py", "/README.md"):
            with self.subTest(path=path):
                status, _, _ = self.request("GET", path)
                self.assertEqual(status, 404)

    def test_unlisted_extension_is_404(self):
        status, _, _ = self.request("GET", "/vendor/pyodide/pyodide.mjs.map")
        self.assertEqual(status, 404)

    def test_directory_index_and_no_listing(self):
        status, _, body = self.request("GET", "/js/")
        self.assertEqual(status, 404)
        status, _, body = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn(b"Python Academy", body)

    def test_query_string_ignored_safely(self):
        status, _, _ = self.request("GET", "/index.html?x=<script>alert(1)</script>")
        self.assertEqual(status, 200)

    def test_error_page_does_not_reflect_path(self):
        status, _, body = self.request("GET", "/nope-<script>alert(1)</script>")
        self.assertIn(status, (400, 404))
        self.assertNotIn(b"<script>alert", body)


class MethodsAndHost(ServerTestCase):
    def test_only_get_and_head(self):
        for method in ("POST", "PUT", "DELETE", "PATCH", "OPTIONS"):
            with self.subTest(method=method):
                status, headers, _ = self.request(method, "/")
                self.assertEqual(status, 405)
                self.assertEqual(headers["allow"], "GET, HEAD")
        for method in ("TRACE", "CONNECT"):
            with self.subTest(method=method):
                status, _, _ = self.request(method, "/")
                self.assertNotEqual(status, 200)

    def test_head_has_no_body(self):
        status, headers, body = self.request("HEAD", "/")
        self.assertEqual(status, 200)
        self.assertEqual(body, b"")
        self.assertGreater(int(headers["content-length"]), 0)

    def test_dns_rebinding_host_rejected(self):
        for host in ("evil.example", "evil.example:8000", "localhost.evil.example", "127.0.0.1.evil.example", None):
            with self.subTest(host=host):
                status, _, _ = self.request("GET", "/", host=host)
                self.assertIn(status, (400, 403))

    def test_allowed_hosts_accepted(self):
        for host in ("localhost", "localhost:8000", "127.0.0.1:1234", "[::1]:8000", "learn.example.com", "LEARN.example.com:443"):
            with self.subTest(host=host):
                status, _, _ = self.request("GET", "/", host=host)
                self.assertEqual(status, 200)

    def test_cache_policy(self):
        _, headers, _ = self.request("GET", "/js/app.js")
        self.assertEqual(headers["cache-control"], "no-cache")
        _, headers, _ = self.request("GET", "/vendor/pyodide/pyodide.mjs")
        self.assertIn("immutable", headers["cache-control"])


class StaticHosting(unittest.TestCase):
    """The app must also work (and stay locked down) on hosts like GitHub Pages: sub-path URLs, no custom headers."""

    def setUp(self):
        self.html = (server.ROOT / "index.html").read_text(encoding="utf-8")

    def test_meta_csp_matches_server_csp(self):
        import re

        match = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]+)"', self.html)
        self.assertIsNotNone(match, "index.html needs a CSP <meta> for hosts that can't send headers")
        meta = [d.strip() for d in match.group(1).split(";")]
        header = [d for d in (x.strip() for x in server.CSP.split(";")) if not d.startswith("frame-ancestors")]
        self.assertEqual(meta, header, "meta CSP drifted from server.CSP (frame-ancestors is header-only)")
        self.assertLess(self.html.index("Content-Security-Policy"), self.html.index("<script"), "CSP meta must precede scripts")

    def test_no_root_absolute_urls_so_subpath_hosting_works(self):
        import re

        self.assertNotRegex(self.html, r'(?:src|href)="/[^/]', "index.html must use relative URLs")
        for path in (server.ROOT / "js").glob("*.js"):
            text = path.read_text(encoding="utf-8")
            for match in re.finditer(r"""(?:fetch|new URL|new Worker)\(\s*['"`](/[^/][^'"`]*)""", text):
                self.fail(f"{path.name} uses a root-absolute URL: {match.group(1)}")
        self.assertNotRegex((server.ROOT / "css" / "style.css").read_text(encoding="utf-8"), r"url\(\s*['\"]?/")

    def test_frame_guard_present(self):
        app = (server.ROOT / "js" / "app.js").read_text(encoding="utf-8")
        self.assertIn("window.top !== window.self", app)


class Integrity(unittest.TestCase):
    def test_vendored_pyodide_matches_recorded_hashes(self):
        self.assertEqual(server.verify_vendor_files(), [])

    def test_tampering_is_detected(self):
        target = server.VENDOR_SUMS.parent / "pyodide.mjs"
        original = target.read_bytes()
        try:
            target.write_bytes(original + b"\n// tampered")
            self.assertIn("hash mismatch: pyodide.mjs", server.verify_vendor_files())
        finally:
            target.write_bytes(original)
        self.assertEqual(server.verify_vendor_files(), [])


if __name__ == "__main__":
    unittest.main()
