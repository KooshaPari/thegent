"""Configuration models"""

from pydantic import BaseModel, Field
from typing import Literal, Any
from pydantic_settings import BaseSettings


class EnvironmentConfig(BaseModel):
    """Environment configuration"""
    type: Literal["docker", "daytona", "local", "modal"] = "docker"
    image: str | None = None
    cpus: int = 1
    memory_mb: int = 2048
    timeout_sec: int = 600
    gpu: bool = False
    allow_internet: bool = True


class AgentConfig(BaseModel):
    """Agent configuration"""
    name: str
    version: str | None = None
    model: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)


class TaskConfig(BaseModel):
    """Task configuration"""
    dataset: str
    subset: str | None = None
    max_instances: int | None = None
    seed: int | None = None


class EvaluationConfig(BaseModel):
    """Evaluation configuration"""
    metrics: list[str] = Field(default_factory=lambda: ["speed", "quality", "cost"])
    checkers: list[dict] = Field(default_factory=list)
    timeout_sec: int = 600


class BenchmarkConfig(BaseModel):
    """Full benchmark configuration"""
    environment: EnvironmentConfig
    agent: AgentConfig
    task: TaskConfig
    evaluation: EvaluationConfig


class GlobalSettings(BaseSettings):
    """Global CLI settings"""
    registry_url: str = "https://registry.helios.ai"
    storage_path: str = "~/.helios/storage"
    cache_dir: str = "~/.helios/cache"
    log_level: str = "INFO"
    
    # Provider settings
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_api_key: str | None = None
    
    # Daytona
    daytona_api_key: str | None = None
    
    class Config:
        env_prefix = "HELIOS_"
