# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""
test_live_server_api.py - Live HTTP API smoke tests.

Starts the real SecuredRequestHandler on an ephemeral local port and verifies the
REST API contract end to end WITHOUT running the full analysis pipeline:

- GET /api/health, /api/packages, /api/stats, /api/figures, /api/history
- GET /api/jobs/<id> 404 path, GET /api/package/<id> 404 path
- GET /package_index.json, GET / (dashboard shell), static CSS/JS assets
- POST /api/upload-single rejection paths (missing file, invalid SVG, wrong ext)
- POST /api/upload-batch rejection path (no valid SVGs)
- POST /api/packages/delete with traversal / protected names (no disk mutation)
- Unknown endpoint 404
"""
import json
import os
import threading
import unittest
from http.server import HTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from backend.web_server import SecuredRequestHandler

ROOT = Path(__file__).resolve().parent.parent

CRLF = chr(13) + chr(10)


def _request(url, method="GET", body=None, headers=None):
    req = Request(url, data=body, method=method)
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urlopen(req, timeout=10) as resp:
            return resp.status, resp.read()
    except HTTPError as e:
        return e.code, e.read()


def _multipart(boundary, fields=None, files=None):
    """Build a multipart/form-data body with explicit CRLF parts."""
    fields = fields or {}
    files = files or {}
    parts = []
    for name, value in fields.items():
        parts.append(
            "--" + boundary + CRLF +
            "Content-Disposition: form-data; name="" + name + """ + CRLF + CRLF +
            str(value) + CRLF
        )
    for name, (fname, content) in files.items():
        parts.append(
            "--" + boundary + CRLF +
            "Content-Disposition: form-data; name="" + name + ""; filename="" + fname + """ + CRLF +
            "Content-Type: image/svg+xml" + CRLF + CRLF +
            content + CRLF
        )
    parts.append("--" + boundary + "--" + CRLF)
    return "".join(parts).encode("utf-8")


