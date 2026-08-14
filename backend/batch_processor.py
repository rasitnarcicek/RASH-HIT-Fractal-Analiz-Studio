# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""
batch_processor.py - Batch Folder Processing Engine for RASH-HIT Fractal Studio.
Scans folders for SVG files, runs AnalysisProcessor for each, and returns results
without halting on broken files. By default no batch_summary.csv / batch_summary.json /
batch_report.html files are produced - individual SVG packages are the only output,
and they are discovered by package_index.py as normal analysis packages.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from backend.processor import AnalysisProcessor, ExecutionResult


@dataclass
class BatchExecutionResult:
    batch_id: str
    folder_path: str
    total_files: int
    successful_count: int
    failed_count: int
    min_db_file: str = ""
    min_db_val: float = 999.0
    max_db_file: str = ""
    max_db_val: float = 0.0
    results: List[Dict[str, Any]] = field(default_factory=list)
    output_dir: str = ""
    started_at: str = ""
    finished_at: str = ""
    duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "folder_path": self.folder_path,
            "total_files": self.total_files,
            "successful_count": self.successful_count,
            "failed_count": self.failed_count,
            "min_db_file": self.min_db_file,
            "min_db_val": round(self.min_db_val, 4) if self.min_db_val < 900 else 0.0,
            "max_db_file": self.max_db_file,
            "max_db_val": round(self.max_db_val, 4),
            "results": self.results,
            "output_dir": self.output_dir,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_seconds": round(self.duration_seconds, 3),
        }


