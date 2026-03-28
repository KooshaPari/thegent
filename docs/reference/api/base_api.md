# base API Reference

> **Source**: `src/thegent/integrations/base.py`

Base classes and utilities for integrations.

Provides standard patterns for:
- Configuration loading
- Status tracking
- Enable/disable toggles
- Feature flags

---

## BaseIntegration

Base class for integrations with standard lifecycle.

**Inherits from**: `ABC`

### Methods

#### BaseIntegration.__init__

```python
__init__(self: Any, name: str, config: Any)
```

---

#### BaseIntegration.check_available

```python
check_available(self: Any)
```

Check if integration is available.

---

#### BaseIntegration.connect

```python
connect(self: Any)
```

Connect to integration.

---

#### BaseIntegration.disable

```python
disable(self: Any)
```

Disable integration.

---

#### BaseIntegration.disconnect

```python
disconnect(self: Any)
```

Disconnect from integration.

---

#### BaseIntegration.enable

```python
enable(self: Any)
```

Enable integration.

---

#### BaseIntegration.enabled

```python
enabled(self: Any)
```

Whether integration is enabled.

---

#### BaseIntegration.error

```python
error(self: Any)
```

Last error message, if any.

---

#### BaseIntegration.get_info

```python
get_info(self: Any)
```

Get integration metadata.

---

#### BaseIntegration.status

```python
status(self: Any)
```

Current integration status.

---

---

## DataclassConfig

Base dataclass config with env loading support.

Inherit from this for dataclass-based configs:
    @dataclass
    class MyConfig(DataclassConfig):
        base_url: str = "http://localhost"
        api_key: str = ""

### Methods

#### DataclassConfig.from_env

```python
from_env(cls: Any, prefix: str)
```

Load config from environment variables.

---

---

## FeatureFlag

Simple feature flag with environment variable support.

Usage:
    FLAG = FeatureFlag("MY_FEATURE", default=False)

    if FLAG.enabled:
        ...

### Methods

#### FeatureFlag.__init__

```python
__init__(self: Any, name: str, default: bool, env_prefix: str)
```

---

#### FeatureFlag.enabled

```python
enabled(self: Any)
```

Check if feature is enabled via environment variable.

---

---

## FeatureRegistry

Registry for all feature flags.

### Methods

#### FeatureRegistry.all_enabled

```python
all_enabled(cls: Any)
```

---

#### FeatureRegistry.get

```python
get(cls: Any, name: str)
```

---

#### FeatureRegistry.register

```python
register(cls: Any, flag: FeatureFlag)
```

---

---

## IntegrationInfo

Basic integration metadata.

---

## IntegrationStatus

Standard integration status values.

**Inherits from**: `StrEnum`

---

## SerializableMixin

Mixin providing to_dict/from_dict for dataclasses.

Automatically handles:
- Enum values → serialized as .value
- datetime objects → serialized as .isoformat()
- Path objects → serialized as str()
- Nested SerializableMixin objects → .to_dict()
- Nested dicts/lists → recursive serialization

Usage:
    @dataclass
    class MyModel(SerializableMixin):
        name: str
        value: int = 0

    m = MyModel(name="test", value=42)
    d = m.to_dict()  # {"name": "test", "value": 42}
    m2 = MyModel.from_dict(d)  # MyModel(name="test", value=42)

### Methods

#### SerializableMixin.copy

```python
copy(self: Any)
```

Create a shallow copy with optional field overrides.

**Parameters**:

- `**overrides`: Field values to override in the copy

**Returns**: New instance with copied values and any overrides applied

---

#### SerializableMixin.diff

```python
diff(self: Any, other: SerializableMixin)
```

Compare this instance with another and return field differences.

**Parameters**:

- `other`: Another instance to compare with

**Returns**: Dict mapping field names to (self_value, other_value) tuples
for fields that differ. Empty dict if instances are equal.

---

#### SerializableMixin.from_dict

```python
from_dict(cls: Any, data: dict[(str, Any)])
```

Create instance from dictionary with type-aware deserialization.

Automatically converts:
- ISO strings → datetime (when field type is datetime)
- Strings → Path (when field type is Path)
- Values → Enum (when field type is Enum)
- Dicts → nested SerializableMixin (when field type is SerializableMixin subclass)

---

#### SerializableMixin.from_json

```python
from_json(cls: Any, json_str: str)
```

Create instance from JSON string.

**Parameters**:

- `json_str`: JSON string to parse

**Returns**: New instance from parsed JSON

---

