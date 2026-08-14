# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""backend.gpu — GPU compute kernels (Stage 2: smoke-test only).

The smoke kernel here is NOT a production fractal-analysis kernel. It exists
only to prove that Taichi can (a) initialize on CUDA, (b) run a deterministic
integer kernel, and (c) produce byte-for-byte identical results to a NumPy CPU
reference. Real SVG/grid kernels arrive in Stages 6-9.
"""
from __future__ import annotations

from backend.gpu.smoke_kernel import run_cuda_smoke, run_cpu_smoke, SmokeResult

__all__ = ["run_cuda_smoke", "run_cpu_smoke", "SmokeResult"]
