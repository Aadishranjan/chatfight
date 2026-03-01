# Copyright (c) 2026 Aadish Ranjan

import asyncio
import os
import shutil
import time


def _format_uptime(seconds: float) -> str:
    total = int(max(seconds, 0))
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    return f"{hours}h:{minutes}m:{secs}s"


def _read_cpu_snapshot():
    with open("/proc/stat", "r", encoding="utf-8") as f:
        cpu = f.readline().strip().split()
    values = [int(v) for v in cpu[1:]]
    idle = values[3] + values[4] if len(values) > 4 else values[3]
    total = sum(values)
    return total, idle


async def _cpu_percent_linux() -> float:
    try:
        total_1, idle_1 = _read_cpu_snapshot()
        await asyncio.sleep(0.2)
        total_2, idle_2 = _read_cpu_snapshot()
        total_delta = total_2 - total_1
        idle_delta = idle_2 - idle_1
        if total_delta <= 0:
            return 0.0
        used = total_delta - idle_delta
        return max(0.0, min(100.0, (used / total_delta) * 100.0))
    except Exception:
        try:
            load_1m = os.getloadavg()[0]
            cpus = os.cpu_count() or 1
            return max(0.0, min(100.0, (load_1m / cpus) * 100.0))
        except Exception:
            return 0.0


def _memory_percent_linux() -> float:
    try:
        data = {}
        with open("/proc/meminfo", "r", encoding="utf-8") as f:
            for line in f:
                key, value = line.split(":", 1)
                data[key] = int(value.strip().split()[0])
        total = data.get("MemTotal", 0)
        available = data.get("MemAvailable", 0)
        if total <= 0:
            return 0.0
        used = total - available
        return max(0.0, min(100.0, (used / total) * 100.0))
    except Exception:
        return 0.0


def _disk_percent() -> float:
    try:
        usage = shutil.disk_usage("/")
        if usage.total <= 0:
            return 0.0
        return (usage.used / usage.total) * 100.0
    except Exception:
        return 0.0


def _uptime_seconds() -> float:
    try:
        with open("/proc/uptime", "r", encoding="utf-8") as f:
            return float(f.readline().split()[0])
    except Exception:
        return time.monotonic()


async def collect_system_stats() -> dict:
    cpu = await _cpu_percent_linux()
    ram = _memory_percent_linux()
    disk = _disk_percent()
    uptime = _format_uptime(_uptime_seconds())
    return {
        "uptime": uptime,
        "cpu_percent": round(cpu, 1),
        "ram_percent": round(ram, 1),
        "disk_percent": round(disk, 1),
    }
