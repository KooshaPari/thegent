"""
Configuration Validation with Schema Support.

Provides declarative validation for configuration values.
"""

from typing import Any, Callable, Optional, TypeVar, Generic
from dataclasses import dataclass, field


class ValidationError(Exception):
    """Raised when configuration validation fails."""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation error for '{field}': {message}")

    def __repr__(self) -> str:
        return f"ValidationError(field={self.field!r}, message={self.message!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ValidationError):
            return self.field == other.field and self.message == other.message
        return False


@dataclass
class SchemaField:
    """Defines a configuration field with validation rules.

    Args:
        field_type: Type annotation for the field
        required: Whether the field is required (default: True)
        default: Default value if not required
        validator: Optional validation function
        description: Human-readable description
        choices: Optional list of valid choices
        min_value: Minimum value (for numeric types)
        max_value: Maximum value (for numeric types)
        pattern: Regex pattern (for string types)
        min_length: Minimum length (for string types)
        max_length: Maximum length (for string types)
    """

    field_type: type
    required: bool = True
    default: Any = None
    validator: Optional[Callable[[Any], bool]] = None
    description: str = ""
    choices: Optional[list[Any]] = None
    # Numeric constraints
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    # String constraints
    pattern: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None

    def __post_init__(self) -> None:
        """Compile regex pattern if provided."""
        if self.pattern is not None:
            import re
            self._pattern = re.compile(self.pattern)
        else:
            self._pattern = None

    def validate(self, value: Any, field_name: str) -> list[ValidationError]:
        """Validate a value against this field's rules.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check required
        if value is None:
            if self.required:
                errors.append(ValidationError(field_name, "required field is missing"))
            return errors

        # Check type
        if self.field_type not in (Any, type(None)) and not isinstance(value, self.field_type):
            # Try type coercion
            try:
                if self.field_type == bool and isinstance(value, str):
                    pass  # Special handling for bool strings
                else:
                    value = self.field_type(value)
            except (ValueError, TypeError):
                errors.append(
                    ValidationError(
                        field_name,
                        f"expected {self.field_type.__name__}, got {type(value).__name__}"
                    )
                )
                return errors

        # Check choices
        if self.choices is not None and value not in self.choices:
            errors.append(
                ValidationError(
                    field_name,
                    f"value must be one of {self.choices}, got {value!r}"
                )
            )

        # Numeric constraints
        if isinstance(value, (int, float)) and self.field_type in (int, float):
            if self.min_value is not None and value < self.min_value:
                errors.append(
                    ValidationError(field_name, f"value must be >= {self.min_value}")
                )
            if self.max_value is not None and value > self.max_value:
                errors.append(
                    ValidationError(field_name, f"value must be <= {self.max_value}")
                )

        # String constraints
        if isinstance(value, str):
            if self.min_length is not None and len(value) < self.min_length:
                errors.append(
                    ValidationError(field_name, f"length must be >= {self.min_length}")
                )
            if self.max_length is not None and len(value) > self.max_length:
                errors.append(
                    ValidationError(field_name, f"length must be <= {self.max_length}")
                )
            if self._pattern is not None and not self._pattern.match(value):
                errors.append(
                    ValidationError(field_name, f"value does not match pattern {self.pattern!r}")
                )

        # Custom validator
        if self.validator is not None:
            try:
                if not self.validator(value):
                    errors.append(
                        ValidationError(field_name, "failed custom validation")
                    )
            except Exception as e:
                errors.append(
                    ValidationError(field_name, f"validator raised: {e}")
                )

        return errors


class ConfigSchema:
    """
    Schema-based configuration validator.

    Can be used in two ways:
    1. Subclass and define fields:
        class AppConfigSchema(ConfigSchema):
            def __init__(self):
                self.fields = {
                    'port': SchemaField(int, required=True, min_value=1, max_value=65535),
                    'debug': SchemaField(bool, required=False, default=False),
                }

        schema = AppConfigSchema()
        validated = schema.validate({'port': 8080})

    2. Instantiate directly with add_field():
        schema = ConfigSchema('AppConfig')
        schema.add_field('port', int, required=True, min_value=1, max_value=65535)
        schema.add_field('debug', bool, required=False, default=False)
        validated = schema.validate({'port': 8080})
    """

    def __init__(self, name: str = "ConfigSchema"):
        """Initialize schema with optional name."""
        self._name = name
        self.fields: dict[str, SchemaField] = {}

    def add_field(
        self,
        name: str,
        field_type: type,
        *,
        required: bool = True,
        default: Any = None,
        validator: Optional[Callable[[Any], bool]] = None,
        description: str = "",
        choices: Optional[list[Any]] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        pattern: Optional[str] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
    ) -> "ConfigSchema":
        """Add a field to the schema (fluent interface).

        Returns self for chaining.
        """
        self.fields[name] = SchemaField(
            field_type=field_type,
            required=required,
            default=default,
            validator=validator,
            description=description,
            choices=choices,
            min_value=min_value,
            max_value=max_value,
            pattern=pattern,
            min_length=min_length,
            max_length=max_length,
        )
        return self

    @property
    def name(self) -> str:
        """Get schema name."""
        return self._name

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        """Validate configuration data against schema.

        Args:
            data: Configuration dictionary to validate

        Returns:
            Validated configuration with defaults applied

        Raises:
            ValidationError: If validation fails
        """
        result = {}
        all_errors: list[ValidationError] = []

        for field_name, field_def in self.fields.items():
            value = data.get(field_name)
            errors = field_def.validate(value, field_name)
            all_errors.extend(errors)

            if not errors:
                # Apply type coercion
                if field_def.field_type == bool and isinstance(value, str):
                    value = value.lower() in ("true", "1", "yes", "on")
                elif field_def.field_type != Any and value is not None:
                    try:
                        value = field_def.field_type(value)
                    except (ValueError, TypeError):
                        pass
                result[field_name] = value

        if all_errors:
            error_msg = "; ".join(f"{e.field}: {e.message}" for e in all_errors)
            raise ValidationError("config", error_msg)

        return result

    def get_errors(self, data: dict[str, Any]) -> list[ValidationError]:
        """Get validation errors without raising.

        Args:
            data: Configuration dictionary to validate

        Returns:
            List of validation errors (empty if valid)
        """
        all_errors: list[ValidationError] = []

        for field_name, field_def in self.fields.items():
            value = data.get(field_name)
            errors = field_def.validate(value, field_name)
            all_errors.extend(errors)

        return all_errors

    def is_valid(self, data: dict[str, Any]) -> bool:
        """Check if configuration data is valid.

        Args:
            data: Configuration dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        return len(self.get_errors(data)) == 0

    @classmethod
    def from_dict(cls, schema_dict: dict[str, dict[str, Any]]) -> type:
        """Create a ConfigSchema subclass from a dictionary.

        Example:
            schema_dict = {
                'port': {'type': int, 'required': True, 'min_value': 1},
                'debug': {'type': bool, 'default': False},
            }
            AppSchema = ConfigSchema.from_dict(schema_dict)
        """
        class DynamicSchema(ConfigSchema):
            def __init__(self):
                self.fields = {}
                for name, spec in schema_dict.items():
                    self.fields[name] = SchemaField(
                        field_type=spec.get('type', str),
                        required=spec.get('required', True),
                        default=spec.get('default'),
                        validator=spec.get('validator'),
                        description=spec.get('description', ''),
                        choices=spec.get('choices'),
                        min_value=spec.get('min_value'),
                        max_value=spec.get('max_value'),
                        pattern=spec.get('pattern'),
                        min_length=spec.get('min_length'),
                        max_length=spec.get('max_length'),
                    )

        return DynamicSchema


# Common field validators
def is_url(value: str) -> bool:
    """Validate that a value is a valid URL."""
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(url_pattern.match(value))


def is_email(value: str) -> bool:
    """Validate that a value is a valid email address."""
    import re
    email_pattern = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    return bool(email_pattern.match(value))


def is_port(value: int) -> bool:
    """Validate that a value is a valid port number."""
    return 1 <= value <= 65535


def is_positive(value: float) -> bool:
    """Validate that a value is positive."""
    return value > 0


def is_non_negative(value: float) -> bool:
    """Validate that a value is non-negative."""
    return value >= 0
