# E2E Command Matrix

Use these commands for quick governance checks, split-suite execution, and the full quality gate.

| Goal | Command |
| --- | --- |
| Fast governance checks | `pytest -q tests/e2e/test_split_hygiene.py tests/e2e/test_readme_e2e_commands.py tests/e2e/test_cli_alias_rewrite_contract.py` |
| Alias rewrite contract unit (direct) | `pytest -q tests/e2e/test_cli_alias_rewrite_contract.py` |
| Alias rewrite real-app contract unit (direct) | `pytest -q tests/e2e/test_cli_alias_rewrite_real_app.py` |
| Alias unsupported rationale contract (direct) | `pytest -q tests/e2e/test_cli_alias_unsupported_rationale.py` |
| Compat unit suite (direct) | `pytest -q tests/e2e/test_cli_runner_compat.py` |
| Compat helper extract/rewrite guard suite (direct) | `pytest -q tests/e2e/test_cli_runner_extracts.py tests/e2e/test_cli_runner_rewrite_guards.py` |
| Compat import governance (direct) | `pytest -q tests/e2e/test_cli_runner_import_governance.py` |
| Compat skip-message contract suite (direct) | `pytest -q tests/e2e/test_cli_runner_skip_message_contract.py` |
| Compat skip-prefix contract suite (direct) | `pytest -q tests/e2e/test_cli_runner_skip_prefix_contract.py` |
| Compat edge-token suite (direct) | `pytest -q tests/e2e/test_cli_runner_unicode_tokens.py` |
| Command-surface unit (direct) | `pytest -q tests/e2e/test_command_surface.py` |
| Utility module pairing governance (direct) | `pytest -q tests/e2e/test_e2e_module_pairing.py` |
| Governance health artifact (direct) | `pytest -q tests/e2e/test_governance_health_artifact.py` |
| Governance inventory artifact (direct) | `pytest -q tests/e2e/test_governance_inventory_artifact.py` |
| Governance set equality (direct) | `pytest -q tests/e2e/test_governance_set_equality.py` |
| Governance sync contracts (direct) | `pytest -q tests/e2e/test_governance_sync_contracts.py` |
| README bundle order contract (direct) | `pytest -q tests/e2e/test_readme_bundle_order_contract.py` |
| README direct e2e collect-only governance (direct) | `pytest -q tests/e2e/test_readme_collect_only_commands.py` |
| README command normalized-duplicates (direct) | `pytest -q tests/e2e/test_readme_command_normalized_duplicates.py` |
| README command uniqueness (direct) | `pytest -q tests/e2e/test_readme_command_uniqueness.py` |
| README row order contract (direct) | `pytest -q tests/e2e/test_readme_row_order_contract.py` |
| Real-app command families contract (direct) | `pytest -q tests/e2e/test_real_app_command_families.py` |
| Real-app help anchor contract (direct) | `pytest -q tests/e2e/test_real_app_help_anchor_contract.py` |
| Smoke runner governance (direct) | `pytest -q tests/e2e/test_smoke_runner_governance.py` |
| Split marker governance (direct) | `pytest -q tests/e2e/test_split_marker_governance.py` |
| Full e2e governance unit bundle (direct) | `pytest -q tests/e2e/test_cli_alias_rewrite_contract.py tests/e2e/test_cli_alias_rewrite_real_app.py tests/e2e/test_cli_alias_unsupported_rationale.py tests/e2e/test_cli_runner_compat.py tests/e2e/test_cli_runner_extracts.py tests/e2e/test_cli_runner_import_governance.py tests/e2e/test_cli_runner_rewrite_guards.py tests/e2e/test_cli_runner_skip_message_contract.py tests/e2e/test_cli_runner_skip_prefix_contract.py tests/e2e/test_cli_runner_unicode_tokens.py tests/e2e/test_command_surface.py tests/e2e/test_e2e_module_pairing.py tests/e2e/test_governance_artifact_schema_policy.py tests/e2e/test_governance_delta_report.py tests/e2e/test_governance_health_artifact.py tests/e2e/test_governance_inventory_artifact.py tests/e2e/test_governance_registry_order.py tests/e2e/test_governance_set_equality.py tests/e2e/test_governance_sync_contracts.py tests/e2e/test_helper_governance_loophole_contract.py tests/e2e/test_readme_bundle_order_contract.py tests/e2e/test_readme_collect_only_commands.py tests/e2e/test_readme_command_normalized_duplicates.py tests/e2e/test_readme_command_uniqueness.py tests/e2e/test_readme_direct_command_token_sanitizer.py tests/e2e/test_readme_e2e_commands.py tests/e2e/test_readme_row_file_bijection.py tests/e2e/test_readme_row_order_contract.py tests/e2e/test_real_app_command_families.py tests/e2e/test_real_app_help_anchor_contract.py tests/e2e/test_smoke_runner_governance.py tests/e2e/test_split_hygiene.py tests/e2e/test_split_marker_governance.py tests/e2e/test_split_marker_placement_consistency.py tests/e2e/test_top_level_command_snapshot_contract.py tests/e2e/test_unsupported_alias_real_app_evidence.py` |
| Alias rewrite governance tests | `pytest -q tests/test_e2e_cli_aliases.py -k rewrite` |
| Split E2E suite run | `pytest -q tests/test_e2e_cli_core_a.py tests/test_e2e_cli_core_b.py tests/test_e2e_cli_aliases.py tests/test_e2e_cli_overlays.py -m e2e` |
| Full quality run | `task quality` |

## CompatCliRunner Rewrite Policy

- Exact alias path only: rewrite applies only to the bare alias path invocation.
- Argumentful or optionful invocations are not rewritten.
- When CLI path drift is detected for non-rewritten forms, tests skip.

## CompatCliRunner Troubleshooting

- Skip-on-drift is only for `No such command` path drift in non-rewritten forms.
- `No such option` is still a real failure and should not be skipped.

## Alias Rewrite Governance Invariants

- Exact-path rewrite: rewrite applies only to the bare alias path invocation.
- No duplicate old prefixes: each alias source prefix appears once in the mapping.
- List/tuple-of-strings requirement: argv inputs for rewrite checks must be list/tuple command tokens.