#### SerializableMixin.from_json_file

```python
from_json_file(cls: Any, path: Any)
```

Create instance from JSON file.

**Parameters**:

- `path`: File path to read

**Returns**: New instance from parsed JSON file

---

#### SerializableMixin.merge

```python
merge(self: Any, other: SerializableMixin)
```

Merge fields from another instance into a new instance.

**Parameters**:

- `other`: Instance to merge from
- `overwrite`: If True (default), other's non-None values overwrite self's.
If False, only fill in None fields from other.

**Returns**: New merged instance

---

#### SerializableMixin.patch

```python
patch(self: Any)
```

Apply updates to create a new instance (alias for copy).

More explicit name for the copy operation when making targeted changes.

**Parameters**:

- `**updates`: Field values to update

**Returns**: New instance with updates applied

---

#### SerializableMixin.to_dict

```python
to_dict(self: Any)
```

Convert to dictionary with automatic type serialization.

---

#### SerializableMixin.to_json

```python
to_json(self: Any)
```

Serialize instance to JSON string.

**Parameters**:

- `indent`: JSON indentation level (None for compact)
- `sort_keys`: Whether to sort dictionary keys

**Returns**: JSON string representation

---

#### SerializableMixin.to_json_file

```python
to_json_file(self: Any, path: Any)
```

Write instance to JSON file.

**Parameters**:

- `path`: File path to write
- `indent`: JSON indentation level (default: 2 for readability)

---

---

## SingletonMixin

Thread-safe singleton mixin for classes.

Provides a consistent singleton pattern with:
- Thread-safe initialization (double-checked locking)
- Lazy instantiation
- Reset capability for testing

Usage:
    class MyService(SingletonMixin):
        def __init__(self, config: str = "default"):
            self.config = config

    # Get singleton instance
    service = MyService.get_instance()

    # Get with custom args (only used on first call)
    service = MyService.get_instance(config="custom")

    # Reset for testing
    MyService.reset_instance()

Note:
    - First call to get_instance() creates the instance
    - Subsequent calls return the same instance
    - Args passed after first call are ignored
    - Use reset_instance() to clear for testing

### Methods

#### SingletonMixin.get_instance

```python
get_instance(cls: Any)
```

Get the singleton instance, creating it if necessary.

**Parameters**:

- `*args`: Positional arguments for __init__ (only used on first call)
- `**kwargs`: Keyword arguments for __init__ (only used on first call)

**Returns**: The singleton instance

---

#### SingletonMixin.has_instance

```python
has_instance(cls: Any)
```

Check if an instance exists.

---

#### SingletonMixin.reset_instance

```python
reset_instance(cls: Any)
```

Reset the singleton instance.

Useful for testing to get a fresh instance.
Warning: Not thread-safe during reset.

---

---

## _Missing

Sentinel for missing values.

### Methods

---

## all_enabled

```python
all_enabled(cls: Any) -> dict[(str, bool)]
```

---

## check_available

```python
check_available(self: Any)
```

Check if integration is available.

---

## connect

```python
connect(self: Any)
```

Connect to integration.

---

## copy

```python
copy(self: Any)
```

Create a shallow copy with optional field overrides.

**Parameters**:

- `**overrides`: Field values to override in the copy

**Returns**: New instance with copied values and any overrides applied

**Examples**:

```python
p1 = Person(name="Alice", age=30)
p2 = p1.copy(age=35)  # Person(name="Alice", age=35)
```

---

## diff

```python
diff(self: Any, other: SerializableMixin)
```

Compare this instance with another and return field differences.

**Parameters**:

- `other`: Another instance to compare with

**Returns**: Dict mapping field names to (self_value, other_value) tuples
for fields that differ. Empty dict if instances are equal.

**Examples**:

```python
p1 = Person(name="Alice", age=30)
p2 = Person(name="Alice", age=35)
diff = p1.diff(p2)  # {"age": (30, 35)}
```

---

## disable

```python
disable(self: Any)
```

Disable integration.

---

## disconnect

```python
disconnect(self: Any)
```

Disconnect from integration.

---

## enable

```python
enable(self: Any)
```

Enable integration.

---

## enabled

```python
enabled(self: Any)
```

Whether integration is enabled.

---

## error

```python
error(self: Any)
```

Last error message, if any.

---

## feature

```python
feature(name: str, default: bool)
```

Create and register a feature flag.

---

## from_dict

```python
from_dict(cls: Any, data: dict[(str, Any)])
```

Create instance from dictionary with type-aware deserialization.

