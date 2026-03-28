"""
Config Core - Environment-based configuration management.

Provides environment variable and secrets management
following the Phenotype hand-roll rules.

Example usage:
    from config_core import BaseConfig, ConfigResolver, ConfigValidator, SchemaField

    # Simple environment-based config
    class AppConfig(BaseConfig):
        _env_prefix = "APP"

        def __init__(self):
            self.port = self.get_int("PORT", default=8080)
            self.debug = self.get_bool("DEBUG", default=False)

    config = AppConfig.from_env()

    # Hierarchical config resolution
    resolver = ConfigResolver(
        base_defaults={"debug": False},
        env="production",
        prefix="APP"
    )
    config = (
        resolver
        .load_file("config.json")
        .override_from_env()
        .resolve()
    )

    # Schema-based validation
    schema = ConfigSchema.from_dict({
        'port': {'type': int, 'required': True, 'min_value': 1},
        'debug': {'type': bool, 'default': False},
    })
    validated = schema.validate({'port': 8080})
"""

from .base_config import (
    BaseConfig,
    ConfigError,
    RequiredConfigMissingError,
    ConfigTypeError,
    Secret,
    DatabaseConfig,
    RedisConfig,
)
from .resolver import (
    ConfigResolver,
    EnvironmentConfigResolver,
    ResolutionError,
    ConfigSource,
)
from .validation import (
    ConfigSchema,
    SchemaField,
    ValidationError,
    is_url,
    is_email,
    is_port,
    is_positive,
    is_non_negative,
)

# Re-export for backwards compatibility
from .loader import BaseConfigLoader

__all__ = [
    # Base config
    "BaseConfig",
    "BaseConfigLoader",
    "ConfigError",
    "RequiredConfigMissingError",
    "ConfigTypeError",
    "Secret",
    "DatabaseConfig",
    "RedisConfig",
    # Resolver
    "ConfigResolver",
    "EnvironmentConfigResolver",
    "ResolutionError",
    "ConfigSource",
    # Validation
    "ConfigSchema",
    "SchemaField",
    "ValidationError",
    # Validators
    "is_url",
    "is_email",
    "is_port",
    "is_positive",
    "is_non_negative",
]

__version__ = "0.1.0"
