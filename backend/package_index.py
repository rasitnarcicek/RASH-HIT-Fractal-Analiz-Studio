"""RASH-HIT Fractal Studio - Package Index & Metadata Scanner Module.

Single source of truth for discovering, validating, auditing, and indexing
analysis output packages in outputs/ directory.

All asset URLs are generated here as *relative* paths (no leading slash and
no ``/outputs/`` prefix). This works in server mode (web server document
root = outputs/) and when the dashboard is served from frontend/.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any


def build_package_id(folder_rel: str, motif: str, gen_at: str) -> str:
    """Generate a clean, unique package_id from motif, timestamp, or relative path."""
    clean_motif = re.sub(r'[\/\\:*?"<>|\x00-\x1f]', '_', motif or 'pkg').strip('. ')
    if not clean_motif:
        clean_motif = 'pkg'
    clean_date = re.sub(r'[^0-9]', '', gen_at or '')
    if len(clean_date) >= 14:
        date_stamp = clean_date[:14]
    else:
        date_stamp = clean_motif

    # Include parent batch folder name if nested to guarantee uniqueness
    parts = folder_rel.replace('\\', '/').strip('/').split('/')
    if len(parts) > 1 and parts[0].startswith('batch_'):
        b_stamp = parts[0].replace('batch_', '')
        return f"{clean_motif}_{b_stamp}"

    return f"{clean_motif}_{date_stamp}" if date_stamp != clean_motif else clean_motif


def _read_result_json(pkg_dir: Path) -> tuple:
    """Read result.json and return (data, errors)."""
    errors: List[str] = []
    res_data: Dict[str, Any] = {}
    res_json_path = pkg_dir / "result.json"
    if not res_json_path.exists():
        errors.append("Missing result.json file")
    else:
        try:
            res_data = json.loads(res_json_path.read_text(encoding="utf-8", errors="replace"))
        except Exception as e:
            errors.append(f"Invalid result.json: {e}")
    return res_data, errors

def _count_files(dir_p: Path, ext: str) -> int:
    """Count files with a given suffix inside a directory (non-recursive)."""
    if not dir_p.is_dir():
        return 0
    return sum(1 for f in dir_p.iterdir() if f.is_file() and f.suffix.lower() == ext)


def _parse_figure_name(stem: str):
    """Parse '01_4x8_map' / '01_4x8_cells' -> ('L01', '4x8')."""
    m = re.match(r"^(\d{2})_(\d+x\d+)(?:_.*)?$", stem)
    if m:
        return f"L{m.group(1)}", m.group(2)
    m2 = re.match(r"^(\d{2})_(\d+)x(\d+)$", stem)
    if m2:
        return f"L{m2.group(1)}", f"{m2.group(2)}x{m2.group(3)}"
    return stem, ""


_RH_ENGINE_RLE_MARKER = "run-length / row-run merged"
# The exporter writes the RLE marker just above the filled rects, so reading
# only the head chunk of each SVG is enough (keeps library scans cheap).
_RH_ENGINE_SVG_HEAD_BYTES = 8192


def _collect_rh_engine_metadata(pkg_dir: Path, tables_data: Path, figures_dir: Path):
    """RASH-HIT Fractal Engine high-level output policy markers for dashboard cards.

    Returns ``(cells_omitted_levels, row_run_levels)`` (sorted lists of level
    ints, both may be empty):

    - ``cells_omitted_levels``: levels whose per-cell payloads were omitted,
      read from the authoritative ``tables/tables_data.json`` flag
      (``levels.Lxx.cells_omitted == true``).
    - ``row_run_levels``: levels whose SVG map uses run-length / row-run
      merged filled rects (detected via the RASH-HIT Fractal Engine marker comment the
      exporter writes into the figure).

    Both scans are defensive: any unreadable/malformed artifact is skipped.
    """
    cells_omitted: List[int] = []
    if tables_data.is_file():
        try:
            data = json.loads(tables_data.read_text(encoding="utf-8", errors="replace"))
            for key, lvl in (data.get("levels") or {}).items():
                if isinstance(lvl, dict) and lvl.get("cells_omitted"):
                    m = re.match(r"^L(\d+)$", str(key))
                    if m:
                        cells_omitted.append(int(m.group(1)))
        except Exception:
            pass

    row_run_levels: List[int] = []
    if figures_dir.is_dir():
        for f in sorted(figures_dir.iterdir()):
            if not f.is_file() or f.suffix.lower() != ".svg":
                continue
            try:
                # The exporter writes the marker just above the filled rects,
                # so reading the head chunk is enough for even huge L9 maps.
                with open(f, "r", encoding="utf-8", errors="replace") as fh:
                    head = fh.read(_RH_ENGINE_SVG_HEAD_BYTES)
                if _RH_ENGINE_RLE_MARKER in head:
                    lvl, _grid = _parse_figure_name(f.stem)
                    m = re.match(r"^L(\d+)$", lvl)
                    if m:
                        row_run_levels.append(int(m.group(1)))
            except Exception:
                continue
    return sorted(cells_omitted), sorted(row_run_levels)


def _compute_input_sha256(res_data: Dict[str, Any], output_root: Path) -> str:
    """ISSUE-013: populate input_sha256 from the source SVG when it exists.

    Uses the raw source path from result.json (input_file/source_file) - falls
    back to the project root or the output root when the path is relative.
    Returns "" when the source file cannot be located (kept optional).
    """
    sha = str(res_data.get("input_sha256") or "")
    if sha:
        return sha
    src_raw = str(res_data.get("input_file") or res_data.get("source_file") or "").strip()
    if not src_raw:
        return ""
    import hashlib
    src_path = Path(src_raw)
    candidates = [src_path]
    if not src_path.is_absolute():
        candidates.append(Path.cwd() / src_path)
        candidates.append(output_root / src_path)
    for cand in candidates:
        try:
            if cand.is_file():
                return hashlib.sha256(cand.read_bytes()).hexdigest()
        except OSError:
            continue
    return ""


def scan_package_directory(pkg_dir, output_root):
    """Scan a single package directory and produce a metadata dict."""
    pkg_dir = Path(pkg_dir)
    output_root = Path(output_root)
    try:
        folder_rel = str(pkg_dir.relative_to(output_root)).replace("\\", "/")
    except Exception:
        folder_rel = pkg_dir.name

    res_data, res_errors = _read_result_json(pkg_dir)
    warnings: List[str] = []
    errors: List[str] = list(res_errors)

    # --- Extract result.json fields using the real schema ---
    mprof = res_data.get("motif_profile") or {}
    motif = mprof.get("motif") if isinstance(mprof, dict) else None
    if not motif:
        motif = res_data.get("motif") or pkg_dir.name

    source_file = res_data.get("source_file") or res_data.get("input_file") or ""
    source_file = Path(source_file).name if source_file else ""
    gen_at = res_data.get("generated_at") or res_data.get("finished_at") or res_data.get("started_at") or ""
    db = res_data.get("fractal_dimension")
    r2 = res_data.get("r_squared")
    confidence_score = res_data.get("confidence_score")
    confidence_label = res_data.get("confidence_label")
    levels = res_data.get("computed_levels_count") or res_data.get("levels")
    if levels is None and isinstance(res_data.get("scale_table"), list):
        levels = len(res_data["scale_table"])
    runtime_ms = res_data.get("total_time_ms")
    if runtime_ms is None and res_data.get("duration_seconds") is not None:
        runtime_ms = res_data["duration_seconds"] * 1000.0

    # --- Max level from scale_table (dynamic L-filter, no L10 limit) ---
    max_level = 0
    scale_table = res_data.get("scale_table") or []
    for row in scale_table:
        lv = row.get("level") if isinstance(row, dict) else None
        if isinstance(lv, int) and lv > max_level:
            max_level = lv
    if max_level == 0 and isinstance(levels, int):
        max_level = levels

    # Per-level scale rows for the Level Metrics Table / detail views.
    scale_rows = []
    for row in scale_table:
        if not isinstance(row, dict):
            continue
        occupied = row.get("occupied_count")
        total = row.get("total_count")
        is_num = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
        has_both_dims = bool(row.get("box_size_w") and row.get("box_size_h"))
        scale_rows.append({
            "level": row.get("level"),
            "grid": row.get("grid_label", ""),
            "grid_label": row.get("grid_label", ""),
            "total_count": total,
            "occupied_count": occupied,
            "empty_count": (total - occupied) if is_num(total) and is_num(occupied) else None,
            "occupancy_percent": round((occupied / total) * 100, 2) if is_num(total) and total > 0 and is_num(occupied) else None,
            "cell_size": f"{row.get('box_size_w')}x{row.get('box_size_h')}" if has_both_dims else "",
            "included_in_fit": row.get("included_in_fit", True),
        })

    # --- Asset presence checks ---
    report_html = pkg_dir / "report" / "report.html"
    report_pdf = pkg_dir / "report" / "report.pdf"
    tables_html = pkg_dir / "tables" / "tables.html"
    tables_data = pkg_dir / "tables" / "tables_data.json"
    workbook = pkg_dir / "excel" / "workbook.xlsx"
    manifest = pkg_dir / "manifest" / "manifest.json"
    figures_dir = pkg_dir / "figures"
    tables_dir = pkg_dir / "tables"

    has_html = report_html.is_file()
    has_pdf = report_pdf.is_file()
    has_tables = tables_html.is_file()
    has_tables_data = tables_data.is_file()
    has_wb = workbook.is_file()
    has_manifest = manifest.is_file()
    has_svg = _count_files(figures_dir, ".svg") > 0
    has_xlsx = _count_files(tables_dir, ".xlsx") > 0

    figure_count = _count_files(figures_dir, ".svg")
    xlsx_count = _count_files(tables_dir, ".xlsx")

    # RASH-HIT Fractal Engine markers: cells_omitted levels (tables_data.json) + row-run SVG maps.
    cells_omitted_levels, row_run_levels = _collect_rh_engine_metadata(
        pkg_dir, tables_data, figures_dir
    )

    # --- Status determination: complete / partial / broken ---
    # tables/tables.html + tables/tables_data.json are no longer generated
    # (user request 2026-08-05), so they are never required for completeness.
    if res_errors:
        status = "broken"
    else:
        required = [has_html, has_wb, has_manifest]
        if all(required):
            status = "complete"
        elif any(required):
            status = "partial"
        else:
            status = "partial"

    # --- Warnings for missing optional assets ---
    if not has_html:
        warnings.append("Missing report/report.html")
    if not has_pdf:
        warnings.append("Missing report/report.pdf")
    if not has_wb:
        warnings.append("Missing excel/workbook.xlsx")
    if not has_manifest:
        warnings.append("Missing manifest/manifest.json")
    if not has_svg:
        warnings.append("No SVG maps found in figures/")

    # --- Build relative asset URLs (frontend never computes paths) ---
    def _url(rel: str) -> str:
        return f"{folder_rel}/{rel}"

    report_url = _url("report/report.html") if has_html else None
    report_pdf_url = _url("report/report.pdf") if has_pdf else None
    tables_url = _url("tables/tables.html") if has_tables else None
    workbook_url = _url("excel/workbook.xlsx") if has_wb else None
    manifest_url = _url("manifest/manifest.json") if has_manifest else None
    figures_url = _url("figures/") if has_svg else None
    tables_data_url = _url("tables/tables_data.json") if has_tables_data else None

    pkg_id = build_package_id(folder_rel, motif, gen_at)

    # --- Backward-compatible versioning metadata (additive; never breaks old fields) ---
    run_id = pkg_id
    package_version = "v1"
    ts_match = re.search(r"_(\d{8}_\d{6})(?:_(\d{3}))?$", folder_rel)
    if ts_match:
        run_id = f"{motif}_{ts_match.group(1)}"
        package_version = f"v{ts_match.group(1)}"
        if ts_match.group(2):
            package_version += f".{ts_match.group(2)}"

    return {
        "package_id": pkg_id,
        "run_id": run_id,
        "package_version": package_version,
        "original_motif": motif,
        "package_folder": folder_rel,
        "folder": folder_rel,
        "motif": motif,
        "source_file": source_file,
        "generated_at": gen_at,
        "db": db,
        "r2": r2,
        "confidence_score": confidence_score,
        "confidence_label": confidence_label,
        "levels": levels,
        "max_level": max_level,
        "runtime_ms": runtime_ms,
        "status": status,
        "report_url": report_url,
        "report_pdf_url": report_pdf_url,
        "tables_url": tables_url,
        "workbook_url": workbook_url,
        "manifest_url": manifest_url,
        "figures_url": figures_url,
        "tables_data_url": tables_data_url,
        "scale_rows": scale_rows,
        "figure_count": figure_count,
        "xlsx_count": xlsx_count,
        "warnings": warnings,
        "errors": errors,
        # RASH-HIT Fractal Engine high-level output policy markers (dashboard cards)
        "rh_engine_cells_omitted_count": len(cells_omitted_levels),
        "rh_engine_cells_omitted_levels": cells_omitted_levels,
        "rh_engine_row_run_count": len(row_run_levels),
        "rh_engine_row_run_levels": row_run_levels,
        "rh_engine_uses_row_runs": bool(row_run_levels),
        # Output-type presence flags (used by dashboard Output Filters)
        "has_html_report": has_html,
        "has_pdf_report": has_pdf,
        "has_excel_workbook": has_wb,
        "has_interactive_tables": has_tables,
        "has_xlsx_tables": has_xlsx,
        "has_svg_maps": has_svg,
        "has_manifest": has_manifest,
        "has_tables_data": has_tables_data,
        "svg_maps": _get_svg_maps(pkg_dir, folder_rel),
        "xlsx_cells": _get_xlsx_cells(pkg_dir, folder_rel),
        # --- Backward-compatible aliases used by existing dashboard JS ---
        "total_time_ms": runtime_ms,
        "has_report_html": has_html,
        "engine": "CPU Exact Vector Geometry Engine",
        "measure_mode": res_data.get("measure_mode", "area") or "area",
        "input_sha256": _compute_input_sha256(res_data, output_root),
    }


def scan_all_packages(output_root: Path) -> List[Dict[str, Any]]:
    """Scan outputs/ recursively and return metadata for every analysis package.

    Recognises a directory as a package when it contains result.json or any of
    the standard export sub-folders (report/, tables/, figures/, excel/, manifest/).
    Batch individual_results folders are discovered naturally because they carry
    the same package layout.
    """
    output_root = Path(output_root).resolve()
    packages: List[Dict[str, Any]] = []
    seen_ids: Dict[str, int] = {}

    if not output_root.is_dir():
        return packages

    # Skip top-level generated artifacts that are not packages.
    skip_names = {"index.html", "package_index.json", "index_manifest.json"}
    package_dirs: List[Path] = []

    for dirpath, dirnames, filenames in os.walk(output_root):
        # Do not descend into hidden dirs or node_modules copies
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d != "node_modules"]
        pdir = Path(dirpath)
        if pdir == output_root:
            continue
        if pdir.name in skip_names:
            continue

        # A package must contain result.json OR at least one export sub-folder.
        has_result = (pdir / "result.json").is_file()
        has_export = any(
            (pdir / sub).exists()
            for sub in ("report", "tables", "figures", "excel", "manifest")
        )
        if not (has_result or has_export):
            continue

        # Skip packages nested inside another already-detected package folder
        # (stale nested dirs like outputs/16D/16D must not surface as broken).
        if any(str(pdir).startswith(str(pd) + os.sep) for pd in package_dirs):
            continue
        package_dirs.append(pdir)

        pkg = scan_package_directory(pdir, output_root)
        if not pkg:
            continue

        # Guarantee unique package_id when duplicates collide.
        pid = pkg["package_id"]
        if pid in seen_ids:
            seen_ids[pid] += 1
            pid = f"{pid}_{seen_ids[pid]}"
        else:
            seen_ids[pid] = 1
        pkg["package_id"] = pid
        packages.append(pkg)

    # Default ordering: newest first (Date Newest)
    packages.sort(key=lambda p: str(p.get("generated_at") or ""), reverse=True)
    return packages


def update_package_index(output_root) -> Path:
    """Scan an output root and write machine-readable outputs/package_index.json.

    The index file is a JSON *list* of package metadata dicts (the same records
    served by GET /api/packages). Returns the Path of the written index file.
    """
    output_root = Path(output_root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    packages = scan_all_packages(output_root)
    index_path = output_root / "package_index.json"
    index_path.write_text(json.dumps(packages, indent=2, ensure_ascii=False), encoding="utf-8")
    return index_path


def get_all_figures(output_root: Path) -> List[Dict[str, Any]]:
    """Return every SVG map figure across all packages with ready-to-use URLs.

    Each figure dict follows the frontend contract:
      {package_id, motif, level, grid, file_name, url}
    The url is a *relative* path (no /outputs/ prefix) so it works when served
    by the web server (document root = outputs/) or via frontend/.
    """
    output_root = Path(output_root).resolve()
    figures: List[Dict[str, Any]] = []
    for pkg in scan_all_packages(output_root):
        figs_dir = output_root / pkg["folder"] / "figures"
        if not figs_dir.is_dir():
            continue
        for f in sorted(figs_dir.iterdir()):
            if not f.is_file() or f.suffix.lower() != ".svg":
                continue
            level, grid = _parse_figure_name(f.stem)
            figures.append({
                "package_id": pkg["package_id"],
                "motif": pkg["motif"],
                "level": level,
                "grid": grid,
                "file_name": f.name,
                "url": f"{pkg['folder']}/figures/{f.name}",
            })
    return figures


def build_stats(packages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Derive KPI stats from a package list (Total, Avg Db, Avg R2, counts, latest)."""
    total = len(packages)
    dbs = [p["db"] for p in packages if isinstance(p.get("db"), (int, float))]
    r2s = [p["r2"] for p in packages if isinstance(p.get("r2"), (int, float))]
    avg_db = round(sum(dbs) / len(dbs), 4) if dbs else 0.0
    avg_r2 = round(sum(r2s) / len(r2s), 4) if r2s else 0.0
    t_svg = sum(int(p.get("figure_count") or 0) for p in packages)
    t_xlsx = sum(int(p.get("xlsx_count") or 0) for p in packages)
    latest = max([str(p.get("generated_at") or "") for p in packages], default="N/A")
    # Both legacy (package_index) and new (dashboard) field names are returned
    # so KPI cards stay correct regardless of which contract the caller uses.
    return {
        "total_count": total,
        "total_packages": total,
        "avg_db": avg_db,
        "avg_r2": avg_r2,
        "total_svg_maps": t_svg,
        "total_figures": t_svg,
        "total_xlsx_cells": t_xlsx,
        "total_xlsx": t_xlsx,
        "latest_str": latest,
        "latest_generated": latest,
    }


