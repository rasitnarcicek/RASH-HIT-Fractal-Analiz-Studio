# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""Diagnostics aggregation (Stage 2).

Produces a safe, human-readable terminal report and a JSON file. Personal user
paths are stripped. This module does NOT perform any GPU compute — it only
summarises what device_scanner / memory_policy report.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from backend.compute import device_scanner
from backend.compute.backend_types import MemoryProfile
from backend.compute.memory_policy import budget_for_fractions, compute_budget


def _strip_paths(obj):
    """Recursively replace any string containing a user home path with '<home>'."""
    import os
    home = os.path.expanduser("~")
    if isinstance(obj, dict):
        return {k: _strip_paths(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_strip_paths(v) for v in obj]
    if isinstance(obj, str) and home in obj:
        return obj.replace(home, "<home>")
    return obj


def build_report() -> dict:
    env = device_scanner.scan_environment()
    gpus = [device_scanner.GPUDevice(**g) if isinstance(g, dict) else g for g in env["gpus"]]

    nvidia = [g for g in gpus if g.vendor == "NVIDIA"]
    # Default memory examples on the primary NVIDIA device (if any).
    mem_examples = {}
    total = 6144.0
    free = 6144.0
    if nvidia:
        total = nvidia[0].total_vram_mb
        free = nvidia[0].free_vram_mb
    for frac, b in budget_for_fractions(total, free).items():
        if b is None:
            mem_examples[frac] = None
        else:
            mem_examples[frac] = {
                "free_vram_mb": round(b.free_vram_mb, 1),
                "reserve_mb": round(b.reserve_mb, 1),
                "selected_budget_mb": round(b.selected_budget_mb, 1),
                "remaining_for_system_mb": round(b.remaining_for_system_mb, 1),
            }

    report = {
        "os": env["os"],
        "cpu": env["cpu"],
        "ram": env["ram"],
        "gpus": [g.__dict__ for g in gpus],
        "nvidia_smi_available": env["nvidia_smi_available"],
        "nvcc_available": env["nvcc_available"],
        "cuda_toolkit_path": env["cuda_toolkit_path"],
        "memory_examples_50_60_70": mem_examples,
    }
    return report


def print_report(report: dict) -> None:
    r = report
    print("=" * 64)
    print("RASH-HIT Fractal Studio — Compute Environment Diagnostics")
    print("=" * 64)
    print(f"OS      : {r['os'].get('system')} {r['os'].get('release')} ({r['os'].get('machine')})")
    print(f"Python  : {r['os'].get('python_version')} ({r['os'].get('python_bits')}-bit)")
    print(f"CPU     : {r['cpu'].get('name')} | "
          f"cores={r['cpu'].get('physical_cores')} logical={r['cpu'].get('logical_processors')}")
    print(f"RAM     : total={r['ram'].get('total_gb')} GB free={r['ram'].get('free_gb')} GB")
    print("-" * 64)
    print(f"NVIDIA-SMI available : {r['nvidia_smi_available']}")
    print(f"nvcc available       : {r['nvcc_available']}")
    print(f"CUDA_PATH            : {r['cuda_toolkit_path'] or '(unset)'}")
    print("-" * 64)
    for g in r["gpus"]:
        print(f"GPU[{g.get('index')}] {g.get('name')} ({g.get('vendor')})")
        print(f"    total={g.get('total_vram_mb'):.0f} MB "
              f"free={g.get('free_vram_mb'):.0f} MB "
              f"driver={g.get('driver_version')}")
        print(f"    CUDA candidate={g.get('is_nvidia_cuda_candidate')} "
              f"Vulkan candidate={g.get('is_vulkan_candidate')} "
              f"src={g.get('info_source')}")
    print("-" * 64)
    for frac, ex in r["memory_examples_50_60_70"].items():
        if ex is None:
            print(f"Memory {int(frac*100)}%: (unavailable)")
            continue
        print(f"Memory {int(frac*100)}%: budget={ex['selected_budget_mb']:.1f} MB "
              f"(free={ex['free_vram_mb']:.0f}, reserve={ex['reserve_mb']:.0f}, "
              f"remaining={ex['remaining_for_system_mb']:.0f})")
    print("=" * 64)


def write_json(report: dict, path: str = "diagnostics/compute_environment.json") -> str:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    safe = _strip_paths(report)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(safe, f, indent=2, ensure_ascii=False)
    return path