def run_batch_analysis(
    folder_path: str | Path,
    output_dir: Optional[str | Path] = None,
    mode: str = "balanced",
    levels: Optional[int] = None,
    progress_callback: Optional[Callable[[int, int, str, ExecutionResult], None]] = None,
    level_callback=None,
    export_batch_summary: bool = False,
    overwrite: bool = False,
    profile: Optional[str] = None,
    batch_profile: Optional[str] = None,
) -> BatchExecutionResult:
    """Scans a directory for SVG files and executes batch fractal analysis."""
    start_time_all = time.time()
    start_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    folder_p = Path(folder_path).resolve()
    batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    if output_dir:
        out_root = Path(output_dir).resolve() / batch_id
    else:
        out_root = Path("outputs").resolve() / batch_id

    out_root.mkdir(parents=True, exist_ok=True)
    indiv_out_dir = out_root / "individual_results"
    indiv_out_dir.mkdir(parents=True, exist_ok=True)

    svg_files = sorted(folder_p.rglob("*.svg")) if folder_p.is_dir() else []
    total_files = len(svg_files)

    batch_res = BatchExecutionResult(
        batch_id=batch_id,
        folder_path=str(folder_p),
        total_files=total_files,
        successful_count=0,
        failed_count=0,
        output_dir=str(out_root),
        started_at=start_iso,
    )

    if total_files == 0:
        batch_res.finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        batch_res.duration_seconds = time.time() - start_time_all
        return batch_res

    results_list: List[Dict[str, Any]] = []

    for idx, svg_p in enumerate(svg_files, 1):
        proc = AnalysisProcessor(
            input_path=svg_p,
            output_dir=indiv_out_dir,
            mode=mode,
            levels=levels,
            overwrite=overwrite,
            profile=batch_profile or profile or "lean",
        )
        res = proc.run(level_callback=level_callback)

        if res.status == "SUCCESS":
            batch_res.successful_count += 1
            db_val = res.fractal_dimension
            if db_val < batch_res.min_db_val:
                batch_res.min_db_val = db_val
                batch_res.min_db_file = str(svg_p.relative_to(folder_p))
            if db_val > batch_res.max_db_val:
                batch_res.max_db_val = db_val
                batch_res.max_db_file = str(svg_p.relative_to(folder_p))
        else:
            batch_res.failed_count += 1

        res_dict = res.to_dict()
        res_dict["file_name"] = str(svg_p.relative_to(folder_p))
        results_list.append(res_dict)

        if progress_callback:
            try:
                progress_callback(idx, total_files, str(svg_p.relative_to(folder_p)), res)
            except Exception:
                pass

    batch_res.results = results_list
    batch_res.finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    batch_res.duration_seconds = time.time() - start_time_all

    # 1. Write batch_summary.json (opt-in only; default dashboard keeps clean library)
    if export_batch_summary:
        (out_root / "batch_summary.json").write_text(json.dumps(batch_res.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

        # 2. Write batch_summary.csv
        csv_lines = ["file_name,motif,db,r2,confidence_score,confidence_label,shape_count,computed_levels,duration_seconds,status,error_message"]
        for r in results_list:
            fname = r.get("file_name", "")
            motif = r.get("motif_profile", {}).get("motif", "")
            db = r.get("fractal_dimension", 0.0)
            r2 = r.get("r_squared", 0.0)
            conf_score = r.get("confidence_score", 0.0)
            conf_lbl = r.get("confidence_label", "")
            shapes = r.get("svg_health", {}).get("total_shape_elements", 0)
            lvls = r.get("computed_levels_count", 0)
            dur = r.get("duration_seconds", 0.0)
            st = r.get("status", "")
            errs = "; ".join(r.get("errors", []))
            csv_lines.append(f'"{fname}","{motif}",{db:.4f},{r2:.4f},{conf_score:.1f},"{conf_lbl}",{shapes},{lvls},{dur:.3f},"{st}","{errs}"')

        (out_root / "batch_summary.csv").write_text("\n".join(csv_lines), encoding="utf-8-sig")

        # 3. Write batch_report.html (opt-in only)
        _generate_batch_report_html(batch_res, out_root / "batch_report.html")

    return batch_res


def _generate_batch_report_html(batch_res: BatchExecutionResult, out_path: Path):
    """Renders a standalone comparative HTML batch analysis report."""
    rows_html = []
    for r in batch_res.results:
        fname = r.get("file_name", "")
        db = r.get("fractal_dimension", 0.0)
        r2 = r.get("r_squared", 0.0)
        conf_lbl = r.get("confidence_label", "")
        shapes = r.get("svg_health", {}).get("total_shape_elements", 0)
        st = r.get("status", "")
        dur = r.get("duration_seconds", 0.0)

        is_min = (fname == batch_res.min_db_file and batch_res.successful_count > 1)
        is_max = (fname == batch_res.max_db_file and batch_res.successful_count > 1)

        badge_cls = "badge-pass" if st == "SUCCESS" else "badge-err"
        highlight_str = ""
        if is_max:
            highlight_str = ' <span style="background:#DBEAFE;color:#1E4ED8;font-size:10px;padding:2px 6px;border-radius:4px;font-weight:bold;">MAX Db</span>'
        elif is_min:
            highlight_str = ' <span style="background:#FEF3C7;color:#B45309;font-size:10px;padding:2px 6px;border-radius:4px;font-weight:bold;">MIN Db</span>'

        rows_html.append(
            f'<tr><td><strong>{fname}</strong>{highlight_str}</td>'
            f'<td style="font-weight:bold;color:#2454A6;">{db:.4f}</td>'
            f'<td style="color:#166534;">{r2:.4f}</td>'
            f'<td>{conf_lbl}</td>'
            f'<td>{shapes:,}</td>'
            f'<td>{dur:.2f} s</td>'
            f'<td><span class="{badge_cls}">{st}</span></td></tr>'
        )

    rows_str = "\n".join(rows_html)
    html = f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RASH-HIT Fractal Studio - Batch Analysis Report ({batch_res.batch_id})</title>
  <style>
    :root {{ --bg:#F5F7FB; --panel:#FFFFFF; --text:#0F172A; --muted:#64748B; --border:#D8DEE9; --accent:#2454A6; --pass:#177245; --passbg:#E9F8EF; --hdr:#10203D; }}
    [data-theme="dark"] {{ --bg:#0F172A; --panel:#1E293B; --text:#F1F5F9; --muted:#94A3B8; --border:#334155; --accent:#60A5FA; --pass:#86EFAC; --passbg:#14532D; --hdr:#0B1220; }}
    body {{ font-family: Inter, sans-serif; background: var(--bg); color: var(--text); padding: 28px; line-height: 1.6; margin: 0; }}
    .container {{ max-width: 1100px; margin: 0 auto; }}
    .header {{ background: linear-gradient(135deg, #10203D, #2454A6); color: #fff; padding: 28px; border-radius: 16px; margin-bottom: 24px; }}
    .header h1 {{ margin: 0 0 6px; font-size: 24px; }}
    .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 24px; }}
    .kpi-card {{ background: var(--panel); border: 1px solid var(--border); padding: 16px; border-radius: 12px; text-align: center; }}
    .kpi-val {{ font-size: 22px; font-weight: bold; color: var(--accent); }}
    table {{ width: 100%; border-collapse: separate; border-spacing: 0; border: 1px solid var(--border); border-radius: 12px; overflow: hidden; background: var(--panel); }}
    th {{ background: var(--hdr); color: #fff; padding: 11px 14px; text-align: left; font-size: 11px; text-transform: uppercase; }}
    td {{ padding: 10px 14px; border-bottom: 1px solid var(--border); font-family: Consolas, monospace; font-size: 12px; }}
    .badge-pass {{ background: #DCFCE7; color: #166534; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px; }}
    .badge-err {{ background: #FEE2E2; color: #991B1B; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px; }}
  </style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>Batch Comparative Analysis Report</h1>
    <div style="font-size:13px;color:#DDE8F8;">Batch ID: {batch_res.batch_id} &nbsp;|&nbsp; Folder: {batch_res.folder_path}</div>
  </div>

  <div class="kpi-grid">
    <div class="kpi-card"><div>Total Files</div><div class="kpi-val">{batch_res.total_files}</div></div>
    <div class="kpi-card"><div>Successful</div><div class="kpi-val" style="color:#166534;">{batch_res.successful_count}</div></div>
    <div class="kpi-card"><div>Failed</div><div class="kpi-val" style="color:#DC2626;">{batch_res.failed_count}</div></div>
    <div class="kpi-card"><div>Min Db</div><div class="kpi-val">{batch_res.min_db_val:.4f}</div><div style="font-size:10px;color:var(--muted);">{batch_res.min_db_file}</div></div>
    <div class="kpi-card"><div>Max Db</div><div class="kpi-val">{batch_res.max_db_val:.4f}</div><div style="font-size:10px;color:var(--muted);">{batch_res.max_db_file}</div></div>
  </div>

  <h2>Comparative Results Matrix</h2>
  <table>
    <thead><tr><th>File Name</th><th>Fractal Db</th><th>R² Fit</th><th>Confidence</th><th>Shapes</th><th>Time</th><th>Status</th></tr></thead>
    <tbody>
      {rows_str}
    </tbody>
  </table>
</div>
</body>
</html>"""

    out_path.write_text(html, encoding="utf-8")
