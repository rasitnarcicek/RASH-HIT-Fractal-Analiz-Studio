# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""Tests for the common engine contract (Stage 3.7)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.engine_contract import (  # noqa: E402
    EngineInput, EngineKind, run_engine, run_engine_by_name,
    UnsupportedOperationError,
)

FIX = ROOT / "tests" / "fixtures" / "svg_reference"


def _inp(name: str, levels: int = 5):
    return EngineInput(input_path=str(FIX / name), levels=levels)


def test_cpu_reference_runs_and_matches_shape():
    out = run_engine(EngineKind.CPU_REFERENCE, _inp("diagonal_line.svg", levels=5))
    assert out.engine == "cpu_reference"
    assert len(out.levels) == 5
    # occupied + empty == total for every level
    for lv in out.levels:
        assert lv.occupied_cells + lv.empty_cells == lv.total_cells
        assert lv.total_cells > 0


def test_gpu_experimental_is_placeholder_not_selectable():
    with pytest.raises(UnsupportedOperationError):
        run_engine(EngineKind.GPU_EXPERIMENTAL, _inp("diagonal_line.svg"))


def test_auto_resolves_to_cpu():
    from backend.engine_contract import resolve_engine
    assert resolve_engine(EngineKind.AUTO) == EngineKind.CPU_REFERENCE


def test_run_engine_by_name_rejects_unknown():
    with pytest.raises(UnsupportedOperationError):
        run_engine_by_name("gpu_experimental", _inp("diagonal_line.svg"))


def test_cpu_reference_matches_reference_json():
    """cpu_reference output must agree with the frozen reference (3.5/3.6)."""
    import json
    out = run_engine(EngineKind.CPU_REFERENCE, _inp("horizontal_line.svg", levels=10))
    ref_path = ROOT / "tests" / "reference_results" / "horizontal_line.json"
    if not ref_path.exists():
        pytest.skip("reference not generated yet")
    ref = json.loads(ref_path.read_text(encoding="utf-8"))
    for lv in out.levels:
        r = ref["per_level"][str(lv.level)]
        assert lv.occupied_cells == r["occupied_cells"]
        assert lv.total_cells == r["total_cells"]
