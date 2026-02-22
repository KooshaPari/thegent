"""Governance contracts for README direct-row label-to-file bijection."""

from __future__ import annotations

from pathlib import Path
import re
import shlex


README_PATH = Path(__file__).with_name("README.md")
REPO_ROOT = README_PATH.parents[2]

_DIRECT_GOVERNANCE_PATTERN = re.compile(r"^pytest -q tests/e2e/test_[a-z0-9_]+\.py$")
_TEST_PATH_PATTERN = re.compile(r"^tests/e2e/test_[a-z0-9_]+\.py$")
_LABEL_STOPWORDS = {
    "command",
    "commands",
    "contract",
    "contracts",
    "direct",
    "e2e",
    "governance",
    "suite",
    "test",
    "tests",
    "unit",
}


def _readme_lines() -> list[str]:
    return README_PATH.read_text(encoding="utf-8").splitlines()


def _command_table_rows() -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    in_table = False

    for line in _readme_lines():
        stripped = line.strip()
        if not stripped:
            if in_table:
                break
            continue
        if not stripped.startswith("|"):
            if in_table:
                break
            continue

        parts = [part.strip() for part in stripped.split("|")[1:-1]]
        if len(parts) != 2:
            continue
        label, command = parts
        if label in {"Goal", "---"}:
            in_table = True
            continue
        in_table = True
        if command.startswith("`") and command.endswith("`"):
            command = command[1:-1].strip()
        rows.append((label, command))

    return rows


def _direct_governance_rows() -> list[tuple[str, str]]:
    return [(label, command) for label, command in _command_table_rows() if _DIRECT_GOVERNANCE_PATTERN.fullmatch(command)]


def _test_paths_in_snippet(snippet: str) -> list[str]:
    return [token for token in shlex.split(snippet) if _TEST_PATH_PATTERN.fullmatch(token)]


def _label_key_tokens(label: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-z0-9]+", label.lower())
        if len(token) >= 3 and token not in _LABEL_STOPWORDS
    ]


def _token_matches_slug(token: str, file_slug: str) -> bool:
    singular = token[:-1] if token.endswith("s") and len(token) > 3 else token
    return token in file_slug or singular in file_slug


def test_each_direct_governance_row_maps_to_exactly_one_test_path() -> None:
    rows = _direct_governance_rows()
    assert rows, "README command table should include direct e2e governance rows"

    for label, command in rows:
        paths = _test_paths_in_snippet(command)
        assert len(paths) == 1, (
            f"README row '{label}' must map to exactly one tests/e2e file path, "
            f"found {len(paths)} in: {command}"
        )


def test_direct_governance_row_paths_exist_and_roughly_match_row_label() -> None:
    rows = _direct_governance_rows()
    assert rows, "README command table should include direct e2e governance rows"

    for label, command in rows:
        path = _test_paths_in_snippet(command)[0]
        resolved = REPO_ROOT / path
        assert resolved.exists(), f"README row '{label}' points to a missing test file: {path}"

        file_slug = resolved.stem.lower().replace("_", "-")
        key_tokens = _label_key_tokens(label)
        assert key_tokens, f"README row '{label}' must include at least one key token for label/file checks"

        assert any(_token_matches_slug(token, file_slug) for token in key_tokens), (
            f"README row '{label}' should roughly correspond to '{resolved.name}' via key-token overlap; "
            f"expected one of {key_tokens} to appear in slug '{file_slug}'"
        )


def test_direct_governance_rows_map_to_unique_test_paths() -> None:
    rows = _direct_governance_rows()
    assert rows, "README command table should include direct e2e governance rows"

    direct_paths = [_test_paths_in_snippet(command)[0] for _, command in rows]
    assert len(direct_paths) == len(set(direct_paths)), (
        "README direct governance rows must be a 1:1 mapping to tests/e2e files; "
        "duplicate file tokens were found across rows"
    )


def test_direct_governance_row_label_slug_token_signatures_are_unique() -> None:
    rows = _direct_governance_rows()
    assert rows, "README command table should include direct e2e governance rows"

    signatures: dict[tuple[str, ...], str] = {}
    for label, command in rows:
        path = _test_paths_in_snippet(command)[0]
        file_slug = Path(path).stem.lower().replace("_", "-")
        matched_tokens = tuple(
            sorted(token for token in _label_key_tokens(label) if _token_matches_slug(token, file_slug))
        )
        assert matched_tokens, (
            f"README row '{label}' must produce at least one label/file token match for strict bijection checks"
        )
        assert matched_tokens not in signatures, (
            "README direct governance rows must not share the same label/file token signature; "
            f"rows '{signatures[matched_tokens]}' and '{label}' both map to {matched_tokens}"
        )
        signatures[matched_tokens] = label
