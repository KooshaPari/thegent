"""Environment abstraction - Base classes for execution environments"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from helios.models.environment import EnvironmentType, ExecResult


class Environment(ABC):
    """Abstract base class for environments"""
    
    type: EnvironmentType
    
    @abstractmethod
    async def start(self, force_build: bool = False) -> None:
        """Start the environment"""
        ...
    
    @abstractmethod
    async def stop(self, delete: bool = True) -> None:
        """Stop the environment"""
        ...
    
    @abstractmethod
    async def upload_file(
        self,
        source: Path | str,
        target: str
    ) -> None:
        """Upload a file to the environment"""
        ...
    
    @abstractmethod
    async def upload_dir(
        self,
        source: Path | str,
        target: str
    ) -> None:
        """Upload a directory to the environment"""
        ...
    
    @abstractmethod
    async def download_file(
        self,
        source: str,
        target: Path | str
    ) -> None:
        """Download a file from the environment"""
        ...
    
    @abstractmethod
    async def download_dir(
        self,
        source: str,
        target: Path | str
    ) -> None:
        """Download a directory from the environment"""
        ...
    
    @abstractmethod
    async def exec(
        self,
        command: str,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
        timeout_sec: int | None = None
    ) -> ExecResult:
        """Execute a command in the environment"""
        ...
    
    @property
    def supports_gpus(self) -> bool:
        """Whether this environment supports GPUs"""
        return False
    
    @property
    def can_disable_internet(self) -> bool:
        """Whether this environment can disable internet"""
        return True


class EnvironmentFactory:
    """Factory for creating environments"""
    
    _environments: dict[EnvironmentType, type[Environment]] = {}
    
    @classmethod
    def register(
        cls,
        env_type: EnvironmentType,
        env_class: type[Environment]
    ):
        """Register an environment class"""
        cls._environments[env_type] = env_class
    
    @classmethod
    def create(
        cls,
        env_type: EnvironmentType,
        **config
    ) -> Environment:
        """Create an environment by type"""
        if env_type not in cls._environments:
            raise KeyError(
                f"Environment type '{env_type.value}' not found. "
                f"Available: {[e.value for e in cls._environments.keys()]}"
            )
        return cls._environments[env_type](**config)
    
    @classmethod
    def list(cls) -> list[EnvironmentType]:
        """List registered environment types"""
        return list(cls._environments.keys())


def register_environment(env_type: EnvironmentType):
    """Decorator to register an environment"""
    def decorator(env_class: type[Environment]):
        EnvironmentFactory.register(env_type, env_class)
        return env_class
    return decorator
