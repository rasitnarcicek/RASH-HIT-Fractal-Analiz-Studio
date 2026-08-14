# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""Shared data types for the compute layer (Stage 2)."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class ComputeBackend(str, Enum):
    """Candidate compute backends. Resolution order is defined by the selector."""
    AUTO = "auto"
    CUDA = "cuda"
    VULKAN = "vulkan"
    CPU = "cpu"


class MemoryProfile(str, Enum):
    """Dynamic VRAM budget profiles (fraction of free VRAM)."""
    SAFE = "safe"          # ~50%
    AUTOMATIC = "automatic"  # ~60%
    PERFORMANCE = "performance"  # ~75%
    CUSTOM = "custom"


@dataclass
class GPUDevice:
    """A single detected display/compute device."""
    index: int
    name: str
    vendor: str                       # "NVIDIA" | "Intel" | "AMD" | "Unknown"
    is_discrete: bool
    total_vram_mb: float = 0.0
    used_vram_mb: float = 0.0
    free_vram_mb: float = 0.0
    driver_version: str = ""
    is_nvidia_cuda_candidate: bool = False
    is_vulkan_candidate: bool = False
    info_source: str = ""             # where the data came from
    reliability: str = "UNKNOWN"      # CONFIRMED | PROBABLE | UNKNOWN

    @property
    def free_vram_gb(self) -> float:
        return self.free_vram_mb / 1024.0


@dataclass
class MemoryBudget:
    """Result of a dynamic VRAM budget computation."""
    total_vram_mb: float
    free_vram_mb: float
    reserve_mb: float
    configured_fraction: float
    candidate_from_free_mb: float
    safe_free_limit_mb: float
    total_limit_mb: float
    selected_budget_mb: float
    remaining_for_system_mb: float
    usable: bool                      # False => GPU cannot be used under this policy
    reason: str = ""