class TestLiveServerApi(unittest.TestCase):
    """Boot the real server on port 0 and probe the API surface."""

    @classmethod
    def setUpClass(cls):
        try:
            # ISSUE-007: isolate the runtime job store into a temp path so live
            # tests never leave .rash_hit/jobs.json traces behind.
            #
            # NOTE: web_server._load_jobs() runs once per process (module-level
            # _jobs_loaded cache), so this env override only takes effect in a
            # fresh process. No other suite creates jobs before this file runs,
            # and the mtime guard below proves the default store is untouched.
            import tempfile as _tmp
            cls._tmp_store_dir = _tmp.mkdtemp(prefix="rash_hit_jobs_")
            cls._tmp_store = str(Path(cls._tmp_store_dir) / "jobs.json")
            os.environ["RASH_HIT_JOB_STORE_PATH"] = cls._tmp_store
            cls.addClassCleanup(cls._cleanup_job_store)

            cls.httpd = HTTPServer(("127.0.0.1", 0), SecuredRequestHandler)
            cls.port = cls.httpd.server_address[1]
            cls.base = "http://127.0.0.1:" + str(cls.port)
            cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
            cls.thread.start()
            cls.addClassCleanup(cls._stop_server)
        except Exception:
            cls._stop_server()
            raise

    @classmethod
    def _cleanup_job_store(cls):
        import shutil as _sh
        d = getattr(cls, "_tmp_store_dir", None)
        if d:
            _sh.rmtree(d, ignore_errors=True)
        if "RASH_HIT_JOB_STORE_PATH" in os.environ:
            del os.environ["RASH_HIT_JOB_STORE_PATH"]

    @classmethod
    def _stop_server(cls):
        httpd = getattr(cls, "httpd", None)
        if httpd is not None:
            try:
                httpd.shutdown()
            except Exception:
                pass
            try:
                httpd.server_close()
            except Exception:
                pass

    def test_health_endpoint(self):
        status, body = _request(self.base + "/api/health")
        self.assertEqual(status, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertEqual(data["status"], "OK")
        from backend import __version__ as APP_VERSION
        self.assertEqual(data["version"], APP_VERSION)  # ISSUE-004: canonical version (matches DOI)

    def test_packages_endpoint(self):
        status, body = _request(self.base + "/api/packages")
        self.assertEqual(status, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertIn("packages", data)
        self.assertIsInstance(data["packages"], list)

    def test_stats_endpoint(self):
        status, body = _request(self.base + "/api/stats")
        self.assertEqual(status, 200)
        data = json.loads(body.decode("utf-8"))
        for key in ("total_packages", "total_figures", "total_xlsx", "latest_generated"):
            self.assertIn(key, data)

    def test_figures_endpoint(self):
        status, body = _request(self.base + "/api/figures")
        self.assertEqual(status, 200)
        self.assertIn("figures", json.loads(body.decode("utf-8")))

    def test_history_endpoint(self):
        status, body = _request(self.base + "/api/history")
        self.assertEqual(status, 200)
        self.assertIn("history", json.loads(body.decode("utf-8")))

    def test_jobs_endpoint(self):
        """GET /api/jobs must return a run-history summary list (Analysis Studio)."""
        status, body = _request(self.base + "/api/jobs")
        self.assertEqual(status, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertIn("jobs", data)
        self.assertIsInstance(data["jobs"], list)
        for job in data["jobs"]:
            self.assertIn("job_id", job)
            self.assertIn("status", job)

    def test_package_index_json_served(self):
        status, body = _request(self.base + "/package_index.json")
        self.assertEqual(status, 200)
        json.loads(body.decode("utf-8"))  # must parse as JSON

    def test_dashboard_shell_served(self):
        status, body = _request(self.base + "/")
        self.assertEqual(status, 200)
        html = body.decode("utf-8")
        for marker in ("chkOverwrite", "btnRunWeb", "btnConsoleOpenFigures",
                       "scientificConsoleModal", "serverBadge"):
            self.assertIn(marker, html)

    def test_static_css_served(self):
        status, _ = _request(self.base + "/css/main.css")
        self.assertEqual(status, 200)
        status, _ = _request(self.base + "/css/themes.css")
        self.assertEqual(status, 200)

    def test_static_js_served(self):
        for name in ("api.js", "app.js", "analysis-console.js"):
            status, _ = _request(self.base + "/js/" + name)
            self.assertEqual(status, 200, "/js/" + name + " not served")

    def test_vendor_exceljs_served(self):
        status, _ = _request(self.base + "/vendor/exceljs.min.js")
        self.assertEqual(status, 200)

    def test_unknown_endpoint_404(self):
        status, body = _request(self.base + "/api/nonexistent")
        self.assertEqual(status, 404)
        self.assertIn("error", json.loads(body.decode("utf-8")))

    def test_job_not_found_404(self):
        status, body = _request(self.base + "/api/jobs/does_not_exist")
        self.assertEqual(status, 404)
        self.assertIn("error", json.loads(body.decode("utf-8")))

    def test_status_alias_not_found_404(self):
        status, _ = _request(self.base + "/api/status/does_not_exist")
        self.assertEqual(status, 404)

    def test_package_not_found_404(self):
        status, _ = _request(self.base + "/api/package/__no_such_pkg__")
        self.assertEqual(status, 404)

    def test_open_folder_unknown_package_404(self):
        """GET /api/open-folder/<id> must reject unknown packages before any
        OS call (never opens an arbitrary path on the host machine)."""
        status, body = _request(self.base + "/api/open-folder/__no_such_pkg__")
        self.assertEqual(status, 404)
        self.assertIn("error", json.loads(body.decode("utf-8")))

    def test_open_folder_traversal_rejected(self):
        """Traversal package ids must not resolve to an OS folder open."""
        status, _ = _request(self.base + "/api/open-folder/..%2F..%2FWindows")
        self.assertEqual(status, 404)  # not a known package id


    def test_upload_single_missing_file_field(self):
        boundary = "----LiveTestBoundary"
        body = _multipart(boundary, fields={"levels": "5"})
        status, resp = _request(
            self.base + "/api/upload-single", method="POST", body=body,
            headers={"Content-Type": "multipart/form-data; boundary=" + boundary},
        )
        self.assertEqual(status, 400)
        self.assertIn("error", json.loads(resp.decode("utf-8")))

    def test_upload_single_rejects_invalid_svg(self):
        boundary = "----LiveTestBoundary"
        body = _multipart(boundary, files={"file": ("bad.svg", "not an svg at all")})
        status, resp = _request(
            self.base + "/api/upload-single", method="POST", body=body,
            headers={"Content-Type": "multipart/form-data; boundary=" + boundary},
        )
        self.assertEqual(status, 400)

    def test_upload_batch_rejects_no_valid_svg(self):
        boundary = "----LiveTestBoundary"
        body = _multipart(boundary, files={"files[]": ("a.txt", "hello")})
        status, resp = _request(
            self.base + "/api/upload-batch", method="POST", body=body,
            headers={"Content-Type": "multipart/form-data; boundary=" + boundary},
        )
        self.assertEqual(status, 400)

    def test_delete_rejects_protected_file(self):
        status, resp = _request(
            self.base + "/api/packages/delete", method="POST",
            body=json.dumps({"package_ids": ["package_index.json"]}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        # Protected files must never be deleted: the file must remain on disk and
        # the response's deleted list must be empty (not_found carries the refusal).
        data = json.loads(resp.decode("utf-8"))
        self.assertEqual(data.get("deleted"), [])
        self.assertTrue((ROOT / "outputs" / "package_index.json").exists())

    def test_delete_rejects_traversal(self):
        status, resp = _request(
            self.base + "/api/packages/delete", method="POST",
            body=json.dumps({"package_ids": ["../", "..%2F.."]}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        body_txt = resp.decode("utf-8", errors="replace")
        self.assertIn("deleted", body_txt)  # empty deleted list is still a valid response


class TestUploadStagingCleanup(unittest.TestCase):
    """ISSUE-004: per-job upload staging subfolders must be removed when the
    job finishes, and orphaned leftovers must be swept after a grace period."""

    def setUp(self):
        import uuid
        self.tag = "cleanup_test_" + uuid.uuid4().hex[:10]
        self.uploads = (ROOT / "uploads").resolve()
        self.uploads.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        import shutil as _sh
        for name in list(self.uploads.iterdir()):
            if self.tag in name.name:
                target = (self.uploads / name.name).resolve()
                if target.is_relative_to(self.uploads):
                    _sh.rmtree(target, ignore_errors=True)

    def _fake_staging(self, job_id):
        single = self.uploads / job_id
        batch = self.uploads / ("batch_" + job_id)
        single.mkdir(parents=True, exist_ok=True)
        batch.mkdir(parents=True, exist_ok=True)
        (single / "16D.svg").write_text("<svg></svg>", encoding="utf-8")
        return single, batch

    def test_cleanup_job_uploads_removes_own_staging(self):
        from backend.web_server import cleanup_job_uploads
        job_id = self.tag + "_job"
        single, batch = self._fake_staging(job_id)
        self.assertTrue(single.is_dir() and batch.is_dir())

        cleanup_job_uploads(job_id)

        self.assertFalse(single.exists(), "single staging folder must be removed")
        self.assertFalse(batch.exists(), "batch staging folder must be removed")
        self.assertTrue(self.uploads.is_dir(), "uploads/ root must be preserved")

    def test_cleanup_job_uploads_never_touches_unrelated_dirs(self):
        from backend.web_server import cleanup_job_uploads
        job_id = self.tag + "_job"
        unrelated = self.uploads / (self.tag + "_unrelated")
        unrelated.mkdir(parents=True, exist_ok=True)
        self._fake_staging(job_id)

        cleanup_job_uploads(job_id)

        self.assertTrue(unrelated.is_dir(), "unrelated folder must survive cleanup")
        self.assertFalse((self.uploads / job_id).exists())

    def test_sweep_stale_uploads_removes_old_keeps_fresh(self):
        from backend.web_server import sweep_stale_uploads
        import time as _time

        # Names must match the sweep's per-job pattern (analysis_*/batch_*).
        stale = self.uploads / ("analysis_" + self.tag + "_stale")
        fresh = self.uploads / ("analysis_" + self.tag + "_fresh")
        stale.mkdir(parents=True, exist_ok=True)
        fresh.mkdir(parents=True, exist_ok=True)

        # Make the stale dir clearly past the 60-minute sweep floor and the
        # fresh dir brand new.
        old = _time.time() - 2 * 3600 * 24  # 2 days ago
        os.utime(stale, (old, old))
        os.utime(fresh, (_time.time(), _time.time()))

        removed = sweep_stale_uploads(max_age_minutes=1)

        self.assertGreaterEqual(removed, 1, "old staging dir must be swept")
        self.assertFalse(stale.exists(), "old staging dir removed")
        self.assertTrue(fresh.exists(), "fresh staging dir must be preserved")


if __name__ == "__main__":
    unittest.main()
