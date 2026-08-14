# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Rasit Narcicek
"""
test_web_server_api.py - Unit tests for the backend.web_server REST API layer.

Covers pure helper functions of web_server.py without starting a live server:
owerwrite flag coercion, multipart/form-data parsing, job store schema
completeness, log cap enforcement, SVG content validation, and final package
URL construction. Never runs the full analysis pipeline.
"""
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from backend.web_server import (
    MAX_LOGS_PER_JOB,
    _build_final_package,
    _parse_multipart,
    _parse_overwrite_flag,
    add_job_log,
    create_job,
    is_valid_svg,
)
from backend.processor import ExecutionResult


class TestParseOverwriteFlag(unittest.TestCase):
    """Overwrite flag must coerce all frontend/CLI value types."""

    def test_none_defaults_false(self):
        self.assertFalse(_parse_overwrite_flag(None))

    def test_string_true_variants(self):
        for v in ("1", "true", "TRUE", "yes", "on"):
            self.assertTrue(_parse_overwrite_flag(v), v)

    def test_string_false_variants(self):
        for v in ("0", "false", "no", "off", ""):
            self.assertFalse(_parse_overwrite_flag(v), v)

    def test_bool_passthrough(self):
        self.assertTrue(_parse_overwrite_flag(True))
        self.assertFalse(_parse_overwrite_flag(False))

    def test_int_coercion(self):
        self.assertTrue(_parse_overwrite_flag(1))
        self.assertFalse(_parse_overwrite_flag(0))


class TestMultipartParsing(unittest.TestCase):
    """stdlib multipart parser handles browser FormData bodies."""

    def _body(self, fields, files):
        boundary = "----WebKitFormBoundaryUNIT"
        parts = []
        for name, value in fields.items():
            parts.append(
                f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode()
            )
        for name, (fname, content) in files.items():
            parts.append(
                f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"; filename=\"{fname}\"\r\n"
                f"Content-Type: image/svg+xml\r\n\r\n".encode() + content + b"\r\n"
            )
        parts.append(f"--{boundary}--\r\n".encode())
        return b"".join(parts)

    def test_parses_fields_and_files(self):
        content_type = 'multipart/form-data; boundary=----WebKitFormBoundaryUNIT'
        svg = b'<svg xmlns="http://www.w3.org/2000/svg"><rect width="10" height="10"/></svg>'
        body = self._body({"levels": "5", "overwrite": "false"}, {"file": ("16D.svg", svg)})
        parsed = _parse_multipart(content_type, body)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["fields"]["levels"], "5")
        self.assertEqual(parsed["fields"]["overwrite"], "false")
        self.assertEqual(parsed["files"]["file"][0][0], "16D.svg")
        self.assertEqual(parsed["files"]["file"][0][1], svg)

    def test_rejects_non_multipart(self):
        self.assertIsNone(_parse_multipart("application/json", b"{}"))

    def test_rejects_missing_boundary(self):
        self.assertIsNone(_parse_multipart("multipart/form-data", b"x"))

class TestJobStoreSchema(unittest.TestCase):
    """create_job must return the full Scientific Console contract."""

    EXPECTED_KEYS = {
        "job_id", "mode", "status", "current_file", "total_files", "completed_files",
        "requested_levels", "current_level", "elapsed_seconds", "current_step",
        "start_time", "steps", "scale_rows", "regression", "batch_queue", "logs",
        "final_package",
    }
    EXPECTED_REGRESSION_KEYS = {
        "status", "db", "r2", "confidence_score", "confidence_label", "academic_comment",
    }

    def _store(self):
        import backend.web_server as ws
        return ws.JOBS_STORE

    def test_job_schema_complete(self):
        job_id = create_job(mode="single", total_files=1, current_file="16D.svg", levels=7)
        try:
            job = self._store()[job_id]
            self.assertEqual(set(job.keys()), self.EXPECTED_KEYS)
            self.assertEqual(job["mode"], "single")
            self.assertEqual(job["total_files"], 1)
            self.assertEqual(job["requested_levels"], 7)
            self.assertEqual(job["status"], "queued")
            self.assertEqual(job["scale_rows"], [])
            self.assertEqual(set(job["regression"].keys()), self.EXPECTED_REGRESSION_KEYS)
            self.assertEqual(len(job["steps"]), 7)
            self.assertIsNone(job["final_package"])
        finally:
            self._store().pop(job_id, None)

    def test_log_cap_enforced(self):
        job_id = create_job()
        try:
            for i in range(MAX_LOGS_PER_JOB + 50):
                add_job_log(job_id, f"log line {i}")
            self.assertLessEqual(len(self._store()[job_id]["logs"]), MAX_LOGS_PER_JOB)
            first_msg = self._store()[job_id]["logs"][0]["message"]
            self.assertNotEqual(first_msg, "log line 0")
        finally:
            self._store().pop(job_id, None)


