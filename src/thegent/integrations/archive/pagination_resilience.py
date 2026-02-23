"""Pagination resilience helpers for pull flows.

# @trace WL-295
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Page(Generic[T]):
    """Represents a paginated response page."""

    items: list[T]
    next_token: str | None


def collect_paginated_items(
    fetch_page: Callable[[str | None], Page[T]],
    *,
    max_pages: int = 100,
) -> list[T]:
    """Collect all paginated items with loop and safety guards.

    Raises RuntimeError when a token loop is detected.
    Raises ValueError for invalid max_pages.
    """
    if max_pages <= 0:
        raise ValueError("max_pages must be positive")

    token: str | None = None
    seen_tokens: set[str] = set()
    collected: list[T] = []

    for _ in range(max_pages):
        page = fetch_page(token)
        collected.extend(page.items)

        if page.next_token is None:
            return collected

        if page.next_token in seen_tokens:
            raise RuntimeError(f"pagination token loop detected: {page.next_token}")

        seen_tokens.add(page.next_token)
        token = page.next_token

    raise RuntimeError("max_pages exceeded before pagination completed")
