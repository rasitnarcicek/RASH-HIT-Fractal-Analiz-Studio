# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""Non-invasive pipeline timing profiler (Stage 3.3).

This module adds wall-clock timing AROUND the existing pipeline steps WITHOUT
changing any scientific result. It is opt-in: ``AnalysisProcessor`` only
records timings when ``enable_profiling=True`` is passed. Timing uses a
monotonic high-resolution clock (``time.perf_counter``) and never affects
the computed Db / R^2 / cell counts.

Design rules honoured:
- No fake precision for very small durations (we report raw seconds).
- Profiling failure must never abort the analysis (all wrapped in try/except).
- Profiling state lives outside the result payload until explicitly exported.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class PipelineProfiler:
    """Collects per-step timings for one analysis run.

    Phase keys follow the canonical 7-step pipeline in ``processor.py``:
      step_1_input_validation, step_2_svg_health, step_3_geometry_parsing,
      step_4_grid_setup, step_5_box_counting, step_6_regression,
      step_7_export, total.
    Granular sub-phases (e.g. per-level intersection) are recorded under
    ``sub`` for later breakdown.
    """

    enabled: bool = False
    _t0_total: float = 0.0
    _phase_starts: Dict[str, float] = field(default_factory=dict)
    phases: Dict[str, float] = field(default_factory=dict)
    sub: Dict[str, Any] = field(default_factory=dict)

    def start(self) -> None:
        if not self.enabled:
            return
        self._t0_total = time.perf_counter()

    def begin_phase(self, key: str) -> None:
        if not self.enabled:
            return
        self._phase_starts[key] = time.perf_counter()

    def end_phase(self, key: str) -> None:
        if not self.enabled or key not in self._phase_starts:
            return
        dt = time.perf_counter() - self._phase_starts[key]
        self.phases[key] = self.phases.get(key, 0.0) + dt
        self._phase_starts.pop(key, None)

    def finish(self) -> None:
        if not self.enabled:
            return
        # Close any phase left open.
        for k in list(self._phase_starts.keys()):
            self.end_phase(k)
        if self._t0_total:
            self.phases["total"] = time.perf_counter() - self._t0_total

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for k, v in self.phases.items():
            out[k] = round(v, 6)
        if self.sub:
            out["sub"] = self.sub
        return out

    def write_json(self, path: Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema": "rashhit.cpu.profile/v1",
            "timings_seconds": self.to_dict(),
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path


def sha256_of_file(path: Path) -> str:
    """Return SHA-256 of a file's bytes (used for input-identifying refs)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_cpu_profile(path: Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
