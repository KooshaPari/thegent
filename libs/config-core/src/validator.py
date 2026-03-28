"""Configuration validation with schema support."""

from typing import Any, Callable, Dict, List, Optional


class ValidationError(Exception):
    """Raised when configuration validation fails."""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation error for '{field}': {message}")


class SchemaField:
    """Defines a configuration field with validation rules.

    Args:
        field_type: Type annotation for the field
        required: Whether the field is required
        default: Default value if not required
        validator: Optional validation function
        description: Human-readable description
    """

    def __init__(
        self,
        field_type: type,
        required: bool = True,
        default: Any = None,
        validator: Optional[Callable[[Any], bool]] = None,
        description: str = "",
    ):
        self.field_type = field_type
        self.required = required
        self.default = default
        self.validator = validator
        self.description = description


class ConfigValidator:
    """Validates configuration against a schema.

    Example:
        schema = {
            'port': SchemaField(int, required=True, validator=lambda x: 0 < x < 65536),
            'debug': SchemaField(bool, required=False, default=False),
        }
        validator = ConfigValidator(schema)
        config = validator.validate({'port': 8080, 'debug': True})
    """

    def __init__(self, schema: Dict[str, SchemaField]):
        """Initialize validator with field schema.

        Args:
            schema: Dictionary mapping field names to SchemaField definitions
        """
        self.schema = schema
        self._errors: List[ValidationError] = []

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration data against schema.

        Args:
            data: Configuration dictionary to validate

        Returns:
            Validated configuration with defaults applied

        Raises:
            ValidationError: If validation fails and raise_on_error is True
        """
        result = {}
        self._errors = []

        for field_name, field_def in self.schema.items():
            value = data.get(field_name)

            # Handle missing values
            if value is None:
                if field_def.required:
                    self._errors.append(
                        ValidationError(field_name, "required field is missing")
                    )
                else:
                    result[field_name] = field_def.default
                continue

            # Type validation
            if not isinstance(value, field_def.field_type):
                try:
                    value = field_def.field_type(value)
                except (ValueError, TypeError):
                    self._errors.append(
                        ValidationError(
                            field_name,
                            f"expected {field_def.field_type.__name__}, got {type(value).__name__}",
                        )
                    )
                    continue

            # Custom validation
            if field_def.validator and not field_def.validator(value):
                self._errors.append(
                    ValidationError(field_name, "failed custom validation")
                )
                continue

            result[field_name] = value

        if self._errors:
            error_messages = "; ".join(e.message for e in self._errors)
            raise ValidationError("config", error_messages)

        return result

    @property
    def errors(self) -> List[ValidationError]:
        """Get list of validation errors without raising."""
        return self._errors
