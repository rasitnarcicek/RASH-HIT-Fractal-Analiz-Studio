# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""Runtime configuration for the compute layer (Stage 2).

Defines the default memory policy constants and the mapping between
MemoryProfile enum values and the fraction of FREE VRAM they consume.
No hardware access happens here.
"""
from __future__ import annotations

from typing import Dict
from backend.compute.backend_types import MemoryProfile

# Default dynamic memory policy (Stage 2 baseline; tuned later in Stage 4).
DEFAULT_CONFIGURED_FRACTION = 0.60       # AUTOMATIC profile
DEFAULT_MAXIMUM_TOTAL_FRACTION = 0.80    # hard cap on total VRAM
DEFAULT_MINIMUM_BUDGET_MB = 512          # below this => GPU deemed unusable

# Per-profile fraction of FREE VRAM.
PROFILE_FRACTIONS: Dict[MemoryProfile, float] = {
    MemoryProfile.SAFE: 0.50,
    MemoryProfile.AUTOMATIC: 0.60,
    MemoryProfile.PERFORMANCE: 0.75,
    MemoryProfile.CUSTOM: 0.60,          # overridden by caller when CUSTOM
}

# Reserve policy by total VRAM (GB).
#   total <= 6 GB        -> 1024 MB
#   6 < total <= 12 GB   -> 1536 MB
#   total > 12 GB        -> 2048 MB
RESERVE_TIERS = [
    (6.0, 1024),
    (12.0, 1536),
    (float("inf"), 2048),
]


def reserve_for_total_vram(total_vram_mb: float) -> float:
    """Return the minimum safety reserve in MB for a given total VRAM."""
    total_gb = total_vram_mb / 1024.0
    for upper_gb, reserve_mb in RESERVE_TIERS:
        if total_gb <= upper_gb:
            return float(reserve_mb)
    return 2048.0


def fraction_for_profile(profile: MemoryProfile, custom_fraction: float = 0.60) -> float:
    """Resolve the free-VRAM fraction for a profile (CUSTOM uses custom_fraction)."""
    if profile is MemoryProfile.CUSTOM:
        return custom_fraction
    return PROFILE_FRACTIONS[profile]
