"""Agent interface - Protocol and base classes"""

from typing import Protocol, Any
from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass

from helios.models.agent import AgentInfo, AgentContext, AgentResult


class Agent(Protocol):
    """Any agent must implement this protocol"""
    
    @property
    def info(self) -> AgentInfo:
        """Return agent information"""
        ...
    
    async def setup(self, environment: Any) -> None:
        """Set up the agent in the environment"""
        ...
    
    async def run(
        self,
        instruction: str,
        environment: Any,
        context: AgentContext
    ) -> AgentResult:
        """Run the agent with an instruction"""
        ...


class BaseAgent(ABC):
    """Base class for agents with common functionality"""
    
    SUPPORTS_ATIF: bool = False
    
    def __init__(
        self,
        model_name: str | None = None,
        config: dict[str, Any] | None = None
    ):
        self.model_name = model_name
        self.config = config or {}
    
    @property
    def info(self) -> AgentInfo:
        return AgentInfo(
            name=self.name(),
            version=self.version(),
            model_name=self.model_name,
            model_provider=self._parse_provider(self.model_name)
        )
    
    @staticmethod
    @abstractmethod
    def name() -> str:
        """Return agent name"""
        ...
    
    @abstractmethod
    def version(self) -> str | None:
        """Return agent version"""
        ...
    
    @abstractmethod
    async def setup(self, environment: Any) -> None:
        """Set up the agent"""
        ...
    
    @abstractmethod
    async def run(
        self,
        instruction: str,
        environment: Any,
        context: AgentContext
    ) -> AgentResult:
        """Run the agent"""
        ...
    
    def _parse_provider(self, model_name: str | None) -> str | None:
        if not model_name or "/" not in model_name:
            return None
        return model_name.split("/")[0]


class AgentFactory:
    """Factory for creating agents"""
    
    _agents: dict[str, type[BaseAgent]] = {}
    
    @classmethod
    def register(cls, name: str, agent_class: type[BaseAgent]):
        """Register an agent class"""
        cls._agents[name] = agent_class
    
    @classmethod
    def create(cls, name: str, **kwargs) -> BaseAgent:
        """Create an agent by name"""
        if name not in cls._agents:
            raise KeyError(f"Agent '{name}' not found. Available: {list(cls._agents.keys())}")
        return cls._agents[name](**kwargs)
    
    @classmethod
    def list(cls) -> list[str]:
        """List registered agents"""
        return list(cls._agents.keys())


def register_agent(name: str):
    """Decorator to register an agent"""
    def decorator(agent_class: type[BaseAgent]):
        AgentFactory.register(name, agent_class)
        return agent_class
    return decorator
