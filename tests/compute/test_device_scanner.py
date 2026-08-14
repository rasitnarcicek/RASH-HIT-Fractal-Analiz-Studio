# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""Tests for device_scanner (Stage 2). These run on any machine; they validate
the scanner does not crash and returns sane structure, not specific hardware."""
import os
import sys

import pytest

from backend.compute import device_scanner


def test_scan_os_returns_expected_keys():
    os_info = device_scanner.scan_os()
    assert os_info["python_version"].startswith("3.")
    assert os_info["python_bits"] in ("32", "64")


def test_scan_cpu_returns_counts():
    cpu = device_scanner.scan_cpu()
    assert cpu["logical_processors"] >= 1
    assert isinstance(cpu["name"], str)


def test_scan_ram_returns_gb():
    ram = device_scanner.scan_ram()
    # Either real info, or both zero (environment without WMI); never negative.
    assert ram["total_bytes"] >= 0
    assert ram["free_bytes"] >= 0


def test_scan_gpus_returns_list():
    gpus = device_scanner.scan_gpus()
    assert isinstance(gpus, list)
    for g in gpus:
        assert g.index >= 0
        assert g.vendor in ("NVIDIA", "Intel", "AMD", "Unknown")


def test_scan_environment_full():
    env = device_scanner.scan_environment()
    assert "os" in env and "cpu" in env and "ram" in env and "gpus" in env
    # nvcc availability is machine-specific but must be a bool
    assert isinstance(env["nvcc_available"], bool)
