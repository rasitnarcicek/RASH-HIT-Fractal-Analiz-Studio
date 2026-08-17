# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""
processor.py - Unified Core Processing Engine for RASH-HIT Fractal Studio.
Provides a single authoritative motor powering CLI Terminal Launcher, Web Dashboard REST API,
and Direct CLI execution with 100% computational parity.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from backend.confidence import evaluate_confidence, generate_motif_profile
from backend.output_profiles import load_output_profile
from backend.regression import compute_loglog_regression, generate_loglog_plot_svg
from backend.svg_health import inspect_svg_health
from backend.profile import sha256_of_file


@dataclass
class StepProgress:
    step_index: int
    total_steps: int
    name: str
    status: str  # "PENDING", "RUNNING", "SUCCESS", "ERROR"
    percent: float
    start_time_iso: str = ""
    end_time_iso: str = ""
    duration_sec: float = 0.0
    message: str = ""
    error_message: str = ""
    output_files: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_index": self.step_index,
            "total_steps": self.total_steps,
            "name": self.name,
            "status": self.status,
            "percent": round(self.percent, 1),
            "start_time_iso": self.start_time_iso,
            "end_time_iso": self.end_time_iso,
            "duration_sec": round(self.duration_sec, 3),
            "message": self.message,
            "error_message": self.error_message,
            "output_files": self.output_files,
        }


@dataclass
class ExecutionResult:
    job_id: str
    input_file: str
    output_dir: str
    analysis_mode: str
    requested_levels: int
    computed_levels_count: int
    status: str  # "SUCCESS", "FAILED"
    package_id: str = ""
    source_file: str = ""
    generated_at: str = ""
    engine_version: str = "1.0.0"
    analysis_profile_version: str = "1"
    svg_health: Dict[str, Any] = field(default_factory=dict)
    scale_table: List[Dict[str, Any]] = field(default_factory=list)
    fractal_dimension: float = 1.0
    r_squared: float = 0.0
    confidence_score: float = 0.0
    confidence_label: str = "Uncertain"
    confidence_details: Dict[str, Any] = field(default_factory=dict)
    motif_profile: Dict[str, Any] = field(default_factory=dict)
    steps: List[StepProgress] = field(default_factory=list)
    level_grid: List[Dict[str, Any]] = field(default_factory=list)
    output_files: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    started_at: str = ""
    finished_at: str = ""
    duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "package_id": self.package_id,
            "input_file": self.input_file,
            "source_file": self.source_file,
            "output_dir": self.output_dir,
            "analysis_mode": self.analysis_mode,
            "requested_levels": self.requested_levels,
            "computed_levels_count": self.computed_levels_count,
            "levels": self.computed_levels_count,
            "status": self.status,
            "generated_at": self.generated_at,
            "created_at": self.generated_at,
            "engine_version": self.engine_version,
            "analysis_profile_version": self.analysis_profile_version,
            "svg_health": self.svg_health,
            "scale_table": self.scale_table,
            "level_grid": self.level_grid,
            "fractal_dimension": round(self.fractal_dimension, 4),
            "r_squared": round(self.r_squared, 4),
            "confidence_score": round(self.confidence_score, 1),
            "confidence_label": self.confidence_label,
            "confidence_details": self.confidence_details,
            "motif_profile": self.motif_profile,
            "steps": [s.to_dict() for s in self.steps],
            "output_files": self.output_files,
            "warnings": self.warnings,
            "errors": self.errors,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_seconds": round(self.duration_seconds, 3),
            "total_time_ms": round(self.duration_seconds * 1000.0, 2),
        }


# Mode level mapping
MODE_LEVEL_MAP = {
    "fast": 5,
    "balanced": 7,
    "precise": 9,
    "academic": 10,
    "batch": 7,
}