class TestSvgValidation(unittest.TestCase):
    """is_valid_svg guards against non-SVG uploads."""

    def test_accepts_svg_tag(self):
        self.assertTrue(is_valid_svg(b'<svg xmlns="http://www.w3.org/2000/svg"></svg>'))

    def test_accepts_namespace(self):
        self.assertTrue(is_valid_svg(b'<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg">'))

    def test_rejects_plain_text(self):
        self.assertFalse(is_valid_svg(b"hello world, not an svg"))

    def test_rejects_empty(self):
        self.assertFalse(is_valid_svg(b""))


class TestFinalPackageBuilder(unittest.TestCase):
    """_build_final_package must produce correct relative URLs."""

    def _make_pkg(self, root, folder):
        pkg = root / folder
        (pkg / "report").mkdir(parents=True)
        (pkg / "tables").mkdir()
        (pkg / "excel").mkdir()
        (pkg / "manifest").mkdir()
        (pkg / "figures").mkdir()
        (pkg / "report" / "report.html").write_text("<html></html>", encoding="utf-8")
        (pkg / "report" / "report.pdf").write_bytes(b"%PDF")
        (pkg / "tables" / "tables.html").write_text("<html></html>", encoding="utf-8")
        (pkg / "excel" / "workbook.xlsx").write_bytes(b"PK")
        (pkg / "manifest" / "manifest.json").write_text("{}", encoding="utf-8")
        (pkg / "figures" / "01_4x8_map.svg").write_text("<svg></svg>", encoding="utf-8")
        return pkg

    def test_builds_urls_for_existing_package(self):
        real_out = Path("outputs").resolve()
        test_folder = "__ws_api_unit_test__"
        self._make_pkg(real_out, test_folder)
        try:
            res = ExecutionResult(
                job_id="j1", input_file="16D.svg", output_dir=str(real_out),
                analysis_mode="balanced", requested_levels=7, computed_levels_count=7,
                status="SUCCESS", package_id=test_folder,
                fractal_dimension=1.88, r_squared=0.99,
            )
            res.motif_profile = {"motif": "16D"}
            res.generated_at = "2026-08-01 18:10:20"
            fp = _build_final_package(res)
            self.assertIsNotNone(fp)
            self.assertEqual(fp["package_id"], test_folder)
            self.assertTrue(fp["report_url"].startswith(test_folder + "/"))
            self.assertTrue(fp["tables_url"].startswith(test_folder + "/"))
            self.assertTrue(fp["workbook_url"].startswith(test_folder + "/"))
            self.assertTrue(fp["manifest_url"].startswith(test_folder + "/"))
            self.assertTrue(fp["figures_url"].startswith(test_folder + "/"))
        finally:
            shutil.rmtree(real_out / test_folder, ignore_errors=True)

    def test_returns_none_without_package_id(self):
        res = ExecutionResult(
            job_id="j1", input_file="x.svg", output_dir="outputs",
            analysis_mode="balanced", requested_levels=7, computed_levels_count=0,
            status="FAILED",
        )
        self.assertIsNone(_build_final_package(res))

    def test_final_package_carries_rh_engine_markers(self):
        """final_package must expose the RASH-HIT Fractal Engine package-level policy markers
        (cells-omitted / row-run levels) so the Scientific Console NegSpace
        tooltip can show package-based detail on top of per-level metrics."""
        import json
        real_out = Path("outputs").resolve()
        test_folder = "__ws_api_rh_engine_test__"
        self._make_pkg(real_out, test_folder)
        try:
            # tables_data.json marks L02+L03 as cells_omitted (RASH-HIT Fractal Engine high-level
            # policy), and an SVG figure carries the run-length marker comment.
            td = real_out / test_folder / "tables" / "tables_data.json"
            td.write_text(json.dumps({
                "levels": {
                    "L02": {"cells_omitted": True},
                    "L03": {"cells_omitted": True},
                }
            }), encoding="utf-8")
            fig = real_out / test_folder / "figures" / "02_4x4_map.svg"
            fig.write_text("<svg><!-- run-length / row-run merged --></svg>", encoding="utf-8")

            res = ExecutionResult(
                job_id="j1", input_file="16D.svg", output_dir=str(real_out),
                analysis_mode="balanced", requested_levels=7, computed_levels_count=7,
                status="SUCCESS", package_id=test_folder,
                fractal_dimension=1.88, r_squared=0.99,
            )
            res.motif_profile = {"motif": "16D"}
            res.generated_at = "2026-08-05 00:00:00"
            fp = _build_final_package(res)
            self.assertIsNotNone(fp)
            self.assertEqual(fp["rh_engine_cells_omitted_count"], 2)
            self.assertEqual(fp["rh_engine_cells_omitted_levels"], [2, 3])
            self.assertEqual(fp["rh_engine_row_run_count"], 1)
            self.assertEqual(fp["rh_engine_row_run_levels"], [2])
            self.assertTrue(fp["rh_engine_uses_row_runs"])
        finally:
            shutil.rmtree(real_out / test_folder, ignore_errors=True)

    def test_final_package_rh_engine_markers_default_clean(self):
        """Legacy packages without RASH-HIT Fractal Engine artifacts must yield zero markers."""
        real_out = Path("outputs").resolve()
        test_folder = "__ws_api_rh_engine_plain__"
        self._make_pkg(real_out, test_folder)
        try:
            res = ExecutionResult(
                job_id="j1", input_file="16D.svg", output_dir=str(real_out),
                analysis_mode="balanced", requested_levels=7, computed_levels_count=7,
                status="SUCCESS", package_id=test_folder,
                fractal_dimension=1.88, r_squared=0.99,
            )
            res.motif_profile = {"motif": "16D"}
            res.generated_at = "2026-08-05 00:00:00"
            fp = _build_final_package(res)
            self.assertEqual(fp["rh_engine_cells_omitted_count"], 0)
            self.assertEqual(fp["rh_engine_cells_omitted_levels"], [])
            self.assertEqual(fp["rh_engine_row_run_count"], 0)
            self.assertEqual(fp["rh_engine_row_run_levels"], [])
            self.assertFalse(fp["rh_engine_uses_row_runs"])
        finally:
            shutil.rmtree(real_out / test_folder, ignore_errors=True)

