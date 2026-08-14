# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""backend.compute — hardware discovery & compute backend selection layer.

Read-only diagnostic modules only at this stage (Stage 2). No production
analysis engine is implemented here yet; the modules below feed the
backend selector built in Stage 3.
"""
from __future__ import annotations

from backend.compute.exceptions import (
    ComputeError,
    DeviceScanError,
    MemoryPolicyError,
    BackendInitError,
    VRAMUnavailable,
)
from backend.compute.backend_types import (
    GPUDevice,
    ComputeBackend,
    MemoryProfile,
)

__all__ = [
    "ComputeError",
    "DeviceScanError",
    "MemoryPolicyError",
    "BackendInitError",
    "VRAMUnavailable",
    "GPUDevice",
    "ComputeBackend",
    "MemoryProfile",
]
