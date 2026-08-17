# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""Stage 3.7 — Common engine contract for CPU / GPU / validation motors.

This module defines the SHARED input/output contract that the current CPU
engine and any future GPU engine must satisfy. It is intentionally free of any
PySide / web / CLI dependency so it can be imported anywhere.

IMPORTANT (Stage 3 scope):
- Only ``cpu_reference`` is fully implemented here; it wraps the EXISTING
  ``AnalysisProcessor`` without rewriting its algorithm.
- ``gpu_experimental`` is a PLACEHOLDER that raises ``NotImplementedError`` so
  it can never be silently selected for production analysis.
- ``auto`` currently resolves to ``cpu_reference`` (GPU is not production-ready).
- ``validate`` runs CPU and is intended to cross-check a future GPU result.

The contract does NOT:
- produce reports (that stays in processor/academic_exporter),
- compute Db / R^2 (that stays in regression),
- change AnalysisProcessor's default behaviour.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    TypeAlias = Any  # type: ignore

# Local contract exception (no cross-module dependency on backend.compute).
class UnsupportedOperationError(RuntimeError):
    """Raised when an engine/backend is selected but not implemented."""


class EngineKind(str, Enum):
    CPU_REFERENCE = "cpu_reference"
    GPU_EXPERIMENTAL = "gpu_experimental"
    AUTO = "auto"
    VALIDATE = "validate"


@dataclass
class EngineInput:
    """Normalized input handed to any engine."""
    input_path: str
    levels: int = 10
    boundary_policy: str = "touch_counts"   # documented default of the CPU engine
    fill_rule: str = "evenodd"
    flattening_settings: Dict[str, Any] = field(default_factory=dict)
    grid_origin: tuple = (0.0, 0.0)
    measure_mode: str = "area"
    enable_profiling: bool = False
    # placeholders for future GPU paths
    cancellation_token: Optional[Any] = None
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None


@dataclass
class LevelResult:
    level: int
    rows: int
    columns: int
    total_cells: int
    occupied_cells: int
    empty_cells: int
    occupancy_ratio: float
    optional_occupied_cell_ids: Optional[List[Any]] = None
    timings: Dict[str, float] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    backend_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EngineOutput:
    engine: str
    levels: List[LevelResult]
    fractal_dimension: float = 1.0
    r_squared: float = 0.0
    input_sha256: str = ""
    warnings: List[str] = field(default_factory=list)
    backend_metadata: Dict[str, Any] = field(default_factory=dict)


def _run_cpu_reference(inp: EngineInput) -> EngineOutput:
    """Execute the existing CPU engine through the common contract."""
    from backend.processor import AnalysisProcessor
    import tempfile
    from backend.profile import sha256_of_file
    from pathlib import Path

    with tempfile.TemporaryDirectory() as td:
        proc = AnalysisProcessor(
            input_path=inp.input_path,
            output_dir=td,
            levels=inp.levels,
            measure_mode=inp.measure_mode,
            enable_profiling=inp.enable_profiling,
            export_artifacts=False,
        )
        res = proc.run()
        if res.status != "SUCCESS":
            raise RuntimeError(f"cpu_reference failed: {res.errors}")
        result_json = Path(td) / res.package_id / "result.json"
        data = __import__("json").loads(result_json.read_text(encoding="utf-8"))
        lgrid = {int(r["level"]): r for r in data.get("level_grid", [])}
        levels = [LevelResult(
            level=row["level"],
            rows=row["rows"],
            columns=row["columns"],
            total_cells=row["total_cells"],
            occupied_cells=row["filled_cells"],
            empty_cells=row["empty_cells"],
            occupancy_ratio=round(row["occupancy_percent"] / 100.0, 6),
        ) for row in lgrid.values()]
        return EngineOutput(
            engine="cpu_reference",
            levels=levels,
            fractal_dimension=res.fractal_dimension,
            r_squared=res.r_squared,
            input_sha256=sha256_of_file(Path(inp.input_path)),
            warnings=list(res.warnings),
            backend_metadata={"source": "AnalysisProcessor"},
        )


def _run_gpu_experimental_placeholder(inp: EngineInput) -> EngineOutput:
    raise UnsupportedOperationError(
        "gpu_experimental is a placeholder for Stage 6-9 and is NOT selectable "
        "for production analysis yet. Use cpu_reference."
    )


_ENGINE_DISPATCH = {
    EngineKind.CPU_REFERENCE: _run_cpu_reference,
    EngineKind.GPU_EXPERIMENTAL: _run_gpu_experimental_placeholder,
    EngineKind.VALIDATE: _run_cpu_reference,  # validation currently uses CPU as ground truth
}


def resolve_engine(kind: EngineKind) -> EngineKind:
    """Resolve the concrete engine. AUTO -> CPU until GPU is production-ready."""
    if kind == EngineKind.AUTO:
        return EngineKind.CPU_REFERENCE
    return kind


def run_engine(kind: EngineKind, inp: EngineInput) -> EngineOutput:
    kind = resolve_engine(kind)
    fn = _ENGINE_DISPATCH.get(kind)
    if fn is None:
        raise UnsupportedOperationError(f"engine {kind} is not available")
    return fn(inp)


# Backwards-compatible alias used by callers that pass a plain string.
def run_engine_by_name(name: str, inp: EngineInput) -> EngineOutput:
    try:
        kind = EngineKind(name)
    except ValueError:
        raise UnsupportedOperationError(f"unknown engine '{name}'")
    return run_engine(kind, inp)
