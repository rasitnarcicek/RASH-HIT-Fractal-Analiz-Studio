# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""Dynamic GPU memory budget policy (Stage 2).

No fixed GB amounts. The budget is derived from the device's CURRENT free
VRAM each time an analysis is about to start (re-measured at the last
moment — see ``compute_budget`` ``measure_free_vram_mb`` hook).

Formula (mirrors the project spec):

    candidate_from_free = free_vram * configured_fraction
    safe_free_limit    = max(0, free_vram - reserve_vram)
    total_limit        = total_vram * maximum_total_fraction
    selected_budget    = min(candidate_from_free, safe_free_limit, total_limit)

If selected_budget < minimum_budget_mb => usable = False (GPU not usable
under this policy; the caller must fall back to CPU).
"""
from __future__ import annotations

from typing import Callable, Optional

from backend.compute.backend_types import MemoryBudget, MemoryProfile
from backend.compute.exceptions import MemoryPolicyError
from backend.compute.runtime_config import (
    DEFAULT_CONFIGURED_FRACTION,
    DEFAULT_MAXIMUM_TOTAL_FRACTION,
    DEFAULT_MINIMUM_BUDGET_MB,
    fraction_for_profile,
    reserve_for_total_vram,
)


def _clamp_fraction(fraction: float) -> float:
    if not (0.0 < fraction <= 0.85):
        raise MemoryPolicyError(
            f"configured_fraction must be in (0, 0.85], got {fraction!r}"
        )
    return fraction


def compute_budget(
    total_vram_mb: float,
    free_vram_mb: float,
    profile: MemoryProfile = MemoryProfile.AUTOMATIC,
    custom_fraction: float = DEFAULT_CONFIGURED_FRACTION,
    maximum_total_fraction: float = DEFAULT_MAXIMUM_TOTAL_FRACTION,
    minimum_budget_mb: float = DEFAULT_MINIMUM_BUDGET_MB,
    measure_free_vram_mb: Optional[Callable[[], float]] = None,
) -> MemoryBudget:
    """Compute the dynamic VRAM budget for a single device.

    ``measure_free_vram_mb`` is an optional callable returning the *current*
    free VRAM in MB. When provided, free_vram_mb is re-measured at call time
    (supports 're-measure immediately before analysis starts').
    """
    if total_vram_mb <= 0:
        raise MemoryPolicyError("total_vram_mb must be > 0")
    if free_vram_mb < 0:
        raise MemoryPolicyError("free_vram_mb must be >= 0")

    if measure_free_vram_mb is not None:
        try:
            free_vram_mb = float(measure_free_vram_mb())
        except Exception as exc:  # noqa: BLE001 — surface as policy error, do not crash caller
            raise MemoryPolicyError(f"free VRAM re-measure failed: {exc}") from exc

    if maximum_total_fraction <= 0 or maximum_total_fraction > 1.0:
        raise MemoryPolicyError(
            f"maximum_total_fraction must be in (0, 1], got {maximum_total_fraction!r}"
        )

    fraction = _clamp_fraction(fraction_for_profile(profile, custom_fraction))
    reserve_mb = reserve_for_total_vram(total_vram_mb)

    candidate_from_free_mb = free_vram_mb * fraction
    safe_free_limit_mb = max(0.0, free_vram_mb - reserve_mb)
    total_limit_mb = total_vram_mb * maximum_total_fraction
    selected = min(candidate_from_free_mb, safe_free_limit_mb, total_limit_mb)

    usable = selected >= minimum_budget_mb
    reason = "" if usable else (
        f"selected budget {selected:.0f} MB < minimum {minimum_budget_mb:.0f} MB"
    )

    remaining = max(0.0, free_vram_mb - selected)
    return MemoryBudget(
        total_vram_mb=total_vram_mb,
        free_vram_mb=free_vram_mb,
        reserve_mb=reserve_mb,
        configured_fraction=fraction,
        candidate_from_free_mb=candidate_from_free_mb,
        safe_free_limit_mb=safe_free_limit_mb,
        total_limit_mb=total_limit_mb,
        selected_budget_mb=selected,
        remaining_for_system_mb=remaining,
        usable=usable,
        reason=reason,
    )


def budget_for_fractions(
    total_vram_mb: float,
    free_vram_mb: float,
    fractions=(0.50, 0.60, 0.70),
) -> dict:
    """Helper used by diagnostics: report budgets at 50/60/70% of free VRAM."""
    out = {}
    for f in fractions:
        try:
            b = compute_budget(
                total_vram_mb, free_vram_mb,
                profile=MemoryProfile.CUSTOM, custom_fraction=f,
            )
            out[f] = b
        except MemoryPolicyError as exc:
            out[f] = None
    return out