class TestScaleRowSchema(unittest.TestCase):
    """_build_scale_row must produce the exact Live Scale Table contract."""

    class _LM:
        level = 3
        grid_label = "16x32"
        cell_w = 8.86
        cell_h = 8.86
        filled_cells = 272
        total_cells = 512
        occupancy_percent = 53.125
        execution_time_ms = 10.0

    EXPECTED_KEYS = {
        "level", "grid_label", "box_size_w", "box_size_h", "inv_box_size",
        "occupied_count", "total_count", "empty_count", "occupancy_percent",
        "log_inv_r", "log_nr", "included_in_fit", "exclusion_reason",
        "duration_seconds", "status",
        # RASH-HIT Fractal Engine: Negative Space Cache metrics on the real per-level callback row.
        "empty_parents_skipped", "negative_space_cached_cells",
        # RASH-HIT Fractal Engine expanded realtime metrics (absent on legacy models -> 0/"").
        "candidate_count", "active_parent_count", "empty_candidate_count",
        "active_growth_rate", "empty_descendants_skipped_estimate",
        "cell_storage_mode", "output_policy_note",
    }

    def test_scale_row_keys_and_values(self):
        from backend.web_server import _build_scale_row
        row = _build_scale_row(self._LM())
        self.assertEqual(set(row.keys()), self.EXPECTED_KEYS)
        self.assertEqual(row["level"], 3)
        self.assertEqual(row["grid_label"], "16x32")
        self.assertEqual(row["occupied_count"], 272)
        self.assertEqual(row["total_count"], 512)
        self.assertEqual(row["occupancy_percent"], 53.12)
        self.assertEqual(row["status"], "DONE")
        self.assertAlmostEqual(row["log_nr"], 2.4345, places=3)
        # RASH-HIT Fractal Engine metrics default to 0 when the level model has no pruning data.
        self.assertEqual(row["empty_parents_skipped"], 0)
        self.assertEqual(row["negative_space_cached_cells"], 0)

    def test_scale_row_carries_rh_engine_metrics(self):
        """Real per-level callback rows must surface the Negative Space Cache
        metrics computed by the counting engine (RASH-HIT Fractal Engine)."""
        from backend.web_server import _build_scale_row
        lm = self._LM()
        lm.empty_parents_skipped = 19
        lm.negative_space_cached_cells = 76
        row = _build_scale_row(lm)
        self.assertEqual(row["empty_parents_skipped"], 19)
        self.assertEqual(row["negative_space_cached_cells"], 76)

    def test_scale_row_no_zero_logs(self):
        from backend.web_server import _build_scale_row
        lm = self._LM()
        lm.filled_cells = 0
        row = _build_scale_row(lm)
        self.assertEqual(row["log_nr"], 0.0)
        self.assertEqual(row["occupied_count"], 0)


