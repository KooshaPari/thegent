"""Security configuration and settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SecuritySettings(BaseSettings):
    """Security configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="THGENT_SECURITY_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Guardrails
    enable_guardrails: bool = Field(default=True, description="Enable security guardrails")
    enable_rate_limiting: bool = Field(default=True, description="Enable rate limiting")
    enable_command_validation: bool = Field(default=True, description="Enable command validation")

    # Rate limits
    rate_limit_commands_per_minute: int = Field(default=100, description="Max commands per minute")
    rate_limit_file_ops_per_minute: int = Field(default=200, description="Max file operations per minute")
    rate_limit_network_per_minute: int = Field(default=50, description="Max network requests per minute")

    # Token optimization
    max_context_tokens: int = Field(default=100000, description="Maximum context tokens")
    target_context_tokens: int = Field(default=50000, description="Target context tokens")
    enable_secret_removal: bool = Field(default=True, description="Remove secrets from context")

    # Input validation
    max_input_length: int = Field(default=100000, description="Maximum input length")
    max_filename_length: int = Field(default=255, description="Maximum filename length")
    enable_input_sanitization: bool = Field(default=True, description="Enable input sanitization")

    # Logging
    log_security_violations: bool = Field(default=True, description="Log security violations")
    log_blocked_commands: bool = Field(default=True, description="Log blocked commands")
