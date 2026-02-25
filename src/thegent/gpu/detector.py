"""
GPU Detector

Detects available GPU hardware and capabilities.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class GPUVendor(Enum):
    NVIDIA = "nvidia"
    AMD = "amd"
    APPLE = "apple"
    UNKNOWN = "unknown"


@dataclass
class GPUInfo:
    """Information about a GPU."""
    index: int
    vendor: GPUVendor
    name: str
    memory_total: int  # bytes
    memory_free: int
    compute_capability: Optional[str] = None

    @property
    def memory_gb(self) -> float:
        return self.memory_total / (1024 ** 3)


class GPUDetector:
    """Detects available GPUs."""

    def __init__(self):
        self._gpus: list[GPUInfo] = []
        self._cuda_available = False
        self._metal_available = False
        self._rocm_available = False

    def detect(self) -> list[GPUInfo]:
        """Detect all available GPUs."""
        self._gpus = []

        # Check CUDA
        self._detect_cuda()

        # Check Metal (Apple)
        self._detect_metal()

        # Check ROCm (AMD)
        self._detect_rocm()

        return self._gpus

    def _detect_cuda(self) -> None:
        """Detect NVIDIA CUDA GPUs."""
        try:
            import torch
            if torch.cuda.is_available():
                self._cuda_available = True
                for i in range(torch.cuda.device_count()):
                    props = torch.cuda.get_device_properties(i)
                    self._gpus.append(GPUInfo(
                        index=i,
                        vendor=GPUVendor.NVIDIA,
                        name=props.name,
                        memory_total=props.total_memory,
                        memory_free=torch.cuda.memory_reserved(i),
                        compute_capability=f"{props.major}.{props.minor}"
                    ))
        except ImportError:
            pass

    def _detect_metal(self) -> None:
        """Detect Apple Metal GPUs."""
        try:
            import torch
            if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                self._metal_available = True
                self._gpus.append(GPUInfo(
                    index=0,
                    vendor=GPUVendor.APPLE,
                    name="Apple Metal",
                    memory_total=0,  # Shared memory
                    memory_free=0
                ))
        except ImportError:
            pass

    def _detect_rocm(self) -> None:
        """Detect AMD ROCm GPUs."""
        try:
            import torch
            if hasattr(torch.version, 'hip') and torch.version.hip:
                self._rocm_available = True
                for i in range(torch.cuda.device_count()):  # ROCm uses CUDA API
                    props = torch.cuda.get_device_properties(i)
                    self._gpus.append(GPUInfo(
                        index=i,
                        vendor=GPUVendor.AMD,
                        name=props.name,
                        memory_total=props.total_memory,
                        memory_free=torch.cuda.memory_reserved(i)
                    ))
        except ImportError:
            pass

    @property
    def has_gpu(self) -> bool:
        return len(self._gpus) > 0

    @property
    def best_gpu(self) -> Optional[GPUInfo]:
        if not self._gpus:
            return None
        return max(self._gpus, key=lambda g: g.memory_total)

    def summary(self) -> dict:
        return {
            "has_gpu": self.has_gpu,
            "cuda": self._cuda_available,
            "metal": self._metal_available,
            "rocm": self._rocm_available,
            "gpu_count": len(self._gpus),
            "gpus": [
                {"name": g.name, "memory_gb": g.memory_gb, "vendor": g.vendor.value}
                for g in self._gpus
            ]
        }
