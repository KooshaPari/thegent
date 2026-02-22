"""Govern command snippet uniqueness and full-bundle path coverage checks."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import shlex

from tests.e2e import test_split_hygiene

README_PATH = Path(__file__).with_name("README.md")

FULL_E2E_GOVERNANCE_TEST_PATHS = (
    "tests/e2e/test_split_hygiene.py",
    "tests/e2e/test_readme_e2e_commands.py",
    "tests/e2e/test_readme_row_order_contract.py",
    "tests/e2e/test_readme_row_file_bijection.py",
    "tests/e2e/test_readme_command_uniqueness.py",
    "tests/e2e/test_readme_command_normalized_duplicates.py",
    "tests/e2e/test_readme_bundle_order_contract.py",
    "tests/e2e/test_readme_collect_only_commands.py",
    "tests/e2e/test_readme_direct_command_token_sanitizer.py",
    "tests/e2e/test_governance_sync_contracts.py",
    "tests/e2e/test_governance_registry_order.py",
    "tests/e2e/test_governance_health_artifact.py",
    "tests/e2e/test_governance_artifact_schema_policy.py",
    "tests/e2e/test_governance_inventory_artifact.py",
    "tests/e2e/test_governance_set_equality.py",
    "tests/e2e/test_governance_delta_report.py",
    "tests/e2e/test_cli_alias_rewrite_contract.py",
    "tests/e2e/test_cli_alias_rewrite_real_app.py",
    "tests/e2e/test_cli_alias_unsupported_rationale.py",
    "tests/e2e/test_unsupported_alias_real_app_evidence.py",
    "tests/e2e/test_real_app_command_families.py",
    "tests/e2e/test_real_app_help_anchor_contract.py",
    "tests/e2e/test_top_level_command_snapshot_contract.py",
    "tests/e2e/test_cli_runner_compat.py",
    "tests/e2e/test_cli_runner_extracts.py",
    "tests/e2e/test_cli_runner_rewrite_guards.py",
    "tests/e2e/test_cli_runner_skip_message_contract.py",
    "tests/e2e/test_cli_runner_skip_prefix_contract.py",
    "tests/e2e/test_cli_runner_unicode_tokens.py",
    "tests/e2e/test_cli_runner_import_governance.py",
    "tests/e2e/test_helper_governance_loophole_contract.py",
    "tests/e2e/test_command_surface.py",
    "tests/e2e/test_e2e_module_pairing.py",
    "tests/e2e/test_smoke_runner_governance.py",
    "tests/e2e/test_split_marker_placement_consistency.py",
    "tests/e2e/test_split_marker_governance.py",
)


def _readme_text() -> str:
    return README_PATH.read_text(encoding="utf-8")


def _backticked_pytest_or_task_snippets(text: str) -> list[str]:
    snippets = [snippet.strip() for snippet in re.findall(r"`([^`]+)`", text)]
    command_snippets: list[str] = []
    for snippet in snippets:
        tokens = shlex.split(snippet)
        if not tokens:
            continue
        if tokens[0] in {"pytest", "task"}:
            command_snippets.append(snippet)
    return command_snippets


def _full_bundle_command_snippet(text: str) -> str:
    match = re.search(
        r"\|\s*Full e2e governance unit bundle \(direct\)\s*\|\s*`([^`]+)`\s*\|",
        text,
    )
    assert match, "README must contain the full governance unit bundle row"
    return match.group(1)


def _test_path_tokens(snippet: str) -> list[str]:
    return [token for token in shlex.split(snippet) if token.startswith("tests/") and token.endswith(".py")]


def _command_table_rows(text: str) -> list[tuple[str, str]]:
    return [
        (goal.strip(), snippet.strip())
        for goal, snippet in re.findall(r"\|\s*([^|]+?)\s*\|\s*`([^`]+)`\s*\|", text)
    ]


def test_no_duplicate_backticked_pytest_or_task_command_snippets() -> None:
    snippets = _backticked_pytest_or_task_snippets(_readme_text())
    assert snippets, "README should include at least one backticked pytest/task command snippet"

    counts = Counter(snippets)
    duplicates = [snippet for snippet, count in counts.items() if count > 1]
    assert not duplicates, "README should not duplicate exact pytest/task snippets: " + "; ".join(duplicates)


def test_full_bundle_row_contains_each_governance_test_exactly_once() -> None:
    snippet = _full_bundle_command_snippet(_readme_text())
    path_tokens = _test_path_tokens(snippet)
    counts = Counter(path_tokens)

    duplicate_paths = [path for path, count in counts.items() if count > 1]
    assert not duplicate_paths, "Full bundle command should not repeat test paths: " + ", ".join(duplicate_paths)

    missing_paths = [path for path in FULL_E2E_GOVERNANCE_TEST_PATHS if counts[path] != 1]
    assert not missing_paths, "Full bundle command must include each governance test exactly once: " + ", ".join(missing_paths)

    unexpected_paths = [path for path in path_tokens if path not in FULL_E2E_GOVERNANCE_TEST_PATHS]
    assert not unexpected_paths, "Full bundle command contains unexpected test paths: " + ", ".join(unexpected_paths)


def test_full_bundle_readme_and_split_hygiene_path_sequences_match_exactly() -> None:
    readme_paths = _test_path_tokens(_full_bundle_command_snippet(_readme_text()))
    split_hygiene_paths = _test_path_tokens(test_split_hygiene.REQUIRED_E2E_GOVERNANCE_BUNDLE_COMMAND)
    assert readme_paths == split_hygiene_paths, (
        "README full bundle path sequence must match "
        "test_split_hygiene.REQUIRED_E2E_GOVERNANCE_BUNDLE_COMMAND exactly"
    )


def test_full_bundle_first_and_last_path_sentinels_are_stable() -> None:
    readme_paths = _test_path_tokens(_full_bundle_command_snippet(_readme_text()))
    assert readme_paths, "README full bundle command must include at least one path token"
    assert readme_paths[0] == "tests/e2e/test_cli_alias_rewrite_contract.py", (
        "README full bundle command must start with test_cli_alias_rewrite_contract.py"
    )
    assert readme_paths[-1] == "tests/e2e/test_unsupported_alias_real_app_evidence.py", (
        "README full bundle command must end with test_unsupported_alias_real_app_evidence.py"
    )


def test_full_bundle_path_count_matches_required_governance_test_entries() -> None:
    readme_paths = _test_path_tokens(_full_bundle_command_snippet(_readme_text()))
    required_test_entry_count = sum(
        1
        for path in test_split_hygiene.REQUIRED_E2E_GOVERNANCE_FILES
        if path.name.startswith("test_")
    )
    assert len(readme_paths) == required_test_entry_count, (
        "README full bundle path count must match the number of test_* entries in "
        "test_split_hygiene.REQUIRED_E2E_GOVERNANCE_FILES"
    )


def test_full_bundle_readme_path_sequence_is_lexicographically_sorted() -> None:
    readme_paths = _test_path_tokens(_full_bundle_command_snippet(_readme_text()))
    assert readme_paths == sorted(readme_paths), (
        "README full bundle path sequence must be lexicographically sorted"
    )


def test_full_bundle_path_list_matches_full_governance_tuple_membership_exactly() -> None:
    readme_paths = _test_path_tokens(_full_bundle_command_snippet(_readme_text()))
    assert set(readme_paths) == set(FULL_E2E_GOVERNANCE_TEST_PATHS), (
        "README full bundle path set must exactly match FULL_E2E_GOVERNANCE_TEST_PATHS membership"
    )


def test_full_bundle_includes_alias_trio_in_canonical_adjacent_order() -> None:
    readme_paths = _test_path_tokens(_full_bundle_command_snippet(_readme_text()))
    alias_trio = (
        "tests/e2e/test_cli_alias_rewrite_contract.py",
        "tests/e2e/test_cli_alias_rewrite_real_app.py",
        "tests/e2e/test_cli_alias_unsupported_rationale.py",
    )
    counts = Counter(readme_paths)
    missing_or_duplicate = [path for path in alias_trio if counts[path] != 1]
    assert not missing_or_duplicate, (
        "README full bundle must include each alias trio path exactly once: "
        + ", ".join(missing_or_duplicate)
    )

    start_idx = readme_paths.index(alias_trio[0])
    assert tuple(readme_paths[start_idx : start_idx + len(alias_trio)]) == alias_trio, (
        "README full bundle must include alias trio paths in canonical adjacent order"
    )


def test_full_bundle_row_has_no_duplicate_non_path_tokens_excluding_initial_pytest_q() -> None:
    tokens = shlex.split(_full_bundle_command_snippet(_readme_text()))
    assert tokens[:2] == ["pytest", "-q"], "README full bundle command must begin with `pytest -q`"

    non_path_tokens = [token for token in tokens if not (token.startswith("tests/") and token.endswith(".py"))]
    duplicate_non_path_tokens = [
        token for token, count in Counter(non_path_tokens[2:]).items() if count > 1
    ]
    assert not duplicate_non_path_tokens, (
        "README full bundle command must not repeat non-path tokens after `pytest -q`: "
        + ", ".join(duplicate_non_path_tokens)
    )


def test_readme_full_bundle_includes_single_file_direct_rows_exactly_once() -> None:
    text = _readme_text()
    bundle_counts = Counter(_test_path_tokens(_full_bundle_command_snippet(text)))

    direct_single_file_paths: list[str] = []
    for goal, command in _command_table_rows(text):
        if not goal.endswith("(direct)") or "bundle" in goal.lower():
            continue
        tokens = shlex.split(command)
        if tokens[:2] != ["pytest", "-q"]:
            continue
        path_tokens = _test_path_tokens(command)
        if len(path_tokens) == 1:
            direct_single_file_paths.append(path_tokens[0])

    assert direct_single_file_paths, "README should contain direct single-file governance rows"

    missing_or_duplicate = [
        path for path in direct_single_file_paths if bundle_counts[path] != 1
    ]
    assert not missing_or_duplicate, (
        "README full bundle path list must include each direct single-file row path exactly once: "
        + ", ".join(missing_or_duplicate)
    )
