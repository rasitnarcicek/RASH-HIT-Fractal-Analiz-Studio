# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""Device scanner (Stage 2, read-only diagnostics).

Enumerates OS, CPU, RAM and all display/compute devices. For NVIDIA devices
it prefers nvidia-ml-py (NVML), then falls back to a safe ``nvidia-smi`` query,
then to Windows hardware info. No command is ever run with ``shell=True`` and
every subprocess has a timeout. A missing command is reported, never fatal.

Personal user paths are never written into diagnostic output.
"""
from __future__ import annotations

import os
import subprocess
import sys
from typing import List, Optional

from backend.compute.backend_types import GPUDevice
from backend.compute.exceptions import DeviceScanError


def _run(args: List[str], timeout: float = 8.0) -> Optional[str]:
    """Run a command (no shell). Return stdout text or None on any failure."""
    try:
        proc = subprocess.run(
            args, capture_output=True, text=True, timeout=timeout,
            creationflags=0x08000000,  # CREATE_NO_WINDOW
        )
        if proc.returncode != 0:
            return None
        return proc.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None


def scan_os() -> dict:
    import platform
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "python_bits": "64" if sys.maxsize > 2**32 else "32",
    }


def scan_cpu() -> dict:
    import os
    name = "Unknown"
    physical = 0
    logical = 0
    if sys.platform == "win32":
        # Robust: ask PowerShell for a JSON object, parse it in Python.
        txt = _run(["powershell", "-NoProfile", "-Command",
                    "(Get-CimInstance Win32_Processor | "
                    "Select-Object Name,NumberOfCores,NumberOfLogicalProcessors | "
                    "ConvertTo-Json -Compress)"])
        if txt:
            try:
                import json
                obj = json.loads(txt.strip().splitlines()[-1])
                if isinstance(obj, dict):
                    obj = [obj]
                first = obj[0]
                name = (first.get("Name") or "Unknown").split("\n")[0]
                physical = int(first.get("NumberOfCores") or 0)
                logical = int(first.get("NumberOfLogicalProcessors") or 0)
            except Exception:
                pass
    if logical == 0:
        logical = os.cpu_count() or 0
    if physical == 0:
        # Best-effort: assume hyperthreading 2x on consumer parts.
        physical = max(1, logical // 2) if logical else 0
    return {
        "name": name,
        "physical_cores": physical,
        "logical_processors": logical,
    }


def scan_ram() -> dict:
    total = 0
    free = 0
    if sys.platform == "win32":
        txt = _run(["powershell", "-NoProfile", "-Command",
                    "(Get-CimInstance Win32_OperatingSystem | "
                    "Select-Object TotalVisibleMemorySize,FreePhysicalMemory | "
                    "ConvertTo-Json -Compress)"])
        if txt:
            try:
                import json
                obj = json.loads(txt.strip().splitlines()[-1])
                # Values are in KB.
                total = int(obj.get("TotalVisibleMemorySize") or 0) * 1024
                free = int(obj.get("FreePhysicalMemory") or 0) * 1024
            except Exception:
                pass
    return {
        "total_bytes": total,
        "free_bytes": free,
        "total_gb": round(total / (1024**3), 2) if total else 0.0,
        "free_gb": round(free / (1024**3), 2) if free else 0.0,
    }


def _nvidia_smi_query() -> Optional[dict]:
    """Parse `nvidia-smi --query-gpu` into a dict of lists (or None)."""
    out = _run([
        "nvidia-smi", "--query-gpu=index,name,driver_version,memory.total,memory.used,memory.free",
        "--format=csv,noheader,nounits",
    ])
    if not out:
        return None
    rows = []
    for line in out.strip().splitlines():
        parts = [p.strip() for p in line.split(',')]
        if len(parts) < 6:
            continue
        try:
            rows.append({
                "index": int(parts[0]),
                "name": parts[1],
                "driver": parts[2],
                "total_mb": float(parts[3]),
                "used_mb": float(parts[4]),
                "free_mb": float(parts[5]),
            })
        except ValueError:
            continue
    return {"rows": rows} if rows else None


def _nvml_query() -> Optional[dict]:
    """Try nvidia-ml-py (pynvml) for authoritative VRAM. Returns dict or None."""
    try:
        import pynvml  # nvidia-ml-py
    except Exception:
        return None
    try:
        pynvml.nvmlInit()
        try:
            count = pynvml.nvmlDeviceGetCount()
            rows = []
            for i in range(count):
                h = pynvml.nvmlDeviceGetHandleByIndex(i)
                mem = pynvml.nvmlDeviceGetMemoryInfo(h)
                name = pynvml.nvmlDeviceGetName(h)
                try:
                    drv = pynvml.nvmlSystemGetDriverVersion()
                except Exception:
                    drv = ""
                rows.append({
                    "index": i,
                    "name": name,
                    "driver": drv,
                    "total_mb": mem.total / (1024**2),
                    "used_mb": mem.used / (1024**2),
                    "free_mb": mem.free / (1024**2),
                })
            return {"rows": rows, "source": "nvml"}
        finally:
            pynvml.nvmlShutdown()
    except Exception:
        return None


def scan_gpus() -> List[GPUDevice]:
    """Enumerate all display/compute devices (multi-GPU aware)."""
    devices: List[GPUDevice] = []

    # 1) NVIDIA: NVML preferred, then nvidia-smi, then Windows CIM.
    nvml = _nvml_query()
    smi = _nvidia_smi_query()
    nvidia_rows = (nvml or smi or {}).get("rows", [])
    nvidia_source = (nvml or smi or {}).get("source", "nvidia-smi")

    for r in nvidia_rows:
        total = r["total_mb"]
        free = r["free_mb"]
        devices.append(GPUDevice(
            index=r["index"], name=r["name"], vendor="NVIDIA",
            is_discrete=True,
            total_vram_mb=total, used_vram_mb=r["used_mb"], free_vram_mb=free,
            driver_version=r.get("driver", ""),
            is_nvidia_cuda_candidate=True,
            is_vulkan_candidate=True,
            info_source=nvidia_source, reliability="CONFIRMED",
        ))

    # 2) Windows CIM for non-NVIDIA / integrated GPUs (Intel/AMD).
    cim_rows = _windows_video_controllers()
    nvidia_names = {d.name for d in devices}
    for c in cim_rows:
        if c["name"] in nvidia_names:
            continue  # already captured via NVML/SMI
        vendor = _guess_vendor(c["name"])
        total_mb = c.get("adapter_ram_mb", 0.0) or 0.0
        devices.append(GPUDevice(
            index=len(devices), name=c["name"], vendor=vendor,
            is_discrete=(vendor == "NVIDIA" or vendor == "AMD"),
            total_vram_mb=total_mb,
            used_vram_mb=0.0, free_vram_mb=total_mb,
            driver_version=c.get("driver", ""),
            is_nvidia_cuda_candidate=(vendor == "NVIDIA"),
            is_vulkan_candidate=(vendor in ("NVIDIA", "Intel", "AMD")),
            info_source="Win32_VideoController", reliability="PROBABLE",
        ))
    return devices


def _windows_video_controllers() -> List[dict]:
    txt = _run(["powershell", "-NoProfile", "-Command",
                "Get-CimInstance Win32_VideoController | "
                "Select-Object Name,AdapterRAM,DriverVersion | ConvertTo-Json"])
    rows = []
    if not txt:
        return rows
    txt = txt.strip()
    if txt.startswith('['):
        import json
        try:
            arr = json.loads(txt)
        except Exception:
            return rows
    else:
        import json
        try:
            arr = [json.loads(txt)]
        except Exception:
            return rows
    for item in arr:
        rows.append({
            "name": item.get("Name", ""),
            "adapter_ram_mb": (item.get("AdapterRAM") or 0) / (1024**2),
            "driver": item.get("DriverVersion", ""),
        })
    return rows


def _guess_vendor(name: str) -> str:
    n = (name or "").lower()
    if "nvidia" in n:
        return "NVIDIA"
    if "intel" in n:
        return "Intel"
    if "amd" in n or "radeon" in n:
        return "AMD"
    return "Unknown"


def scan_environment() -> dict:
    """Full environment scan used by diagnostics."""
    return {
        "os": scan_os(),
        "cpu": scan_cpu(),
        "ram": scan_ram(),
        "gpus": [d.__dict__ for d in scan_gpus()],
        "nvidia_smi_available": _run(["nvidia-smi", "-L"]) is not None,
        "nvcc_available": _run(["nvcc", "--version"]) is not None,
        "cuda_toolkit_path": _env("CUDA_PATH"),
    }


def _env(key: str) -> str:
    import os
    return os.environ.get(key, "")
