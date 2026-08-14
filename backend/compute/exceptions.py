# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""Exceptions for the compute backend layer (Stage 2, diagnostic scope)."""
from __future__ import annotations


class ComputeError(Exception):
    """Base class for compute-layer errors."""


class DeviceScanError(ComputeError):
    """Raised when hardware/device enumeration fails."""


class MemoryPolicyError(ComputeError):
    """Raised when a dynamic GPU memory budget cannot be computed safely."""


class BackendInitError(ComputeError):
    """Raised when a compute backend (CUDA/CPU) fails to initialize."""


class VRAMUnavailable(ComputeError):
    """Raised when VRAM information cannot be read from the device."""
