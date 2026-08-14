# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""Taichi smoke kernel for Stage 2 backend validation.

Goal (NOT a production engine): prove CUDA/CPU backends run a deterministic
integer kernel and match a NumPy reference exactly.

Kernel semantics (kept trivial & exact):
    out[i] = (a[i] * 3 + b[i]) % 1024          # int32 path
    out[i] = (a[i] * 3 + b[i]) % 4096          # int64 path
Both a and b are seeded deterministically, so the expected output is known.

Each backend is exercised in its OWN subprocess by tools/run_cuda_smoke_test.py
(see Stage 2.8) so a CUDA crash cannot take down the diagnostic harness.
"""

from __future__ import annotations

import statistics
import time
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np

# Deterministic seeds so results are reproducible across runs.
SEED = 20260714
ARRAY_LEN = 1 << 16  # 65536 elements — small, fast, well within tiny VRAM budget
MOD32 = 1024
MOD64 = 4096


@dataclass
class SmokeResult:
    backend: str
    ok: bool
    dtype: str
    n: int
    matches_reference: bool = False
    first_call_ms: float = 0.0
    hot_mean_ms: float = 0.0
    hot_min_ms: float = 0.0
    hot_max_ms: float = 0.0
    hot_median_ms: float = 0.0
    error: str = ""
    note: str = ""


def _make_arrays(dtype: str):
    rng = np.random.default_rng(SEED)
    if dtype == "int32":
        a = rng.integers(0, MOD32, size=ARRAY_LEN, dtype=np.int32)
        b = rng.integers(0, MOD32, size=ARRAY_LEN, dtype=np.int32)
    else:
        a = rng.integers(0, MOD64, size=ARRAY_LEN, dtype=np.int64)
        b = rng.integers(0, MOD64, size=ARRAY_LEN, dtype=np.int64)
    return a, b


def _reference(a, b, dtype: str):
    mod = MOD32 if dtype == "int32" else MOD64
    return ((a.astype(np.int64) * 3 + b.astype(np.int64)) % mod).astype(a.dtype)


def _taichi_kernel(arch, a, b, dtype: str, n_warm=1, n_hot=10):
    import taichi as ti

    ti.init(arch=arch, fast_math=False, offline_cache=True,
            log_level="warn", verbose=False)

    mod = MOD32 if dtype == "int32" else MOD64
    n = a.shape[0]
    out = np.zeros(n, dtype=a.dtype)

    a_t = ti.field(dtype=getattr(ti, dtype), shape=n)
    b_t = ti.field(dtype=getattr(ti, dtype), shape=n)
    out_t = ti.field(dtype=getattr(ti, dtype), shape=n)

    a_t.from_numpy(a)
    b_t.from_numpy(b)

    @ti.kernel
    def compute():
        for i in range(n):
            out_t[i] = (a_t[i] * 3 + b_t[i]) % mod

    # cold / JIT compile call
    t0 = time.perf_counter()
    compute()
    ti.sync()
    first_call_ms = (time.perf_counter() - t0) * 1000.0

    # hot repeats
    hots: List[float] = []
    for _ in range(n_hot):
        t0 = time.perf_counter()
        compute()
        ti.sync()
        hots.append((time.perf_counter() - t0) * 1000.0)

    out = out_t.to_numpy()
    return out, first_call_ms, hots


def run_smoke(backend: str, dtype: str = "int32", n_hot: int = 10) -> SmokeResult:
    """Run a single backend smoke test. backend in {'cpu','cuda'}."""
    a, b = _make_arrays(dtype)
    ref = _reference(a, b, dtype)
    try:
        import taichi as ti
        arch = ti.cuda if backend == "cuda" else ti.cpu
        out, first_ms, hots = _taichi_kernel(arch, a, b, dtype, n_hot=n_hot)
        matches = bool(np.array_equal(out, ref))
        res = SmokeResult(
            backend=backend, ok=True, dtype=dtype, n=a.shape[0],
            matches_reference=matches,
            first_call_ms=first_ms,
            hot_mean_ms=statistics.mean(hots),
            hot_min_ms=min(hots),
            hot_max_ms=max(hots),
            hot_median_ms=statistics.median(hots),
            note="Taichi kernel executed",
        )
        if not matches:
            res.ok = False
            res.error = "GPU result != NumPy reference"
        return res
    except Exception as exc:  # noqa: BLE001 — capture, never crash the harness
        return SmokeResult(
            backend=backend, ok=False, dtype=dtype, n=a.shape[0],
            error=f"{type(exc).__name__}: {exc}",
            note="Backend initialization or kernel failed",
        )


def run_cpu_smoke(dtype: str = "int32") -> SmokeResult:
    return run_smoke("cpu", dtype)


def run_cuda_smoke(dtype: str = "int32") -> SmokeResult:
    return run_smoke("cuda", dtype)
