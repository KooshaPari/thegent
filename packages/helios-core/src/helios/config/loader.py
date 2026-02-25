"""Configuration loader and validators"""

import os
import yaml
import toml
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from helios.models.config import BenchmarkConfig, GlobalSettings, EnvironmentConfig


class ConfigLoader:
    """Load and parse configuration files"""
    
    @staticmethod
    def load_yaml(path: Path | str) -> dict[str, Any]:
        """Load YAML config file"""
        with open(path) as f:
            return yaml.safe_load(f) or {}
    
    @staticmethod
    def load_toml(path: Path | str) -> dict[str, Any]:
        """Load TOML config file"""
        with open(path) as f:
            return toml.load(f)
    
    @staticmethod
    def load(path: Path | str) -> dict[str, Any]:
        """Auto-detect format and load config file"""
        path = Path(path)
        suffix = path.suffix.lower()
        
        if suffix in (".yaml", ".yml"):
            return ConfigLoader.load_yaml(path)
        elif suffix == ".toml":
            return ConfigLoader.load_toml(path)
        else:
            raise ValueError(f"Unsupported config format: {suffix}")
    
    @staticmethod
    def load_benchmark(path: Path | str) -> BenchmarkConfig:
        """Load and validate benchmark config"""
        data = ConfigLoader.load(path)
        return BenchmarkConfig(**data)
    
    @staticmethod
    def load_global(path: Path | str | None = None) -> GlobalSettings:
        """Load global settings"""
        if path:
            data = ConfigLoader.load(path)
            return GlobalSettings(**data)
        
        # Try default locations
        default_paths = [
            Path.home() / ".helios" / "config.yaml",
            Path.home() / ".helios" / "config.toml",
            Path.cwd() / "helios.yaml",
            Path.cwd() / "helios.toml",
        ]
        
        for p in default_paths:
            if p.exists():
                data = ConfigLoader.load(p)
                return GlobalSettings(**data)
        
        # Return defaults
        return GlobalSettings()


class ConfigValidator:
    """Validate configuration"""
    
    @staticmethod
    def validate_benchmark(config: BenchmarkConfig) -> list[str]:
        """Validate benchmark config, return list of errors"""
        errors = []
        
        # Validate environment
        if config.environment.cpus < 1:
            errors.append("CPUs must be >= 1")
        
        if config.environment.memory_mb < 512:
            errors.append("Memory must be >= 512MB")
        
        if config.environment.timeout_sec < 60:
            errors.append("Timeout must be >= 60 seconds")
        
        # Validate task
        if not config.task.dataset:
            errors.append("Dataset is required")
        
        # Validate agent
        if not config.agent.name:
            errors.append("Agent name is required")
        
        return errors
    
    @staticmethod
    def validate_env_vars(env_vars: dict[str, str]) -> list[str]:
        """Validate environment variables"""
        errors = []
        
        # Check for required API keys
        if "OPENAI_API_KEY" in env_vars and not env_vars["OPENAI_API_KEY"]:
            errors.append("OPENAI_API_KEY is empty")
        
        return errors


def merge_configs(*configs: dict[str, Any]) -> dict[str, Any]:
    """Merge multiple config dicts (later ones override)"""
    result = {}
    for config in configs:
        for key, value in config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_configs(result[key], value)
            else:
                result[key] = value
    return result


def get_env_with_prefix(prefix: str) -> dict[str, str]:
    """Get environment variables with a prefix"""
    return {
        key[len(prefix):]: value
        for key, value in os.environ.items()
        if key.startswith(prefix)
    }
