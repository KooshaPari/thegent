# Thegent Phase 7-9 Summary and Training Guide (WP-9010)

## Overview
This document summarizes the major capabilities added in Phases 7, 8, and 9 of thegent program.

## Phase 7: Contract Convergence
- **Negotiation**: Use `thegent govern negotiate <contract_id> <versions>` to ensure client/server compatibility.
- **Streaming Parser**: Enhanced with state tracking and `rollback` support for partial agent outputs.
- **Semantic Policy**: Use `SemanticPolicyEngine` to enforce phase-aware invariants (e.g. COMPLETED must have 100% progress).

## Phase 8: Predictive Reliability
- **Monte Carlo Simulation**: Run `plan analyze` to see PERT and Monte Carlo duration forecasts.
- **Bottlenecks**: Automated detection of high-variance and critical dependency tasks.
- **Surge Watcher**: Proactive safe-mode recommendations based on system load.

## Phase 9: Productized Operations
- **Unified Surface**: All major capabilities are now categorized under `orchestrate`, `govern`, `recover`, `observe`, `plan`.
- **Explainability**: 3-tier progressive disclosure (Summary -> Detail -> Trace).
- **Handoff Enforcement**: Mandatory confirmation for continuity across shifts.
- **What-If Replay**: Branch from historical runs to simulate alternative decisions.

## Operator Training
1. **Negotiate First**: Always run `thegent govern negotiate csm csm-v1` before a major shift.
2. **Analyze Plans**: Use `thegent plan analyze` to identify potential bottlenecks early.
3. **Confirm Handoffs**: Do not leave high-risk tasks unowned at shift end.
4. **Audit Drift**: Monitor `thegent govern trend-analysis` for provider regressions.
