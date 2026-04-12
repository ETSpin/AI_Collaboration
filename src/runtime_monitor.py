"""
Class: RuntimeMonitor
Author: MORS
Date: 4 APR 26

Description:
Provides system-level telemetry for the running environment, including GPU, VRAM,
CPU, and memory usage. This class is responsible for querying the underlying
operating system and hardware to expose real-time resource metrics that can be
used by the application, REPL, or future GUI components.

Responsibilities:
- Report current GPU utilization (if available)
- Report current GPU VRAM usage (if available)
- Report current CPU utilization
- Report current system memory usage
- Provide a clean, stateless interface for system telemetry
- Avoid any model-specific or context-specific logic
"""

import subprocess

import psutil

""" 
try:
    import GPUtil
except ImportError:
    GPUtil = None
 """

class RuntimeMonitor:

    # Return CPU usage percentage
    @staticmethod
    def get_cpu_usage():
        return psutil.cpu_percent(interval=0.1)

    # Return CPU usage percentage
    @staticmethod
    def get_memory_usage():
        mem = psutil.virtual_memory()
        return {
            "total": mem.total,
            "used": mem.used,
            "percent": mem.percent
        }

    # Return GPU utilization percentage, or None if unavailable
    @staticmethod
    def get_gpu_usage():
        data = RuntimeMonitor._run_nvidia_smi()
        if data is None:
            return None
        gpu_util, _, _ = data
        return gpu_util

    # Return the total VRAM on the current system
    @staticmethod
    def get_vram_total():
        data = RuntimeMonitor._run_nvidia_smi()
        if data is None:
            return None
        _, _, mem_total = data
        return mem_total
    
    # Return the available VRAM on the current system
    @staticmethod
    def get_vram_available():
        data = RuntimeMonitor._run_nvidia_smi()
        if data is None:
            return None
        _, mem_used, mem_total = data
        mem_avail = mem_total-mem_used
        return mem_avail

    # Return VRAM usage statistics, or None if unavailable
    @staticmethod
    def get_vram_usage():
        data = RuntimeMonitor._run_nvidia_smi()
        if data is None:
            return None

        _, mem_used, mem_total = data
        percent = (mem_used / mem_total) * 100 if mem_total > 0 else 0

        return {
            "total": mem_total,
            "used": mem_used,
            "free": mem_total - mem_used,
            "percent": percent
        }
    
    # Internal helper to run nvidia-smi and return parsed values - returns None if nvidia-smi is not available or fails
    @staticmethod
    def _run_nvidia_smi():
        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=utilization.gpu,memory.used,memory.total",
                    "--format=csv,noheader,nounits"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=1.0
            )

            if result.returncode != 0:
                return None

            # Expected output: "12, 2048, 8192"
            parts = result.stdout.strip().split(",")
            if len(parts) != 3:
                return None

            gpu_util = float(parts[0].strip())
            mem_used = float(parts[1].strip())
            mem_total = float(parts[2].strip())

            return gpu_util, mem_used, mem_total

        except Exception:
            return None
