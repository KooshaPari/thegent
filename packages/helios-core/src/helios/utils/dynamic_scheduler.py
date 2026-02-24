"""Dynamic parallelization scheduler - Resource-aware job scheduling"""

import os
import subprocess
import multiprocessing
from dataclasses import dataclass
from typing import Optional


@dataclass
class SystemResources:
    """Available system resources"""
    cpu_cores: int
    cpu_cores_available: int
    memory_total_gb: float
    memory_available_gb: float
    docker_max_containers: int
    docker_running_containers: int


@dataclass
class TaskRequirements:
    """Per-task resource requirements"""
    cpus: int = 1
    memory_mb: int = 2048
    disk_mb: int = 10240


class ResourceDetector:
    """Detect available system resources"""
    
    @staticmethod
    def get_cpu_info() -> tuple[int, int]:
        """Get total and available CPU cores"""
        total = multiprocessing.cpu_count()
        available = max(1, total - 2)  # Reserve 2 for OS
        return total, available
    
    @staticmethod
    def get_memory_info() -> tuple[float, float]:
        """Get total and available memory in GB"""
        try:
            result = subprocess.run(
                ["sysctl", "-n", "hw.memsize"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                total_bytes = int(result.stdout.strip())
                total_gb = total_bytes / (1024**3)
                available_gb = total_gb * 0.5
                return total_gb, available_gb
        except:
            pass
        
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        total_kb = int(line.split()[1])
                        total_gb = total_kb / (1024**2)
                    elif line.startswith("MemAvailable:"):
                        avail_kb = int(line.split()[1])
                        avail_gb = avail_kb / (1024**2)
                        return total_gb, avail_gb
        except:
            pass
        
        return 16.0, 8.0  # Fallback
    
    @staticmethod
    def get_docker_info() -> tuple[int, int]:
        """Get Docker max and running container counts"""
        max_containers = 10
        
        try:
            result = subprocess.run(
                ["docker", "info", "--format", "{{.NCPU}}"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                max_containers = int(result.stdout.strip()) * 2
        except:
            pass
        
        try:
            result = subprocess.run(
                ["docker", "ps", "-q"],
                capture_output=True,
                text=True
            )
            running = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
        except:
            running = 0
        
        return max_containers, running
    
    @classmethod
    def detect(cls) -> SystemResources:
        """Detect all system resources"""
        total_cores, avail_cores = cls.get_cpu_info()
        total_mem, avail_mem = cls.get_memory_info()
        max_containers, running = cls.get_docker_info()
        
        return SystemResources(
            cpu_cores=total_cores,
            cpu_cores_available=avail_cores,
            memory_total_gb=total_mem,
            memory_available_gb=avail_mem,
            docker_max_containers=max_containers,
            docker_running_containers=running
        )


class DynamicScheduler:
    """Calculate optimal parallel job count"""
    
    def __init__(
        self,
        task_req: Optional[TaskRequirements] = None,
        safety_margin: float = 0.7
    ):
        self.task_req = task_req or TaskRequirements()
        self.safety_margin = safety_margin
    
    def calculate(self) -> int:
        """Calculate optimal parallel job count"""
        resources = ResourceDetector.detect()
        
        # Calculate based on different constraints
        cpu_jobs = int(
            resources.cpu_cores_available * self.safety_margin / self.task_req.cpus
        )
        
        mem_jobs = int(
            resources.memory_available_gb * 1024 * self.safety_margin / self.task_req.memory_mb
        )
        
        docker_slots = resources.docker_max_containers - resources.docker_running_containers
        docker_jobs = int(docker_slots * self.safety_margin)
        
        # Take minimum of all constraints
        min_jobs = min(cpu_jobs, mem_jobs, docker_jobs)
        
        return max(1, min_jobs)
    
    def calculate_simple(self) -> int:
        """Simple calculation without Docker constraint"""
        resources = ResourceDetector.detect()
        
        cpu_jobs = int(
            resources.cpu_cores_available * self.safety_margin / self.task_req.cpus
        )
        mem_jobs = int(
            resources.memory_available_gb * 1024 * self.safety_margin / self.task_req.memory_mb
        )
        
        return max(1, min(cpu_jobs, mem_jobs))
