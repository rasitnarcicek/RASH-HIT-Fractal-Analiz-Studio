# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""
confidence.py - Academic confidence score computation and motif complexity profiler.
Evaluates regression R2, valid scale counts, SVG health score, and generates a humble motif profile.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class ConfidenceAssessment:
    score: float  # 0.0 to 100.0
    label: str  # "High" / "Moderate" / "Low"
    scale_quality: str  # "Good" / "Insufficient" / "Limited"
    svg_suitability: str  # "High" / "Moderate" / "Low"
    academic_comment: str
    recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": round(self.score, 1),
            "label": self.label,
            "scale_quality": self.scale_quality,
            "svg_suitability": self.svg_suitability,
            "academic_comment": self.academic_comment,
            "recommendation": self.recommendation,
        }


@dataclass
class MotifProfile:
    motif: str
    db: float
    complexity_class: str  # "Very High" / "High" / "Moderate" / "Low"
    linear_density: str  # "High" / "Moderate" / "Sparse"
    space_fill_balance: str  # "Balanced" / "Dense" / "Sparse"
    scale_consistency: str  # "High" / "Moderate" / "Low"
    academic_note: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "motif": self.motif,
            "db": round(self.db, 4),
            "complexity_class": self.complexity_class,
            "linear_density": self.linear_density,
            "space_fill_balance": self.space_fill_balance,
            "scale_consistency": self.scale_consistency,
            "academic_note": self.academic_note,
        }


def evaluate_confidence(
    db: float,
    r2: float,
    valid_scales: int,
    svg_suitability_score: float,
    total_shape_elements: int,
) -> ConfidenceAssessment:
    """Computes overall scientific confidence score and academic guidance."""
    base = 0.0

    # R2 weight (40%)
    if r2 >= 0.99:
        base += 40.0
    elif r2 >= 0.95:
        base += 32.0
    elif r2 >= 0.90:
        base += 24.0
    else:
        base += (r2 / 0.90) * 20.0

    # Valid scale count weight (30%)
    if valid_scales >= 7:
        base += 30.0
    elif valid_scales >= 5:
        base += 22.0
    elif valid_scales >= 3:
        base += 15.0
    else:
        base += 5.0

    # SVG Health weight (30%)
    base += (min(100.0, svg_suitability_score) / 100.0) * 30.0

    score = max(0.0, min(100.0, base))

    if score >= 80.0 and r2 >= 0.95:
        label = "High"
        scale_qual = "Good"
        svg_suit = "High"
        comm = f"High log-log regression fit (R² = {r2:.4f}). The result is suitable for academic reporting."
        recom = "The result can be included directly in an academic publication."
    elif score >= 60.0 and r2 >= 0.85:
        label = "Moderate"
        scale_qual = "Acceptable"
        svg_suit = "Moderate"
        comm = f"Moderate regression fit (R² = {r2:.4f}). The scale range is acceptable."
        recom = "Validation with a more precise mode (precise/academic) is recommended."
    else:
        label = "Low"
        scale_qual = "Insufficient / Limited"
        svg_suit = "Low"
        comm = f"R² = {r2:.4f} or the number of valid scales ({valid_scales}) may be insufficient."
        recom = "The motif scale range may be insufficient or the SVG structure too simple."

    return ConfidenceAssessment(
        score=score,
        label=label,
        scale_quality=scale_qual,
        svg_suitability=svg_suit,
        academic_comment=comm,
        recommendation=recom,
    )


def generate_motif_profile(
    motif_name: str,
    db: float,
    r2: float,
    total_elements: int,
    avg_occupancy_pct: float,
) -> MotifProfile:
    """Generates a humble, objective motif complexity profile."""
    if db >= 1.65:
        comp_cls = "Very High"
    elif db >= 1.45:
        comp_cls = "High"
    elif db >= 1.25:
        comp_cls = "Moderate"
    else:
        comp_cls = "Low"

    if total_elements > 200:
        lin_den = "High"
    elif total_elements > 40:
        lin_den = "Moderate"
    else:
        lin_den = "Sparse"

    if avg_occupancy_pct >= 60.0:
        space_bal = "Dense"
    elif avg_occupancy_pct >= 30.0:
        space_bal = "Balanced"
    else:
        space_bal = "Sparse"

    if r2 >= 0.98:
        scale_cons = "High"
    elif r2 >= 0.90:
        scale_cons = "Moderate"
    else:
        scale_cons = "Low"

    note = (
        f"Motif ({motif_name}), with fractal dimension {db:.4f} and %{avg_occupancy_pct:.1f} average occupancy, is "
        f"evaluated in the {comp_cls.lower()} complexity class. "
        f"Hierarchical consistency across scales is at a {scale_cons.lower()} level."
    )

    return MotifProfile(
        motif=motif_name,
        db=db,
        complexity_class=comp_cls,
        linear_density=lin_den,
        space_fill_balance=space_bal,
        scale_consistency=scale_cons,
        academic_note=note,
    )
