from __future__ import annotations

"""Tests for GW-73: Prompt library / versioning.

# @trace FR-PROMPT-073
"""

import pytest

from thegent.prompts.library import (
    get_prompt_library,
    reset_prompt_library,
)

pytestmark = pytest.mark.requirement("FR-PROMPT-073")


# ---------------------------------------------------------------------------
# Fixture: reset singleton before and after every test
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_library():
    reset_prompt_library()
    yield
    reset_prompt_library()


# ---------------------------------------------------------------------------
# 1. add — version assignment
# ---------------------------------------------------------------------------


def test_add_prompt_version_1():
    lib = get_prompt_library()
    entry = lib.add("greet", "Hello, world!")
    assert entry.version == 1
    assert entry.name == "greet"
    assert entry.content == "Hello, world!"


def test_add_prompt_increments_version():
    lib = get_prompt_library()
    lib.add("greet", "Hello, world!")
    entry2 = lib.add("greet", "Hi there!")
    assert entry2.version == 2
    assert entry2.content == "Hi there!"


# ---------------------------------------------------------------------------
# 2. get — latest and specific version
# ---------------------------------------------------------------------------


def test_get_latest_version():
    lib = get_prompt_library()
    lib.add("greet", "v1 content")
    lib.add("greet", "v2 content")
    latest = lib.get("greet")
    assert latest is not None
    assert latest.version == 2
    assert latest.content == "v2 content"


def test_get_specific_version():
    lib = get_prompt_library()
    lib.add("greet", "v1 content")
    lib.add("greet", "v2 content")
    v1 = lib.get("greet", version=1)
    assert v1 is not None
    assert v1.version == 1
    assert v1.content == "v1 content"


def test_get_nonexistent_returns_none():
    lib = get_prompt_library()
    result = lib.get("does_not_exist")
    assert result is None


def test_get_invalid_version_returns_none():
    lib = get_prompt_library()
    lib.add("greet", "Hello")
    result = lib.get("greet", version=99)
    assert result is None


# ---------------------------------------------------------------------------
# 3. get_all_versions
# ---------------------------------------------------------------------------


def test_get_all_versions_ordered():
    lib = get_prompt_library()
    lib.add("msg", "first")
    lib.add("msg", "second")
    lib.add("msg", "third")
    versions = lib.get_all_versions("msg")
    assert len(versions) == 3
    assert versions[0].version == 1
    assert versions[1].version == 2
    assert versions[2].version == 3
    assert versions[0].content == "first"
    assert versions[2].content == "third"


# ---------------------------------------------------------------------------
# 4. list_names
# ---------------------------------------------------------------------------


def test_list_names_sorted():
    lib = get_prompt_library()
    lib.add("zebra", "z content")
    lib.add("alpha", "a content")
    lib.add("middle", "m content")
    names = lib.list_names()
    assert names == ["alpha", "middle", "zebra"]


def test_list_names_empty():
    lib = get_prompt_library()
    assert lib.list_names() == []


# ---------------------------------------------------------------------------
# 5. delete
# ---------------------------------------------------------------------------


def test_delete_existing():
    lib = get_prompt_library()
    lib.add("to_delete", "some content")
    result = lib.delete("to_delete")
    assert result is True
    assert lib.get("to_delete") is None


def test_delete_nonexistent():
    lib = get_prompt_library()
    result = lib.delete("ghost")
    assert result is False


# ---------------------------------------------------------------------------
# 6. search
# ---------------------------------------------------------------------------


def test_search_by_name():
    lib = get_prompt_library()
    lib.add("customer_greeting", "Hello customer")
    lib.add("internal_note", "For internal use only")
    results = lib.search("greeting")
    names = [e.name for e in results]
    assert "customer_greeting" in names
    assert "internal_note" not in names


def test_search_by_content():
    lib = get_prompt_library()
    lib.add("prompt_a", "You are a helpful assistant.")
    lib.add("prompt_b", "Translate the following text.")
    results = lib.search("translate")
    names = [e.name for e in results]
    assert "prompt_b" in names
    assert "prompt_a" not in names


def test_search_case_insensitive():
    lib = get_prompt_library()
    lib.add("MyPrompt", "the quick brown fox")
    results = lib.search("QUICK")
    assert len(results) == 1
    assert results[0].name == "MyPrompt"


def test_search_no_match():
    lib = get_prompt_library()
    lib.add("hello", "say hello")
    lib.add("bye", "say goodbye")
    results = lib.search("xyzzy_no_match")
    assert results == []


# ---------------------------------------------------------------------------
# 7. Singleton behaviour
# ---------------------------------------------------------------------------


def test_singleton():
    lib1 = get_prompt_library()
    lib2 = get_prompt_library()
    assert lib1 is lib2


def test_reset_singleton():
    lib1 = get_prompt_library()
    lib1.add("temp", "some content")
    reset_prompt_library()
    lib2 = get_prompt_library()
    assert lib2 is not lib1
    assert lib2.get("temp") is None


# ---------------------------------------------------------------------------
# 8. tags and metadata stored
# ---------------------------------------------------------------------------


def test_tags_and_metadata_stored():
    lib = get_prompt_library()
    entry = lib.add(
        "tagged_prompt",
        "Do something useful.",
        description="A useful prompt",
        tags=["production", "v2"],
        metadata={"author": "alice", "reviewed": True},
    )
    assert entry.description == "A useful prompt"
    assert entry.tags == ["production", "v2"]
    assert entry.metadata == {"author": "alice", "reviewed": True}

    # Verify they round-trip through get()
    retrieved = lib.get("tagged_prompt")
    assert retrieved is not None
    assert retrieved.tags == ["production", "v2"]
    assert retrieved.metadata["author"] == "alice"
