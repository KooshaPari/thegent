"""Base models for thegent.

Common base classes for data models across the codebase.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class Status(str, Enum):
    """Common status values."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BaseResponse(BaseModel):
    """Base response model."""

    success: bool = Field(default=True, description="Whether the operation succeeded")
    message: str | None = Field(default=None, description="Optional message")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Response timestamp")


class BaseRequest(BaseModel):
    """Base request model."""

    request_id: str | None = Field(default=None, description="Request ID for tracing")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Request timestamp")


class PaginatedRequest(BaseRequest):
    """Base paginated request."""

    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=50, ge=1, le=1000, description="Items per page")


class PaginatedResponse(BaseResponse):
    """Base paginated response."""

    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page")
    page_size: int = Field(description="Items per page")
    has_next: bool = Field(description="Whether there are more pages")
    has_prev: bool = Field(description="Whether there are previous pages")


class ErrorResponse(BaseResponse):
    """Error response model."""

    success: bool = Field(default=False)
    error_code: str | None = Field(default=None, description="Error code")
    details: dict[str, Any] | None = Field(default=None, description="Additional error details")


class BaseModel(BaseModel):
    """Enhanced base model with common functionality."""

    id: str | None = Field(default=None, description="Unique identifier")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Last update timestamp"
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()

    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaseModel:
        """Create from dictionary."""
        return cls(**data)


class AuditableModel(BaseModel):
    """Model with audit trail."""

    created_by: str | None = Field(default=None, description="Creator")
    updated_by: str | None = Field(default=None, description="Last updater")
    version: int = Field(default=1, description="Version number")

    def increment_version(self) -> None:
        """Increment version number."""
        self.version += 1
        self.updated_at = datetime.now(timezone.utc)