class TestRemoveReadonlyImport(unittest.TestCase):
    """_remove_readonly (shutil.rmtree onerror callback) depends on the os module."""

    def test_os_module_importable_from_web_server(self):
        import backend.web_server as ws
        self.assertTrue(hasattr(ws, "os"), "web_server module must have 'os' importable")

    def test_remove_readonly_can_chmod_and_delete_readonly_file(self):
        """_remove_readonly must successfully make read-only files writable and delete them."""
        import os
        import stat
        from backend.web_server import _remove_readonly
        with tempfile.TemporaryDirectory() as d:
            ro_dir = Path(d) / "readonly_pkg"
            ro_dir.mkdir()
            ro_file = ro_dir / "read_only.txt"
            ro_file.write_text("protected", encoding="utf-8")
            os.chmod(str(ro_file), stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)

            # Without _remove_readonly, shutil.rmtree would fail on read-only files.
            shutil.rmtree(ro_dir, onerror=_remove_readonly)
            self.assertFalse(ro_dir.exists(), "Read-only package folder must be deleted via _remove_readonly")


class TestJobStepHelpers(unittest.TestCase):
    """update_job_step must drive the step timeline contract."""

    def _store(self):
        import backend.web_server as ws
        return ws.JOBS_STORE

    def test_update_step_marks_running_then_done(self):
        import backend.web_server as ws
        job_id = ws.create_job()
        try:
            ws.update_job_step(job_id, ws.AnalysisProcessor.STANDARD_STEP_NAMES[0], "running")
            job = self._store()[job_id]
            self.assertEqual(job["status"], "running")
            self.assertEqual(job["steps"][0]["status"], "running")
            ws.update_job_step(job_id, ws.AnalysisProcessor.STANDARD_STEP_NAMES[0], "done")
            job = self._store()[job_id]
            self.assertEqual(job["steps"][0]["status"], "done")
            self.assertIn("finished_at", job["steps"][0])
        finally:
            self._store().pop(job_id, None)

    def test_scale_row_appends_and_tracks_level(self):
        import backend.web_server as ws
        job_id = ws.create_job()
        try:
            ws.add_job_scale_row(job_id, {"level": 1, "occupied_count": 28, "total_count": 32, "occupancy_percent": 87.5})
            ws.add_job_scale_row(job_id, {"level": 2, "occupied_count": 84, "total_count": 128, "occupancy_percent": 65.6})
            job = self._store()[job_id]
            self.assertEqual(len(job["scale_rows"]), 2)
            self.assertEqual(job["current_level"], 2)
            self.assertEqual(job["scale_rows"][0]["level"], 1)
            self.assertEqual(job["scale_rows"][1]["level"], 2)
        finally:
            self._store().pop(job_id, None)

