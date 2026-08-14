# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""
web_server.py - Security-scoped Python HTTP Server & REST API for RASH-HIT Fractal Studio.
Provides standard library REST API endpoints for single analysis, batch analysis,
job status polling, drag-and-drop file uploads, package indexing, figures listing,
and static asset serving with path traversal protection.
"""
from __future__ import annotations

import sys
from pathlib import Path
# Bootstrap: when executed directly (python backend/web_server.py), make the
# project root importable so `backend.*` packages resolve.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import os
import re
import shutil
import subprocess
import threading
import time
import webbrowser
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from backend.batch_processor import run_batch_analysis
from backend.package_index import scan_all_packages, get_all_figures, build_stats, build_history
from backend import __version__ as APP_VERSION
from backend.processor import AnalysisProcessor, ExecutionResult, StepProgress

# Security Constants

def _remove_readonly(func, path, exc_info):
    import stat
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass

def _open_in_os_explorer(folder_path: Path) -> bool:
    """Open a directory in the OS file explorer (best effort, never raises).

    Windows uses os.startfile (Explorer), macOS `open`, Linux `xdg-open`.
    """
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(folder_path))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(folder_path)])
        else:
            subprocess.Popen(["xdg-open", str(folder_path)])
        return True
    except Exception:
        return False


def _uploads_root() -> Path:
    return Path("uploads").resolve()

def cleanup_job_uploads(job_id: str):
    if not job_id:
        return
    root = _uploads_root()
    for sub in (job_id, f"batch_{job_id}"):
        target = (root / sub).resolve()
        try:
            if target.is_relative_to(root) and target.is_dir():
                shutil.rmtree(target, onerror=_remove_readonly)
        except Exception:
            pass

def sweep_stale_uploads(max_age_minutes: float = 24 * 60):
    max_age_minutes = max(max_age_minutes, 60)
    root = _uploads_root()
    if not root.is_dir():
        return 0
    cutoff = time.time() - max_age_minutes * 60
    removed = 0
    try:
        for child in list(root.iterdir()):
            if not child.is_dir():
                continue
            if not (child.name.startswith("analysis_") or child.name.startswith("batch_")):
                continue
            try:
                mtime = child.stat().st_mtime
            except OSError:
                continue
            if mtime < cutoff:
                shutil.rmtree(child, onerror=_remove_readonly)
                removed += 1
    except Exception:
        pass
    return removed

MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTENSIONS = {".svg"}

JOBS_STORE: Dict[str, Dict[str, Any]] = {}
JOBS_LOCK = threading.RLock()  # Reentrant: update_job_step/add_job_scale_row call add_job_log while holding it
MAX_JOBS_STORE = 50
MAX_LOGS_PER_JOB = 500


_jobs_loaded = False

def _job_store_path() -> Path:
    override = os.environ.get("RASH_HIT_JOB_STORE_PATH", "").strip()
    if override:
        return Path(override)
    return Path(".rash_hit/jobs.json").resolve()

def _save_jobs():
    with JOBS_LOCK:
        try:
            p = _job_store_path()
            p.parent.mkdir(parents=True, exist_ok=True)
            serializable = {}
            for jid, job in JOBS_STORE.items():
                jc = dict(job)
                serializable[jid] = jc
            p.write_text(json.dumps(serializable, indent=2), encoding="utf-8")
        except Exception:
            pass

def _load_jobs():
    global _jobs_loaded
    with JOBS_LOCK:
        if _jobs_loaded:
            return
        try:
            p = _job_store_path()
            if p.is_file():
                data = json.loads(p.read_text(encoding="utf-8"))
                for jid, job in data.items():
                    if job.get("status") in ("running", "queued"):
                        job["status"] = "interrupted"
                    JOBS_STORE[jid] = job
        except Exception:
            pass
        _jobs_loaded = True

def create_job(mode: str = "single", total_files: int = 1, current_file: str = "", levels: int = 7) -> str:
    _load_jobs()
    with JOBS_LOCK:
        if len(JOBS_STORE) >= MAX_JOBS_STORE:
            oldest = list(JOBS_STORE.keys())[:len(JOBS_STORE) - MAX_JOBS_STORE + 1]
            for k in oldest:
                JOBS_STORE.pop(k, None)

        job_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(JOBS_STORE)+1}"
        JOBS_STORE[job_id] = {
            "job_id": job_id,
            "mode": mode,
            "status": "queued",
            "current_file": current_file,
            "total_files": total_files,
            "completed_files": 0,
            "requested_levels": levels,
            "current_level": 0,
            "elapsed_seconds": 0.0,
            "current_step": "Job created",
            "start_time": time.time(),
            "steps": [{"name": n, "status": "waiting"} for n in AnalysisProcessor.STANDARD_STEP_NAMES],
            "scale_rows": [],
            "regression": {
                "status": "waiting",
                "db": None,
                "r2": None,
                "confidence_score": None,
                "confidence_label": None,
                "academic_comment": None
            },
            "batch_queue": [],
            "logs": [
                {"time": time.strftime("%H:%M:%S"), "level": "info", "message": f"Job created: {job_id}"}
            ],
            "final_package": None
        }
        _save_jobs()
        return job_id

def add_job_log(job_id: str, message: str, level: str = "info"):
    _load_jobs()
    with JOBS_LOCK:
        job = JOBS_STORE.get(job_id)
        if not job:
            return
        logs = job["logs"]
        if len(logs) >= MAX_LOGS_PER_JOB:
            logs.pop(0)
        logs.append({"time": time.strftime("%H:%M:%S"), "level": level, "message": message})
        _save_jobs()

def update_job_step(job_id: str, step_name: str, step_status: str = "running", extra_log: str = None):
    _load_jobs()
    with JOBS_LOCK:
        job = JOBS_STORE.get(job_id)
        if not job:
            return
        job["current_step"] = step_name
        job["elapsed_seconds"] = round(time.time() - job["start_time"], 1)
        if step_status == "running":
            job["status"] = "running"
        for st in job["steps"]:
            if st["name"] == step_name:
                st["status"] = step_status
                if step_status == "running" and "started_at" not in st:
                    st["started_at"] = time.strftime("%H:%M:%S")
                elif step_status in ("done", "failed"):
                    st["finished_at"] = time.strftime("%H:%M:%S")
        _save_jobs()
        if extra_log:
            add_job_log(job_id, extra_log, "error" if step_status == "failed" else "info")

def add_job_scale_row(job_id: str, row: Dict[str, Any]):
    _load_jobs()
    with JOBS_LOCK:
        job = JOBS_STORE.get(job_id)
        if not job:
            return
        job["scale_rows"].append(row)
        _save_jobs()
        job["current_level"] = row.get("level", job["current_level"])
        add_job_log(job_id, f"Level {row.get('level')} completed: {row.get('occupied_count')}/{row.get('total_count')} cells ({row.get('occupancy_percent')}%)", "success")




def is_valid_svg(content: bytes) -> bool:
    try:
        text = content.decode("utf-8", errors="ignore").strip()
        return "<svg" in text.lower() or "http://www.w3.org/2000/svg" in text
    except Exception:
        return False


def _parse_multipart(content_type: str, body: bytes):
    """Parse a multipart/form-data body using only the stdlib.

    Returns {"fields": {name: str}, "files": {name: [(filename, bytes), ...]}}
    or None when the body is not valid multipart data.
    """
    if not content_type or "multipart/form-data" not in content_type:
        return None
    m = re.search(r'boundary=(?:"([^"]+)"|([^;]+))', content_type)
    boundary = (m.group(1) or m.group(2)).strip() if m else None
    if not boundary:
        return None
    delimiter = b"--" + boundary.encode("utf-8")
    parts = body.split(delimiter)
    fields: Dict[str, str] = {}
    files: Dict[str, List[tuple]] = {}
    for part in parts:
        stripped = part.strip(b"\r\n")
        if not stripped or stripped == b"--":
            continue
        # Tolerate both CRLF (browser FormData) and LF (stdlib encoders) bodies
        header_blob, sep, content = part.partition(b"\r\n\r\n")
        if not sep:
            header_blob, sep, content = part.partition(b"\n\n")
        if not sep:
            continue
        # Drop only the trailing newline(s) that precede the next boundary delimiter
        content = content.rstrip(b"\r\n")
        headers = header_blob.decode("utf-8", errors="ignore")
        disp = re.search(
            r'Content-Disposition:\s*form-data;\s*name="([^"]+)"(?:;\s*filename="([^"]*)")?',
            headers, re.IGNORECASE,
        )
        if not disp:
            continue
        name = disp.group(1)
        filename = disp.group(2)
        if filename is not None:
            files.setdefault(name, []).append((filename, content))
        else:
            fields[name] = content.decode("utf-8", errors="ignore").strip()
    if not fields and not files:
        return None
    return {"fields": fields, "files": files}


def _build_scale_row(lm) -> Dict[str, Any]:
    """Convert a freshly completed LevelReportModel into the Live Scale Table row schema."""
    import math
    avg_size = (lm.cell_w + lm.cell_h) / 2.0
    inv_r = 1.0 / avg_size if avg_size > 0 else 1.0
    log_inv_r = math.log10(inv_r) if inv_r > 0 else 0.0
    log_nr = math.log10(lm.filled_cells) if lm.filled_cells > 0 else 0.0
    
    empty_cells = lm.total_cells - lm.filled_cells
    inc_fit = getattr(lm, "included_in_fit", True)
    excl_reason = getattr(lm, "exclusion_reason", "")
    
    return {
        "level": lm.level,
        "grid_label": lm.grid_label,
        "box_size_w": round(lm.cell_w, 4),
        "box_size_h": round(lm.cell_h, 4),
        "inv_box_size": round(inv_r, 4),
        "occupied_count": lm.filled_cells,
        "total_count": lm.total_cells,
        "empty_count": empty_cells,
        "occupancy_percent": round(lm.occupancy_percent, 2),
        "log_inv_r": round(log_inv_r, 4),
        "log_nr": round(log_nr, 4),
        "included_in_fit": inc_fit,
        "exclusion_reason": excl_reason,
        "duration_seconds": round(lm.execution_time_ms / 1000.0, 3),
        "status": "DONE",
        # Negative space cache & realtime metrics for test compatibility
        "empty_parents_skipped": getattr(lm, "empty_descendants_skipped_estimate", getattr(lm, "empty_parents_skipped", 0)),
        "negative_space_cached_cells": getattr(lm, "negative_space_cached_cells", 0),
        "candidate_count": getattr(lm, "candidate_count", 0),
        "active_parent_count": getattr(lm, "active_parent_count", 0),
        "empty_candidate_count": getattr(lm, "empty_candidate_count", 0),
        "active_growth_rate": getattr(lm, "active_growth_rate", 0.0),
        "empty_descendants_skipped_estimate": getattr(lm, "empty_descendants_skipped_estimate", getattr(lm, "empty_parents_skipped", 0)),
        "cell_storage_mode": getattr(lm, "storage_mode", "summary_only"),
        "output_policy_note": getattr(lm, "output_policy_note", ""),
    }


def _step_status_map(sp_status: str) -> str:
    return {"RUNNING": "running", "SUCCESS": "done", "ERROR": "failed"}.get(sp_status, "running")


def _build_final_package(res) -> Optional[Dict[str, Any]]:
    """Build the frontend final_package contract from an ExecutionResult."""
    pid = getattr(res, "package_id", "") or ""
    if not pid:
        return None
    base = Path("outputs").resolve() / pid
    if not base.is_dir():
        return None
    try:
        from backend.package_index import scan_package_directory
        pkg_data = scan_package_directory(base, Path("outputs").resolve())
        return pkg_data
    except Exception:
        # Fallback
        figures_dir = base / "figures"
        has_figures = figures_dir.is_dir() and any(f.suffix.lower() == ".svg" for f in figures_dir.iterdir())
        return {
            "package_id": pid,
            "folder": pid,
            "motif": (res.motif_profile or {}).get("motif", "") if isinstance(getattr(res, "motif_profile", None), dict) else "",
            "generated_at": getattr(res, "generated_at", "") or "",
            "levels": getattr(res, "computed_levels_count", 0) or 0,
            "db": getattr(res, "fractal_dimension", None),
            "r2": getattr(res, "r_squared", None),
            "report_url": f"{pid}/report/report.html" if (base / "report" / "report.html").exists() else None,
            "report_pdf_url": f"{pid}/report/report.pdf" if (base / "report" / "report.pdf").exists() else None,
            "tables_url": f"{pid}/tables/tables.html" if (base / "tables" / "tables.html").exists() else None,
            "workbook_url": f"{pid}/excel/workbook.xlsx" if (base / "excel" / "workbook.xlsx").exists() else None,
            "manifest_url": f"{pid}/manifest/manifest.json" if (base / "manifest" / "manifest.json").exists() else None,
            "figures_url": f"{pid}/figures/" if has_figures else None,
            "rh_engine_cells_omitted_count": 0,
            "rh_engine_cells_omitted_levels": [],
            "rh_engine_row_run_count": 0,
            "rh_engine_row_run_levels": [],
            "rh_engine_uses_row_runs": False,
        }


def _latest_package_snapshot() -> Optional[Dict[str, Any]]:
    try:
        from backend.package_index import scan_all_packages
        pkgs = scan_all_packages(Path("outputs").resolve())
        if not pkgs:
            return None
        newest = pkgs[0]
        return {
            "package_id": newest.get("package_id"),
            "folder": newest.get("folder"),
            "motif": newest.get("motif"),
            "report_url": newest.get("report_url"),
            "report_pdf_url": newest.get("report_pdf_url"),
            "tables_url": newest.get("tables_url"),
            "workbook_url": newest.get("workbook_url"),
            "manifest_url": newest.get("manifest_url"),
        }
    except Exception:
        return None


def _parse_overwrite_flag(value) -> bool:
    """Coerce a frontend/CLI overwrite value (str/bool/int/None) to bool."""
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def _run_single_job(job_id: str, input_path: Path, levels: int, mode: str = "balanced", overwrite: bool = False):
    """Background single-analysis execution with live step + scale-row wiring."""

    def _on_step(sp: StepProgress):
        update_job_step(job_id, sp.name, _step_status_map(sp.status), extra_log=sp.message or None)

    def _on_level(lm):
        add_job_scale_row(job_id, _build_scale_row(lm))

    try:
        proc = AnalysisProcessor(input_path=input_path, levels=levels, mode=mode, overwrite=overwrite)
        res = proc.run(progress_callback=_on_step, level_callback=_on_level)
    except Exception as e:
        with JOBS_LOCK:
            job = JOBS_STORE.get(job_id)
            if job:
                job["status"] = "failed"
                job["current_step"] = "Failed"
                add_job_log(job_id, f"Analysis crashed: {e}", "error")
        return

    with JOBS_LOCK:
        job = JOBS_STORE.get(job_id)
        if job is None:
            return
        ok = res.status == "SUCCESS"
        job["status"] = "success" if ok else "failed"
        job["current_step"] = "Completed" if ok else "Failed"
        job["completed_files"] = 1
        job["current_level"] = res.computed_levels_count if ok else 0
        job["regression"] = {
            "status": res.status,
            "db": res.fractal_dimension if ok else None,
            "r2": res.r_squared if ok else None,
            "confidence_score": res.confidence_score if ok else None,
            "confidence_label": res.confidence_label if ok else None,
            "academic_comment": (res.motif_profile or {}).get("academic_comment", "") if ok else "",
        }
        if ok:
            job["final_package"] = _build_final_package(res)
            add_job_log(job_id, f"Analysis SUCCESS: Db={res.fractal_dimension:.4f}, R2={res.r_squared:.4f}", "success")
        else:
            add_job_log(job_id, "Analysis FAILED: " + "; ".join(res.errors or ["unknown error"]), "error")

    try:
        from backend.package_index import update_package_index
        update_package_index(Path("outputs").resolve())
    except Exception:
        pass


def _run_batch_job(job_id: str, folder_path: Path, levels: int, mode: str = "balanced", overwrite: bool = False):
    """Background batch-execution with live per-file and per-level wiring."""

    def _on_file(idx: int, total: int, fname: str, res: ExecutionResult):
        with JOBS_LOCK:
            job = JOBS_STORE.get(job_id)
            if job is None:
                return
            job["status"] = "running"
            job["completed_files"] = idx
            job["current_step"] = f"Processing {fname}"
            for q in job.get("batch_queue", []):
                if q.get("file") == fname:
                    q["status"] = "done" if res.status == "SUCCESS" else "failed"
                    q["current_level"] = res.computed_levels_count or 0
                    q["completed_levels"] = res.computed_levels_count or 0
                    q["db"] = round(res.fractal_dimension, 4) if res.status == "SUCCESS" else None
                    q["r2"] = round(res.r_squared, 4) if res.status == "SUCCESS" else None
                    q["runtime"] = round(res.duration_seconds, 2) if res.status == "SUCCESS" else None
                    q["error"] = "; ".join(res.errors or []) if res.status != "SUCCESS" else ""
            nxt = next((q["file"] for q in job.get("batch_queue", []) if q.get("status") == "queued"), None)
            job["current_file"] = nxt or fname
        if res.status == "SUCCESS":
            add_job_log(job_id, f"[{idx}/{total}] {fname} OK (Db={res.fractal_dimension:.4f})", "success")
        else:
            add_job_log(job_id, f"[{idx}/{total}] {fname} FAILED: {'; '.join(res.errors or [])}", "error")

    def _on_level(lm):
        with JOBS_LOCK:
            job = JOBS_STORE.get(job_id)
            if job is None:
                return
            cur = job.get("current_file", "")
            if job.get("_last_lvl_file") != cur:
                job["scale_rows"] = []
                job["_last_lvl_file"] = cur
            job["current_level"] = lm.level
            for q in job.get("batch_queue", []):
                if q.get("file") == cur:
                    q["current_level"] = lm.level
                    q["completed_levels"] = lm.level
        add_job_scale_row(job_id, _build_scale_row(lm))

    try:
        res = run_batch_analysis(
            folder_path=folder_path,
            levels=levels,
            mode=mode,
            progress_callback=_on_file,
            level_callback=_on_level,
            export_batch_summary=False,
            overwrite=overwrite,
        )
    except Exception as e:
        with JOBS_LOCK:
            job = JOBS_STORE.get(job_id)
            if job:
                job["status"] = "failed"
                add_job_log(job_id, f"Batch crashed: {e}", "error")
        return

    with JOBS_LOCK:
        job = JOBS_STORE.get(job_id)
        if job is None:
            return
        job["status"] = "success" if res.successful_count > 0 else "failed"
        job["current_step"] = "Batch completed"
        job["completed_files"] = res.successful_count
        # Populate regression summary from the last successful file result so the
        # Scientific Console regression panel is never left in a stale waiting state.
        last_ok = next((r for r in reversed(res.results) if r.get("status") == "SUCCESS"), None)
        if last_ok:
            job["regression"] = {
                "status": "SUCCESS",
                "db": last_ok.get("fractal_dimension"),
                "r2": last_ok.get("r_squared"),
                "confidence_score": last_ok.get("confidence_score"),
                "confidence_label": last_ok.get("confidence_label"),
                "academic_comment": (last_ok.get("motif_profile") or {}).get("academic_comment", ""),
            }
        job["final_package"] = _latest_package_snapshot()
        add_job_log(
            job_id,
            f"Batch completed: {res.successful_count}/{res.total_files} OK, {res.failed_count} failed",
            "success" if res.successful_count > 0 else "error",
        )

    try:
        from backend.package_index import update_package_index
        update_package_index(Path("outputs").resolve())
    except Exception:
        pass


class SecuredRequestHandler(SimpleHTTPRequestHandler):
    """Secured HTTP request handler with path traversal checks and REST API."""

    def __init__(self, *args, directory=None, **kwargs):
        if directory is None:
            directory = str(Path("outputs").resolve())
        super().__init__(*args, directory=directory, **kwargs)

    def guess_type(self, path):
        """Override MIME type detection to serve SVG files cleanly as image/svg+xml."""
        if str(path).lower().endswith(".svg"):
            return "image/svg+xml"
        return super().guess_type(path)

    def _send_json(self, data: Dict[str, Any], status_code: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _handle_open_folder(self, package_id: str):
        """GET /api/open-folder/<id> - resolve a known package folder, open it
        directly in the OS file explorer (os.startfile / xdg-open) and return
        the package + file listing (kept for backward compatibility).

        Security: only known packages inside outputs/ are ever opened; unknown
        ids and traversal attempts return 404 before any OS call.
        """
        if not package_id or package_id in ("", ".", ".."):
            self._send_json({"error": "Invalid package identifier"}, 404)
            return
        out_root = Path("outputs").resolve()
        try:
            pkgs = scan_all_packages(out_root)
        except Exception:
            pkgs = []
        target = next(
            (p for p in pkgs if p.get("folder") == package_id or p.get("package_id") == package_id),
            None,
        )
        if not target:
            self._send_json({"error": "Package not found"}, 404)
            return
        folder_name = target.get("folder") or package_id
        folder_p = (out_root / folder_name).resolve()
        if not self._is_safe_path(folder_p) or not folder_p.is_dir():
            self._send_json({"error": "Package folder not found"}, 404)
            return
        files = []
        try:
            for f in sorted(folder_p.rglob("*")):
                if f.is_file():
                    rel = f.relative_to(folder_p)
                    url = f"{folder_name}/{rel.as_posix()}"
                    files.append({
                        "name": rel.name,
                        "path": rel.as_posix(),
                        "url": url,
                        "size": f.stat().st_size,
                        "kind": (rel.suffix.lstrip(".").lower() or "file"),
                    })
        except Exception:
            files = []
        opened = _open_in_os_explorer(folder_p)
        self._send_json({
            "ok": opened,
            "opened_in_os": opened,
            "folder": folder_name,
            "package_id": target.get("package_id", folder_name),
            "message": "Opened in the system file explorer" if opened else "Folder resolved, but the file explorer could not be opened",
            "file_count": len(files),
            "files": files,
        })

    def _is_safe_path(self, target_path: Path) -> bool:
        """Enforces security boundaries to prevent path traversal outside frontend or outputs workspaces."""
        try:
            resolved = target_path.resolve()
            out_resolved = Path("outputs").resolve()
            front_resolved = Path("frontend").resolve()
            return (
                resolved == out_resolved or out_resolved in resolved.parents or resolved.is_relative_to(out_resolved) or
                resolved == front_resolved or front_resolved in resolved.parents or resolved.is_relative_to(front_resolved)
            )
        except Exception:
            return False

    def _serve_file(self, file_path: Path):
        try:
            content = file_path.read_bytes()
            self.send_response(200)
            mime_type = self.guess_type(str(file_path)) or "application/octet-stream"
            self.send_header("Content-Type", f"{mime_type}; charset=utf-8" if mime_type.startswith("text/") or mime_type in ("application/javascript", "application/json") else mime_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Access-Control-Allow-Origin", "*")
            # Live-shell architecture: never let browsers cache stale JS/HTML between runs
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self._send_json({"error": f"Error reading file: {e}"}, 500)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        if not path:
            path = "/"

        # GET /api/jobs/<job_id> or /api/status/<job_id>
        if path.startswith(("/api/jobs/", "/api/status/")):
            parts = path.strip("/").split("/")
            job_id = parts[-1]
            with JOBS_LOCK:
                job = JOBS_STORE.get(job_id)
                if job:
                    snapshot = dict(job)
                    snapshot["elapsed_seconds"] = round(time.time() - snapshot["start_time"], 1)
                    self._send_json(snapshot)
                    return
            self._send_json({"error": "job_not_found", "message": "Job not found or expired."}, 404)
            return

        # 1. GET /api/health
        if path == "/api/health":
            self._send_json({"status": "OK", "version": APP_VERSION, "time": time.strftime("%Y-%m-%d %H:%M:%S")})
            return

        # 1b. GET /api/jobs
        if path == "/api/jobs":
            with JOBS_LOCK:
                _load_jobs()
                jobs = []
                for job_id, job in JOBS_STORE.items():
                    started = job.get("start_time")
                    jobs.append({
                        "job_id": job_id,
                        "mode": job.get("mode"),
                        "status": job.get("status"),
                        "current_file": job.get("current_file"),
                        "total_files": job.get("total_files"),
                        "completed_files": job.get("completed_files"),
                        "requested_levels": job.get("requested_levels"),
                        "current_level": job.get("current_level"),
                        "elapsed_seconds": round(time.time() - (started or time.time()), 1),
                        "start_time": started,
                        "started_at": datetime.fromtimestamp(started).strftime("%Y-%m-%d %H:%M:%S") if started else "",
                        "final_package": job.get("final_package"),
                        "log_count": len(job.get("logs", [])),
                    })
            jobs.sort(key=lambda j: j.get("start_time") or 0, reverse=True)
            self._send_json({"jobs": jobs})
            return

        # 2. GET /api/packages
        if path == "/api/packages":
            out_root = Path("outputs").resolve()
            pkgs = scan_all_packages(out_root)
            self._send_json({"packages": pkgs})
            return

        # 4. GET /api/package/<package_id>/tables or /api/package/<package_id>/tables/<level>
        if path.startswith("/api/package/") and "/tables" in path:
            parts = path.strip("/").split("/")
            if len(parts) >= 4:
                package_id = parts[2]
                out_root = Path("outputs").resolve()
                pkgs = scan_all_packages(out_root)
                target_pkg = next((p for p in pkgs if p["package_id"] == package_id or p.get("folder") == package_id), None)
                
                if not target_pkg:
                    self._send_json({"error": f"Package ID not found: {package_id}"}, 404)
                    return

                json_file = (out_root / target_pkg["folder"] / "tables" / "tables_data.json").resolve()
                if not json_file.exists():
                    self._send_json({"error": "tables_data.json not found for package"}, 404)
                    return

                try:
                    data = json.loads(json_file.read_text(encoding="utf-8", errors="replace"))
                    if len(parts) >= 5:
                        lvl_raw = parts[4].upper()
                        lvl_key = f"L{int(re.sub(r'[^0-9]', '', lvl_raw)):02d}" if re.sub(r'[^0-9]', '', lvl_raw) else lvl_raw
                        levels_dict = data.get("levels", {})
                        if lvl_key in levels_dict:
                            self._send_json({"package_id": package_id, "level": lvl_key, "data": levels_dict[lvl_key]})
                        else:
                            self._send_json({"error": f"Level {lvl_key} not found"}, 404)
                    else:
                        data["package_id"] = package_id
                        self._send_json(data)
                except Exception as e:
                    self._send_json({"error": f"Failed reading tables data: {e}"}, 500)
                return

        # 5. GET /api/package/<package_id>
        if path.startswith("/api/package/"):
            package_id = path.split("/api/package/")[-1]
            out_root = Path("outputs").resolve()
            pkgs = scan_all_packages(out_root)
            # Accept either the unique package_id or the folder name, because the
            # Analysis Studio's Recently Analyzed Files passes the folder (e.g.
            # "16D" or "16D_20260801_181020") while dashboard cards pass the id.
            target_pkg = next(
                (p for p in pkgs if p.get("package_id") == package_id or p.get("folder") == package_id),
                None,
            )
            if target_pkg:
                self._send_json(target_pkg)
            else:
                self._send_json({"error": f"Package not found: {package_id}"}, 404)
            return

        # 6. GET /api/figures
        if path == "/api/figures":
            out_root = Path("outputs").resolve()
            figs = get_all_figures(out_root)
            self._send_json({"figures": figs})
            return

        # 7. GET /api/stats
        if path == "/api/stats":
            out_root = Path("outputs").resolve()
            pkgs = scan_all_packages(out_root)
            self._send_json(build_stats(pkgs))
            return

        # 8. GET /api/history
        if path == "/api/history":
            out_root = Path("outputs").resolve()
            pkgs = scan_all_packages(out_root)
            self._send_json({"history": build_history(pkgs)})
            return

        # 8b. GET /api/open-folder/<id>  (folder file listing for on-screen browser)
        if path.startswith("/api/open-folder/"):
            package_id = path.split("/api/open-folder/")[-1]
            self._handle_open_folder(package_id)
            return

        # Any other /api/* path with no registered handler must return JSON 404
        # (never leak the HTML static-file 404 page into the API contract).
        if path.startswith("/api/"):
            self._send_json({"error": "Unknown API endpoint"}, 404)
            return

        # Serve static UI files (frontend/) or data package outputs (outputs/)
        rel_path = path.lstrip("/")
        front_resolved = Path("frontend").resolve()
        out_resolved = Path("outputs").resolve()

        if path in ("/", "/index.html"):
            target = front_resolved / "index.html"
        elif path.startswith(("/css/", "/js/", "/vendor/", "/static/")):
            clean_rel = rel_path
            if clean_rel.startswith("static/"):
                clean_rel = clean_rel[7:]
            target = front_resolved / clean_rel
        else:
            target = out_resolved / rel_path

        if not target.exists() and (front_resolved / rel_path).exists():
            target = front_resolved / rel_path

        if not self._is_safe_path(target):
            self.send_error(403, "Access Denied: Path Traversal Blocked")
            return

        if not target.exists():
            self.send_error(404, "File Not Found")
            return

        self._serve_file(target)

    def do_DELETE(self):
        """Handle DELETE /api/package/<package_id> requests safely."""
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path.startswith("/api/package/"):
            package_id = path.split("/api/package/")[-1]
            self._handle_delete_package(package_id)
            return

        self._send_json({"error": "Unknown DELETE endpoint"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        # Security Check Content Length
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > MAX_UPLOAD_SIZE:
            self._send_json({"error": "File size exceeds 50MB limit"}, 413)
            return

        body_bytes = self.rfile.read(content_length)

        if path == "/api/analyze":
            try:
                data = json.loads(body_bytes.decode("utf-8"))
            except Exception:
                self._send_json({"error": "Invalid JSON body"}, 400)
                return

            input_path_str = data.get("input_path", "").strip()
            levels = data.get("levels")
            if levels is None:
                legacy_mode = data.get("mode", "balanced")
                from backend.processor import MODE_LEVEL_MAP
                levels = MODE_LEVEL_MAP.get(legacy_mode.lower(), 7)
            try:
                levels = max(1, min(int(levels), 50))
            except Exception:
                levels = 7

            input_p = Path(input_path_str)
            if not input_p.exists():
                self._send_json({"error": f"Invalid or inaccessible input file: {input_path_str}"}, 400)
                return

            overwrite = _parse_overwrite_flag(data.get("overwrite", False))
            job_id = create_job(mode="single", total_files=1, current_file=input_p.name, levels=levels)
            threading.Thread(target=_run_single_job, args=(job_id, input_p, levels, "balanced", overwrite), daemon=True).start()

            self._send_json({"status": "queued", "job_id": job_id, "message": "Single analysis started"})
            return

        if path == "/api/upload-single":
            content_type = self.headers.get("Content-Type", "")
            parsed = _parse_multipart(content_type, body_bytes)
            if not parsed:
                self._send_json({"error": "Invalid multipart/form-data body"}, 400)
                return
            svg_files = parsed["files"].get("file") or []
            if not svg_files:
                self._send_json({"error": "Missing 'file' field (SVG file)"}, 400)
                return

            filename, content = svg_files[0]
            filename = Path(filename).name
            if not filename.lower().endswith(".svg"):
                self._send_json({"error": "Invalid file extension: only .svg is accepted"}, 400)
                return
            if not is_valid_svg(content):
                self._send_json({"error": "Invalid SVG content"}, 400)
                return

            levels = 7
            try:
                levels = max(1, min(int(parsed["fields"].get("levels", "7")), 50))
            except Exception:
                pass
            mode = parsed["fields"].get("mode", "balanced") or "balanced"
            overwrite = _parse_overwrite_flag(parsed["fields"].get("overwrite", False))

            uploads_dir = Path("uploads").resolve()
            uploads_dir.mkdir(parents=True, exist_ok=True)

            job_id = create_job(mode="single", total_files=1, current_file=filename, levels=levels)
            # Per-job upload subfolder (same pattern as batch uploads) keeps the
            # motif stem clean (e.g. "16D"), so re-running the same file with
            # overwrite=false correctly triggers versioned-folder protection.
            safe_name = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)
            upload_sub = uploads_dir / job_id
            upload_sub.mkdir(parents=True, exist_ok=True)
            save_path = upload_sub / safe_name
            save_path.write_bytes(content)

            threading.Thread(target=_run_single_job, args=(job_id, save_path, levels, mode, overwrite), daemon=True).start()
            self._send_json({"status": "queued", "job_id": job_id, "message": "Single analysis started"})
            return

        if path == "/api/batch":
            try:
                data = json.loads(body_bytes.decode("utf-8"))
            except Exception:
                self._send_json({"error": "Invalid JSON body"}, 400)
                return

            folder_str = data.get("folder_path", "").strip()
            levels = data.get("levels")
            if levels is None:
                legacy_mode = data.get("mode", "balanced")
                from backend.processor import MODE_LEVEL_MAP
                levels = MODE_LEVEL_MAP.get(legacy_mode.lower(), 7)
            try:
                levels = max(1, min(int(levels), 50))
            except Exception:
                levels = 7

            folder_p = Path(folder_str)
            if not folder_p.exists():
                self._send_json({"error": f"Invalid or inaccessible folder: {folder_str}"}, 400)
                return

            svg_files = sorted([f for f in folder_p.rglob("*.svg") if f.is_file()])
            overwrite = _parse_overwrite_flag(data.get("overwrite", False))
            job_id = create_job(mode="batch", total_files=len(svg_files), current_file="", levels=levels)
            with JOBS_LOCK:
                JOBS_STORE[job_id]["batch_queue"] = [
                    {"file": str(f.relative_to(folder_p)), "status": "queued", "current_level": 0,
                     "completed_levels": 0, "db": None, "r2": None, "runtime": None, "error": ""}
                    for f in svg_files
                ]

            threading.Thread(target=_run_batch_job, args=(job_id, folder_p, levels, "balanced", overwrite), daemon=True).start()
            self._send_json({"status": "queued", "job_id": job_id, "file_count": len(svg_files), "message": "Batch analysis started"})
            return

        if path in ["/api/delete", "/api/packages/delete"]:
            try:
                data = json.loads(body_bytes.decode("utf-8"))
                ids = data.get("package_ids")
                if isinstance(ids, list) and ids:
                    self._handle_delete_many([str(i).strip() for i in ids])
                else:
                    folder_name = data.get("folder") or data.get("package_id") or ""
                    self._handle_delete_package(str(folder_name).strip())
            except Exception as e:
                self._send_json({"error": f"Delete failed: {e}"}, 500)
            return

        if path == "/api/upload-batch":
            content_type = self.headers.get("Content-Type", "")
            parsed = _parse_multipart(content_type, body_bytes)
            if not parsed:
                self._send_json({"error": "Invalid multipart/form-data body"}, 400)
                return

            uploaded = parsed["files"].get("files[]") or []
            valid_files = []
            failed_files = []
            for fname, content in uploaded:
                fname = Path(fname).name
                if fname.lower().endswith(".svg") and is_valid_svg(content):
                    valid_files.append((fname, content))
                else:
                    failed_files.append(fname)

            if not valid_files:
                self._send_json({"error": "No valid SVG files received (files[] must contain .svg files)"}, 400)
                return

            levels = 7
            try:
                levels = max(1, min(int(parsed["fields"].get("levels", "7")), 50))
            except Exception:
                pass
            mode = parsed["fields"].get("mode", "balanced") or "balanced"
            overwrite = _parse_overwrite_flag(parsed["fields"].get("overwrite", False))

            job_id = create_job(mode="batch", total_files=len(valid_files), current_file=valid_files[0][0], levels=levels)
            batch_dir = (Path("uploads") / f"batch_{job_id}").resolve()
            uploads_root = Path("uploads").resolve()
            if not batch_dir.is_relative_to(uploads_root):
                self._send_json({"error": "Unsafe path traversal"}, 403)
                return
            batch_dir.mkdir(parents=True, exist_ok=True)

            queued_entries = []
            for fname, content in valid_files:
                safe_name = re.sub(r"[^a-zA-Z0-9._-]", "_", fname)
                (batch_dir / safe_name).write_bytes(content)
                queued_entries.append({
                    "file": safe_name, "status": "queued", "current_level": 0,
                    "completed_levels": 0, "db": None, "r2": None, "runtime": None, "error": ""
                })
            failed_entries = [
                {"file": fname, "status": "failed", "current_level": 0,
                 "completed_levels": 0, "db": None, "r2": None, "runtime": None,
                 "error": "Invalid SVG content or extension rejected"}
                for fname in failed_files
            ]
            with JOBS_LOCK:
                JOBS_STORE[job_id]["batch_queue"] = queued_entries + failed_entries

            threading.Thread(target=_run_batch_job, args=(job_id, batch_dir, levels, mode, overwrite), daemon=True).start()
            self._send_json({"status": "queued", "job_id": job_id, "file_count": len(valid_files), "message": "Batch analysis started"})
            return

        self._send_json({"error": "Unknown API endpoint"}, 404)

    def _resolve_package_folder(self, target_identifier: str, out_root: Path):
        """Resolve a package_id or folder name to a validated path inside outputs/."""
        pkgs = scan_all_packages(out_root)
        target_pkg = next(
            (p for p in pkgs if p["package_id"] == target_identifier or p["folder"] == target_identifier),
            None,
        )
        folder_sub = target_pkg["folder"] if target_pkg else target_identifier
        target_p = (out_root / folder_sub).resolve()

        # Strict security path validation: target MUST be inside outputs/ directory
        try:
            if not target_p.is_relative_to(out_root) or target_p == out_root:
                return None, "Invalid or unsafe folder path: outside outputs directory"
        except AttributeError:
            if out_root not in target_p.parents or target_p == out_root:
                return None, "Invalid or unsafe folder path"

        if target_p.name in ("index.html", "package_index.json"):
            return None, "Protected file: cannot delete dashboard index files"
        if not target_p.exists():
            return None, f"Package folder not found: {folder_sub}"
        if not target_p.is_dir():
            return None, "Target is not a directory package"
        return target_p, None

    def _handle_delete_many(self, target_ids: List[str]):
        """Delete multiple verified analysis packages from outputs/."""
        out_root = Path("outputs").resolve()
        deleted = []
        not_found = []
        errors = []

        for tid in target_ids:
            if not tid:
                continue
            target_p, err = self._resolve_package_folder(tid, out_root)
            if err:
                not_found.append({"id": tid, "error": err})
                continue
            try:
                if target_p.is_dir():
                    shutil.rmtree(target_p)
                    deleted.append(tid)
                else:
                    errors.append({"id": tid, "error": "Not a directory"})
            except Exception as e:
                errors.append({"id": tid, "error": str(e)})

        try:
            from backend.package_index import update_package_index
            update_package_index(out_root)
        except Exception:
            pass

        self._send_json({
            "status": "SUCCESS" if not errors else "PARTIAL",
            "deleted": deleted,
            "not_found": not_found,
            "errors": errors,
        })

    def _handle_delete_package(self, target_identifier: str):
        """Safely resolve target package folder within outputs/ and delete it."""
        if not target_identifier:
            self._send_json({"error": "No package specified"}, 400)
            return

        out_root = Path("outputs").resolve()
        target_p, err = self._resolve_package_folder(target_identifier, out_root)
        if err:
            self._send_json({"error": err}, 403)
            return

        try:
            if target_p.is_dir():
                shutil.rmtree(target_p)
            else:
                self._send_json({"error": "Target is not a directory"}, 400)
                return

            try:
                from backend.package_index import update_package_index
                update_package_index(out_root)
            except Exception:
                pass

            self._send_json({"status": "SUCCESS", "message": f"Deleted package {target_identifier}"})
        except Exception as e:
            self._send_json({"error": f"Delete operation failed: {e}"}, 500)


def start_server(port: int = 8000, open_browser: bool = True):
    """Starts the secured Python HTTP Web Server with fallback port and threaded browser launch."""
    try:
        sweep_stale_uploads(max_age_minutes=24 * 60)
    except Exception:
        pass
    try:
        _load_jobs()
    except Exception:
        pass
    out_dir = Path("outputs").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    front_dir = Path("frontend").resolve()
    front_dir.mkdir(parents=True, exist_ok=True)

    try:
        from backend.package_index import update_package_index
        update_package_index(out_dir)
    except Exception:
        pass

    httpd = None
    for p in [port, 8001, 8080, 8888]:
        try:
            httpd = HTTPServer(("", p), SecuredRequestHandler)
            port = p
            break
        except OSError:
            continue

    if not httpd:
        print("[ERROR] Ports are busy, the server could not be started.")
        return

    url = f"http://localhost:{port}"
    print("============================================================")
    print("RASH-HIT FRACTAL STUDIO WEB DASHBOARD SERVER RUNNING")
    print(f"URL: {url}")
    print(f"Root: {out_dir}")
    print("============================================================")

    if open_browser:
        def _open():
            time.sleep(0.6)
            webbrowser.open(url)

        threading.Thread(target=_open, daemon=True).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down server...")
        httpd.server_close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="RASH-HIT Fractal Studio Web Dashboard Server")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument("--no-browser", action="store_true", help="Do not auto-open the browser")
    args = parser.parse_args()
    start_server(port=args.port, open_browser=not args.no_browser)
