"""Benchmark definitions - Base classes and registry"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from helios.models.task import TaskMetadata, TaskInput, TaskResources


@dataclass
class BenchmarkMetadata:
    """Metadata about a benchmark"""
    name: str
    description: str
    version: str
    task_count: int
    categories: list[str] = field(default_factory=list)
    url: str | None = None


class Benchmark(ABC):
    """Abstract base class for benchmarks"""
    
    @property
    @abstractmethod
    def metadata(self) -> BenchmarkMetadata:
        """Return benchmark metadata"""
        ...
    
    @abstractmethod
    def get_task(self, instance_id: str) -> tuple[TaskMetadata, TaskInput]:
        """Get a specific task by instance ID"""
        ...
    
    @abstractmethod
    def list_instances(self) -> list[str]:
        """List all available instance IDs"""
        ...


class BenchmarkRegistry:
    """Registry of all available benchmarks"""
    
    _benchmarks: dict[str, type[Benchmark]] = {}
    
    @classmethod
    def register(cls, name: str, benchmark_class: type[Benchmark]):
        """Register a benchmark class"""
        cls._benchmarks[name] = benchmark_class
    
    @classmethod
    def get(cls, name: str) -> type[Benchmark]:
        """Get a benchmark class by name"""
        if name not in cls._benchmarks:
            raise KeyError(f"Benchmark '{name}' not found. Available: {list(cls._benchmarks.keys())}")
        return cls._benchmarks[name]
    
    @classmethod
    def list(cls) -> list[str]:
        """List all registered benchmark names"""
        return list(cls._benchmarks.keys())


def register_benchmark(name: str):
    """Decorator to register a benchmark"""
    def decorator(benchmark_class: type[Benchmark]):
        BenchmarkRegistry.register(name, benchmark_class)
        return benchmark_class
    return decorator
