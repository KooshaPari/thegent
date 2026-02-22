"""Strict mapping mode for connector state and field validation.

# @trace WL-190
"""

from __future__ import annotations

from dataclasses import dataclass


class StrictMappingError(Exception):
    """Raised when strict mapping validation fails."""



@dataclass
class StrictMappingConfig:
    """Configuration for strict mapping validation.

    Attributes:
        enabled: Whether strict mapping is enabled.
        unknown_state_action: Action to take on unknown state ('fail', 'warn', 'skip').
    """

    enabled: bool = True
    unknown_state_action: str = "fail"

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.unknown_state_action not in ("fail", "warn", "skip"):
            raise ValueError(
                f"unknown_state_action must be 'fail', 'warn', or 'skip', "
                f"got '{self.unknown_state_action}'"
            )


class StrictMappingValidator:
    """Validator for strict mapping of remote states and field values."""

    def __init__(self, config: StrictMappingConfig | None = None) -> None:
        """Initialize the validator.

        Args:
            config: StrictMappingConfig instance. Defaults to enabled mode with 'fail' action.
        """
        self.config = config or StrictMappingConfig()

    def validate_remote_state(
        self, state: str, known_states: list[str]
    ) -> tuple[bool, str | None]:
        """Validate that a remote state is in the known states list.

        Args:
            state: The remote state to validate.
            known_states: List of known/valid states.

        Returns:
            Tuple of (is_valid, error_message).
            error_message is None if valid, or a string describing the issue.

        Raises:
            StrictMappingError: If enabled and state is unknown and action is 'fail'.
        """
        if state in known_states:
            return True, None

        if not self.config.enabled:
            return True, None

        error_msg = f"Unknown state '{state}' not in known states: {known_states}"

        if self.config.unknown_state_action == "fail":
            raise StrictMappingError(error_msg)
        if self.config.unknown_state_action == "warn":
            return False, error_msg
        # skip
        return False, None

    def validate_field_value(
        self, field: str, value: str, allowed_values: list[str]
    ) -> tuple[bool, str | None]:
        """Validate that a field value is in the allowed values list.

        Args:
            field: The field name.
            value: The field value to validate.
            allowed_values: List of allowed values for this field.

        Returns:
            Tuple of (is_valid, error_message).
            error_message is None if valid, or a string describing the issue.

        Raises:
            StrictMappingError: If enabled and value is not allowed and action is 'fail'.
        """
        if value in allowed_values:
            return True, None

        if not self.config.enabled:
            return True, None

        error_msg = (
            f"Field '{field}' has invalid value '{value}'. "
            f"Allowed values: {allowed_values}"
        )

        if self.config.unknown_state_action == "fail":
            raise StrictMappingError(error_msg)
        if self.config.unknown_state_action == "warn":
            return False, error_msg
        # skip
        return False, None
