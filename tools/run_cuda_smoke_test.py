#!/usr/bin/env python
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""tools/run_cuda_smoke_test.py

Stage 2.8/2.9 — runs the CUDA and CPU Taichi smoke tests in SEPARATE Python
subprocesses (one per backend) so a CUDA crash cannot take down the caller.
A failed CUDA process is captured as a non-zero exit + JSON error; the harness
continues.

Usage:
    python tools/run_cuda_smoke_test.py
Exit code: 0 if at least CPU smoke passed (CUDA optional), else 1.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def _run_backend(backend: str, dtype: str) -> dict:
    code = (
        "import sys, json\n"
        "from backend.gpu.smoke_kernel import run_smoke\n"
        f"r = run_smoke({backend!r}, dtype={dtype!r})\n"
        "print(json.dumps(r.__dict__, default=str))\n"
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            cwd=str(ROOT), capture_output=True, text=True, timeout=300,
            creationflags=0x08000000,
        )
    except subprocess.TimeoutExpired:
        return {"backend": backend, "ok": False, "error": "timeout (>300s)"}
    if proc.returncode != 0:
        tail = proc.stderr.strip().splitlines()[-5:]
        return {"backend": backend, "ok": False,
                "error": "process failed", "stderr": "\n".join(tail)}
    try:
        return json.loads(proc.stdout.strip().splitlines()[-1])
    except Exception:
        return {"backend": backend, "ok": False, "error": "no json output",
                "stdout": proc.stdout[-500:]}


def main() -> int:
    print("=" * 64)
    print("RASH-HIT Fractal Studio — CUDA/CPU Smoke Test (Stage 2)")
    print("=" * 64)
    results = {}
    for backend in ("cpu", "cuda"):
        print(f"\n>>> Running {backend} smoke test (int32) ...")
        r = _run_backend(backend, "int32")
        results[backend] = r
        if r.get("ok"):
            print(f"    OK   matches_reference={r.get('matches_reference')} "
                  f"first={r.get('first_call_ms'):.1f}ms "
                  f"hot_mean={r.get('hot_mean_ms'):.3f}ms "
                  f"hot_min={r.get('hot_min_ms'):.3f}ms "
                  f"hot_max={r.get('hot_max_ms'):.3f}ms")
        else:
            print(f"    FAIL {r.get('error')}")
            if r.get("stderr"):
                print("    " + r["stderr"].replace("\n", "\n    "))

    # int64 micro-test (functional support only, not a science decision)
    print("\n>>> int64 micro-test (cpu) ...")
    r64 = _run_backend("cpu", "int64")
    if r64.get("ok"):
        print(f"    int64 cpu OK matches_reference={r64.get('matches_reference')} "
              f"hot_mean={r64.get('hot_mean_ms'):.3f}ms")
    else:
        print(f"    int64 cpu FAIL {r64.get('error')}")

    Path("diagnostics").mkdir(exist_ok=True)
    with open("diagnostics/smoke_results.json", "w", encoding="utf-8") as f:
        json.dump({"int32": results, "int64_cpu": r64}, f, indent=2, default=str)

    cpu_ok = results.get("cpu", {}).get("ok", False)
    cuda_ok = results.get("cuda", {}).get("ok", False)
    print("\n" + "=" * 64)
    print(f"SUMMARY: CPU smoke = {'PASS' if cpu_ok else 'FAIL'}; "
          f"CUDA smoke = {'PASS' if cuda_ok else 'FAIL'}")
    print("=" * 64)
    # CPU must pass; CUDA failure is reportable, not fatal for the harness.
    return 0 if cpu_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