class AnalysisProcessor:
    """Unified execution engine for single and batch SVG fractal analysis."""

    STANDARD_STEP_NAMES = [
        "1. Input Validation & Security",
        "2. SVG Health & Structure Inspection",
        "3. Vector Geometry Parsing & Normalization",
        "4. Level Settings & Doubling Grid Setup",
        "5. Hierarchical Box-Counting Computation",
        "6. Log-Log Regression & Confidence Evaluation",
        "7. Package Export & Artifact Generation",
    ]

    def __init__(
        self,
        input_path: str | Path,
        output_dir: Optional[str | Path] = None,
        mode: str = "balanced",
        levels: Optional[int] = None,
        engine: str = "cpu",
        measure_mode: str = "area",
        overwrite: bool = False,
        progress_callback: Optional[Callable[[StepProgress], None]] = None,
        profile: Optional[str] = "lean",
        enable_profiling: bool = False,
        export_artifacts: bool = True,
    ):
        self.input_path = Path(input_path).resolve()
        self.mode = mode.lower() if mode else "balanced"
        self.requested_levels = levels if levels is not None else MODE_LEVEL_MAP.get(self.mode, 7)
        self.engine = engine
        self.measure_mode = measure_mode
        # Data-protective default: never silently overwrite an existing package.
        self.overwrite = bool(overwrite)
        self.progress_callback = progress_callback
        self.profile = profile or "lean"
        self.enable_profiling = bool(enable_profiling)
        self.export_artifacts = bool(export_artifacts)

        if output_dir:
            self.output_root = Path(output_dir).resolve()
        else:
            self.output_root = Path("outputs").resolve()

        self.job_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.steps: List[StepProgress] = [
            StepProgress(
                step_index=idx + 1,
                total_steps=len(self.STANDARD_STEP_NAMES),
                name=name,
                status="PENDING",
                percent=(idx / len(self.STANDARD_STEP_NAMES)) * 100.0,
            )
            for idx, name in enumerate(self.STANDARD_STEP_NAMES)
        ]

    def _update_step(
        self,
        step_idx: int,
        status: str,
        message: str = "",
        error_message: str = "",
        output_files: Optional[List[str]] = None,
    ):
        sp = self.steps[step_idx - 1]
        sp.status = status
        now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if status == "RUNNING" and not sp.start_time_iso:
            sp.start_time_iso = now_iso
            sp._start_t = time.time()
        elif status in ("SUCCESS", "ERROR"):
            sp.end_time_iso = now_iso
            if hasattr(sp, "_start_t"):
                sp.duration_sec = time.time() - sp._start_t

        if message:
            sp.message = message
        if error_message:
            sp.error_message = error_message
        if output_files:
            sp.output_files.extend(output_files)

        sp.percent = ((step_idx) / len(self.STANDARD_STEP_NAMES)) * 100.0 if status == "SUCCESS" else sp.percent

        if self.progress_callback:
            try:
                self.progress_callback(sp)
            except Exception:
                pass

    def run(self, progress_callback=None, level_callback=None) -> ExecutionResult:
        """Executes the full unified processing pipeline.

        progress_callback (Callable[[StepProgress], None]) receives step updates;
        level_callback (Callable[[LevelReportModel], None]) receives each completed
        box-counting level immediately after it finishes. Both are optional and
        temporarily override any constructor-level callback for this run.
        """
        if progress_callback is not None:
            self.progress_callback = progress_callback
        self._level_callback = level_callback

        from backend.profile import PipelineProfiler
        prof = PipelineProfiler(enabled=self.enable_profiling)
        prof.start()

        start_time_all = time.time()
        start_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        res = ExecutionResult(
            job_id=self.job_id,
            input_file=str(self.input_path),
            output_dir=str(self.output_root),
            analysis_mode=self.mode,
            requested_levels=self.requested_levels,
            computed_levels_count=0,
            status="FAILED",
            started_at=start_iso,
        )

        # ---------------------------------------------------------------------
        # STEP 1: Input Validation & Security
        # ---------------------------------------------------------------------
        prof.begin_phase("step_1_input_validation")
        self._update_step(1, "RUNNING", message="Validating input file path and permissions...")
        if not self.input_path.exists():
            err_msg = f"Error: Input file not found -> '{self.input_path}'"
            res.errors.append(err_msg)
            self._update_step(1, "ERROR", error_message=err_msg)
            res.finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            res.duration_seconds = time.time() - start_time_all
            prof.finish()
            return res

        if self.input_path.suffix.lower() != ".svg":
            err_msg = f"Error: Unsupported file format ('{self.input_path.suffix}'). Only the '.svg' extension is supported."
            res.errors.append(err_msg)
            self._update_step(1, "ERROR", error_message=err_msg)
            res.finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            res.duration_seconds = time.time() - start_time_all
            prof.finish()
            return res

        self._update_step(1, "SUCCESS", message=f"Input file validated: {self.input_path.name}")
        prof.end_phase("step_1_input_validation")

        # ---------------------------------------------------------------------
        # STEP 2: SVG Health & Structure Inspection
        # ---------------------------------------------------------------------
        prof.begin_phase("step_2_svg_health")
        self._update_step(2, "RUNNING", message="Inspecting SVG health, viewBox, shape elements, and transforms...")
        health_res = inspect_svg_health(self.input_path)
        res.svg_health = health_res.to_dict()
        res.warnings.extend(health_res.warnings)
        res.errors.extend(health_res.errors)

        if not health_res.is_valid_xml or health_res.total_shape_elements == 0:
            err_msg = f"SVG Health Check Failed: {'; '.join(health_res.errors)}"
            self._update_step(2, "ERROR", error_message=err_msg)
            res.finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            res.duration_seconds = time.time() - start_time_all
            prof.finish()
            return res

        self._update_step(
            2,
            "SUCCESS",
            message=f"SVG Health Score: {health_res.suitability_score}/100 ({health_res.suitability}) - {health_res.total_shape_elements} shapes.",
        )
        prof.end_phase("step_2_svg_health")

        # ---------------------------------------------------------------------
        # STEP 3: Vector Geometry Parsing & Normalization
        # ---------------------------------------------------------------------
        prof.begin_phase("step_3_geometry_parsing")
        self._update_step(3, "RUNNING", message="Parsing vector paths, polygon geometries, and viewbox bounds...")
        from backend.svg_loader import load_svg_geometries

        try:
            geoms, vw, vh = load_svg_geometries(self.input_path)
        except Exception as e:
            err_msg = f"SVG geometry loading error: {e}"
            res.errors.append(err_msg)
            self._update_step(3, "ERROR", error_message=err_msg)
            res.finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            res.duration_seconds = time.time() - start_time_all
            prof.finish()
            return res

        self._update_step(3, "SUCCESS", message=f"Loaded {len(geoms)} vector geometries (ViewBox: {vw:.2f} x {vh:.2f}).")
        prof.end_phase("step_3_geometry_parsing")

        # ---------------------------------------------------------------------
        # STEP 4: Level Settings & Doubling Grid Setup
        # ---------------------------------------------------------------------
        prof.begin_phase("step_4_grid_setup")
        self._update_step(4, "RUNNING", message=f"Setting up doubling grid hierarchy for L01..L{self.requested_levels:02d}...")
        from backend.grid_planner import generate_doubling_grid_spec

        grid_specs = generate_doubling_grid_spec(vw, vh, levels=self.requested_levels)
        self._update_step(4, "SUCCESS", message=f"Generated {len(grid_specs)} grid levels (4x8 up to {grid_specs[-1][0]}x{grid_specs[-1][1]}).")
        prof.end_phase("step_4_grid_setup")

        # ---------------------------------------------------------------------
        # STEP 5: Hierarchical Box-Counting Computation
        # ---------------------------------------------------------------------
        prof.begin_phase("step_5_box_counting")
        self._update_step(5, "RUNNING", message="Computing vector-grid intersections across doubling grid levels...")
        from backend.intersection_hierarchical import compute_hierarchical_box_counting

        start_comp = time.time()

        def _per_level(lm):
            if self._level_callback is not None:
                try:
                    self._level_callback(lm)
                except Exception:
                    pass

        lvl_report_models, summary_dict = compute_hierarchical_box_counting(
            geoms, vw, vh, grid_specs,
            measure_mode=self.measure_mode,
            progress_callback=_per_level if self._level_callback is not None else None,
        )
        total_comp_ms = (time.time() - start_comp) * 1000.0
        prof.end_phase("step_5_box_counting")

        levels_data_raw = []
        for idx, lm in enumerate(lvl_report_models):
            cols, rows = grid_specs[idx] if idx < len(grid_specs) else (0, 0)
            total = lm.total_cells
            occ = lm.filled_cells
            emp = lm.empty_cells
            occ_pct = (occ / total * 100.0) if total > 0 else 0.0
            levels_data_raw.append({
                "level": int(lm.level),
                "grid_label": lm.grid_label,
                "rows": rows,
                "columns": cols,
                "cell_w": lm.cell_w,
                "cell_h": lm.cell_h,
                "filled_cells": occ,
                "empty_cells": emp,
                "total_cells": total,
                "occupancy_percent": occ_pct,
                "execution_time_ms": lm.execution_time_ms,
                "mode": lm.mode,
            })

        res.computed_levels_count = len(levels_data_raw)
        res.level_grid = levels_data_raw
        self._update_step(5, "SUCCESS", message=f"Box-counting completed for {len(levels_data_raw)} levels in {total_comp_ms:.2f} ms.")

        # ---------------------------------------------------------------------
        # STEP 6: Log-Log Regression & Confidence Evaluation
        # ---------------------------------------------------------------------
        prof.begin_phase("step_6_regression")
        self._update_step(6, "RUNNING", message="Calculating log-log linear regression slope (Db), R2, and scientific confidence...")
        reg_res = compute_loglog_regression(levels_data_raw)
        res.fractal_dimension = reg_res.db
        res.r_squared = reg_res.r2
        res.scale_table = [s.to_dict() for s in reg_res.scale_table]

        conf_eval = evaluate_confidence(
            db=reg_res.db,
            r2=reg_res.r2,
            valid_scales=reg_res.valid_scales_count,
            svg_suitability_score=health_res.suitability_score,
            total_shape_elements=health_res.total_shape_elements,
        )
        res.confidence_score = conf_eval.score
        res.confidence_label = conf_eval.label
        res.confidence_details = conf_eval.to_dict()

        avg_occ = sum(l["occupancy_percent"] for l in levels_data_raw) / len(levels_data_raw) if levels_data_raw else 0.0
        motif_name = self.input_path.stem
        m_prof = generate_motif_profile(
            motif_name=motif_name,
            db=reg_res.db,
            r2=reg_res.r2,
            total_elements=health_res.total_shape_elements,
            avg_occupancy_pct=avg_occ,
        )
        res.motif_profile = m_prof.to_dict()

        self._update_step(
            6,
            "SUCCESS",
            message=f"Db = {reg_res.db:.4f}, R2 = {reg_res.r2:.4f}, Confidence: {conf_eval.label} ({conf_eval.score:.1f}/100)",
        )
        prof.end_phase("step_6_regression")

        # ---------------------------------------------------------------------
        # STEP 7: Package Export & Artifact Generation
        # ---------------------------------------------------------------------
        prof.begin_phase("step_7_export")
        self._update_step(7, "RUNNING", message="Exporting HTML/PDF report, XLSX tables, loglog plot, and manifest...")

        # Default package location (used by both paths).
        safe_name = motif_name.replace(" ", "_")
        output_pkg_dir = self.output_root / safe_name

        if self.export_artifacts:
            from backend.academic_exporter import AnalysisReportModel, export_academic_package_v3

            report_model = AnalysisReportModel(
                motif=motif_name,
                safe_name=safe_name,
                generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                source_file=str(self.input_path),
                viewbox_width=vw,
                viewbox_height=vh,
                aspect_ratio=vw / vh if vh > 0 else 1.0,
                vector_geometry_count=len(geoms),
                analysis_engine="CPU Exact Vector Geometry Engine",
                db=reg_res.db,
                r2=reg_res.r2,
                total_time_ms=total_comp_ms,
                levels=lvl_report_models,
            )

            profile_obj = load_output_profile(self.profile)
            output_pkg_dir = export_academic_package_v3(
                report_model, self.output_root, profile=profile_obj, overwrite=self.overwrite,
            )

            # Generate Log-Log SVG Plot
            loglog_plot_path = output_pkg_dir / "report" / "loglog_plot.svg"
            generate_loglog_plot_svg(reg_res, loglog_plot_path)
        else:
            # Lightweight path (reference generation / benchmarking): keep the
            # machine-readable result.json only, skip heavy PDF/XLSX/plot.
            output_pkg_dir.mkdir(parents=True, exist_ok=True)

        # Write Machine-Readable result.json (always; required downstream).
        res.status = "SUCCESS"
        res.finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        res.duration_seconds = time.time() - start_time_all
        res.package_id = output_pkg_dir.name
        res.source_file = str(self.input_path)
        res.generated_at = res.finished_at
        res.engine_version = "1.0.0"
        res.analysis_profile_version = "1"

        # Collect output file paths
        out_files = [str(p.relative_to(output_pkg_dir).as_posix()) for p in output_pkg_dir.rglob("*") if p.is_file()]
        res.output_files = out_files

        json_result_path = output_pkg_dir / "result.json"
        json_result_path.write_text(json.dumps(res.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

        self._update_step(7, "SUCCESS", message=f"Package generated at: {output_pkg_dir}", output_files=out_files)

        # Update machine-readable package index (package_index.json) only when
        # we actually produced a full package (lightweight runs skip it).
        if self.export_artifacts:
            try:
                from backend.package_index import update_package_index
                update_package_index(self.output_root)
            except Exception:
                pass
        prof.end_phase("step_7_export")
        prof.finish()

        # Expose profiling payload on the result (non-scientific metadata only).
        if prof.enabled:
            res.profiling = {
                "input_sha256": sha256_of_file(self.input_path),
                "engine": "cpu",
                "levels": [lv["level"] for lv in levels_data_raw],
                "timings_seconds": prof.to_dict(),
            }
            # Best-effort JSON sidecar (never fails the analysis).
            try:
                prof.write_json(output_pkg_dir / "cpu_profile.json")
            except Exception:
                pass

        return res
