"""Tests for WL-295 pull pagination resilience."""

from __future__ import annotations

import pytest

from thegent.integrations.pagination_resilience import Page, collect_paginated_items


@pytest.mark.requirement("WL-295")
def test_collect_paginated_items_happy_path() -> None:
    pages = {
        None: Page(items=[1, 2], next_token="a"),
        "a": Page(items=[3], next_token="b"),
        "b": Page(items=[4], next_token=None),
    }

    def fetch(token: str | None) -> Page[int]:
        return pages[token]

    assert collect_paginated_items(fetch) == [1, 2, 3, 4]


@pytest.mark.requirement("WL-295")
def test_collect_paginated_items_detects_token_loop() -> None:
    pages = {
        None: Page(items=[1], next_token="a"),
        "a": Page(items=[2], next_token="a"),
    }

    def fetch(token: str | None) -> Page[int]:
        return pages[token]

    with pytest.raises(RuntimeError, match="token loop"):
        collect_paginated_items(fetch)


@pytest.mark.requirement("WL-295")
def test_collect_paginated_items_respects_max_pages() -> None:
    counter = {"n": 0}

    def fetch(_token: str | None) -> Page[int]:
        counter["n"] += 1
        return Page(items=[counter["n"]], next_token=f"next-{counter['n']}")

    with pytest.raises(RuntimeError, match="max_pages exceeded"):
        collect_paginated_items(fetch, max_pages=2)