def build_history(packages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build a compact run-history list from the package list."""
    return [
        {
            "package_id": p.get("package_id"),
            "motif": p.get("motif"),
            "generated_at": p.get("generated_at"),
            "status": p.get("status"),
            "db": p.get("db"),
            "r2": p.get("r2"),
            "levels": p.get("levels"),
            "folder": p.get("folder"),
        }
        for p in packages
    ]


def _get_svg_maps(pkg_dir: Path, folder_rel: str) -> List[Dict[str, Any]]:
    figs_dir = pkg_dir / "figures"
    maps = []
    if figs_dir.is_dir():
        for f in sorted(figs_dir.iterdir()):
            if f.is_file() and f.suffix.lower() == ".svg":
                lvl, grid = _parse_figure_name(f.stem)
                maps.append({
                    "rel_path": f"figures/{f.name}",
                    "file_name": f.name,
                    "level": lvl,
                    "grid": grid,
                    "url": f"{folder_rel}/figures/{f.name}"
                })
    return maps


def _get_xlsx_cells(pkg_dir: Path, folder_rel: str) -> List[Dict[str, Any]]:
    tables_dir = pkg_dir / "tables"
    cells = []
    if tables_dir.is_dir():
        for f in sorted(tables_dir.iterdir()):
            if f.is_file() and f.suffix.lower() == ".xlsx":
                lvl, grid = _parse_figure_name(f.stem)
                cells.append({
                    "rel_path": f"tables/{f.name}",
                    "file_name": f.name,
                    "level": lvl,
                    "grid": grid,
                    "url": f"{folder_rel}/tables/{f.name}"
                })
    return cells
