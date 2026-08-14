# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""Tests for the dynamic GPU memory budget policy (Stage 2)."""
import pytest
from backend.compute.backend_types import MemoryProfile
from backend.compute.memory_policy import compute_budget
from backend.compute.exceptions import MemoryPolicyError


def test_4gb_total_3gb_free():
    b = compute_budget(4096.0, 3072.0, profile=MemoryProfile.AUTOMATIC)
    # reserve 1024 (<=6GB tier); candidate=3072*0.6=1843.2; safe=3072-1024=2048;
    # total_limit=4096*0.8=3276.8 -> selected=min=1843.2
    assert b.selected_budget_mb == pytest.approx(1843.2, abs=0.1)
    assert b.usable is True


def test_6gb_total_6gb_free():
    b = compute_budget(6144.0, 6144.0, profile=MemoryProfile.AUTOMATIC)
    # candidate=6144*0.6=3686.4; safe=6144-1024=5120; total=4915.2
    assert b.selected_budget_mb == pytest.approx(3686.4, abs=0.1)
    assert b.usable is True


def test_8gb_total_4gb_free():
    b = compute_budget(8192.0, 4096.0, profile=MemoryProfile.AUTOMATIC)
    # reserve 1536 (6-12GB tier); candidate=4096*0.6=2457.6; safe=4096-1536=2560; total=6553.6
    assert b.selected_budget_mb == pytest.approx(2457.6, abs=0.1)
    assert b.usable is True


def test_12gb_total_10gb_free():
    b = compute_budget(12288.0, 10240.0, profile=MemoryProfile.AUTOMATIC)
    # reserve 1536; candidate=10240*0.6=6144; safe=10240-1536=8704; total=9830.4
    assert b.selected_budget_mb == pytest.approx(6144.0, abs=0.1)
    assert b.usable is True


def test_16gb_total_14gb_free():
    b = compute_budget(16384.0, 14336.0, profile=MemoryProfile.AUTOMATIC)
    # reserve 2048 (>12GB tier); candidate=14336*0.6=8601.6; safe=14336-2048=12288; total=13107.2
    assert b.selected_budget_mb == pytest.approx(8601.6, abs=0.1)
    assert b.usable is True


def test_24gb_total_7gb_free():
    b = compute_budget(24576.0, 7168.0, profile=MemoryProfile.AUTOMATIC)
    # reserve 2048; candidate=7168*0.6=4300.8; safe=7168-2048=5120; total=19660.8
    assert b.selected_budget_mb == pytest.approx(4300.8, abs=0.1)
    assert b.usable is True


def test_free_less_than_reserve_unusable():
    # 4GB total, only 512 MB free -> reserve 1024 means safe_limit negative,
    # candidate=512*0.6=307.2 < 512 min budget => unusable
    b = compute_budget(4096.0, 512.0, profile=MemoryProfile.AUTOMATIC)
    assert b.usable is False
    assert b.selected_budget_mb < 512.0


def test_invalid_fraction_raises():
    with pytest.raises(MemoryPolicyError):
        compute_budget(6144.0, 6144.0, profile=MemoryProfile.CUSTOM, custom_fraction=0.9)
    with pytest.raises(MemoryPolicyError):
        compute_budget(6144.0, 6144.0, profile=MemoryProfile.CUSTOM, custom_fraction=0.0)


def test_memory_info_unreadable_raises():
    def boom():
        raise RuntimeError("cannot read VRAM")
    with pytest.raises(MemoryPolicyError):
        compute_budget(6144.0, 6144.0, measure_free_vram_mb=boom)


def test_profiles_differ():
    total, free = 6144.0, 6144.0
    safe = compute_budget(total, free, profile=MemoryProfile.SAFE)
    auto = compute_budget(total, free, profile=MemoryProfile.AUTOMATIC)
    perf = compute_budget(total, free, profile=MemoryProfile.PERFORMANCE)
    assert safe.selected_budget_mb < auto.selected_budget_mb < perf.selected_budget_mb
