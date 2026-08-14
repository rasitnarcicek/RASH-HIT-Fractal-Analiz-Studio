# RASH-HIT Fractal Studio — GPU Infrastructure Setup (Stage 2)

This document records the Stage 2 scope: dependency compatibility, hardware
discovery, dynamic VRAM policy and a minimal Taichi CUDA/CPU smoke test.

## Scope of Stage 2 (what is NOT done yet)

- No production GPU analysis engine.
- No SVG-to-GPU kernel, segment traversal, polygon-fill kernel, or quadtree
  GPU kernel.
- `backend.processor.AnalysisProcessor` is untouched; `--engine` still accepts
  only `cpu` in the CLI.
- Web interface backend selection is NOT added yet.

## Installed GPU research dependencies (`requirements-gpu.txt`)

Installed **only into the project `.venv`** (never global / Hermes venv):

- `taichi==1.7.4`
- `psutil`
- `pytest-benchmark`
- `nvidia-ml-py` (NVML for authoritative VRAM)

NumPy (2.4.6) and pytest (9.1.1) already existed; Taichi 1.7.4's
`--dry-run` confirmed it does **not** require changing them.

## Hardware discovery (`backend/compute/device_scanner.py`)

Enumerates OS, CPU, RAM and all display/compute devices. For NVIDIA it prefers
`nvidia-ml-py` (NVML), then `nvidia-smi`, then Windows `Win32_VideoController`.
No command uses `shell=True`; every subprocess has a timeout; a missing command
is reported, never fatal.

## Dynamic VRAM policy (`backend/compute/memory_policy.py`)

No fixed GB. Budget derived from the device's CURRENT free VRAM:

```
candidate_from_free = free_vram * configured_fraction
safe_free_limit    = max(0, free_vram - reserve_vram)
total_limit        = total_vram * maximum_total_fraction   # default 0.80
selected_budget    = min(candidate_from_free, safe_free_limit, total_limit)
```

Defaults: `configured_fraction=0.60`, `maximum_total_fraction=0.80`,
`minimum_budget_mb=512`. Reserve by total VRAM: ≤6 GB → 1024 MB; 6–12 GB →
1536 MB; >12 GB → 2048 MB. If `selected_budget < minimum_budget_mb` the GPU is
deemed unusable and the caller must fall back to CPU.

Free VRAM is re-measurable at analysis start via the
`measure_free_vram_mb` hook.

## Smoke test (`backend/gpu/smoke_kernel.py`)

Trivial, deterministic integer kernel (NOT a fractal kernel):

```
out[i] = (a[i] * 3 + b[i]) % modulus      # int32 -> mod 1024, int64 -> mod 4096
```

- Run CPU and CUDA backends in **separate subprocesses** (so a CUDA crash
  cannot take down the harness).
- Each must match a NumPy CPU reference byte-for-byte.
- Cold (JIT) call timed separately from ≥10 hot repeats; mean/min/max/median
  reported.

## Acceptance criteria (Stage 2)

- GPU packages installed only in project `.venv`; `pip check` clean.
- Existing CPU dependencies intact.
- CPU smoke test passes.
- CUDA smoke test passes **or** a clear error report exists (no crash).
- int32 correct; int64 functional support reported.
- All dynamic-memory test cases pass (`tests/compute/test_memory_policy.py`).
- Existing project tests still pass.
- No driver / Toolkit / Visual Studio 2022 changes.