if __name__ == "__main__":
    unittest.main()


class TestMultipartMalformed(unittest.TestCase):
    """ISSUE-008: malformed multipart bodies must be rejected (None) instead of
    being silently mis-parsed into an empty result."""

    CT = "multipart/form-data; boundary=----WebKitFormBoundaryUNIT"
    B = b"----WebKitFormBoundaryUNIT"
    CRLF = b"\r\n"
    CLOSE = b"----WebKitFormBoundaryUNIT--"

    def test_malformed_body_with_no_valid_parts_returns_none(self):
        body = self.B + self.CRLF + b"garbage-not-a-part" + self.CRLF + self.CLOSE + self.CRLF
        self.assertIsNone(_parse_multipart(self.CT, body))

    def test_truncated_part_without_separator_returns_none(self):
        # A part that never terminates with CRLFCRLF/LFLF must be rejected,
        # never silently dropped.
        body = (
            self.B + self.CRLF
            + b'Content-Disposition: form-data; name="file"; filename="x.svg"' + self.CRLF
            + self.CLOSE + self.CRLF
        )
        self.assertIsNone(_parse_multipart(self.CT, body))

    def test_part_without_disposition_returns_none(self):
        # A part lacking Content-Disposition is malformed multipart.
        body = (
            self.B + self.CRLF
            + b"Content-Length: 5" + self.CRLF + self.CRLF + b"hello" + self.CRLF
            + self.CLOSE + self.CRLF
        )
        self.assertIsNone(_parse_multipart(self.CT, body))


class TestJobPersistence(unittest.TestCase):
    """ISSUE-006: job state must survive a server restart via the runtime
    jobs store file (outside outputs/ - pure-data rule)."""

    def setUp(self):
        import backend.web_server as ws
        self.ws = ws
        self._orig_path = os.environ.get("RASH_HIT_JOB_STORE_PATH")
        self._tmp = tempfile.mkdtemp()
        os.environ["RASH_HIT_JOB_STORE_PATH"] = str(Path(self._tmp) / "jobs.json")
        os.environ["RASH_HIT_JOB_STORE"] = "1"
        ws._jobs_loaded = False

    def tearDown(self):
        if self._orig_path is None:
            os.environ.pop("RASH_HIT_JOB_STORE_PATH", None)
        else:
            os.environ["RASH_HIT_JOB_STORE_PATH"] = self._orig_path
        shutil.rmtree(self._tmp, ignore_errors=True)
        self.ws._jobs_loaded = False

    def test_job_survives_restart_marked_interrupted(self):
        ws = self.ws
        job_id = ws.create_job(mode="single", total_files=1, current_file="16D.svg", levels=7)
        # Simulate a server restart: fresh process has an empty in-memory store.
        ws.JOBS_STORE.clear()
        ws._jobs_loaded = False
        ws._load_jobs()
        job = ws.JOBS_STORE.get(job_id)
        self.assertIsNotNone(job, "job must be restored from disk after restart")
        self.assertEqual(job["status"], "interrupted",
                         "orphaned mid-flight job must be marked interrupted")
        self.assertEqual(job["requested_levels"], 7)
