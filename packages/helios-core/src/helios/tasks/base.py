"""Task system - Task registry and base classes"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
import importlib
import pkgutil

from helios.models.task import TaskMetadata, TaskInput, TaskResources


class Task(ABC):
    """Abstract base class for tasks"""
    
    @property
    @abstractmethod
    def metadata(self) -> TaskMetadata:
        """Return task metadata"""
        ...
    
    @property
    @abstractmethod
    def input(self) -> TaskInput:
        """Return task input"""
        ...
    
    @abstractmethod
    async def load(self, instance_id: str) -> None:
        """Load a specific instance of the task"""
        ...
    
    @abstractmethod
    async def validate(self) -> bool:
        """Validate task configuration"""
        ...


class TaskRegistry:
    """Registry of all available tasks"""
    
    _tasks: dict[str, type[Task]] = {}
    
    @classmethod
    def register(cls, name: str, task_class: type[Task]):
        """Register a task class"""
        cls._tasks[name] = task_class
    
    @classmethod
    def get(cls, name: str) -> type[Task]:
        """Get a task class by name"""
        if name not in cls._tasks:
            raise KeyError(f"Task '{name}' not found. Available: {list(cls._tasks.keys())}")
        return cls._tasks[name]
    
    @classmethod
    def list(cls) -> list[str]:
        """List all registered task names"""
        return list(cls._tasks.keys())
    
    @classmethod
    def unregister(cls, name: str):
        """Unregister a task"""
        del cls._tasks[name]


def register_task(name: str):
    """Decorator to register a task class"""
    def decorator(task_class: type[Task]):
        TaskRegistry.register(name, task_class)
        return task_class
    return decorator


# Auto-discovery of tasks
def discover_tasks(package_name: str):
    """Auto-discover tasks from a package"""
    try:
        package = importlib.import_module(package_name)
        for _, name, _ in pkgutil.iter_modules(package.__path__):
            importlib.import_module(f"{package_name}.{name}")
    except ImportError:
        pass
