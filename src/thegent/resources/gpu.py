"""GPU utilization monitoring for thegent resource management."""

from __future__ import annotations

import importlib
import subprocess
from dataclasses import dataclass, field
from typing import Any


class GpuMonitorError(Exception):
    """Raised when GPU monitoring fails unexpectedly."""


@dataclass
class GpuInfo:
    """Information about a single GPU device."""

    device_id: int
    name: str
    utilization_pct: float
    memory_used_mb: float
    memory_total_mb: float
    temperature_c: float | None = field(default=None)


def _run_subprocess(args: list[str], timeout: int = 10) -> subprocess.CompletedProcess[str]:
    """Run a subprocess command safely.

    Args:
        args: Command and arguments list.
        timeout: Timeout in seconds.

    Returns:
        CompletedProcess result.
    """
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def _import_pynvml() -> Any:
    """Import pynvml dynamically.

    Returns:
        The pynvml module if available.

    Raises:
        ImportError: If pynvml is not installed.
    """
    return importlib.import_module("pynvml")


class GpuMonitor:
    """Monitors GPU utilization using pynvml or nvidia-smi fallback.

    Tries pynvml (nvidia-ml-py) first for efficiency; falls back to
    parsing ``nvidia-smi --query-gpu`` CSV output if pynvml is absent.
    When no GPU hardware is detected, all methods return empty/zero values
    rather than raising.
    """

    _NVIDIA_SMI_QUERY = (
        "index,name,utilization.gpu,memory.used,memory.total,temperature.gpu"
    )
    _NVIDIA_SMI_FORMAT = "csv,noheader,nounits"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """Return True if GPU monitoring is possible on this machine.

        Checks pynvml first, then falls back to probing nvidia-smi.
        """
        if self._pynvml_available():
            return True
        return self._nvidia_smi_available()

    def get_gpus(self) -> list[GpuInfo]:
        """Return a list of GpuInfo for every detected GPU.

        Tries pynvml first; falls back to nvidia-smi subprocess.
        Returns an empty list when no GPUs are detected or no tooling
        is available — never raises for "no GPU" conditions.

        Raises:
            GpuMonitorError: On unexpected errors during data collection.
        """
        try:
            if self._pynvml_available():
                return self._get_gpus_pynvml()
        except GpuMonitorError:
            raise
        except Exception as exc:
            raise GpuMonitorError(f"pynvml query failed: {exc}") from exc

        try:
            return self._get_gpus_nvidia_smi()
        except GpuMonitorError:
            raise
        except Exception as exc:
            raise GpuMonitorError(f"nvidia-smi query failed: {exc}") from exc

    def get_total_utilization(self) -> float:
        """Return average GPU utilization across all GPUs (0.0 if none)."""
        gpus = self.get_gpus()
        if not gpus:
            return 0.0
        return sum(g.utilization_pct for g in gpus) / len(gpus)

    # ------------------------------------------------------------------
    # Internal helpers - pynvml path
    # ------------------------------------------------------------------

    def _pynvml_available(self) -> bool:
        """Return True if pynvml can be imported and initialised."""
        try:
            pynvml = _import_pynvml()
            pynvml.nvmlInit()
            pynvml.nvmlShutdown()
            return True
        except Exception:
            return False

    def _get_gpus_pynvml(self) -> list[GpuInfo]:
        """Collect GPU info via pynvml (nvidia-ml-py)."""
        pynvml = _import_pynvml()
        pynvml.nvmlInit()
        try:
            count = pynvml.nvmlDeviceGetCount()
            gpus: list[GpuInfo] = []
            for idx in range(count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                name = pynvml.nvmlDeviceGetName(handle)
                if isinstance(name, bytes):
                    name = name.decode("utf-8", errors="replace")
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
                try:
                    temp: float | None = float(
                        pynvml.nvmlDeviceGetTemperature(
                            handle, pynvml.NVML_TEMPERATURE_GPU
                        )
                    )
                except Exception:
                    temp = None
                gpus.append(
                    GpuInfo(
                        device_id=idx,
                        name=name,
                        utilization_pct=float(util.gpu),
                        memory_used_mb=mem.used / 1024 / 1024,
                        memory_total_mb=mem.total / 1024 / 1024,
                        temperature_c=temp,
                    )
                )
            return gpus
        finally:
            pynvml.nvmlShutdown()

    # ------------------------------------------------------------------
    # Internal helpers - nvidia-smi path
    # ------------------------------------------------------------------

    def _nvidia_smi_available(self) -> bool:
        """Return True if nvidia-smi is present and returns exit code 0."""
        try:
            result = _run_subprocess(
                ["nvidia-smi", "--query-gpu=index", "--format=csv,noheader"],
                timeout=5,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            return False

    def _get_gpus_nvidia_smi(self) -> list[GpuInfo]:
        """Collect GPU info by parsing nvidia-smi CSV output."""
        try:
            result = _run_subprocess(
                [
                    "nvidia-smi",
                    f"--query-gpu={self._NVIDIA_SMI_QUERY}",
                    f"--format={self._NVIDIA_SMI_FORMAT}",
                ],
                timeout=10,
            )
        except FileNotFoundError:
            return []
        except subprocess.TimeoutExpired as exc:
            raise GpuMonitorError("nvidia-smi timed out") from exc

        if result.returncode != 0:
            return []

        return self._parse_nvidia_smi_output(result.stdout)

    def _parse_nvidia_smi_output(self, output: str) -> list[GpuInfo]:
        """Parse CSV output from nvidia-smi --query-gpu.

        Expected columns (noheader, nounits):
            index, name, utilization.gpu, memory.used, memory.total,
            temperature.gpu

        Args:
            output: Raw stdout string from nvidia-smi.

        Returns:
            List of GpuInfo, one per non-blank line. Malformed lines are
            skipped.
        """
        gpus: list[GpuInfo] = []
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 5:
                continue
            try:
                device_id = int(parts[0])
                name = parts[1]
                util_pct = float(parts[2])
                mem_used = float(parts[3])
                mem_total = float(parts[4])
                temp: float | None = None
                if len(parts) >= 6 and parts[5] not in ("N/A", "[N/A]", ""):
                    temp = float(parts[5])
                gpus.append(
                    GpuInfo(
                        device_id=device_id,
                        name=name,
                        utilization_pct=util_pct,
                        memory_used_mb=mem_used,
                        memory_total_mb=mem_total,
                        temperature_c=temp,
                    )
                )
            except (ValueError, IndexError):
                continue
        return gpus
