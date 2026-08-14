# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""CUDA/CPU smoke tests (Stage 2).

CPU smoke must ALWAYS run and pass. CUDA smoke is skipped automatically when no
real CUDA GPU/driver is available, so these tests never fail the suite merely
because the machine lacks a usable CUDA backend. A genuine CUDA *failure* (driver
present but kernel mismatch) is still surfaced as a pytest failure.
"""
import numpy as np
import pytest

taichi = pytest.importorskip("taichi")


def test_cpu_smoke_matches_reference():
    from backend.gpu.smoke_kernel import run_cpu_smoke
    res = run_cpu_smoke("int32")
    assert res.ok, f"CPU smoke failed: {res.error}"
    assert res.matches_reference, "CPU Taichi result != NumPy reference"
    assert res.hot_mean_ms >= 0


def test_int64_cpu_functional():
    from backend.gpu.smoke_kernel import run_cpu_smoke
    res = run_cpu_smoke("int64")
    # Functional support only — report status, must at least run and match reference.
    assert res.ok, f"int64 CPU smoke failed: {res.error}"
    assert res.matches_reference


def test_cuda_smoke_or_skip():
    import taichi as ti
    # Skip cleanly if Taichi cannot init CUDA (no GPU / no driver).
    try:
        ti.init(arch=ti.cuda, fast_math=False, offline_cache=True,
                log_level="error", verbose=False)  # 'error' valid in Taichi 1.7.4
    except Exception as exc:
        pytest.skip(f"CUDA backend unavailable: {exc}")
    from backend.gpu.smoke_kernel import run_cuda_smoke
    res = run_cuda_smoke("int32")
    # If CUDA truly initialized but result mismatched, that is a real failure.
    assert res.ok, f"CUDA smoke failed: {res.error}"
    assert res.matches_reference, "CUDA Taichi result != NumPy reference"
