"""Type aliases for thegent.

Centralized type definitions to improve code consistency.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Generator, Iterable
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, TypeVar, Union

# Paths
PathLike = str | Path

# Time
Timestamp = datetime
Duration = float  # seconds

# Results
Result = Any
Error = Exception

# Status
Status = Literal["pending", "running", "success", "failed", "cancelled"]

# JSON
JSON = dict[str, Any] | list[Any] | str | int | float | bool | None
JSONObject = dict[str, Any]
JSONArray = list[Any]

# Async
AsyncFunc = Callable[..., Awaitable[Any]]
SyncFunc = Callable[..., Any]

# Type variables
T = TypeVar("T")
U = TypeVar("U")

# Error handling
SafeResult = tuple[bool, T | None]  # (success, result)

# HTTP
HTTPMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
HTTPStatus = int

# Optional types
OptionalStr = str | None
OptionalInt = int | None
OptionalFloat = float | None
OptionalBool = bool | None
OptionalPath = Path | None
