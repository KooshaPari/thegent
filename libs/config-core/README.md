# Config Core

Shared configuration management for the Phenotype ecosystem.

## Modules

- `src/base_config.py` - Base configuration class with environment variable support
- `src/resolver.py` - Hierarchical configuration resolution
- `src/validation.py` - Schema-based configuration validation
- `src/loader.py` - Legacy base loader (for backwards compatibility)

## Usage

### Simple Environment-Based Config

```python
from config_core import BaseConfig

class AppConfig(BaseConfig):
    _env_prefix = "APP"

    def __init__(self):
        self.port = self.get_int("PORT", default=8080)
        self.debug = self.get_bool("DEBUG", default=False)

config = AppConfig.from_env()
```

### Hierarchical Config Resolution

```python
from config_core import ConfigResolver

resolver = ConfigResolver(
    base_defaults={"debug": False},
    env="production",
    prefix="APP"
)
config = (
    resolver
    .load_file("config.json")
    .load_environment({"debug": True})  # environment-specific overrides
    .override_from_env()
    .resolve()
)
```

### Schema-Based Validation

```python
from config_core import ConfigSchema, SchemaField, is_port

class AppConfigSchema(ConfigSchema):
    def __init__(self):
        self.fields = {
            'port': SchemaField(int, required=True, min_value=1, max_value=65535),
            'debug': SchemaField(bool, required=False, default=False),
            'log_level': SchemaField(str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR']),
        }

schema = AppConfigSchema()
validated = schema.validate({'port': 8080})
```

## Standards

- All configs extend `BaseConfig`
- Use type-safe getters (`get_str`, `get_int`, `get_bool`)
- Validate required fields in `validate()` method

## Migration from Inline Config Code

If you have duplicated config code in your repos, migrate like this:

**Before (duplicated pattern):**
```python
# In your_repo/src/config.py
import os

def get_config():
    return {
        "port": int(os.environ.get("APP_PORT", 8080)),
        "debug": os.environ.get("APP_DEBUG", "false").lower() == "true",
    }
```

**After (using lib):**
```python
# In your_repo/src/config.py
# REPLACED: Use libs/config-core instead
# from libs.config_core import BaseConfig, ConfigResolver
```

Then import from `libs.config_core` in your config initialization.

## Integration Points

Consuming repos should import from:
```python
# Import path for consuming repos
from libs.config_core import BaseConfig, ConfigResolver, ConfigSchema
```
