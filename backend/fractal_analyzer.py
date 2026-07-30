# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek

"""
fractal_analyzer.py — Mathematical Fractal Dimension ($D_b$), $R^2$, Entropy, and Lacunarity Analyzer.
Calculates linear least squares log-log regression across grid levels.
"""

from __future__ import annotations
import math
from typing import List, Dict, Any
import numpy as np

from backend.intersection_cpu import CPULevelResult


class FractalAnalysisResult:
    """Contains overall fractal analysis results, Db, R^2, and level statistics."""
    def __init__(
        self,
        fractal_dimension_db: float,
        r2_score: float,
        level_results: List[CPULevelResult],
        scaling_levels_used: List[int]
    ):
        self.fractal_dimension_db = fractal_dimension_db
        self.r2_score = r2_score
        self.level_results = level_results
        self.scaling_levels_used = scaling_levels_used

    def to_dict(self) -> Dict[str, Any]:
        return {
            'fractal_dimension_db': round(self.fractal_dimension_db, 4),
            'r2_score': round(self.r2_score, 4),
            'scaling_levels_used': self.scaling_levels_used,
            'levels': [res.to_dict() for res in self.level_results]
        }


def compute_fractal_dimension(
    level_results: List[CPULevelResult],
    selected_levels: List[int] = None
) -> FractalAnalysisResult:
    """
    Computes linear regression slope Db = d(log N) / d(log 1/eps) and R^2 score.
    """
    if not level_results:
        return FractalAnalysisResult(0.0, 0.0, [], [])

    # Filter levels if specific selection is requested
    if selected_levels:
        target_results = [r for r in level_results if r.level.level_idx in selected_levels]
    else:
        target_results = level_results

    # Collect log(1/eps) and log(N_filled)
    x_vals: List[float] = []
    y_vals: List[float] = []
    used_indices: List[int] = []

    for r in target_results:
        if r.filled_count > 0 and r.level.log_inv_epsilon >= 0:
            x_vals.append(r.level.log_inv_epsilon)
            y_vals.append(math.log(r.filled_count))
            used_indices.append(r.level.level_idx)

    if len(x_vals) < 2:
        return FractalAnalysisResult(0.0, 0.0, level_results, used_indices)

    x = np.array(x_vals, dtype=np.float64)
    y = np.array(y_vals, dtype=np.float64)

    # Linear regression y = m*x + c
    A = np.vstack([x, np.ones(len(x))]).T
    m, c = np.linalg.lstsq(A, y, rcond=None)[0]

    # R^2 fit
    y_pred = m * x + c
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    if ss_tot > 0:
        r2 = 1.0 - (ss_res / ss_tot)
    else:
        # Zero variance: all log(N) values are identical (e.g. constant fill counts).
        # Return NaN to signal a degenerate fit rather than overstating quality.
        import math as _math
        r2 = _math.nan

    return FractalAnalysisResult(float(m), float(r2), level_results, used_indices)