Automatically converts:
- ISO strings → datetime (when field type is datetime)
- Strings → Path (when field type is Path)
- Values → Enum (when field type is Enum)
- Dicts → nested SerializableMixin (when field type is SerializableMixin subclass)

---

## from_env

```python
from_env(cls: Any, prefix: str)
```

Load config from environment variables.

---

## from_json

```python
from_json(cls: Any, json_str: str)
```

Create instance from JSON string.

**Parameters**:

- `json_str`: JSON string to parse

**Returns**: New instance from parsed JSON

**Raises**:

- `json.JSONDecodeError`: If JSON is invalid

**Examples**:

```python
person = Person.from_json('{"name": "Alice", "age": 30}')
```

---

## from_json_file

```python
from_json_file(cls: Any, path: Any)
```

Create instance from JSON file.

**Parameters**:

- `path`: File path to read

**Returns**: New instance from parsed JSON file

**Raises**:

- `FileNotFoundError`: If file doesn't exist
- `json.JSONDecodeError`: If JSON is invalid

---

## get

```python
get(cls: Any, name: str) -> Any
```

---

## get_info

```python
get_info(self: Any)
```

Get integration metadata.

---

## get_instance

```python
get_instance(cls: Any)
```

Get the singleton instance, creating it if necessary.

**Parameters**:

- `*args`: Positional arguments for __init__ (only used on first call)
- `**kwargs`: Keyword arguments for __init__ (only used on first call)

**Returns**: The singleton instance

---

## has_instance

```python
has_instance(cls: Any)
```

Check if an instance exists.

---

## hashable_dataclass

```python
hashable_dataclass(cls: type)
```

Decorator to make a dataclass hashable using SerializableMixin hash.

Also restores the SerializableMixin __repr__ for cleaner output.

Usage:
    @hashable_dataclass
    @dataclass
    class MyModel(SerializableMixin):
        name: str
        value: int = 0

Or:
    @dataclass
    @hashable_dataclass
    class MyModel(SerializableMixin):
        name: str
        value: int = 0

---

## load_env_config

```python
load_env_config(prefix: str, defaults: Any)
```

Load configuration from environment variables with prefix.

**Parameters**:

- `prefix`: Environment variable prefix (e.g., "MYAPP_")
- `defaults`: Default values for config keys

**Returns**: Dict with config values from env (with type conversion)

---

## load_file_config

```python
load_file_config(path: Any, defaults: Any)
```

Load configuration from JSON or YAML file.

**Parameters**:

- `path`: Path to config file (.json, .yaml, .yml)
- `defaults`: Default values

**Returns**: Merged config dict

---

## merge

```python
merge(self: Any, other: SerializableMixin)
```

Merge fields from another instance into a new instance.

**Parameters**:

- `other`: Instance to merge from
- `overwrite`: If True (default), other's non-None values overwrite self's.
If False, only fill in None fields from other.

**Returns**: New merged instance

**Examples**:

```python
p1 = Person(name="Alice", age=None, city="NYC")
p2 = Person(name="Bob", age=30, city=None)
merged = p1.merge(p2)  # Person(name="Bob", age=30, city="NYC")
merged = p1.merge(p2, overwrite=False)  # Person(name="Alice", age=30, city="NYC")
```

---

## patch

```python
patch(self: Any)
```

Apply updates to create a new instance (alias for copy).

More explicit name for the copy operation when making targeted changes.

**Parameters**:

- `**updates`: Field values to update

**Returns**: New instance with updates applied

---

## register

```python
register(cls: Any, flag: FeatureFlag) -> None
```

---

## reset_instance

```python
reset_instance(cls: Any)
```

Reset the singleton instance.

Useful for testing to get a fresh instance.
Warning: Not thread-safe during reset.

---

## status

```python
status(self: Any)
```

Current integration status.

---

## to_dict

```python
to_dict(self: Any)
```

Convert to dictionary with automatic type serialization.

---

## to_json

```python
to_json(self: Any)
```

Serialize instance to JSON string.

**Parameters**:

- `indent`: JSON indentation level (None for compact)
- `sort_keys`: Whether to sort dictionary keys

**Returns**: JSON string representation

**Examples**:

```python
person.to_json()  # '{"name": "Alice", "age": 30}'
person.to_json(indent=2)  # Pretty-printed
```

---

## to_json_file

```python
to_json_file(self: Any, path: Any)
```

Write instance to JSON file.

**Parameters**:

- `path`: File path to write
- `indent`: JSON indentation level (default: 2 for readability)

---

