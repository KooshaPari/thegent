import { shallowRef, inject, computed, ref, watch, onUnmounted, reactive, markRaw, readonly, nextTick, defineComponent, h, onMounted, watchEffect, watchPostEffect, onUpdated, mergeProps, useSSRContext, provide, unref, withCtx, createVNode, renderSlot, onErrorCaptured, resolveDynamicComponent, createTextVNode, toDisplayString, resolveComponent, createSSRApp } from "vue";
import { usePreferredDark, useDark, useMediaQuery } from "@vueuse/core";
import { L as Layout$1, _ as _sfc_main$j, a as _export_sfc } from "./vue.DCJT_Tnz.js";
import { ssrRenderAttrs, ssrRenderSlot, ssrRenderAttr, ssrInterpolate, ssrRenderTeleport, ssrRenderList, ssrRenderComponent, ssrRenderClass, ssrRenderStyle, ssrIncludeBooleanAttr, ssrRenderVNode, renderToString } from "vue/server-renderer";
import { _ as _sfc_main$k } from "./mermaid.OkLrB7RK.js";
import "./app.js";
import "mermaid";
function deserializeFunctions(r) {
  return Array.isArray(r) ? r.map(deserializeFunctions) : typeof r == "object" && r !== null ? Object.keys(r).reduce((t, n) => (t[n] = deserializeFunctions(r[n]), t), {}) : typeof r == "string" && r.startsWith("_vp-fn_") ? new Function(`return ${r.slice(7)}`)() : r;
}
const siteData = deserializeFunctions(JSON.parse('{"lang":"en-US","dir":"ltr","title":"thegent","description":"AI Agent Governance & MCP Server","base":"/","head":[],"router":{"prefetchLinks":true},"appearance":true,"themeConfig":{"nav":[{"text":"Home","link":"/"},{"text":"Architecture","link":"/ARCHITECTURE_LAYERS.md","activeMatch":"/architecture/"},{"text":"Guides","link":"/guides/","activeMatch":"/guides/"},{"text":"Reference","link":"/reference/","activeMatch":"/reference/"},{"text":"Technical Specs","link":"/SPECS_INDEX.md","activeMatch":"/specs/"}],"sidebar":{"/":[{"text":"Architecture","collapsed":false,"items":[{"text":"Diagrams","collapsed":false,"items":[{"text":"Module Dependencies","link":"/diagrams/module-dependencies.md"},{"text":"Package Structure","link":"/diagrams/package-structure.md"}]},{"text":"Agent Sandboxing Architecture: WASM/Containers/VMs (No Docker)","link":"/architecture/AGENT_SANDBOXING_ARCHITECTURE.md"},{"text":"Python Frontmatter + Native Backmatter Architecture","link":"/architecture/FRONTMATTER_BACKMATTER_ARCHITECTURE.md"},{"text":"Hybrid Mac/Windows Development Environment Architecture","link":"/architecture/HYBRID_MAC_WIN_DEV_ENVIRONMENT.md"}]},{"text":"Changes","collapsed":false,"items":[{"text":"Hexagonal Migration","collapsed":false,"items":[{"text":"Hexagonal Architecture Migration -- thegent","link":"/hexagonal-migration/proposal.md"}]}]},{"text":"Checklists","collapsed":false,"items":[{"text":"Hybrid Mac/Windows Environment Setup Checklist","link":"/checklists/HYBRID_ENV_SETUP_CHECKLIST.md"}]},{"text":"Closure","collapsed":false,"items":[{"text":"DR Rehearsal Report","link":"/closure/DR_REHEARSAL_REPORT.md"},{"text":"Governance & Compliance Bundle","link":"/closure/GOVERNANCE_COMPLIANCE_BUNDLE.md"},{"text":"Phase 6 Readiness Report","link":"/closure/PHASE6_READINESS_REPORT.md"},{"text":"Post-Launch 28-Day Observation Plan","link":"/closure/POST_LAUNCH_28DAY_OBSERVATION.md"},{"text":"Rollback Reserve Plan","link":"/closure/ROLLBACK_RESERVE_PLAN.md"},{"text":"SLO Certification Matrix","link":"/closure/SLO_CERTIFICATION_MATRIX.md"}]},{"text":"Contracts","collapsed":false,"items":[{"text":"Contract Authority","link":"/contracts/CONTRACT_AUTHORITY.md"},{"text":"Fallback Control Plane","link":"/contracts/FALLBACK_POLICY.md"},{"text":"Provider Adapter Contracts (G-RV-05)","link":"/contracts/PROVIDER_ADAPTER_CONTRACTS.md"},{"text":"Contract Upgrade Playbook","link":"/contracts/UPGRADE_PLAYBOOK.md"}]},{"text":"Demos","collapsed":false,"items":[{"text":"Demo Scripts for VitePress Documentation","link":"/demos/README.md"}]},{"text":"Docset","collapsed":false,"items":[{"text":"DAG Node-to-Service Contract Checklist","link":"/docset/DAG_NODE_SERVICE_CONTRACT_CHECKLIST.md"},{"text":"DAG Node-to-Service Contract Checklist","link":"/docset/DAG_NODE_TO_SERVICE_CONTRACT_CHECKLIST.md"},{"text":"E2E Next Chunk Plan — Full-Phase Mega Chunk","link":"/docset/E2E_NEXT_CHUNK_PLAN.md"},{"text":"E2E Remaining Full-Depth Plan","link":"/docset/E2E_REMAINING_FULL_DEPTH_PLAN.md"},{"text":"FastMCP 3.0 Integration Reference for Thegent","link":"/docset/FASTMCP_INTEGRATION.md"},{"text":"Thegent Implementation Status Tracker","link":"/docset/IMPLEMENTATION_STATUS.md"},{"text":"Thegent Optimization, Polish, and Robustness Addendum","link":"/docset/OPTIMIZATION_POLISH_ADDENDUM.md"},{"text":"Thegent Pattern Catalog","link":"/docset/PATTERNS.md"},{"text":"Comprehensive Test Plan Matrix","link":"/docset/PRD_TEST_PLAN_MATRIX.md"},{"text":"Remaining Gaps — Full Depth Analysis","link":"/docset/REMAINING_GAPS_DEEP_DIVE.md"},{"text":"Remaining Gaps — Full Depth Analysis","link":"/docset/REMAINING_GAPS_FULL_DEPTH.md"},{"text":"Thegent Risks and Anti-Patterns Catalog","link":"/docset/RISKS_AND_ANTIPATTERNS.md"},{"text":"WBS-to-Issue Import Matrix","link":"/docset/WBS_TO_ISSUE_IMPORT_MATRIX.md"},{"text":"Thegent CLI Single Source of Truth Audit","link":"/docset/thegent-cli-single-source-of-truth-audit-2026-02-14.md"},{"text":"Thegent Cross-Analysis Matrix (Deep)","link":"/docset/thegent-cross-analysis-matrix-2026-02-14.md"},{"text":"Thegent Final DAG Specification","link":"/docset/thegent-dag-final.md"},{"text":"Thegent DAG Extension — Phases 10 to 12","link":"/docset/thegent-dag-phase10-12-extension.md"},{"text":"thegent DAG Extension — Phases 7, 8, 9","link":"/docset/thegent-dag-phase7-9-extension.md"},{"text":"Thegent Gaps and Discovery Report","link":"/docset/thegent-gaps-and-discovery-2026-02-14.md"},{"text":"Thegent Implementation Log","link":"/docset/thegent-implementation-log-2026-02-14.md"},{"text":"Thegent Kush Docs Deep Dive (Zen + Adjacent Projects)","link":"/docset/thegent-kush-docs-deep-dive-2026-02-14.md"},{"text":"Thegent Mega Research Synthesis","link":"/docset/thegent-mega-research-synthesis-2026-02-14.md"},{"text":"Thegent Orchestration Optimization & Expansion PRD (Living Document)","link":"/docset/thegent-orchestration-optimization-prd.md"},{"text":"Thegent Pattern Enhancement Synthesis","link":"/docset/thegent-patterns-enhancement-synthesis.md"},{"text":"Thegent Phase 10–12 Bundle B Sprint Playbook","link":"/docset/thegent-phase10-12-bundle-b-sprint-playbook.md"},{"text":"Thegent Phase 10–12 Bundle Signoff and Handoff Packages","link":"/docset/thegent-phase10-12-bundle-signoff-and-handoff-packages.md"},{"text":"Thegent Phase 10–12 Closure Readiness Pack Template","link":"/docset/thegent-phase10-12-closure-readiness-pack-template.md"},{"text":"Thegent Phase 10–12 Compact Execution Dashboard","link":"/docset/thegent-phase10-12-compact-execution-dashboard.md"},{"text":"Thegent Phase 10–12 Drift Reconciliation Playbook","link":"/docset/thegent-phase10-12-drift-reconciliation-playbook.md"},{"text":"Thegent Phase 10–12 Execution Bundles Playbook","link":"/docset/thegent-phase10-12-execution-bundles-playbook.md"},{"text":"Thegent Phase 10–12 Execution Synthesis Playbook","link":"/docset/thegent-phase10-12-execution-synthesis-playbook.md"},{"text":"Thegent Phase 10–12 Execution Workboard (Chunk 4)","link":"/docset/thegent-phase10-12-execution-workboard.md"},{"text":"Thegent Phase 10–12 Hard-Stop, Rollback, and Stability Matrix","link":"/docset/thegent-phase10-12-hard-stop-and-rollback-matrix.md"},{"text":"Thegent Phase 10–12 Implementation Chunk Plan","link":"/docset/thegent-phase10-12-implementation-chunk-plan.md"},{"text":"Thegent Phase 10–12 Implementation Issue Queue","link":"/docset/thegent-phase10-12-implementation-issue-queue.md"},{"text":"Thegent Phase 10–12 Implementation Ticket Templates (Chunk 3)","link":"/docset/thegent-phase10-12-implementation-ticket-templates.md"},{"text":"Thegent Phase 10–12 Issue Board Automation Playbook","link":"/docset/thegent-phase10-12-issue-board-automation.md"},{"text":"Thegent Phase 10–12 Issue Board Import Notes","link":"/docset/thegent-phase10-12-issue-board-import-notes.md"},{"text":"Thegent Phase 10–12 Launch Schedule (Day-by-Day Execution Plan)","link":"/docset/thegent-phase10-12-launch-schedule.md"},{"text":"Thegent Phase 10–12 Master Traceability Ledger","link":"/docset/thegent-phase10-12-master-traceability-ledger.md"},{"text":"Thegent — Phase 10–12 PRD (Optimization-Depth and Productization Wave)","link":"/docset/thegent-phase10-12-optimal-design-prd.md"},{"text":"Thegent Phase 10–12 Orchestrator Tooling Stack","link":"/docset/thegent-phase10-12-orchestrator-tooling-stack.md"},{"text":"Thegent Phase 10–12 Policy-as-Code and Automation Contract","link":"/docset/thegent-phase10-12-policy-as-code-and-automation-contract.md"},{"text":"Thegent Phase 10–12 PRD↔WBS Finalization Cross-Map","link":"/docset/thegent-phase10-12-prd-wbs-crossmap-finalization.md"},{"text":"Thegent Phase 10–12 PRD-WBS-DAG-Ticket Validation Framework","link":"/docset/thegent-phase10-12-prd-wbs-dag-ticket-validation.md"},{"text":"Thegent Phase 10–12 Release Readiness and Delta Pack","link":"/docset/thegent-phase10-12-release-readiness-and-delta-pack.md"},{"text":"Thegent Phase 10–12 Test and Readiness Pack","link":"/docset/thegent-phase10-12-test-readiness-pack.md"},{"text":"Thegent Phase 11 Sprint Playbook (Bundles C and D)","link":"/docset/thegent-phase11-control-and-adaptation-sprint-playbook.md"},{"text":"Thegent Phase 12 Sprint Playbook (Bundles E and F)","link":"/docset/thegent-phase12-explainability-and-closure-sprint-playbook.md"},{"text":"Thegent Phase 13+ Extension Boundary Proposal","link":"/docset/thegent-phase13-plus-extension-proposal.md"},{"text":"Thegent Phase 3–6 Closure Acceptance Contract Schema","link":"/docset/thegent-phase3-6-closure-acceptance-contract-schema.md"},{"text":"Thegent Phase 3–6 Closure Acceptance Pack Template","link":"/docset/thegent-phase3-6-closure-acceptance-pack-template.md"},{"text":"Thegent Phase 3–6 Closure Validator Automation Package","link":"/docset/thegent-phase3-6-closure-validator-automation-package.md"},{"text":"Thegent Phase 3–6 Closure Validation Event and Waiver Contract v1","link":"/docset/thegent-phase3-6-closure-validator-event-and-waiver-contract-v1.md"},{"text":"Thegent Phase 3–6 Closure Validator Fault Injection and Chaos Tests","link":"/docset/thegent-phase3-6-closure-validator-fault-injection-and-chaos-tests.md"},{"text":"Thegent Phase 3–6 Closure Validator Implementation Blueprint","link":"/docset/thegent-phase3-6-closure-validator-implementation-blueprint.md"},{"text":"Thegent Phase 3–6 Closure Validator Python Implementation Blueprint","link":"/docset/thegent-phase3-6-closure-validator-python-implementation-blueprint.md"},{"text":"Thegent Phase 3-6 Closure Validator Runtime CLI and Adapter Playbook","link":"/docset/thegent-phase3-6-closure-validator-runtime-cli-and-adapter-playbook.md"},{"text":"Thegent Phase 3–6 Cross-Wave Bridge and Continuity Plan","link":"/docset/thegent-phase3-6-crosswave-bridge-and-continuity-plan.md"},{"text":"Thegent — Phase 3–6 Full-Depth Execution Chunk","link":"/docset/thegent-phase3-6-full-depth-execution-prd.md"},{"text":"Thegent Phase 7–9 Next-Wave PRD (Post-Closure Optimization)","link":"/docset/thegent-phase7-9-next-wave-prd.md"},{"text":"Thegent Phase 7–9 Test and Readiness Pack","link":"/docset/thegent-phase7-9-test-readiness-pack.md"},{"text":"Thegent Orchestration Final Plan Index","link":"/docset/thegent-plan-final-index.md"},{"text":"Thegent Production Orchestration PRD (Final)","link":"/docset/thegent-prd-final.md"},{"text":"Thegent Research Validation Addendum (Zen + Task Tools)","link":"/docset/thegent-research-validation-2026-02-14.md"},{"text":"thegent Third-Party Bundle Manifest","link":"/docset/thegent-third-party-bundle-manifest.md"},{"text":"Thegent Final WBS (Comprehensive)","link":"/docset/thegent-wbs-final.md"},{"text":"Thegent WBS — Phase 10 to Phase 12 (Optimization-Depth and Productization)","link":"/docset/thegent-wbs-phase10-12.md"},{"text":"Thegent WBS — Phase 7 to Phase 9 (Next-Wave Execution)","link":"/docset/thegent-wbs-phase7-9.md"}]},{"text":"Enterprise","collapsed":false,"items":[{"text":"Decommissioning and Sunset Plan","link":"/enterprise/DECOMMISSIONING_PLAN.md"},{"text":"Program Operating Model and Ownership Map","link":"/enterprise/OPERATING_MODEL.md"},{"text":"Security and Compliance Signoff Package","link":"/enterprise/SECURITY_COMPLIANCE_SIGNOFF.md"}]},{"text":"Examples","collapsed":false,"items":[{"text":"VitePress Examples","link":"/examples/README.md"},{"text":"CodePlayground Examples","link":"/examples/code-playground-example.md"},{"text":"Demo GIF Examples","link":"/examples/demo-gif-example.md"},{"text":"Math & Emoji Examples","link":"/examples/math-emoji-example.md"},{"text":"Mermaid Diagram Examples","link":"/examples/mermaid-example.md"},{"text":"Tooltip Component Examples","link":"/examples/tooltip-example.md"}]},{"text":"Governance","collapsed":false,"items":[{"text":"Cost Governance Design (G-GP-06)","link":"/governance/COST_GOVERNANCE_DESIGN.md"},{"text":"HITL (Human-in-the-Loop) Design (G-GP-05)","link":"/governance/HITL_DESIGN.md"},{"text":"NeMo Guardrails Design (G-GP-02)","link":"/governance/NEMO_GUARDRAILS_DESIGN.md"},{"text":"OPA Integration Design (G-GP-01)","link":"/governance/OPA_INTEGRATION_DESIGN.md"},{"text":"Retention Policy Design (G-GP-07)","link":"/governance/RETENTION_POLICY_DESIGN.md"},{"text":"Sandboxing Design (G-GP-08)","link":"/governance/SANDBOXING_DESIGN.md"}]},{"text":"Guides","collapsed":false,"items":[{"text":"Agent Debugging and Remediation Guide","link":"/guides/AGENT_DEBUGGING_AND_REMEDIATION_GUIDE.md"},{"text":"Agent Instructions: thegent Deep-Dive","link":"/guides/AGENT_INSTRUCTIONS_THEGENT.md"},{"text":"Automated Documentation Demos","link":"/guides/AUTOMATED_DEMOS.md"},{"text":"BKM Implementation Guides","link":"/guides/BKM_IMPLEMENTATION_GUIDES.md"},{"text":"Content Tabs Component","link":"/guides/CONTENT_TABS_GUIDE.md"},{"text":"Cross-Platform Desktop Automation — Complete Guide","link":"/guides/CROSS_PLATFORM_COMPLETE.md"},{"text":"Cross-Platform Desktop Automation: Developer Cookbook","link":"/guides/CROSS_PLATFORM_DEVELOPER_COOKBOOK.md"},{"text":"Cross-Platform Desktop Automation: Implementation Templates","link":"/guides/CROSS_PLATFORM_IMPLEMENTATION_TEMPLATES.md"},{"text":"Cross-Platform Desktop Automation: Migration Guide","link":"/guides/CROSS_PLATFORM_MIGRATION_GUIDE.md"},{"text":"Cross-Platform Desktop Automation: Quick Start Guide","link":"/guides/CROSS_PLATFORM_QUICK_START.md"},{"text":"Cross-Platform Desktop Automation: Implementation Roadmap","link":"/guides/CROSS_PLATFORM_ROADMAP.md"},{"text":"Doctor Command Fixes","link":"/guides/DOCTOR_FIXES.md"},{"text":"Fix Shell Corruption Issue","link":"/guides/FIX_SHELL_CORRUPTION.md"},{"text":"Fix Shell Fork Errors: Quick Guide","link":"/guides/FIX_SHELL_FORK_ERRORS.md"},{"text":"Guides Index","link":"/guides/GUIDES_INDEX.md"},{"text":"Hook Rust Benchmark Harness Guide","link":"/guides/HOOK_RUST_BENCHMARK_HARNESS_GUIDE.md"},{"text":"Hybrid Mac/Windows Environment Quick Start Guide","link":"/guides/HYBRID_ENV_QUICK_START.md"},{"text":"Implementation Patterns Guide","link":"/guides/IMPLEMENTATION_PATTERNS.md"},{"text":"Job Pool System - Usage Guide","link":"/guides/JOB_POOL_USAGE.md"},{"text":"OAuth-Only Authentication Policy","link":"/guides/OAUTH_ONLY_AUTHENTICATION.md"},{"text":"Operational Learning Assets (WP-12008)","link":"/guides/OPERATIONAL_LEARNING.md"},{"text":"oxlint Integration Guide (Phase 4)","link":"/guides/OXLINT_INTEGRATION_GUIDE.md"},{"text":"Thegent Phase 10 Summary and Migration Guide (WP-10010)","link":"/guides/PHASE_10_GUIDE.md"},{"text":"Thegent Phase 11 Summary and Evidence Pack (WP-11010)","link":"/guides/PHASE_11_GUIDE.md"},{"text":"Phase 4 Quick Start: ESLint → oxlint Migration","link":"/guides/PHASE_4_QUICK_START.md"},{"text":"Thegent Phase 7-9 Summary and Training Guide (WP-9010)","link":"/guides/PHASE_7_9_GUIDE.md"},{"text":"Prompts Tooling — Cursor / Codex / Claude Aggregate","link":"/guides/PROMPTS_TOOLING.md"},{"text":"Provider Setup Guide","link":"/guides/PROVIDER_SETUP_GUIDE.md"},{"text":"Quality Assurance Guide","link":"/guides/QUALITY_ASSURANCE.md"},{"text":"Quick Fix: Shell Setup Issues","link":"/guides/QUICK_FIX_SHELL_SETUP.md"},{"text":"Runtime Optimization Guide","link":"/guides/RUNTIME_OPTIMIZATION.md"},{"text":"Runtime Resource Management Guide","link":"/guides/RUNTIME_RESOURCE_MANAGEMENT.md"},{"text":"Shell Advanced Features Guide","link":"/guides/SHELL_ADVANCED_FEATURES.md"},{"text":"Shell Corruption Fix - Complete Solution","link":"/guides/SHELL_CORRUPTION_FIX_COMPLETE.md"},{"text":"Complete Shell Environment System","link":"/guides/SHELL_ENVIRONMENT_COMPLETE.md"},{"text":"Shell Environment Management","link":"/guides/SHELL_ENVIRONMENT_MANAGEMENT.md"},{"text":"Shell Optimization Guide","link":"/guides/SHELL_OPTIMIZATION_GUIDE.md"},{"text":"Shell & Zsh Plugin Setup — Long-Term Fix","link":"/guides/SHELL_ZSH_PLUGIN_SETUP.md"},{"text":"Sitback Plugin API","link":"/guides/SITBACK_PLUGINS.md"},{"text":"Starship + direnv Setup Complete","link":"/guides/STARSHIP_DIRENV_SETUP.md"},{"text":"🚀 Hooks Optimization Initiative - START HERE","link":"/guides/START_HERE.md"},{"text":"Task Routing Quick Reference Guide","link":"/guides/TASK_ROUTING_QUICK_REF.md"},{"text":"thegent Testing Guide","link":"/guides/TESTING.md"},{"text":"Thegent CLI Reference Guide","link":"/guides/THGENT_CLI_REFERENCE.md"},{"text":"Troubleshooting Guide","link":"/guides/TROUBLESHOOTING.md"},{"text":"Creating Terminal Recordings with VHS","link":"/guides/VHS_RECORDINGS.md"},{"text":"VitePress Docsite Setup","link":"/guides/VITEPPRESS_SETUP.md"},{"text":"VitePress Rich Documentation — Usage Guide","link":"/guides/VITEPRESS_USAGE_GUIDE.md"},{"text":"Anti-Pattern Detection Guide","link":"/guides/anti-patterns.md"},{"text":"Architecture Enforcement Guide","link":"/guides/architecture-enforcement.md"},{"text":"Guides","link":"/guides/index.md"}]},{"text":"Migration","collapsed":false,"items":[{"text":"Advanced Performance Patterns & Best Practices","link":"/migration/ADVANCED_PATTERNS.md"},{"text":"Complete Solution: Polished, Optimized, Production-Ready","link":"/migration/COMPLETE_SOLUTION.md"},{"text":"Comprehensive Benchmarking Strategy","link":"/migration/COMPREHENSIVE_BENCHMARKING.md"},{"text":"Comprehensive Performance Analysis & Migration Strategy","link":"/migration/COMPREHENSIVE_PERFORMANCE_ANALYSIS.md"},{"text":"Design Principles","link":"/migration/DESIGN_PRINCIPLES.md"},{"text":"Usage Examples","link":"/migration/EXAMPLES.md"},{"text":"Fork Failure (EAGAIN) Analysis & Solutions","link":"/migration/FORK_FAILURE_ANALYSIS.md"},{"text":"Comprehensive Implementation Roadmap","link":"/migration/IMPLEMENTATION_ROADMAP.md"},{"text":"Production Readiness Checklist","link":"/migration/PRODUCTION_READINESS.md"},{"text":"Quick Start Guide","link":"/migration/QUICK_START.md"},{"text":"Shell to Rust/Go Migration Plan","link":"/migration/RUST_GO_MIGRATION_PLAN.md"},{"text":"Performance Optimization Summary","link":"/migration/SUMMARY.md"},{"text":"The Ultimate Guide: Comprehensive Performance Optimization & Migration","link":"/migration/ULTIMATE_GUIDE.md"},{"text":"User Guide: thegent Performance Optimizations","link":"/migration/USER_GUIDE.md"}]},{"text":"Plans","collapsed":false,"items":[{"text":"Fragments","collapsed":false,"items":[{"text":"Lane Strategy Matrix for Hybrid Hook Runtime","link":"/fragments/LANE_STRATEGY_MATRIX.md"},{"text":"No-Regression Enforcement for Hybrid Sync/Async Checks","link":"/fragments/NO_REGRESSION_ENFORCEMENT.md"},{"text":"Performance Optimization Playbook for Hybrid Hook Runtime","link":"/fragments/PERF_OPTIMIZATION_PLAYBOOK.md"},{"text":"Rollout and Operations Runbook for Hybrid Lane System","link":"/fragments/ROLLOUT_AND_OPERATIONS.md"}]},{"text":"Thegent Unified Plan — Master Index","link":"/plans/00-MASTER-INDEX.md"},{"text":"01 — Project State","link":"/plans/01-PROJECT-STATE.md"},{"text":"02 — Unified Work Breakdown Structure","link":"/plans/02-UNIFIED-WBS.md"},{"text":"03 — Unified DAG Specifications","link":"/plans/03-UNIFIED-DAG.md"},{"text":"04 — Unified Requirements","link":"/plans/04-REQUIREMENTS.md"},{"text":"05 — Architecture & Patterns","link":"/plans/05-ARCHITECTURE.md"},{"text":"06 — Implementation Guide","link":"/plans/06-IMPLEMENTATION-GUIDE.md"},{"text":"07 — Test Strategy","link":"/plans/07-TEST-STRATEGY.md"},{"text":"08 — Optimization, Polish, Enhancement & Robustness Catalog","link":"/plans/08-OPTIMIZATION-CATALOG.md"},{"text":"09 — Risk Registry & Anti-Patterns","link":"/plans/09-RISK-REGISTRY.md"},{"text":"10 — Subagent Dispatch Plan","link":"/plans/10-SUBAGENT-DISPATCH.md"},{"text":"12 — Cycleloop Loops & Checker Agent Design","link":"/plans/12-LIFECYCLE-LOOP-DESIGN.md"},{"text":"Design: thegent install CLI Command","link":"/plans/2026-02-14-thegent-install-design.md"},{"text":"thegent install Implementation Plan","link":"/plans/2026-02-14-thegent-install-implementation-plan.md"},{"text":"Research and Elicitation Plan — 2026-02-15","link":"/plans/2026-02-15-RESEARCH-AND-ELICITATION-PLAN.md"},{"text":"thegent sitback — Design & Implementation Plan","link":"/plans/2026-02-15-thegent-sitback-design.md"},{"text":"Tray Application Design - Plugin-Based Architecture","link":"/plans/2026-02-15-tray-application-design.md"},{"text":"AgentDeployer + LifecycleController Integration Review","link":"/plans/2026-02-16-AGENT_DEPLOYER_REVIEW.md"},{"text":"Cycleloop + AgilePlus Integration Plan","link":"/plans/2026-02-16-CYCLELOOP_AGILEPLUS_INTEGRATION.md"},{"text":"Full LiteLLM Feature Integration Plan","link":"/plans/2026-02-16-litellm-full-features-plan.md"},{"text":"LiteLLM Integration Design","link":"/plans/2026-02-16-litellm-integration-design.md"},{"text":"LiteLLM Router Integration Implementation Plan","link":"/plans/2026-02-16-litellm-integration-plan.md"},{"text":"Supermemory.ai Integration Plan (WP-5001-SM)","link":"/plans/2026-02-16-supermemory-integration-plan.md"},{"text":"Design Doc: Agent-Accelerated Production Readiness Optimization","link":"/plans/2026-02-18-production-readiness-optimization-design.md"},{"text":"Agent-Accelerated Production Readiness Implementation Plan","link":"/plans/2026-02-18-production-readiness-optimization-plan.md"},{"text":"Agent Sandboxing Implementation Plan","link":"/plans/AGENT_SANDBOXING_IMPLEMENTATION_PLAN.md"},{"text":"Catalog ↔ CLIProxyAPIPlus Fork Alignment","link":"/plans/CATALOG_CLIPROXY_FORK_ALIGNMENT.md"},{"text":"CLIProxyAPI & Thegent Work Plan – Unified Phased WBS","link":"/plans/CLIPROXY_API_AND_THGENT_UNIFIED_PLAN.md"},{"text":"Agent Orchestration Harness: Multi-Platform (Extreme-Depth Plan)","link":"/plans/CODEX_DONUT_HARNESS_PLAN.md"},{"text":"Cross-Platform Multi-Tenant Desktop Automation Complete Plan","link":"/plans/CROSS_PLATFORM_COMPLETE_PLAN.md"},{"text":"Cross-Platform Multi-Tenant Desktop Automation Implementation Plan","link":"/plans/CROSS_PLATFORM_MULTI_TENANT_IMPLEMENTATION_PLAN.md"},{"text":"Cursor API Integration Research & Plan","link":"/plans/CURSOR_API_INTEGRATION_RESEARCH.md"},{"text":"Debug Tags and Metrics (Transient Response Tags)","link":"/plans/DEBUG_TAGS_AND_METRICS.md"},{"text":"Distributed Model Routing Plan","link":"/plans/DISTRIBUTED_MODEL_ROUTING_PLAN.md"},{"text":"Documentation Expansion Process","link":"/plans/DOCUMENTATION_EXPANSION_PROCESS.md"},{"text":"Documentation Expansion TODO","link":"/plans/DOCUMENTATION_EXPANSION_TODO.md"},{"text":"Documentation Consolidation & Implementation WBS","link":"/plans/DOC_CONSOLIDATION_AND_IMPLEMENTATION_WBS.md"},{"text":"Factory Droid Harness Integration Plan","link":"/plans/FACTORY_DROID_HARNESS_INTEGRATION_PLAN.md"},{"text":"Full Shell → Rust Where Beneficial","link":"/plans/FULL_SHELL_TO_RUST_WHERE_BENEFICIAL.md"},{"text":"Holistic + Harmonious Design & Full Integration Plan","link":"/plans/HOLISTIC_HARMONIOUS_DESIGN_AND_INTEGRATION_PLAN.md"},{"text":"Hook Point Hybrid Latency Expanded Plan","link":"/plans/HOOK_POINT_HYBRID_LATENCY_EXPANDED_PLAN.md"},{"text":"Hook Point Hybrid Latency Master Plan","link":"/plans/HOOK_POINT_HYBRID_LATENCY_MASTER_PLAN.md"},{"text":"Hook Runtime Rust Migration Complete Guide","link":"/plans/HOOK_RUNTIME_RUST_COMPLETE.md"},{"text":"Hook Runtime: Full Rust Migration Design (Deep & Wide)","link":"/plans/HOOK_RUNTIME_RUST_DESIGN.md"},{"text":"Hybrid Mac/Windows Environment Implementation Plan","link":"/plans/HYBRID_ENV_IMPLEMENTATION_PLAN.md"},{"text":"LiteLLM + CLIProxyAPIPlus + Bifrost Harmony","link":"/plans/LITELLM_CLIPROXY_BIFROST_HARMONY.md"},{"text":"MCP Bundle: thegent + Browser Tools (Replace Manual Playwright)","link":"/plans/MCP_BUNDLE_PLAYWRIGHT_REPLACEMENT.md"},{"text":"MCP Tool Optimization, Polish & Enhancement Plan","link":"/plans/MCP_TOOL_OPTIMIZATION_PLAN.md"},{"text":"Multi-Platform Parity Master Plan & Matrix","link":"/plans/MULTI_PLATFORM_PARITY_MASTER_PLAN.md"},{"text":"New Providers Auth Research & Plan","link":"/plans/NEW_PROVIDERS_AUTH_RESEARCH.md"},{"text":"OpenRouter-Style Routing + CLIProxyAPIPlus Integration","link":"/plans/OPENROUTER_STYLE_ROUTING_AND_CLIPROXY.md"},{"text":"Process & Tool Optimization Complete Plan","link":"/plans/PROCESS_OPTIMIZATION_COMPLETE_PLAN.md"},{"text":"Process and Tool Optimization Plan","link":"/plans/PROCESS_OPTIMIZATION_PLAN.md"},{"text":"Prompt History Collection & Audit System: Comprehensive Plan","link":"/plans/PROMPT_HISTORY_COLLECTION_AND_AUDIT_SYSTEM.md"},{"text":"Prompt History Collection & Audit System Complete Guide","link":"/plans/PROMPT_HISTORY_COLLECTION_COMPLETE.md"},{"text":"Remote Compute Implementation Detail","link":"/plans/REMOTE_COMPUTE_IMPLEMENTATION_DETAIL.md"},{"text":"thegent Setup: Proposed Hooks, Plugins, Skills, MCP & Docs","link":"/plans/SETUP_PROPOSED_ITEMS.md"},{"text":"Shell Environment Advanced Enhancement Plan","link":"/plans/SHELL_ENVIRONMENT_ADVANCED_ENHANCEMENT_PLAN.md"},{"text":"Shell Environment Advanced Enhancement - Implementation Summary","link":"/plans/SHELL_ENVIRONMENT_ADVANCED_IMPLEMENTATION_SUMMARY.md"},{"text":"Shell Environment Complete Plan","link":"/plans/SHELL_ENVIRONMENT_COMPLETE_PLAN.md"},{"text":"Shell Environment Implementation Summary","link":"/plans/SHELL_ENVIRONMENT_IMPLEMENTATION_SUMMARY.md"},{"text":"Shell Environment Optimization & Enhancement Plan","link":"/plans/SHELL_ENVIRONMENT_OPTIMIZATION_PLAN.md"},{"text":"Sync/Update Command & Full System Audit Plan","link":"/plans/SYNC_UPDATE_COMMAND_AND_SYSTEM_AUDIT_PLAN.md"},{"text":"Thegent FastMCP 3.0 Implementation Plan","link":"/plans/THGENT_FASTMCP_IMPLEMENTATION_PLAN.md"},{"text":"Runtime Dispatch Consolidation & Fork Fix: Complete","link":"/plans/ULTRA_SHIM_CONSOLIDATION_COMPLETE.md"},{"text":"Ultra-Shim Fork Failure Fix: Root Cause Analysis & Solution","link":"/plans/ULTRA_SHIM_FORK_FAILURE_FIX.md"},{"text":"Unified Login Flow: Open URL + Prompt for Key","link":"/plans/UNIFIED_LOGIN_FLOW.md"},{"text":"Unified System Application Plan","link":"/plans/UNIFIED_SYSTEM_APPLICATION_PLAN.md"}]},{"text":"Reference","collapsed":false,"items":[{"text":"Api","collapsed":false,"items":[{"text":"adapter_policy API Reference","link":"/api/adapter_policy_api.md"},{"text":"adapters API Reference","link":"/api/adapters_api.md"},{"text":"agent_deployer API Reference","link":"/api/agent_deployer_api.md"},{"text":"agents API Reference","link":"/api/agents_api.md"},{"text":"agileplus API Reference","link":"/api/agileplus_api.md"},{"text":"alerting API Reference","link":"/api/alerting_api.md"},{"text":"alerts API Reference","link":"/api/alerts_api.md"},{"text":"analyzer API Reference","link":"/api/analyzer_api.md"},{"text":"api_evolution API Reference","link":"/api/api_evolution_api.md"},{"text":"arbitrage API Reference","link":"/api/arbitrage_api.md"},{"text":"attestation API Reference","link":"/api/attestation_api.md"},{"text":"audit API Reference","link":"/api/audit_api.md"},{"text":"auth_bridge API Reference","link":"/api/auth_bridge_api.md"},{"text":"autopoiesis API Reference","link":"/api/autopoiesis_api.md"},{"text":"backlog API Reference","link":"/api/backlog_api.md"},{"text":"base API Reference","link":"/api/base_api.md"},{"text":"billing API Reference","link":"/api/billing_api.md"},{"text":"black_box_proxy API Reference","link":"/api/black_box_proxy_api.md"},{"text":"breakers API Reference","link":"/api/breakers_api.md"},{"text":"cache API Reference","link":"/api/cache_api.md"},{"text":"cage API Reference","link":"/api/cage_api.md"},{"text":"calibration API Reference","link":"/api/calibration_api.md"},{"text":"capability_registry API Reference","link":"/api/capability_registry_api.md"},{"text":"catalog API Reference","link":"/api/catalog_api.md"},{"text":"checker API Reference","link":"/api/checker_api.md"},{"text":"checkpoint API Reference","link":"/api/checkpoint_api.md"},{"text":"circuit_breaker API Reference","link":"/api/circuit_breaker_api.md"},{"text":"cli API Reference","link":"/api/cli_api.md"},{"text":"cli_document_queue API Reference","link":"/api/cli_document_queue_api.md"},{"text":"cli_impl API Reference","link":"/api/cli_impl_api.md"},{"text":"cliproxy_adapter API Reference","link":"/api/cliproxy_adapter_api.md"},{"text":"cliproxy_data API Reference","link":"/api/cliproxy_data_api.md"},{"text":"cliproxy_manager API Reference","link":"/api/cliproxy_manager_api.md"},{"text":"clode_main API Reference","link":"/api/clode_main_api.md"},{"text":"codex_proxy API Reference","link":"/api/codex_proxy_api.md"},{"text":"collaboration API Reference","link":"/api/collaboration_api.md"},{"text":"compliance API Reference","link":"/api/compliance_api.md"},{"text":"config API Reference","link":"/api/config_api.md"},{"text":"conformance API Reference","link":"/api/conformance_api.md"},{"text":"consistency_checker API Reference","link":"/api/consistency_checker_api.md"},{"text":"constitution API Reference","link":"/api/constitution_api.md"},{"text":"context API Reference","link":"/api/context_api.md"},{"text":"contracts API Reference","link":"/api/contracts_api.md"},{"text":"control_vectors API Reference","link":"/api/control_vectors_api.md"},{"text":"coordination API Reference","link":"/api/coordination_api.md"},{"text":"cost API Reference","link":"/api/cost_api.md"},{"text":"cost_controller API Reference","link":"/api/cost_controller_api.md"},{"text":"cost_tracker API Reference","link":"/api/cost_tracker_api.md"},{"text":"cost_values API Reference","link":"/api/cost_values_api.md"},{"text":"csm API Reference","link":"/api/csm_api.md"},{"text":"cursor_api_runner API Reference","link":"/api/cursor_api_runner_api.md"},{"text":"deferral API Reference","link":"/api/deferral_api.md"},{"text":"design API Reference","link":"/api/design_api.md"},{"text":"design_language API Reference","link":"/api/design_language_api.md"},{"text":"dex_main API Reference","link":"/api/dex_main_api.md"},{"text":"digital_twin API Reference","link":"/api/digital_twin_api.md"},{"text":"direct_agents API Reference","link":"/api/direct_agents_api.md"},{"text":"discovery API Reference","link":"/api/discovery_api.md"},{"text":"dispatch_graph API Reference","link":"/api/dispatch_graph_api.md"},{"text":"dlq API Reference","link":"/api/dlq_api.md"},{"text":"dna_storage API Reference","link":"/api/dna_storage_api.md"},{"text":"doctor API Reference","link":"/api/doctor_api.md"},{"text":"donut_adapter API Reference","link":"/api/donut_adapter_api.md"},{"text":"drift API Reference","link":"/api/drift_api.md"},{"text":"drift_corrector API Reference","link":"/api/drift_corrector_api.md"},{"text":"droid API Reference","link":"/api/droid_api.md"},{"text":"edge_sync API Reference","link":"/api/edge_sync_api.md"},{"text":"egress API Reference","link":"/api/egress_api.md"},{"text":"escalation API Reference","link":"/api/escalation_api.md"},{"text":"ethics_proof API Reference","link":"/api/ethics_proof_api.md"},{"text":"events API Reference","link":"/api/events_api.md"},{"text":"evidence API Reference","link":"/api/evidence_api.md"},{"text":"evidence_graph API Reference","link":"/api/evidence_graph_api.md"},{"text":"evidence_ledger API Reference","link":"/api/evidence_ledger_api.md"},{"text":"evolution API Reference","link":"/api/evolution_api.md"},{"text":"execution API Reference","link":"/api/execution_api.md"},{"text":"exit_codes API Reference","link":"/api/exit_codes_api.md"},{"text":"explainability API Reference","link":"/api/explainability_api.md"},{"text":"explanations API Reference","link":"/api/explanations_api.md"},{"text":"failure_modes API Reference","link":"/api/failure_modes_api.md"},{"text":"fallback_ui API Reference","link":"/api/fallback_ui_api.md"},{"text":"federation API Reference","link":"/api/federation_api.md"},{"text":"fork_guard API Reference","link":"/api/fork_guard_api.md"},{"text":"formal_loop API Reference","link":"/api/formal_loop_api.md"},{"text":"galactic API Reference","link":"/api/galactic_api.md"},{"text":"gardener API Reference","link":"/api/gardener_api.md"},{"text":"gardening API Reference","link":"/api/gardening_api.md"},{"text":"geo_guard API Reference","link":"/api/geo_guard_api.md"},{"text":"governance API Reference","link":"/api/governance_api.md"},{"text":"graph API Reference","link":"/api/graph_api.md"},{"text":"handoff API Reference","link":"/api/handoff_api.md"},{"text":"hardware_id API Reference","link":"/api/hardware_id_api.md"},{"text":"harmonized_paths API Reference","link":"/api/harmonized_paths_api.md"},{"text":"harness API Reference","link":"/api/harness_api.md"},{"text":"health_score API Reference","link":"/api/health_score_api.md"},{"text":"homomorphic API Reference","link":"/api/homomorphic_api.md"},{"text":"human API Reference","link":"/api/human_api.md"},{"text":"hybrid_router API Reference","link":"/api/hybrid_router_api.md"},{"text":"identity API Reference","link":"/api/identity_api.md"},{"text":"information_life API Reference","link":"/api/information_life_api.md"},{"text":"infra API Reference","link":"/api/infra_api.md"},{"text":"input_guardrails API Reference","link":"/api/input_guardrails_api.md"},{"text":"install API Reference","link":"/api/install_api.md"},{"text":"integration API Reference","link":"/api/integration_api.md"},{"text":"kill_switch API Reference","link":"/api/kill_switch_api.md"},{"text":"kpis API Reference","link":"/api/kpis_api.md"},{"text":"lanes API Reference","link":"/api/lanes_api.md"},{"text":"launch API Reference","link":"/api/launch_api.md"},{"text":"learning API Reference","link":"/api/learning_api.md"},{"text":"leasing API Reference","link":"/api/leasing_api.md"},{"text":"ledger API Reference","link":"/api/ledger_api.md"},{"text":"litellm_router API Reference","link":"/api/litellm_router_api.md"},{"text":"liveness API Reference","link":"/api/liveness_api.md"},{"text":"load_based_limits API Reference","link":"/api/load_based_limits_api.md"},{"text":"lock_free API Reference","link":"/api/lock_free_api.md"},{"text":"loop_controller API Reference","link":"/api/loop_controller_api.md"},{"text":"main API Reference","link":"/api/main_api.md"},{"text":"manage_devkit API Reference","link":"/api/manage_devkit_api.md"},{"text":"manager API Reference","link":"/api/manager_api.md"},{"text":"market API Reference","link":"/api/market_api.md"},{"text":"marketplace API Reference","link":"/api/marketplace_api.md"},{"text":"mcp_manage API Reference","link":"/api/mcp_manage_api.md"},{"text":"mcp_server API Reference","link":"/api/mcp_server_api.md"},{"text":"mcp_sitback API Reference","link":"/api/mcp_sitback_api.md"},{"text":"mcp_tools_modes API Reference","link":"/api/mcp_tools_modes_api.md"},{"text":"memory API Reference","link":"/api/memory_api.md"},{"text":"mesh API Reference","link":"/api/mesh_api.md"},{"text":"meta API Reference","link":"/api/meta_api.md"},{"text":"mgmt_manage API Reference","link":"/api/mgmt_manage_api.md"},{"text":"migration API Reference","link":"/api/migration_api.md"},{"text":"models API Reference","link":"/api/models_api.md"},{"text":"models_meta API Reference","link":"/api/models_meta_api.md"},{"text":"modes API Reference","link":"/api/modes_api.md"},{"text":"moral_ui API Reference","link":"/api/moral_ui_api.md"},{"text":"multiverse API Reference","link":"/api/multiverse_api.md"},{"text":"naming API Reference","link":"/api/naming_api.md"},{"text":"never_idle API Reference","link":"/api/never_idle_api.md"},{"text":"omega API Reference","link":"/api/omega_api.md"},{"text":"omega_consensus API Reference","link":"/api/omega_consensus_api.md"},{"text":"omega_safety API Reference","link":"/api/omega_safety_api.md"},{"text":"operations API Reference","link":"/api/operations_api.md"},{"text":"optimizer API Reference","link":"/api/optimizer_api.md"},{"text":"orchestration API Reference","link":"/api/orchestration_api.md"},{"text":"orchestration_modes API Reference","link":"/api/orchestration_modes_api.md"},{"text":"otel_instrumentation API Reference","link":"/api/otel_instrumentation_api.md"},{"text":"output_parser API Reference","link":"/api/output_parser_api.md"},{"text":"overrides API Reference","link":"/api/overrides_api.md"},{"text":"oversight API Reference","link":"/api/oversight_api.md"},{"text":"pareto_viz API Reference","link":"/api/pareto_viz_api.md"},{"text":"parser API Reference","link":"/api/parser_api.md"},{"text":"payments API Reference","link":"/api/payments_api.md"},{"text":"personas API Reference","link":"/api/personas_api.md"},{"text":"phases API Reference","link":"/api/phases_api.md"},{"text":"physical API Reference","link":"/api/physical_api.md"},{"text":"plan_system API Reference","link":"/api/plan_system_api.md"},{"text":"planning API Reference","link":"/api/planning_api.md"},{"text":"platform_paths API Reference","link":"/api/platform_paths_api.md"},{"text":"playbooks API Reference","link":"/api/playbooks_api.md"},{"text":"plugin_lifecycle API Reference","link":"/api/plugin_lifecycle_api.md"},{"text":"policy API Reference","link":"/api/policy_api.md"},{"text":"policy_evolver API Reference","link":"/api/policy_evolver_api.md"},{"text":"preemption API Reference","link":"/api/preemption_api.md"},{"text":"presets API Reference","link":"/api/presets_api.md"},{"text":"probes API Reference","link":"/api/probes_api.md"},{"text":"probing API Reference","link":"/api/probing_api.md"},{"text":"process_registry API Reference","link":"/api/process_registry_api.md"},{"text":"projects API Reference","link":"/api/projects_api.md"},{"text":"promotion API Reference","link":"/api/promotion_api.md"},{"text":"prompts API Reference","link":"/api/prompts_api.md"},{"text":"proof_carrying API Reference","link":"/api/proof_carrying_api.md"},{"text":"protocol API Reference","link":"/api/protocol_api.md"},{"text":"provider_types API Reference","link":"/api/provider_types_api.md"},{"text":"provisioner API Reference","link":"/api/provisioner_api.md"},{"text":"prune_utils API Reference","link":"/api/prune_utils_api.md"},{"text":"quality_values API Reference","link":"/api/quality_values_api.md"},{"text":"quantum_safe API Reference","link":"/api/quantum_safe_api.md"},{"text":"queue_tui API Reference","link":"/api/queue_tui_api.md"},{"text":"rbac API Reference","link":"/api/rbac_api.md"},{"text":"red_team API Reference","link":"/api/red_team_api.md"},{"text":"refactoring API Reference","link":"/api/refactoring_api.md"},{"text":"registry API Reference","link":"/api/registry_api.md"},{"text":"relativistic API Reference","link":"/api/relativistic_api.md"},{"text":"release_packager API Reference","link":"/api/release_packager_api.md"},{"text":"remediation_planner API Reference","link":"/api/remediation_planner_api.md"},{"text":"reputation API Reference","link":"/api/reputation_api.md"},{"text":"research API Reference","link":"/api/research_api.md"},{"text":"resilience API Reference","link":"/api/resilience_api.md"},{"text":"retention API Reference","link":"/api/retention_api.md"},{"text":"role_agent API Reference","link":"/api/role_agent_api.md"},{"text":"router API Reference","link":"/api/router_api.md"},{"text":"routing API Reference","link":"/api/routing_api.md"},{"text":"routing_contracts API Reference","link":"/api/routing_contracts_api.md"},{"text":"sandbox API Reference","link":"/api/sandbox_api.md"},{"text":"scanner API Reference","link":"/api/scanner_api.md"},{"text":"schema_formal API Reference","link":"/api/schema_formal_api.md"},{"text":"scoring API Reference","link":"/api/scoring_api.md"},{"text":"scrapers API Reference","link":"/api/scrapers_api.md"},{"text":"selector API Reference","link":"/api/selector_api.md"},{"text":"self_healing API Reference","link":"/api/self_healing_api.md"},{"text":"semantic_firewall API Reference","link":"/api/semantic_firewall_api.md"},{"text":"session_scraper API Reference","link":"/api/session_scraper_api.md"},{"text":"shadow API Reference","link":"/api/shadow_api.md"},{"text":"heliosShield_bridge API Reference","link":"/api/heliosShield_bridge_api.md"},{"text":"shell_cli API Reference","link":"/api/shell_cli_api.md"},{"text":"shm API Reference","link":"/api/shm_api.md"},{"text":"shm_context API Reference","link":"/api/shm_context_api.md"},{"text":"signatures API Reference","link":"/api/signatures_api.md"},{"text":"simulation API Reference","link":"/api/simulation_api.md"},{"text":"sitback API Reference","link":"/api/sitback_api.md"},{"text":"sitback_plugins API Reference","link":"/api/sitback_plugins_api.md"},{"text":"slack API Reference","link":"/api/slack_api.md"},{"text":"slo_regulator API Reference","link":"/api/slo_regulator_api.md"},{"text":"snapshot API Reference","link":"/api/snapshot_api.md"},{"text":"speed_values API Reference","link":"/api/speed_values_api.md"},{"text":"state_machine API Reference","link":"/api/state_machine_api.md"},{"text":"storage API Reference","link":"/api/storage_api.md"},{"text":"subprocess_manager API Reference","link":"/api/subprocess_manager_api.md"},{"text":"summary API Reference","link":"/api/summary_api.md"},{"text":"support API Reference","link":"/api/support_api.md"},{"text":"swarm API Reference","link":"/api/swarm_api.md"},{"text":"swarm_consensus API Reference","link":"/api/swarm_consensus_api.md"},{"text":"swarm_memory API Reference","link":"/api/swarm_memory_api.md"},{"text":"symbolic API Reference","link":"/api/symbolic_api.md"},{"text":"sync API Reference","link":"/api/sync_api.md"},{"text":"synthesis API Reference","link":"/api/synthesis_api.md"},{"text":"task_router API Reference","link":"/api/task_router_api.md"},{"text":"tasks API Reference","link":"/api/tasks_api.md"},{"text":"teammates API Reference","link":"/api/teammates_api.md"},{"text":"tee_check API Reference","link":"/api/tee_check_api.md"},{"text":"telemetry API Reference","link":"/api/telemetry_api.md"},{"text":"tenancy API Reference","link":"/api/tenancy_api.md"},{"text":"terminal API Reference","link":"/api/terminal_api.md"},{"text":"terminal_cli API Reference","link":"/api/terminal_cli_api.md"},{"text":"thegent API Reference","link":"/api/thegent_api.md"},{"text":"thg_platform API Reference","link":"/api/thg_platform_api.md"},{"text":"tool_adapter API Reference","link":"/api/tool_adapter_api.md"},{"text":"tool_safety API Reference","link":"/api/tool_safety_api.md"},{"text":"traceability API Reference","link":"/api/traceability_api.md"},{"text":"transactions API Reference","link":"/api/transactions_api.md"},{"text":"triggers API Reference","link":"/api/triggers_api.md"},{"text":"trust API Reference","link":"/api/trust_api.md"},{"text":"tui API Reference","link":"/api/tui_api.md"},{"text":"tuning API Reference","link":"/api/tuning_api.md"},{"text":"unified_config API Reference","link":"/api/unified_config_api.md"},{"text":"universal_adapter API Reference","link":"/api/universal_adapter_api.md"},{"text":"utils API Reference","link":"/api/utils_api.md"},{"text":"v1 API Reference","link":"/api/v1_api.md"},{"text":"v2 API Reference","link":"/api/v2_api.md"},{"text":"validation API Reference","link":"/api/validation_api.md"},{"text":"value_lock API Reference","link":"/api/value_lock_api.md"},{"text":"verification API Reference","link":"/api/verification_api.md"},{"text":"verification_gate API Reference","link":"/api/verification_gate_api.md"},{"text":"watchdog API Reference","link":"/api/watchdog_api.md"},{"text":"work_stream API Reference","link":"/api/work_stream_api.md"},{"text":"worker_pool API Reference","link":"/api/worker_pool_api.md"},{"text":"xml_repair API Reference","link":"/api/xml_repair_api.md"},{"text":"zkp API Reference","link":"/api/zkp_api.md"}]},{"text":"Routing System: Project Complete Summary","link":"/reference/00_ROUTING_PROJECT_COMPLETE.md"},{"text":"Agent Identity & Sovereignty Depth (WP-6004)","link":"/reference/AGENT_IDENTITY_SOVEREIGNTY_DEPTH.md"},{"text":"Agent Communication Language (JSON-ACL) & Negotiation (WP-1006)","link":"/reference/AGENT_NEGOTIATION_ACL_DEPTH.md"},{"text":"Agent OS Principals — Depth Document","link":"/reference/AGENT_OS_PRINCIPALS_DEPTH.md"},{"text":"Benchmark Comparison: SWE-Bench vs Terminal Bench 2.0","link":"/reference/BENCHMARK_COMPARISON_SWE_BENCH_VS_TERMINAL_BENCH_2_0.md"},{"text":"Global Claude Code Instructions","link":"/reference/CLAUDE_CORE_GUIDELINES.md"},{"text":"CLAUDE Appendix: thegent-specific and domain workflow rules","link":"/reference/CLAUDE_THEGENT_RUNTIME_APPENDIX.md"},{"text":"Complete Provider Routing Map (All 12+ Providers)","link":"/reference/COMPLETE_PROVIDER_ROUTING_MAP.md"},{"text":"Constitutional Enforcement & Proof of Alignment (WP-3001)","link":"/reference/CONSTITUTIONAL_ENFORCEMENT_DEPTH.md"},{"text":"Context Management & Semantic Compression Depth (WP-5001)","link":"/reference/CONTEXT_MANAGEMENT_DEPTH.md"},{"text":"Cost Enforcement Policy: 2x Limit & Escalation Framework","link":"/reference/COST_ENFORCEMENT_POLICY.md"},{"text":"Cross-Platform Desktop Automation: API Reference","link":"/reference/CROSS_PLATFORM_API_REFERENCE.md"},{"text":"Cross-Platform Multi-Tenant Desktop Automation Quick Reference","link":"/reference/CROSS_PLATFORM_MULTI_TENANT_QUICK_REFERENCE.md"},{"text":"Dominance Proof Reference","link":"/reference/DOMINANCE_PROOF_REFERENCE.md"},{"text":"Economic Governance & Token ROI Modeling (WP-5003)","link":"/reference/ECONOMIC_GOVERNANCE_DEPTH.md"},{"text":"Frontmatter/Backmatter Integration Points","link":"/reference/FRONTMATTER_BACKMATTER_INTEGRATION_POINTS.md"},{"text":"FR Tracker: thegent","link":"/reference/FR_TRACKER.md"},{"text":"Gardener Architecture","link":"/reference/GARDENER_ARCHITECTURE.md"},{"text":"Human-Agent Collaboration (HAC) & HITL Patterns (WP-4001..4009)","link":"/reference/HAC_AND_HITL_PATTERNS.md"},{"text":"Hook Optimization Strategy","link":"/reference/HOOK_OPTIMIZATION_STRATEGY.md"},{"text":"Hybrid Mac/Windows Development Environment - Summary","link":"/reference/HYBRID_ENV_SUMMARY.md"},{"text":"Indexing and Optimization Systems — Reference","link":"/reference/INDEXING_AND_OPTIMIZATION_SYSTEMS.md"},{"text":"TaskRouter + Pareto Routing Integration Architecture","link":"/reference/INTEGRATION_ARCHITECTURE.md"},{"text":"TaskRouter + Pareto Routing Integration — Document Index","link":"/reference/INTEGRATION_INDEX.md"},{"text":"TaskRouter Integration Quick Start","link":"/reference/INTEGRATION_QUICK_START.md"},{"text":"MAIF Artifact Specification & Provenance Depth (WP-3002)","link":"/reference/MAIF_ARTIFACT_SPEC_DEPTH.md"},{"text":"MCP Tool Retry Policy","link":"/reference/MCP_RETRY_POLICY.md"},{"text":"Corrected Model Ranking Using Pareto Frontier","link":"/reference/MODEL_RANKING_CORRECTED.md"},{"text":"Model Routing Decision Tree","link":"/reference/MODEL_ROUTING_DECISION_TREE.md"},{"text":"Model Routing & Cost Governance: Complete Index","link":"/reference/MODEL_ROUTING_INDEX.md"},{"text":"Model Routing & Cost Governance: Quick Reference","link":"/reference/MODEL_ROUTING_SUMMARY.md"},{"text":"Model Routing: Terminal Bench 2.0 Quick Reference","link":"/reference/MODEL_ROUTING_TERMINAL_BENCH_2_0_QUICK_REF.md"},{"text":"Model Selection Documentation Index","link":"/reference/MODEL_SELECTION_INDEX.md"},{"text":"Monitoring Alert Rules","link":"/reference/MONITORING_ALERT_RULES.md"},{"text":"Monitoring Dashboard Specifications","link":"/reference/MONITORING_DASHBOARD_SPEC.md"},{"text":"Monitoring Metrics Reference","link":"/reference/MONITORING_METRICS_REFERENCE.md"},{"text":"Monitoring System Documentation","link":"/reference/MONITORING_README.md"},{"text":"Monitoring Setup Guide","link":"/reference/MONITORING_SETUP_GUIDE.md"},{"text":"Civilizational Multi-Swarm Hierarchy (WP-1006, WP-5004)","link":"/reference/MULTI_SWARM_HIERARCHY_DEPTH.md"},{"text":"OpenTelemetry GenAI & Observability Depth (WP-Y6)","link":"/reference/OTEL_GENAI_AND_HYSTERESIS_DEPTH.md"},{"text":"oxlint Rule Mapping Reference","link":"/reference/OXLINT_RULE_MAPPING.md"},{"text":"Pareto Frontier Algorithm: Pseudocode & Implementation Guide","link":"/reference/PARETO_ALGORITHM_PSEUDOCODE.md"},{"text":"Pareto Frontier: Executive Summary","link":"/reference/PARETO_EXECUTIVE_SUMMARY.md"},{"text":"Pareto Frontier Analysis & Model Ranking Algorithm","link":"/reference/PARETO_FRONTIER_ANALYSIS.md"},{"text":"Pareto Frontier Analysis: Complete Model Evaluation","link":"/reference/PARETO_FRONTIER_COMPLETE_ANALYSIS.md"},{"text":"Pareto Frontier Matrix: Model Selection Guide","link":"/reference/PARETO_FRONTIER_MATRIX.md"},{"text":"Pareto Frontier Quick Reference","link":"/reference/PARETO_FRONTIER_QUICK_REFERENCE.md"},{"text":"Pareto Frontier Analysis: Complete Data Table","link":"/reference/PARETO_FRONTIER_TABLE.md"},{"text":"Pareto Frontier Analysis: Terminal Bench 2.0 (Corrected)","link":"/reference/PARETO_FRONTIER_TERMINAL_BENCH_2_0.md"},{"text":"Pareto Frontier Analysis: Complete Index","link":"/reference/PARETO_INDEX.md"},{"text":"Multi-Objective Provider Routing & Pareto Fronts (WP-1004)","link":"/reference/PARETO_ROUTING_DESIGN.md"},{"text":"Pareto Frontier Visualization & Diagrams","link":"/reference/PARETO_VISUALIZATION.md"},{"text":"Phase 3.5 Quick Reference","link":"/reference/PHASE_3_5_QUICK_REFERENCE.md"},{"text":"Phase 4 UX: Operator Cockpit & Rationale Depth (WP-4001)","link":"/reference/PHASE_4_COCKPIT_UX_DEPTH.md"},{"text":"Phase 5 Scale: Redis & Distributed Robustness (WP-5004)","link":"/reference/PHASE_5_SCALE_ROBUSTNESS_DEPTH.md"},{"text":"POSIX + pwsh Shell Strategy","link":"/reference/POSIX_PWSH_SHELL_STRATEGY.md"},{"text":"Provider Limits and Auto-Fallback","link":"/reference/PROVIDER_LIMITS_AND_FALLBACK.md"},{"text":"Provider Model Behavior Constraints","link":"/reference/PROVIDER_MODEL_BEHAVIOR.md"},{"text":"Provider Model Reference","link":"/reference/PROVIDER_MODEL_REFERENCE.md"},{"text":"Robustness, Breadth, and Depth — Phase Evolution","link":"/reference/ROBUSTNESS_AND_FUTURE_DEPTH.md"},{"text":"Routing Decision Matrix: Task Category Logic","link":"/reference/ROUTING_DECISION_MATRIX.md"},{"text":"Final Routing Recommendation (Terminal Bench 2.0)","link":"/reference/ROUTING_FINAL_RECOMMENDATION.md"},{"text":"Task Routing Implementation Architecture","link":"/reference/ROUTING_IMPLEMENTATION_ARCHITECTURE.md"},{"text":"Model Routing Quick Card (Pocket Reference)","link":"/reference/ROUTING_QUICK_CARD.md"},{"text":"Routing System: Master Summary & Implementation Roadmap","link":"/reference/ROUTING_SYSTEM_MASTER_SUMMARY.md"},{"text":"Rust-Based CLI Tooling","link":"/reference/RUST_TOOLING.md"},{"text":"Agentic CI/CD & Self-Healing Loops (WP-2004)","link":"/reference/SELF_HEALING_AGENTIC_CICD_DEPTH.md"},{"text":"Planning Simulation & Replay Sandbox Depth (WP-4007, WP-12004)","link":"/reference/SIMULATION_AND_SANDBOX_DEPTH.md"},{"text":"MCP Tool SLO Targets (G-OP-08)","link":"/reference/SLO_TARGETS.md"},{"text":"Speed & Quality Index Implementation Plan","link":"/reference/SPEED_QUALITY_INDEX_IMPLEMENTATION_PLAN.md"},{"text":"Starship Prompt — Long-Term Fix for Scan Timeout","link":"/reference/STARSHIP_SETUP.md"},{"text":"Swarm Memory & Multi-Agent Coordination (WP-1006)","link":"/reference/SWARM_MEMORY_COORDINATION_DEPTH.md"},{"text":"Swarm Process Optimizations (Multi-Agent / Multi-Tenant / Multi-Project)","link":"/reference/SWARM_PROCESS_OPTIMIZATIONS.md"},{"text":"Task Categorization & AI Agent Dispatch Routing Design","link":"/reference/TASK_ROUTING_DESIGN.md"},{"text":"Terminal Bench 2.0: Corrected Pareto Frontier & Routing","link":"/reference/TERMINAL_BENCH_2_0_CORRECTED_FRONTIER.md"},{"text":"Tooling & Global Optimizations Audit (In-Depth)","link":"/reference/TOOLING_AND_GLOBAL_OPTIMIZATIONS_AUDIT.md"},{"text":"Tooling and Global Optimizations Audit","link":"/reference/TOOLING_AND_OPTIMIZATION_AUDIT.md"},{"text":"Touchpoint Integration — Deep Dive","link":"/reference/TOUCHPOINT_INTEGRATION_DEEP_DIVE.md"},{"text":"Touchpoint Integration Evaluation","link":"/reference/TOUCHPOINT_INTEGRATION_EVALUATION.md"},{"text":"Unified Work Stream — Design","link":"/reference/UNIFIED_WORK_STREAM_DESIGN.md"},{"text":"WBS Agent Progress — Claim & Coordination","link":"/reference/WBS_AGENT_PROGRESS.md"},{"text":"Unified Work Stream — Canonical","link":"/reference/WORK_STREAM.md"},{"text":"Zen (OpenCode) Integration Analysis","link":"/reference/ZEN_INTEGRATION.md"},{"text":"Reference","link":"/reference/index.md"}]},{"text":"Reports","collapsed":false,"items":[{"text":"BKM Phase 1 Completion Report","link":"/reports/BKM_PHASE_1_COMPLETION_REPORT.md"},{"text":"Critical Issue #2: Git Cache Invalidation Fix - Complete Report","link":"/reports/CACHE_INVALIDATION_FIX_REPORT.md"},{"text":"Critical Issues Fixes - Completion Report","link":"/reports/CRITICAL_FIXES_COMPLETION_REPORT.md"},{"text":"Critical Issue #2: Unsafe Git Cache Invalidation - Executive Summary","link":"/reports/CRITICAL_ISSUE_2_SUMMARY.md"},{"text":"Phase 10-12 Closure and Final Handoff Note (WP-12010)","link":"/reports/FINAL_CLOSURE_NOTE.md"},{"text":"Holistic + Harmonious Design & Integration — Implementation Complete ✅","link":"/reports/HOLISTIC_DESIGN_IMPLEMENTATION_COMPLETE.md"},{"text":"Holistic + Harmonious Design & Integration — Implementation Progress","link":"/reports/HOLISTIC_DESIGN_IMPLEMENTATION_PROGRESS.md"},{"text":"Thegent Implementation Status Report","link":"/reports/IMPLEMENTATION_STATUS.md"},{"text":"Thegent Implementation Summary","link":"/reports/IMPLEMENTATION_SUMMARY.md"},{"text":"P7.1 Verification Report: Per-Project Quality Gate Checks","link":"/reports/P7.1_VERIFICATION_REPORT.md"},{"text":"P7.2 Cross-Project Consistency Report","link":"/reports/P7.2_CROSS_PROJECT_CONSISTENCY.md"},{"text":"Phase 10-12 Closure and Handoff Note (WP-12010)","link":"/reports/PHASE_10_12_CLOSURE.md"},{"text":"Phase 13: Policy Federation Progress Report","link":"/reports/PHASE_13_PROGRESS_REPORT.md"},{"text":"Phase 14: Autonomous Learning and Cost Sensing Progress Report","link":"/reports/PHASE_14_PROGRESS_REPORT.md"},{"text":"Phase 15: Enterprise Lifecycle and Compliance Progress Report","link":"/reports/PHASE_15_PROGRESS_REPORT.md"},{"text":"Phase 3.5 Optimization Summary","link":"/reports/PHASE_3_5_SUMMARY.md"},{"text":"Phase 3.5 Optimization Validation Report","link":"/reports/PHASE_3_5_VALIDATION.md"},{"text":"Phase 3: Job Pool Implementation - Completion Summary","link":"/reports/PHASE_3_COMPLETION_SUMMARY.md"},{"text":"Phase 3 - Job Pool Implementation Report","link":"/reports/PHASE_3_JOB_POOL_IMPLEMENTATION.md"},{"text":"Phase 4: Advanced Bash Optimizations Report","link":"/reports/PHASE_4_ADVANCED_OPTIMIZATIONS.md"},{"text":"Phase 4 Implementation Summary: ESLint → oxlint Migration","link":"/reports/PHASE_4_IMPLEMENTATION_SUMMARY.md"},{"text":"Phase 4: Advanced Bash Optimizations - Implementation Summary","link":"/reports/PHASE_4_SUMMARY.md"},{"text":"🏁 Project Completion Report: thegent","link":"/reports/PROJECT_COMPLETION_REPORT.md"}]},{"text":"Research","collapsed":false,"items":[{"text":"Idea Seeds","collapsed":false,"items":[{"text":"Idea Seed Expansion — Complete","link":"/idea-seeds/IDEA_SEED_EXPANSION_COMPLETE.md"},{"text":"Idea seed: $idea prompt harvesting (Cursor/Codex/Claude)","link":"/idea-seeds/seed_cursor_20260216T103017Z_87c98b2e-9c87-459c-919e-1430c46c5b5b_199.md"},{"text":"Idea seed: $idea prompt harvesting (Cursor/Codex/Claude)","link":"/idea-seeds/seed_cursor_20260216T103017Z_87c98b2e-9c87-459c-919e-1430c46c5b5b_201.md"},{"text":"Idea seed: $idea prompt harvesting (Cursor/Codex/Claude)","link":"/idea-seeds/seed_cursor_20260216T103237Z_87c98b2e-9c87-459c-919e-1430c46c5b5b_199.md"},{"text":"Idea seed: $idea prompt harvesting (Cursor/Codex/Claude)","link":"/idea-seeds/seed_cursor_20260216T103237Z_87c98b2e-9c87-459c-919e-1430c46c5b5b_201.md"}]},{"text":"ADR-013: Multi-Org Policy Federation","link":"/research/ADR-013-POLICY-FEDERATION.md"},{"text":"ADR-014: Autonomous Learning and Cost Sensing","link":"/research/ADR-014-AUTONOMOUS-LEARNING.md"},{"text":"ADR-015: Enterprise Lifecycle and Compliance API","link":"/research/ADR-015-ENTERPRISE-COMPLIANCE.md"},{"text":"Advanced Storage, Workflow & AI Systems: Deep Comparison & Optimization Strategies","link":"/research/ADVANCED_STORAGE_WORKFLOW_AI_SYSTEMS_DEEP_COMPARISON.md"},{"text":"Advanced Strategies & Resilience — Full-Depth Research & Plan","link":"/research/ADVANCED_STRATEGIES_AND_RESILIENCE_RESEARCH.md"},{"text":"Agent Access and Optimization — Audit and Plan","link":"/research/AGENT_ACCESS_AND_OPTIMIZATION_AUDIT_PLAN.md"},{"text":"Agent Delegation Workflow","link":"/research/AGENT_DELEGATION_WORKFLOW.md"},{"text":"Agent File Search — Unified Tool Research","link":"/research/AGENT_FILE_SEARCH_UNIFIED_TOOL_RESEARCH.md"},{"text":"Agent Instructions Template","link":"/research/AGENT_INSTRUCTIONS_TEMPLATE.md"},{"text":"Agent Platforms Complete Research & Integration Guide","link":"/research/AGENT_PLATFORMS_COMPLETE.md"},{"text":"Agent Platforms: kilo, roo, OpenCode, Zen + CLIProxyAPI — Research","link":"/research/AGENT_PLATFORMS_KILO_ROO_OPencode_CLIPROXY_RESEARCH.md"},{"text":"Agent Process Architecture — Research Note","link":"/research/AGENT_PROCESS_ARCHITECTURE_RESEARCH.md"},{"text":"Complete Package Optimization Research - All Installed Packages","link":"/research/ALL_PACKAGES_OPTIMIZATION.md"},{"text":"API, CLI, and DevOps Documentation Tools Research Report","link":"/research/API_CLI_DEVOPS_TOOLING.md"},{"text":"Batch 2 Optimizations - Implementation Summary","link":"/research/BATCH_2_OPTIMIZATIONS.md"},{"text":"Batch 3 Optimizations - Complete ✅","link":"/research/BATCH_3_COMPLETE.md"},{"text":"Batch 3 Optimizations - Planning","link":"/research/BATCH_3_PLAN.md"},{"text":"Batch 4 Optimizations - Complete ✅","link":"/research/BATCH_4_COMPLETE.md"},{"text":"Caching, Indexing & Pre-warming Complete Practical Guide","link":"/research/CACHING_COMPLETE.md"},{"text":"Caching, Indexing & Pre-warming: Deep Research & Strategies","link":"/research/CACHING_INDEXING_PREWARMING_DEEP_RESEARCH.md"},{"text":"Chat Session Wait Pattern","link":"/research/CHAT_SESSION_WAIT_PATTERN.md"},{"text":"CI/CD and Developer Experience Tooling Research Report (2025-2026)","link":"/research/CI_CD_DEVX_TOOLING.md"},{"text":"Multi-Agent Feature Parity Audit","link":"/research/CLAUDE_CODE_FEATURE_PARITY_AUDIT.md"},{"text":"Claude Code: Queue Pending & Blocking Messages (Research & Plan)","link":"/research/CLAUDE_CODE_QUEUE_PENDING_BLOCKING.md"},{"text":"Claude Code Plan & Delegate Modes — Deep Research for thegent Tooling","link":"/research/CLAUDE_PLAN_DELEGATE_MODES_RESEARCH.md"},{"text":"Client-Side Software Package Design & Deployment Research","link":"/research/CLIENT_SIDE_PACKAGE_DESIGN_RESEARCH.md"},{"text":"Codex Hooks, Notifications & Extension Options","link":"/research/CODEX_HOOKS_AND_EXTENSION_OPTIONS.md"},{"text":"Codex + CLIProxyAPIPlus: Research and Plan","link":"/research/CODEX_MINIMAX_CLIPROXY_RESEARCH_AND_PLAN.md"},{"text":"Comprehensive Non-Canonical Audit and Consolidation Plan","link":"/research/COMPREHENSIVE_NON_CANONICAL_AUDIT.md"},{"text":"Continuous Improvement Embedding — Complete","link":"/research/CONTINUOUS_IMPROVEMENT_EMBEDDING_COMPLETE.md"},{"text":"Conversation Dump — 2026-02-16","link":"/research/CONVERSATION_DUMP_2026-02-16.md"},{"text":"Conversation Dump Complete — 2026-02-16 Structured & Expanded","link":"/research/CONVERSATION_DUMP_2026-02-16_COMPLETE.md"},{"text":"Conversation Dump 2026-02-16 — Complete Expansion","link":"/research/CONVERSATION_DUMP_2026-02-16_EXPANDED.md"},{"text":"Cost-Based Routing — Deferred Scope","link":"/research/COST_ROUTING_DEFERRED.md"},{"text":"Cost Routing Deferred — Formal Decision Record","link":"/research/COST_ROUTING_DEFERRED_EXPANDED.md"},{"text":"Cross-Platform Multi-Tenant Desktop Automation: Advanced Patterns","link":"/research/CROSS_PLATFORM_ADVANCED_PATTERNS.md"},{"text":"Cross-Platform Extensions: Wider, Deeper, Polish & Optimization","link":"/research/CROSS_PLATFORM_EXTENSIONS_WIDER_DEEPER_OPTIMIZATION.md"},{"text":"Cross-Platform Gaps and Extensions — Research & Plan","link":"/research/CROSS_PLATFORM_GAPS_AND_EXTENSIONS_RESEARCH.md"},{"text":"Cross-Platform Desktop Automation: Integration Guide","link":"/research/CROSS_PLATFORM_INTEGRATION_GUIDE.md"},{"text":"Cross-Platform Multi-Tenant Desktop Automation Research & Plan","link":"/research/CROSS_PLATFORM_MULTI_TENANT_DESKTOP_AUTOMATION_RESEARCH.md"},{"text":"Cross-Platform Desktop Automation: Performance Benchmarks & SLAs","link":"/research/CROSS_PLATFORM_PERFORMANCE_BENCHMARKS.md"},{"text":"Cross-Platform Research Complete — Comprehensive Consolidated Guide","link":"/research/CROSS_PLATFORM_RESEARCH_COMPLETE.md"},{"text":"Cross-Platform Desktop Automation: Research Completion Summary","link":"/research/CROSS_PLATFORM_RESEARCH_COMPLETION_SUMMARY.md"},{"text":"Cross-Platform Research — Consolidated Comprehensive Guide","link":"/research/CROSS_PLATFORM_RESEARCH_CONSOLIDATED.md"},{"text":"Cross-Platform Desktop Automation: Research Index","link":"/research/CROSS_PLATFORM_RESEARCH_INDEX.md"},{"text":"Cross-Platform Multi-Tenant Desktop Automation: Research Summary","link":"/research/CROSS_PLATFORM_RESEARCH_SUMMARY.md"},{"text":"Cross-Platform Desktop Automation: Security Deep Dive","link":"/research/CROSS_PLATFORM_SECURITY_DEEP_DIVE.md"},{"text":"Cross-Project Analysis — Complete Summary","link":"/research/CROSS_PROJECT_ANALYSIS_COMPLETE.md"},{"text":"Cross-Project Deep Expanded Analysis","link":"/research/CROSS_PROJECT_DEEP_EXPANDED_ANALYSIS.md"},{"text":"Cross-Project Feature Borrowing Plan","link":"/research/CROSS_PROJECT_FEATURE_BORROWING_PLAN.md"},{"text":"Cross-Project Integration Guide — Kush Ecosystem","link":"/research/CROSS_PROJECT_INTEGRATION_GUIDE.md"},{"text":"Cross-Project Patterns Catalog","link":"/research/CROSS_PROJECT_PATTERNS_CATALOG.md"},{"text":"Cross-Project Work Stream Analysis","link":"/research/CROSS_PROJECT_WORK_STREAM_ANALYSIS.md"},{"text":"Delegation Friction Audit","link":"/research/DELEGATION_FRICTION_AUDIT.md"},{"text":"Agent Delegation Session - 2026-02-17","link":"/research/DELEGATION_SESSION_2026-02-17.md"},{"text":"Agent Delegation Status - 2026-02-17","link":"/research/DELEGATION_STATUS_2026-02-17.md"},{"text":"Documentation System — Design Polish Implementation Summary","link":"/research/DESIGN_POLISH_IMPLEMENTATION.md"},{"text":"Documentation System — Design Polish & Intuitive Robust Design Plan","link":"/research/DESIGN_POLISH_PLAN.md"},{"text":"Documentation Generation & Site System — Complete Research & Plan","link":"/research/DOCGEN_DOCSITE_COMPLETE.md"},{"text":"Documentation System — Completion Summary","link":"/research/DOCGEN_DOCSITE_COMPLETION_SUMMARY.md"},{"text":"Documentation Generation & Site System — Deep Audit & Improvement Plan","link":"/research/DOCGEN_DOCSITE_DEEP_AUDIT.md"},{"text":"Extended Web Research — Key Findings & Actionable Insights","link":"/research/DOCGEN_DOCSITE_EXTENDED_RESEARCH_SUMMARY.md"},{"text":"Documentation Generation & Site System — Extended Web Research","link":"/research/DOCGEN_DOCSITE_EXTENDED_WEB_RESEARCH.md"},{"text":"Documentation Generation & Site System — Comprehensive Improvement Plan","link":"/research/DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md"},{"text":"Documentation System — Phase 1 Implementation Complete","link":"/research/DOCGEN_DOCSITE_PHASE1_IMPLEMENTATION.md"},{"text":"Documentation Generation & Site System — Research Summary","link":"/research/DOCGEN_DOCSITE_RESEARCH_SUMMARY.md"},{"text":"Doctor Command: OAuth-Only Authentication Update","link":"/research/DOCTOR_OAUTH_ONLY_UPDATE.md"},{"text":"DX/UX/AX Friction Improvements - 2026-02-18","link":"/research/DX_FRICTION_IMPROVEMENTS_2026-02-18.md"},{"text":"DX/UX/AX Friction Improvements - Session 2 (2026-02-18)","link":"/research/DX_FRICTION_SESSION_2_2026-02-18.md"},{"text":"DX/UX/AX Continuous Improvement System","link":"/research/DX_UX_AX_CONTINUOUS_IMPROVEMENT_SYSTEM.md"},{"text":"ESLint → oxlint Migration Audit (Phase 4)","link":"/research/ESLINT_AUDIT.md"},{"text":"Expansion Complete — Final Report","link":"/research/EXPANSION_COMPLETE_FINAL.md"},{"text":"Expansion Phase — Complete Summary","link":"/research/EXPANSION_PHASE_COMPLETE.md"},{"text":"FastMCP ASGI Uni-Mount System Plan","link":"/research/FASTMCP_ASGI_UNI_MOUNT_PLAN.md"},{"text":"FastMCP Complete — Comprehensive Implementation Guide","link":"/research/FASTMCP_COMPLETE.md"},{"text":"FastMCP Elicitation & Context API Summary","link":"/research/FASTMCP_ELICITATION_CONTEXT.md"},{"text":"FastMCP Features & MCP Transport Spec Gaps","link":"/research/FASTMCP_FEATURES_AND_TRANSPORT_GAPS.md"},{"text":"FastMCP Implementation Guide for thegent","link":"/research/FASTMCP_IMPLEMENTATION_GUIDE.md"},{"text":"FastMCP Middleware","link":"/research/FASTMCP_MIDDLEWARE.md"},{"text":"FastMCP Progress & Tasks API Summary","link":"/research/FASTMCP_PROGRESS_TASKS.md"},{"text":"FastMCP Sampling & Telemetry","link":"/research/FASTMCP_SAMPLING_TELEMETRY.md"},{"text":"FastMCP Spec Deep Dive","link":"/research/FASTMCP_SPEC_DEEP_DIVE.md"},{"text":"FastMCP Storage Backends & EventStore","link":"/research/FASTMCP_STORAGE_EVENTSTORE.md"},{"text":"FastMCP Transforms & Deployment Summary","link":"/research/FASTMCP_TRANSFORMS_DEPLOYMENT.md"},{"text":"Fast Process Monitoring - Research & Implementation","link":"/research/FAST_PROCESS_MONITORING.md"},{"text":"Final Expansion Report — Complete","link":"/research/FINAL_EXPANSION_REPORT.md"},{"text":"Friction Points Log","link":"/research/FRICTION_LOG.md"},{"text":"Friction Points Log - 2026-02-18","link":"/research/FRICTION_LOG_2026-02-18.md"},{"text":"Friction Points Identified During Work Stream Processing","link":"/research/FRICTION_POINTS_IDENTIFIED.md"},{"text":"Git Shim Starship Optimization — Fix for 8+ Minute Prompt Delays","link":"/research/GIT_SHIM_STARSHIP_OPTIMIZATION.md"},{"text":"Git Tooling Audit and Modernization Plan","link":"/research/GIT_TOOLING_AUDIT_AND_PLAN.md"},{"text":"Governance, Policy Enforcement, and Audit Trail Research","link":"/research/GOVERNANCE_POLICY_AUDIT_RESEARCH.md"},{"text":"Governance WP Gaps — Implementation Notes","link":"/research/GOVERNANCE_WP_GAPS.md"},{"text":"Governance WP Gaps — Expanded & BACKLOG Items","link":"/research/GOVERNANCE_WP_GAPS_EXPANDED.md"},{"text":"Hook Rust Migration Complete — Comprehensive Migration Strategy & Timeline","link":"/research/HOOK_RUST_MIGRATION_COMPLETE.md"},{"text":"Hook Runtime Rust Migration: Research Synthesis","link":"/research/HOOK_RUST_MIGRATION_RESEARCH_SYNTHESIS.md"},{"text":"Hook Runtime Rust Migration — Complete Expansion","link":"/research/HOOK_RUST_MIGRATION_RESEARCH_SYNTHESIS_EXPANDED.md"},{"text":"Idea Seeds & Session Storage","link":"/research/IDEA_SEEDS_SESSION_STORAGE.md"},{"text":"Idea Seed Review Complete — Consolidation & Rationale","link":"/research/IDEA_SEED_REVIEW_COMPLETE.md"},{"text":"Index Sprawl Status Update — Complete","link":"/research/INDEX_SPRAWL_STATUS_UPDATE.md"},{"text":"Integration Examples — Kush Ecosystem","link":"/research/INTEGRATION_EXAMPLES.md"},{"text":"In-Depth Tooling and Global Optimizations Audit (2026-02-15)","link":"/research/IN_DEPTH_TOOLING_AUDIT_2026.md"},{"text":"Kush Ecosystem — Architecture Diagram","link":"/research/KUSH_ECOSYSTEM_ARCHITECTURE_DIAGRAM.md"},{"text":"Kush Ecosystem — Complete Documentation Index","link":"/research/KUSH_ECOSYSTEM_COMPLETE.md"},{"text":"Kush Ecosystem — Comprehensive Deep Dive Analysis","link":"/research/KUSH_ECOSYSTEM_DEEP_DIVE.md"},{"text":"Kush Ecosystem — Implementation Status","link":"/research/KUSH_ECOSYSTEM_IMPLEMENTATION_STATUS.md"},{"text":"Kush Ecosystem — Unified Documentation Index","link":"/research/KUSH_ECOSYSTEM_UNIFIED_DOCS_INDEX.md"},{"text":"Library Cache Migration Plan","link":"/research/LIBRARY_CACHE_MIGRATION_PLAN.md"},{"text":"Library-First Audit and Plan","link":"/research/LIBRARY_FIRST_AUDIT_AND_PLAN.md"},{"text":"Library Replacement Audit — Deep & Wide","link":"/research/LIBRARY_REPLACEMENT_AUDIT_DEEP.md"},{"text":"Library Replacement Complete — Comprehensive Audit & Migration Plan","link":"/research/LIBRARY_REPLACEMENT_COMPLETE.md"},{"text":"Library Replacement — Consolidated Migration Plan","link":"/research/LIBRARY_REPLACEMENT_CONSOLIDATED.md"},{"text":"Library Replacement — Phase Design Work Breakdowns (DWBs)","link":"/research/LIBRARY_REPLACEMENT_PHASE_DWBS.md"},{"text":"Markdown Documentation — Completion Summary","link":"/research/MARKDOWN_COMPLETION_SUMMARY.md"},{"text":"Master Expansion TODO — Complete Documentation Sprawl","link":"/research/MASTER_EXPANSION_TODO.md"},{"text":"MCP Full Parity & FastMCP Transport Spec Audit","link":"/research/MCP_FULL_PARITY_AND_FASTMCP_AUDIT.md"},{"text":"MCP and Client Features for Session Notifications","link":"/research/MCP_NOTIFICATION_OPTIONS.md"},{"text":"MD Documentation Normalization Guide","link":"/research/MD_NORMALIZATION_GUIDE.md"},{"text":"Memory Optimization — Long-Term Plan","link":"/research/MEMORY_OPTIMIZATION_LONG_TERM_PLAN.md"},{"text":"Multi-Platform Agent Deep Dive","link":"/research/MULTI_PLATFORM_DEEP_DIVE.md"},{"text":"Next 5 Work Items Summary","link":"/research/NEXT_5_WORK_ITEMS_SUMMARY.md"},{"text":"OpenClaw / Agent Zero as Main Agent — Research","link":"/research/OPENCLAW_AGENTZERO_AS_MAIN_AGENT_RESEARCH.md"},{"text":"OpenClaw, ClawHub, Agent Zero — Use Cases for thegent","link":"/research/OPENCLAW_CLAWHUB_AGENTZERO_USE_CASES.md"},{"text":"Package Optimization Implementation Status","link":"/research/OPTIMIZATION_IMPLEMENTATION_STATUS.md"},{"text":"Package Optimization Migration Guide","link":"/research/OPTIMIZATION_MIGRATION_GUIDE.md"},{"text":"Priority 1 (P1) Expansion — Complete","link":"/research/P1_EXPANSION_COMPLETE.md"},{"text":"Priority 1 (P1) Phase — Complete","link":"/research/P1_PHASE_COMPLETE.md"},{"text":"P3 Polish Complete — Full Research Docs","link":"/research/P3_POLISH_COMPLETE.md"},{"text":"P4 Normalization — Complete","link":"/research/P4_NORMALIZATION_COMPLETE.md"},{"text":"P4 Normalization — Final Status","link":"/research/P4_NORMALIZATION_FINAL.md"},{"text":"P4 Normalization Progress — All MD Docs","link":"/research/P4_NORMALIZATION_PROGRESS.md"},{"text":"P4 Normalization Summary — Complete","link":"/research/P4_NORMALIZATION_SUMMARY.md"},{"text":"P4 Normalization Update — Progress Report","link":"/research/P4_NORMALIZATION_UPDATE.md"},{"text":"Package Design Research Summary","link":"/research/PACKAGE_DESIGN_RESEARCH_SUMMARY.md"},{"text":"Package Optimization Research - Modern Alternatives & Performance Improvements","link":"/research/PACKAGE_OPTIMIZATION_RESEARCH.md"},{"text":"Phase Documents — Complete Expansion","link":"/research/PHASE_DOCUMENTS_EXPANDED.md"},{"text":"Plan Usage and Budget Research","link":"/research/PLAN_USAGE_AND_BUDGET_RESEARCH.md"},{"text":"Proactive Governance Evolution Plan","link":"/research/PROACTIVE_GOVERNANCE_EVOLUTION_PLAN.md"},{"text":"Production Packaging, Polish & Optimization Audit + Plan","link":"/research/PRODUCTION_PACKAGING_POLISH_OPTIMIZATION_AUDIT_AND_PLAN.md"},{"text":"Python Frontmatter + Native Backmatter: Research Audit & Plan","link":"/research/PYTHON_FRONTMATTER_NATIVE_BACKMATTER_AUDIT_PLAN.md"},{"text":"Qwen3.5 Plus 02-15 on OpenRouter — Pareto Research","link":"/research/QWEN3.5_PLUS_OPENROUTER_PARETO_RESEARCH.md"},{"text":"Remaining Markdown Files — Completion Status","link":"/research/REMAINING_MARKDOWN_COMPLETION.md"},{"text":"Remove Directory Dependencies — Production Installation Optimization","link":"/research/REMOVE_DIRECTORY_DEPENDENCIES_AUDIT_AND_PLAN.md"},{"text":"Research, Seed & Fragment Inventory — Sprawl Todo & Unified Work Stream","link":"/research/RESEARCH_SEED_FRAGMENT_INVENTORY_AND_SPRAWL_TODO.md"},{"text":"Runtime Infrastructure: Existing Solutions Audit & Integration Plan","link":"/research/RUNTIME_INFRASTRUCTURE_EXISTING_SOLUTIONS_AUDIT_AND_INTEGRATION_PLAN.md"},{"text":"Runtime Infrastructure Implementation: Complete","link":"/research/RUNTIME_INFRASTRUCTURE_IMPLEMENTATION_COMPLETE.md"},{"text":"Runtime Infrastructure Integration: Phase 2 Complete","link":"/research/RUNTIME_INFRASTRUCTURE_INTEGRATION_PHASE2_COMPLETE.md"},{"text":"Runtime Infrastructure Integration: Phase 3 Complete","link":"/research/RUNTIME_INFRASTRUCTURE_INTEGRATION_PHASE3_COMPLETE.md"},{"text":"Runtime Infrastructure Resource Leaks & Optimization Audit & Plan","link":"/research/RUNTIME_INFRASTRUCTURE_RESOURCE_LEAKS_AUDIT_AND_PLAN.md"},{"text":"Runtime Infrastructure Solutions: Executive Summary","link":"/research/RUNTIME_INFRASTRUCTURE_SOLUTIONS_SUMMARY.md"},{"text":"\\"See Also\\" Section Template","link":"/research/SEE_ALSO_TEMPLATE.md"},{"text":"Self-Optimization Instructions Added to CLAUDE.md","link":"/research/SELF_OPTIMIZATION_INSTRUCTIONS_ADDED.md"},{"text":"Session Research Complete — Comprehensive Deep-Dive","link":"/research/SESSION_RESEARCH_COMPLETE.md"},{"text":"Session Research Fragments — 2026-02-15","link":"/research/SESSION_RESEARCH_FRAGMENTS.md"},{"text":"Session Research Fragments — Complete Expansion","link":"/research/SESSION_RESEARCH_FRAGMENTS_EXPANDED.md"},{"text":"Session Summary - 2026-02-17","link":"/research/SESSION_SUMMARY_2026-02-17.md"},{"text":"Session Wait Loop Setup","link":"/research/SESSION_WAIT_LOOP_SETUP.md"},{"text":"Shared MCP Tool Library — Design Specification","link":"/research/SHARED_MCP_TOOL_LIBRARY.md"},{"text":"Shell Configuration Audit and Consolidation Plan","link":"/research/SHELL_CONFIG_AUDIT_AND_CONSOLIDATION_PLAN.md"},{"text":"Shell Error Fixes — zsh Bad Substitution","link":"/research/SHELL_ERROR_FIXES.md"},{"text":"Shell Startup Optimization Fix","link":"/research/SHELL_STARTUP_OPTIMIZATION_FIX.md"},{"text":"Smart & Robust Process Strategies — Research & Plan","link":"/research/SMART_ROBUST_STRATEGIES_RESEARCH.md"},{"text":"Swarm Management Complete Research & Implementation Guide","link":"/research/SWARM_COMPLETE.md"},{"text":"Swarm Optimization, Management & Scheduling — Deep Research","link":"/research/SWARM_OPTIMIZATION_SCHEDULING_DEEP_RESEARCH.md"},{"text":"Swarm Process Automation — Deep Research & Plan","link":"/research/SWARM_PROCESS_AUTOMATION_DEEP_RESEARCH.md"},{"text":"Swarm & Resource Optimization — Research Index","link":"/research/SWARM_RESEARCH_INDEX.md"},{"text":"System Resources Complete Practical Guide","link":"/research/SYSTEM_RESOURCES_COMPLETE.md"},{"text":"System Resources (FD, CPU, Threads, Ports) — Full-Depth Research & Plan","link":"/research/SYSTEM_RESOURCES_FD_CPU_DEEP_RESEARCH.md"},{"text":"TASK I/O System Improvement Research & Plan","link":"/research/TASK_IO_IMPROVEMENT_RESEARCH_AND_PLAN.md"},{"text":"Thegent Teammates: Research and Implementation Plan (2026-02-15)","link":"/research/TEAMMATES_RESEARCH_AND_PLAN.md"},{"text":"Tenacity vs Custom Retry — Audit & Plan","link":"/research/TENACITY_RETRY_AUDIT_PLAN.md"},{"text":"Thegent Command Model Options and Agent Features Research","link":"/research/THGENT_COMMAND_MODEL_OPTIONS_AND_AGENT_FEATURES_RESEARCH.md"},{"text":"Thegent Documentation Update Summary","link":"/research/THGENT_DOCUMENTATION_UPDATE_SUMMARY.md"},{"text":"TUI Compositor Comparison Research","link":"/research/TUI_COMPOSITOR_COMPARISON.md"},{"text":"Unified Agent Registry API — Design Specification","link":"/research/UNIFIED_AGENT_REGISTRY_API.md"},{"text":"Unified Work Stream Integration — Complete","link":"/research/UNIFIED_WORK_STREAM_INTEGRATION.md"},{"text":"User Queue + TUI: Editable Prompts While Agent Runs","link":"/research/USER_QUEUE_TUI_AND_AGENT_POLL.md"},{"text":"VitePress Enhancements Research Report (2025-2026)","link":"/research/VITEPRESS_ENHANCEMENTS.md"},{"text":"VitePress Rich Documentation — Final Status","link":"/research/VITEPRESS_FINAL_STATUS.md"},{"text":"VitePress Rich Documentation — ✅ IMPLEMENTATION COMPLETE","link":"/research/VITEPRESS_IMPLEMENTATION_COMPLETE.md"},{"text":"VitePress Phase 1 Implementation — ✅ COMPLETE","link":"/research/VITEPRESS_PHASE1_COMPLETE.md"},{"text":"VitePress Phase 1 Implementation — Status","link":"/research/VITEPRESS_PHASE1_IMPLEMENTATION.md"},{"text":"VitePress Phase 2 Implementation — Status","link":"/research/VITEPRESS_PHASE2_IMPLEMENTATION.md"},{"text":"VitePress Phase 3 Implementation — ✅ COMPLETE","link":"/research/VITEPRESS_PHASE3_COMPLETE.md"},{"text":"VitePress Rich Documentation Audit & Implementation Plan","link":"/research/VITEPRESS_RICH_DOCUMENTATION_AUDIT.md"},{"text":"VitePress Rich Documentation — Implementation Plan","link":"/research/VITEPRESS_RICH_DOCUMENTATION_IMPLEMENTATION_PLAN.md"},{"text":"Workflow Improvement Session - 2026-02-17","link":"/research/WORKFLOW_IMPROVEMENT_SESSION_2026-02-17.md"},{"text":"Work Stream Processing Session — 2026-02-18","link":"/research/WORKSTREAM_PROCESSING_SESSION_2026-02-18.md"},{"text":"Work Stream Processing with Continuous Improvements","link":"/research/WORKSTREAM_PROCESSING_WITH_IMPROVEMENTS.md"},{"text":"Workstream Processing Session Summary - 2026-02-18","link":"/research/WORKSTREAM_SESSION_SUMMARY_2026-02-18.md"},{"text":"Work Stream Sync/Update/Audit Coverage - Batch 1","link":"/research/WORK_STREAM_SYNC_UPDATE_AUDIT_COVERAGE_BATCH_1.md"},{"text":"Phase 13: Compliance Profile Mapping","link":"/research/phase13-compliance-profile-mapping.md"},{"text":"Phase 13: Cost Sensitivity Experiment Plan","link":"/research/phase13-cost-sensitivity-experiment-plan.md"},{"text":"Phase 13: Policy Federation Surface Map","link":"/research/phase13-policy-federation-surface-map.md"},{"text":"Phase 13: Tenant Boundary Test Matrix","link":"/research/phase13-tenant-boundary-test-matrix.md"},{"text":"Phase 14: Autonomous Learning and Cost Sensing Surface Map","link":"/research/phase14-autonomous-learning-surface-map.md"},{"text":"Phase 14: Cost Sensing and Learning Test Matrix","link":"/research/phase14-cost-sensing-test-matrix.md"},{"text":"Phase 15: Enterprise Compliance Test Matrix","link":"/research/phase15-enterprise-compliance-test-matrix.md"},{"text":"Phase 15: Enterprise Lifecycle and Compliance Surface Map","link":"/research/phase15-enterprise-lifecycle-surface-map.md"}]},{"text":"Scratchpad","collapsed":false,"items":[{"text":"Session Scratch Board & Optimization Plan","link":"/scratchpad/session_review.md"}]},{"text":"Cross-Project Agent Instructions","link":"/docs/AGENT_INSTRUCTIONS.md"},{"text":"Architecture Layers (G-KD-05)","link":"/docs/ARCHITECTURE_LAYERS.md"},{"text":"Cross-Platform Desktop Automation: Master Document Index","link":"/docs/CROSS_PLATFORM_MASTER_INDEX.md"},{"text":"Discovery Surface (G-DS)","link":"/docs/DISCOVERY.md"},{"text":"Document Queue Integration Guide","link":"/docs/DOCUMENT_QUEUE_INTEGRATION.md"},{"text":"FastMCP Deployment Guide (G-FM-01 Phase 5)","link":"/docs/FASTMCP_DEPLOYMENT_GUIDE.md"},{"text":"FastMCP Graceful Shutdown (G-OP-10)","link":"/docs/FASTMCP_GRACEFUL_SHUTDOWN.md"},{"text":"FastMCP Icons and UX Hints (G-FM-04)","link":"/docs/FASTMCP_ICONS_UX_HINTS.md"},{"text":"FastMCP Optimization & Polish Audit (G-OP-04–G-OP-10)","link":"/docs/FASTMCP_OPTIMIZATION_AUDIT.md"},{"text":"FastMCP Phase Checklist Verification (G-FM-06)","link":"/docs/FASTMCP_PHASE_CHECKLIST_VERIFICATION.md"},{"text":"FastMCP Testing Strategy (G-FM-05)","link":"/docs/FASTMCP_TESTING_STRATEGY.md"},{"text":"Thegent Gap Analysis & Remediation Plan","link":"/docs/GAP_ANALYSIS_AND_REMEDIATION.md"},{"text":"Governance WP Implementation Verification (G-GP-01–09)","link":"/docs/GOVERNANCE_WP_VERIFICATION.md"},{"text":"Multi-Agent Orchestration Mode Catalog","link":"/docs/MULTI_AGENT_MODE_CATALOG.md"},{"text":"Thegent Orchestration Optimization Program (v1.0)","link":"/docs/ORCHESTRATION.md"},{"text":"Planning Simulation Design (G-CA-04)","link":"/docs/PLANNING_SIMULATION_DESIGN.md"},{"text":"Post-Launch Observation Playbook","link":"/docs/POST_LAUNCH_OBSERVATION_PLAYBOOK.md"},{"text":"Thegent Orchestration Runbook (v1.0)","link":"/docs/RUNBOOK.md"},{"text":"Setup Restore — Long-term Fixes Applied","link":"/docs/SETUP-RESTORE.md"},{"text":"State-Aware Orchestration Design","link":"/docs/STATE_AWARE_ORCHESTRATION_DESIGN.md"},{"text":"Thegent FastMCP Verification Runbook","link":"/docs/VERIFICATION_RUNBOOK.md"},{"text":"CLI Command Reference","link":"/docs/cli-examples.md"},{"text":"Cross-Project Links Test","link":"/docs/cross-links-test.md"},{"text":"Index","link":"/docs/index.md"},{"text":"Test Callouts","link":"/docs/test-callouts.md"}],"/research/":[{"text":"Idea Seeds","collapsed":false,"items":[{"text":"Idea Seed Expansion — Complete","link":"/idea-seeds/IDEA_SEED_EXPANSION_COMPLETE.md"},{"text":"Idea seed: $idea prompt harvesting (Cursor/Codex/Claude)","link":"/idea-seeds/seed_cursor_20260216T103017Z_87c98b2e-9c87-459c-919e-1430c46c5b5b_199.md"},{"text":"Idea seed: $idea prompt harvesting (Cursor/Codex/Claude)","link":"/idea-seeds/seed_cursor_20260216T103017Z_87c98b2e-9c87-459c-919e-1430c46c5b5b_201.md"},{"text":"Idea seed: $idea prompt harvesting (Cursor/Codex/Claude)","link":"/idea-seeds/seed_cursor_20260216T103237Z_87c98b2e-9c87-459c-919e-1430c46c5b5b_199.md"},{"text":"Idea seed: $idea prompt harvesting (Cursor/Codex/Claude)","link":"/idea-seeds/seed_cursor_20260216T103237Z_87c98b2e-9c87-459c-919e-1430c46c5b5b_201.md"}]},{"text":"ADR-013: Multi-Org Policy Federation","link":"/research/ADR-013-POLICY-FEDERATION.md"},{"text":"ADR-014: Autonomous Learning and Cost Sensing","link":"/research/ADR-014-AUTONOMOUS-LEARNING.md"},{"text":"ADR-015: Enterprise Lifecycle and Compliance API","link":"/research/ADR-015-ENTERPRISE-COMPLIANCE.md"},{"text":"Advanced Storage, Workflow & AI Systems: Deep Comparison & Optimization Strategies","link":"/research/ADVANCED_STORAGE_WORKFLOW_AI_SYSTEMS_DEEP_COMPARISON.md"},{"text":"Advanced Strategies & Resilience — Full-Depth Research & Plan","link":"/research/ADVANCED_STRATEGIES_AND_RESILIENCE_RESEARCH.md"},{"text":"Agent Access and Optimization — Audit and Plan","link":"/research/AGENT_ACCESS_AND_OPTIMIZATION_AUDIT_PLAN.md"},{"text":"Agent Delegation Workflow","link":"/research/AGENT_DELEGATION_WORKFLOW.md"},{"text":"Agent File Search — Unified Tool Research","link":"/research/AGENT_FILE_SEARCH_UNIFIED_TOOL_RESEARCH.md"},{"text":"Agent Instructions Template","link":"/research/AGENT_INSTRUCTIONS_TEMPLATE.md"},{"text":"Agent Platforms Complete Research & Integration Guide","link":"/research/AGENT_PLATFORMS_COMPLETE.md"},{"text":"Agent Platforms: kilo, roo, OpenCode, Zen + CLIProxyAPI — Research","link":"/research/AGENT_PLATFORMS_KILO_ROO_OPencode_CLIPROXY_RESEARCH.md"},{"text":"Agent Process Architecture — Research Note","link":"/research/AGENT_PROCESS_ARCHITECTURE_RESEARCH.md"},{"text":"Complete Package Optimization Research - All Installed Packages","link":"/research/ALL_PACKAGES_OPTIMIZATION.md"},{"text":"API, CLI, and DevOps Documentation Tools Research Report","link":"/research/API_CLI_DEVOPS_TOOLING.md"},{"text":"Batch 2 Optimizations - Implementation Summary","link":"/research/BATCH_2_OPTIMIZATIONS.md"},{"text":"Batch 3 Optimizations - Complete ✅","link":"/research/BATCH_3_COMPLETE.md"},{"text":"Batch 3 Optimizations - Planning","link":"/research/BATCH_3_PLAN.md"},{"text":"Batch 4 Optimizations - Complete ✅","link":"/research/BATCH_4_COMPLETE.md"},{"text":"Caching, Indexing & Pre-warming Complete Practical Guide","link":"/research/CACHING_COMPLETE.md"},{"text":"Caching, Indexing & Pre-warming: Deep Research & Strategies","link":"/research/CACHING_INDEXING_PREWARMING_DEEP_RESEARCH.md"},{"text":"Chat Session Wait Pattern","link":"/research/CHAT_SESSION_WAIT_PATTERN.md"},{"text":"CI/CD and Developer Experience Tooling Research Report (2025-2026)","link":"/research/CI_CD_DEVX_TOOLING.md"},{"text":"Multi-Agent Feature Parity Audit","link":"/research/CLAUDE_CODE_FEATURE_PARITY_AUDIT.md"},{"text":"Claude Code: Queue Pending & Blocking Messages (Research & Plan)","link":"/research/CLAUDE_CODE_QUEUE_PENDING_BLOCKING.md"},{"text":"Claude Code Plan & Delegate Modes — Deep Research for thegent Tooling","link":"/research/CLAUDE_PLAN_DELEGATE_MODES_RESEARCH.md"},{"text":"Client-Side Software Package Design & Deployment Research","link":"/research/CLIENT_SIDE_PACKAGE_DESIGN_RESEARCH.md"},{"text":"Codex Hooks, Notifications & Extension Options","link":"/research/CODEX_HOOKS_AND_EXTENSION_OPTIONS.md"},{"text":"Codex + CLIProxyAPIPlus: Research and Plan","link":"/research/CODEX_MINIMAX_CLIPROXY_RESEARCH_AND_PLAN.md"},{"text":"Comprehensive Non-Canonical Audit and Consolidation Plan","link":"/research/COMPREHENSIVE_NON_CANONICAL_AUDIT.md"},{"text":"Continuous Improvement Embedding — Complete","link":"/research/CONTINUOUS_IMPROVEMENT_EMBEDDING_COMPLETE.md"},{"text":"Conversation Dump — 2026-02-16","link":"/research/CONVERSATION_DUMP_2026-02-16.md"},{"text":"Conversation Dump Complete — 2026-02-16 Structured & Expanded","link":"/research/CONVERSATION_DUMP_2026-02-16_COMPLETE.md"},{"text":"Conversation Dump 2026-02-16 — Complete Expansion","link":"/research/CONVERSATION_DUMP_2026-02-16_EXPANDED.md"},{"text":"Cost-Based Routing — Deferred Scope","link":"/research/COST_ROUTING_DEFERRED.md"},{"text":"Cost Routing Deferred — Formal Decision Record","link":"/research/COST_ROUTING_DEFERRED_EXPANDED.md"},{"text":"Cross-Platform Multi-Tenant Desktop Automation: Advanced Patterns","link":"/research/CROSS_PLATFORM_ADVANCED_PATTERNS.md"},{"text":"Cross-Platform Extensions: Wider, Deeper, Polish & Optimization","link":"/research/CROSS_PLATFORM_EXTENSIONS_WIDER_DEEPER_OPTIMIZATION.md"},{"text":"Cross-Platform Gaps and Extensions — Research & Plan","link":"/research/CROSS_PLATFORM_GAPS_AND_EXTENSIONS_RESEARCH.md"},{"text":"Cross-Platform Desktop Automation: Integration Guide","link":"/research/CROSS_PLATFORM_INTEGRATION_GUIDE.md"},{"text":"Cross-Platform Multi-Tenant Desktop Automation Research & Plan","link":"/research/CROSS_PLATFORM_MULTI_TENANT_DESKTOP_AUTOMATION_RESEARCH.md"},{"text":"Cross-Platform Desktop Automation: Performance Benchmarks & SLAs","link":"/research/CROSS_PLATFORM_PERFORMANCE_BENCHMARKS.md"},{"text":"Cross-Platform Research Complete — Comprehensive Consolidated Guide","link":"/research/CROSS_PLATFORM_RESEARCH_COMPLETE.md"},{"text":"Cross-Platform Desktop Automation: Research Completion Summary","link":"/research/CROSS_PLATFORM_RESEARCH_COMPLETION_SUMMARY.md"},{"text":"Cross-Platform Research — Consolidated Comprehensive Guide","link":"/research/CROSS_PLATFORM_RESEARCH_CONSOLIDATED.md"},{"text":"Cross-Platform Desktop Automation: Research Index","link":"/research/CROSS_PLATFORM_RESEARCH_INDEX.md"},{"text":"Cross-Platform Multi-Tenant Desktop Automation: Research Summary","link":"/research/CROSS_PLATFORM_RESEARCH_SUMMARY.md"},{"text":"Cross-Platform Desktop Automation: Security Deep Dive","link":"/research/CROSS_PLATFORM_SECURITY_DEEP_DIVE.md"},{"text":"Cross-Project Analysis — Complete Summary","link":"/research/CROSS_PROJECT_ANALYSIS_COMPLETE.md"},{"text":"Cross-Project Deep Expanded Analysis","link":"/research/CROSS_PROJECT_DEEP_EXPANDED_ANALYSIS.md"},{"text":"Cross-Project Feature Borrowing Plan","link":"/research/CROSS_PROJECT_FEATURE_BORROWING_PLAN.md"},{"text":"Cross-Project Integration Guide — Kush Ecosystem","link":"/research/CROSS_PROJECT_INTEGRATION_GUIDE.md"},{"text":"Cross-Project Patterns Catalog","link":"/research/CROSS_PROJECT_PATTERNS_CATALOG.md"},{"text":"Cross-Project Work Stream Analysis","link":"/research/CROSS_PROJECT_WORK_STREAM_ANALYSIS.md"},{"text":"Delegation Friction Audit","link":"/research/DELEGATION_FRICTION_AUDIT.md"},{"text":"Agent Delegation Session - 2026-02-17","link":"/research/DELEGATION_SESSION_2026-02-17.md"},{"text":"Agent Delegation Status - 2026-02-17","link":"/research/DELEGATION_STATUS_2026-02-17.md"},{"text":"Documentation System — Design Polish Implementation Summary","link":"/research/DESIGN_POLISH_IMPLEMENTATION.md"},{"text":"Documentation System — Design Polish & Intuitive Robust Design Plan","link":"/research/DESIGN_POLISH_PLAN.md"},{"text":"Documentation Generation & Site System — Complete Research & Plan","link":"/research/DOCGEN_DOCSITE_COMPLETE.md"},{"text":"Documentation System — Completion Summary","link":"/research/DOCGEN_DOCSITE_COMPLETION_SUMMARY.md"},{"text":"Documentation Generation & Site System — Deep Audit & Improvement Plan","link":"/research/DOCGEN_DOCSITE_DEEP_AUDIT.md"},{"text":"Extended Web Research — Key Findings & Actionable Insights","link":"/research/DOCGEN_DOCSITE_EXTENDED_RESEARCH_SUMMARY.md"},{"text":"Documentation Generation & Site System — Extended Web Research","link":"/research/DOCGEN_DOCSITE_EXTENDED_WEB_RESEARCH.md"},{"text":"Documentation Generation & Site System — Comprehensive Improvement Plan","link":"/research/DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md"},{"text":"Documentation System — Phase 1 Implementation Complete","link":"/research/DOCGEN_DOCSITE_PHASE1_IMPLEMENTATION.md"},{"text":"Documentation Generation & Site System — Research Summary","link":"/research/DOCGEN_DOCSITE_RESEARCH_SUMMARY.md"},{"text":"Doctor Command: OAuth-Only Authentication Update","link":"/research/DOCTOR_OAUTH_ONLY_UPDATE.md"},{"text":"DX/UX/AX Friction Improvements - 2026-02-18","link":"/research/DX_FRICTION_IMPROVEMENTS_2026-02-18.md"},{"text":"DX/UX/AX Friction Improvements - Session 2 (2026-02-18)","link":"/research/DX_FRICTION_SESSION_2_2026-02-18.md"},{"text":"DX/UX/AX Continuous Improvement System","link":"/research/DX_UX_AX_CONTINUOUS_IMPROVEMENT_SYSTEM.md"},{"text":"ESLint → oxlint Migration Audit (Phase 4)","link":"/research/ESLINT_AUDIT.md"},{"text":"Expansion Complete — Final Report","link":"/research/EXPANSION_COMPLETE_FINAL.md"},{"text":"Expansion Phase — Complete Summary","link":"/research/EXPANSION_PHASE_COMPLETE.md"},{"text":"FastMCP ASGI Uni-Mount System Plan","link":"/research/FASTMCP_ASGI_UNI_MOUNT_PLAN.md"},{"text":"FastMCP Complete — Comprehensive Implementation Guide","link":"/research/FASTMCP_COMPLETE.md"},{"text":"FastMCP Elicitation & Context API Summary","link":"/research/FASTMCP_ELICITATION_CONTEXT.md"},{"text":"FastMCP Features & MCP Transport Spec Gaps","link":"/research/FASTMCP_FEATURES_AND_TRANSPORT_GAPS.md"},{"text":"FastMCP Implementation Guide for thegent","link":"/research/FASTMCP_IMPLEMENTATION_GUIDE.md"},{"text":"FastMCP Middleware","link":"/research/FASTMCP_MIDDLEWARE.md"},{"text":"FastMCP Progress & Tasks API Summary","link":"/research/FASTMCP_PROGRESS_TASKS.md"},{"text":"FastMCP Sampling & Telemetry","link":"/research/FASTMCP_SAMPLING_TELEMETRY.md"},{"text":"FastMCP Spec Deep Dive","link":"/research/FASTMCP_SPEC_DEEP_DIVE.md"},{"text":"FastMCP Storage Backends & EventStore","link":"/research/FASTMCP_STORAGE_EVENTSTORE.md"},{"text":"FastMCP Transforms & Deployment Summary","link":"/research/FASTMCP_TRANSFORMS_DEPLOYMENT.md"},{"text":"Fast Process Monitoring - Research & Implementation","link":"/research/FAST_PROCESS_MONITORING.md"},{"text":"Final Expansion Report — Complete","link":"/research/FINAL_EXPANSION_REPORT.md"},{"text":"Friction Points Log","link":"/research/FRICTION_LOG.md"},{"text":"Friction Points Log - 2026-02-18","link":"/research/FRICTION_LOG_2026-02-18.md"},{"text":"Friction Points Identified During Work Stream Processing","link":"/research/FRICTION_POINTS_IDENTIFIED.md"},{"text":"Git Shim Starship Optimization — Fix for 8+ Minute Prompt Delays","link":"/research/GIT_SHIM_STARSHIP_OPTIMIZATION.md"},{"text":"Git Tooling Audit and Modernization Plan","link":"/research/GIT_TOOLING_AUDIT_AND_PLAN.md"},{"text":"Governance, Policy Enforcement, and Audit Trail Research","link":"/research/GOVERNANCE_POLICY_AUDIT_RESEARCH.md"},{"text":"Governance WP Gaps — Implementation Notes","link":"/research/GOVERNANCE_WP_GAPS.md"},{"text":"Governance WP Gaps — Expanded & BACKLOG Items","link":"/research/GOVERNANCE_WP_GAPS_EXPANDED.md"},{"text":"Hook Rust Migration Complete — Comprehensive Migration Strategy & Timeline","link":"/research/HOOK_RUST_MIGRATION_COMPLETE.md"},{"text":"Hook Runtime Rust Migration: Research Synthesis","link":"/research/HOOK_RUST_MIGRATION_RESEARCH_SYNTHESIS.md"},{"text":"Hook Runtime Rust Migration — Complete Expansion","link":"/research/HOOK_RUST_MIGRATION_RESEARCH_SYNTHESIS_EXPANDED.md"},{"text":"Idea Seeds & Session Storage","link":"/research/IDEA_SEEDS_SESSION_STORAGE.md"},{"text":"Idea Seed Review Complete — Consolidation & Rationale","link":"/research/IDEA_SEED_REVIEW_COMPLETE.md"},{"text":"Index Sprawl Status Update — Complete","link":"/research/INDEX_SPRAWL_STATUS_UPDATE.md"},{"text":"Integration Examples — Kush Ecosystem","link":"/research/INTEGRATION_EXAMPLES.md"},{"text":"In-Depth Tooling and Global Optimizations Audit (2026-02-15)","link":"/research/IN_DEPTH_TOOLING_AUDIT_2026.md"},{"text":"Kush Ecosystem — Architecture Diagram","link":"/research/KUSH_ECOSYSTEM_ARCHITECTURE_DIAGRAM.md"},{"text":"Kush Ecosystem — Complete Documentation Index","link":"/research/KUSH_ECOSYSTEM_COMPLETE.md"},{"text":"Kush Ecosystem — Comprehensive Deep Dive Analysis","link":"/research/KUSH_ECOSYSTEM_DEEP_DIVE.md"},{"text":"Kush Ecosystem — Implementation Status","link":"/research/KUSH_ECOSYSTEM_IMPLEMENTATION_STATUS.md"},{"text":"Kush Ecosystem — Unified Documentation Index","link":"/research/KUSH_ECOSYSTEM_UNIFIED_DOCS_INDEX.md"},{"text":"Library Cache Migration Plan","link":"/research/LIBRARY_CACHE_MIGRATION_PLAN.md"},{"text":"Library-First Audit and Plan","link":"/research/LIBRARY_FIRST_AUDIT_AND_PLAN.md"},{"text":"Library Replacement Audit — Deep & Wide","link":"/research/LIBRARY_REPLACEMENT_AUDIT_DEEP.md"},{"text":"Library Replacement Complete — Comprehensive Audit & Migration Plan","link":"/research/LIBRARY_REPLACEMENT_COMPLETE.md"},{"text":"Library Replacement — Consolidated Migration Plan","link":"/research/LIBRARY_REPLACEMENT_CONSOLIDATED.md"},{"text":"Library Replacement — Phase Design Work Breakdowns (DWBs)","link":"/research/LIBRARY_REPLACEMENT_PHASE_DWBS.md"},{"text":"Markdown Documentation — Completion Summary","link":"/research/MARKDOWN_COMPLETION_SUMMARY.md"},{"text":"Master Expansion TODO — Complete Documentation Sprawl","link":"/research/MASTER_EXPANSION_TODO.md"},{"text":"MCP Full Parity & FastMCP Transport Spec Audit","link":"/research/MCP_FULL_PARITY_AND_FASTMCP_AUDIT.md"},{"text":"MCP and Client Features for Session Notifications","link":"/research/MCP_NOTIFICATION_OPTIONS.md"},{"text":"MD Documentation Normalization Guide","link":"/research/MD_NORMALIZATION_GUIDE.md"},{"text":"Memory Optimization — Long-Term Plan","link":"/research/MEMORY_OPTIMIZATION_LONG_TERM_PLAN.md"},{"text":"Multi-Platform Agent Deep Dive","link":"/research/MULTI_PLATFORM_DEEP_DIVE.md"},{"text":"Next 5 Work Items Summary","link":"/research/NEXT_5_WORK_ITEMS_SUMMARY.md"},{"text":"OpenClaw / Agent Zero as Main Agent — Research","link":"/research/OPENCLAW_AGENTZERO_AS_MAIN_AGENT_RESEARCH.md"},{"text":"OpenClaw, ClawHub, Agent Zero — Use Cases for thegent","link":"/research/OPENCLAW_CLAWHUB_AGENTZERO_USE_CASES.md"},{"text":"Package Optimization Implementation Status","link":"/research/OPTIMIZATION_IMPLEMENTATION_STATUS.md"},{"text":"Package Optimization Migration Guide","link":"/research/OPTIMIZATION_MIGRATION_GUIDE.md"},{"text":"Priority 1 (P1) Expansion — Complete","link":"/research/P1_EXPANSION_COMPLETE.md"},{"text":"Priority 1 (P1) Phase — Complete","link":"/research/P1_PHASE_COMPLETE.md"},{"text":"P3 Polish Complete — Full Research Docs","link":"/research/P3_POLISH_COMPLETE.md"},{"text":"P4 Normalization — Complete","link":"/research/P4_NORMALIZATION_COMPLETE.md"},{"text":"P4 Normalization — Final Status","link":"/research/P4_NORMALIZATION_FINAL.md"},{"text":"P4 Normalization Progress — All MD Docs","link":"/research/P4_NORMALIZATION_PROGRESS.md"},{"text":"P4 Normalization Summary — Complete","link":"/research/P4_NORMALIZATION_SUMMARY.md"},{"text":"P4 Normalization Update — Progress Report","link":"/research/P4_NORMALIZATION_UPDATE.md"},{"text":"Package Design Research Summary","link":"/research/PACKAGE_DESIGN_RESEARCH_SUMMARY.md"},{"text":"Package Optimization Research - Modern Alternatives & Performance Improvements","link":"/research/PACKAGE_OPTIMIZATION_RESEARCH.md"},{"text":"Phase Documents — Complete Expansion","link":"/research/PHASE_DOCUMENTS_EXPANDED.md"},{"text":"Plan Usage and Budget Research","link":"/research/PLAN_USAGE_AND_BUDGET_RESEARCH.md"},{"text":"Proactive Governance Evolution Plan","link":"/research/PROACTIVE_GOVERNANCE_EVOLUTION_PLAN.md"},{"text":"Production Packaging, Polish & Optimization Audit + Plan","link":"/research/PRODUCTION_PACKAGING_POLISH_OPTIMIZATION_AUDIT_AND_PLAN.md"},{"text":"Python Frontmatter + Native Backmatter: Research Audit & Plan","link":"/research/PYTHON_FRONTMATTER_NATIVE_BACKMATTER_AUDIT_PLAN.md"},{"text":"Qwen3.5 Plus 02-15 on OpenRouter — Pareto Research","link":"/research/QWEN3.5_PLUS_OPENROUTER_PARETO_RESEARCH.md"},{"text":"Remaining Markdown Files — Completion Status","link":"/research/REMAINING_MARKDOWN_COMPLETION.md"},{"text":"Remove Directory Dependencies — Production Installation Optimization","link":"/research/REMOVE_DIRECTORY_DEPENDENCIES_AUDIT_AND_PLAN.md"},{"text":"Research, Seed & Fragment Inventory — Sprawl Todo & Unified Work Stream","link":"/research/RESEARCH_SEED_FRAGMENT_INVENTORY_AND_SPRAWL_TODO.md"},{"text":"Runtime Infrastructure: Existing Solutions Audit & Integration Plan","link":"/research/RUNTIME_INFRASTRUCTURE_EXISTING_SOLUTIONS_AUDIT_AND_INTEGRATION_PLAN.md"},{"text":"Runtime Infrastructure Implementation: Complete","link":"/research/RUNTIME_INFRASTRUCTURE_IMPLEMENTATION_COMPLETE.md"},{"text":"Runtime Infrastructure Integration: Phase 2 Complete","link":"/research/RUNTIME_INFRASTRUCTURE_INTEGRATION_PHASE2_COMPLETE.md"},{"text":"Runtime Infrastructure Integration: Phase 3 Complete","link":"/research/RUNTIME_INFRASTRUCTURE_INTEGRATION_PHASE3_COMPLETE.md"},{"text":"Runtime Infrastructure Resource Leaks & Optimization Audit & Plan","link":"/research/RUNTIME_INFRASTRUCTURE_RESOURCE_LEAKS_AUDIT_AND_PLAN.md"},{"text":"Runtime Infrastructure Solutions: Executive Summary","link":"/research/RUNTIME_INFRASTRUCTURE_SOLUTIONS_SUMMARY.md"},{"text":"\\"See Also\\" Section Template","link":"/research/SEE_ALSO_TEMPLATE.md"},{"text":"Self-Optimization Instructions Added to CLAUDE.md","link":"/research/SELF_OPTIMIZATION_INSTRUCTIONS_ADDED.md"},{"text":"Session Research Complete — Comprehensive Deep-Dive","link":"/research/SESSION_RESEARCH_COMPLETE.md"},{"text":"Session Research Fragments — 2026-02-15","link":"/research/SESSION_RESEARCH_FRAGMENTS.md"},{"text":"Session Research Fragments — Complete Expansion","link":"/research/SESSION_RESEARCH_FRAGMENTS_EXPANDED.md"},{"text":"Session Summary - 2026-02-17","link":"/research/SESSION_SUMMARY_2026-02-17.md"},{"text":"Session Wait Loop Setup","link":"/research/SESSION_WAIT_LOOP_SETUP.md"},{"text":"Shared MCP Tool Library — Design Specification","link":"/research/SHARED_MCP_TOOL_LIBRARY.md"},{"text":"Shell Configuration Audit and Consolidation Plan","link":"/research/SHELL_CONFIG_AUDIT_AND_CONSOLIDATION_PLAN.md"},{"text":"Shell Error Fixes — zsh Bad Substitution","link":"/research/SHELL_ERROR_FIXES.md"},{"text":"Shell Startup Optimization Fix","link":"/research/SHELL_STARTUP_OPTIMIZATION_FIX.md"},{"text":"Smart & Robust Process Strategies — Research & Plan","link":"/research/SMART_ROBUST_STRATEGIES_RESEARCH.md"},{"text":"Swarm Management Complete Research & Implementation Guide","link":"/research/SWARM_COMPLETE.md"},{"text":"Swarm Optimization, Management & Scheduling — Deep Research","link":"/research/SWARM_OPTIMIZATION_SCHEDULING_DEEP_RESEARCH.md"},{"text":"Swarm Process Automation — Deep Research & Plan","link":"/research/SWARM_PROCESS_AUTOMATION_DEEP_RESEARCH.md"},{"text":"Swarm & Resource Optimization — Research Index","link":"/research/SWARM_RESEARCH_INDEX.md"},{"text":"System Resources Complete Practical Guide","link":"/research/SYSTEM_RESOURCES_COMPLETE.md"},{"text":"System Resources (FD, CPU, Threads, Ports) — Full-Depth Research & Plan","link":"/research/SYSTEM_RESOURCES_FD_CPU_DEEP_RESEARCH.md"},{"text":"TASK I/O System Improvement Research & Plan","link":"/research/TASK_IO_IMPROVEMENT_RESEARCH_AND_PLAN.md"},{"text":"Thegent Teammates: Research and Implementation Plan (2026-02-15)","link":"/research/TEAMMATES_RESEARCH_AND_PLAN.md"},{"text":"Tenacity vs Custom Retry — Audit & Plan","link":"/research/TENACITY_RETRY_AUDIT_PLAN.md"},{"text":"Thegent Command Model Options and Agent Features Research","link":"/research/THGENT_COMMAND_MODEL_OPTIONS_AND_AGENT_FEATURES_RESEARCH.md"},{"text":"Thegent Documentation Update Summary","link":"/research/THGENT_DOCUMENTATION_UPDATE_SUMMARY.md"},{"text":"TUI Compositor Comparison Research","link":"/research/TUI_COMPOSITOR_COMPARISON.md"},{"text":"Unified Agent Registry API — Design Specification","link":"/research/UNIFIED_AGENT_REGISTRY_API.md"},{"text":"Unified Work Stream Integration — Complete","link":"/research/UNIFIED_WORK_STREAM_INTEGRATION.md"},{"text":"User Queue + TUI: Editable Prompts While Agent Runs","link":"/research/USER_QUEUE_TUI_AND_AGENT_POLL.md"},{"text":"VitePress Enhancements Research Report (2025-2026)","link":"/research/VITEPRESS_ENHANCEMENTS.md"},{"text":"VitePress Rich Documentation — Final Status","link":"/research/VITEPRESS_FINAL_STATUS.md"},{"text":"VitePress Rich Documentation — ✅ IMPLEMENTATION COMPLETE","link":"/research/VITEPRESS_IMPLEMENTATION_COMPLETE.md"},{"text":"VitePress Phase 1 Implementation — ✅ COMPLETE","link":"/research/VITEPRESS_PHASE1_COMPLETE.md"},{"text":"VitePress Phase 1 Implementation — Status","link":"/research/VITEPRESS_PHASE1_IMPLEMENTATION.md"},{"text":"VitePress Phase 2 Implementation — Status","link":"/research/VITEPRESS_PHASE2_IMPLEMENTATION.md"},{"text":"VitePress Phase 3 Implementation — ✅ COMPLETE","link":"/research/VITEPRESS_PHASE3_COMPLETE.md"},{"text":"VitePress Rich Documentation Audit & Implementation Plan","link":"/research/VITEPRESS_RICH_DOCUMENTATION_AUDIT.md"},{"text":"VitePress Rich Documentation — Implementation Plan","link":"/research/VITEPRESS_RICH_DOCUMENTATION_IMPLEMENTATION_PLAN.md"},{"text":"Workflow Improvement Session - 2026-02-17","link":"/research/WORKFLOW_IMPROVEMENT_SESSION_2026-02-17.md"},{"text":"Work Stream Processing Session — 2026-02-18","link":"/research/WORKSTREAM_PROCESSING_SESSION_2026-02-18.md"},{"text":"Work Stream Processing with Continuous Improvements","link":"/research/WORKSTREAM_PROCESSING_WITH_IMPROVEMENTS.md"},{"text":"Workstream Processing Session Summary - 2026-02-18","link":"/research/WORKSTREAM_SESSION_SUMMARY_2026-02-18.md"},{"text":"Work Stream Sync/Update/Audit Coverage - Batch 1","link":"/research/WORK_STREAM_SYNC_UPDATE_AUDIT_COVERAGE_BATCH_1.md"},{"text":"Phase 13: Compliance Profile Mapping","link":"/research/phase13-compliance-profile-mapping.md"},{"text":"Phase 13: Cost Sensitivity Experiment Plan","link":"/research/phase13-cost-sensitivity-experiment-plan.md"},{"text":"Phase 13: Policy Federation Surface Map","link":"/research/phase13-policy-federation-surface-map.md"},{"text":"Phase 13: Tenant Boundary Test Matrix","link":"/research/phase13-tenant-boundary-test-matrix.md"},{"text":"Phase 14: Autonomous Learning and Cost Sensing Surface Map","link":"/research/phase14-autonomous-learning-surface-map.md"},{"text":"Phase 14: Cost Sensing and Learning Test Matrix","link":"/research/phase14-cost-sensing-test-matrix.md"},{"text":"Phase 15: Enterprise Compliance Test Matrix","link":"/research/phase15-enterprise-compliance-test-matrix.md"},{"text":"Phase 15: Enterprise Lifecycle and Compliance Surface Map","link":"/research/phase15-enterprise-lifecycle-surface-map.md"}],"/closure/":[{"text":"DR Rehearsal Report","link":"/closure/DR_REHEARSAL_REPORT.md"},{"text":"Governance & Compliance Bundle","link":"/closure/GOVERNANCE_COMPLIANCE_BUNDLE.md"},{"text":"Phase 6 Readiness Report","link":"/closure/PHASE6_READINESS_REPORT.md"},{"text":"Post-Launch 28-Day Observation Plan","link":"/closure/POST_LAUNCH_28DAY_OBSERVATION.md"},{"text":"Rollback Reserve Plan","link":"/closure/ROLLBACK_RESERVE_PLAN.md"},{"text":"SLO Certification Matrix","link":"/closure/SLO_CERTIFICATION_MATRIX.md"}],"/docset/":[{"text":"DAG Node-to-Service Contract Checklist","link":"/docset/DAG_NODE_SERVICE_CONTRACT_CHECKLIST.md"},{"text":"DAG Node-to-Service Contract Checklist","link":"/docset/DAG_NODE_TO_SERVICE_CONTRACT_CHECKLIST.md"},{"text":"E2E Next Chunk Plan — Full-Phase Mega Chunk","link":"/docset/E2E_NEXT_CHUNK_PLAN.md"},{"text":"E2E Remaining Full-Depth Plan","link":"/docset/E2E_REMAINING_FULL_DEPTH_PLAN.md"},{"text":"FastMCP 3.0 Integration Reference for Thegent","link":"/docset/FASTMCP_INTEGRATION.md"},{"text":"Thegent Implementation Status Tracker","link":"/docset/IMPLEMENTATION_STATUS.md"},{"text":"Thegent Optimization, Polish, and Robustness Addendum","link":"/docset/OPTIMIZATION_POLISH_ADDENDUM.md"},{"text":"Thegent Pattern Catalog","link":"/docset/PATTERNS.md"},{"text":"Comprehensive Test Plan Matrix","link":"/docset/PRD_TEST_PLAN_MATRIX.md"},{"text":"Remaining Gaps — Full Depth Analysis","link":"/docset/REMAINING_GAPS_DEEP_DIVE.md"},{"text":"Remaining Gaps — Full Depth Analysis","link":"/docset/REMAINING_GAPS_FULL_DEPTH.md"},{"text":"Thegent Risks and Anti-Patterns Catalog","link":"/docset/RISKS_AND_ANTIPATTERNS.md"},{"text":"WBS-to-Issue Import Matrix","link":"/docset/WBS_TO_ISSUE_IMPORT_MATRIX.md"},{"text":"Thegent CLI Single Source of Truth Audit","link":"/docset/thegent-cli-single-source-of-truth-audit-2026-02-14.md"},{"text":"Thegent Cross-Analysis Matrix (Deep)","link":"/docset/thegent-cross-analysis-matrix-2026-02-14.md"},{"text":"Thegent Final DAG Specification","link":"/docset/thegent-dag-final.md"},{"text":"Thegent DAG Extension — Phases 10 to 12","link":"/docset/thegent-dag-phase10-12-extension.md"},{"text":"thegent DAG Extension — Phases 7, 8, 9","link":"/docset/thegent-dag-phase7-9-extension.md"},{"text":"Thegent Gaps and Discovery Report","link":"/docset/thegent-gaps-and-discovery-2026-02-14.md"},{"text":"Thegent Implementation Log","link":"/docset/thegent-implementation-log-2026-02-14.md"},{"text":"Thegent Kush Docs Deep Dive (Zen + Adjacent Projects)","link":"/docset/thegent-kush-docs-deep-dive-2026-02-14.md"},{"text":"Thegent Mega Research Synthesis","link":"/docset/thegent-mega-research-synthesis-2026-02-14.md"},{"text":"Thegent Orchestration Optimization & Expansion PRD (Living Document)","link":"/docset/thegent-orchestration-optimization-prd.md"},{"text":"Thegent Pattern Enhancement Synthesis","link":"/docset/thegent-patterns-enhancement-synthesis.md"},{"text":"Thegent Phase 10–12 Bundle B Sprint Playbook","link":"/docset/thegent-phase10-12-bundle-b-sprint-playbook.md"},{"text":"Thegent Phase 10–12 Bundle Signoff and Handoff Packages","link":"/docset/thegent-phase10-12-bundle-signoff-and-handoff-packages.md"},{"text":"Thegent Phase 10–12 Closure Readiness Pack Template","link":"/docset/thegent-phase10-12-closure-readiness-pack-template.md"},{"text":"Thegent Phase 10–12 Compact Execution Dashboard","link":"/docset/thegent-phase10-12-compact-execution-dashboard.md"},{"text":"Thegent Phase 10–12 Drift Reconciliation Playbook","link":"/docset/thegent-phase10-12-drift-reconciliation-playbook.md"},{"text":"Thegent Phase 10–12 Execution Bundles Playbook","link":"/docset/thegent-phase10-12-execution-bundles-playbook.md"},{"text":"Thegent Phase 10–12 Execution Synthesis Playbook","link":"/docset/thegent-phase10-12-execution-synthesis-playbook.md"},{"text":"Thegent Phase 10–12 Execution Workboard (Chunk 4)","link":"/docset/thegent-phase10-12-execution-workboard.md"},{"text":"Thegent Phase 10–12 Hard-Stop, Rollback, and Stability Matrix","link":"/docset/thegent-phase10-12-hard-stop-and-rollback-matrix.md"},{"text":"Thegent Phase 10–12 Implementation Chunk Plan","link":"/docset/thegent-phase10-12-implementation-chunk-plan.md"},{"text":"Thegent Phase 10–12 Implementation Issue Queue","link":"/docset/thegent-phase10-12-implementation-issue-queue.md"},{"text":"Thegent Phase 10–12 Implementation Ticket Templates (Chunk 3)","link":"/docset/thegent-phase10-12-implementation-ticket-templates.md"},{"text":"Thegent Phase 10–12 Issue Board Automation Playbook","link":"/docset/thegent-phase10-12-issue-board-automation.md"},{"text":"Thegent Phase 10–12 Issue Board Import Notes","link":"/docset/thegent-phase10-12-issue-board-import-notes.md"},{"text":"Thegent Phase 10–12 Launch Schedule (Day-by-Day Execution Plan)","link":"/docset/thegent-phase10-12-launch-schedule.md"},{"text":"Thegent Phase 10–12 Master Traceability Ledger","link":"/docset/thegent-phase10-12-master-traceability-ledger.md"},{"text":"Thegent — Phase 10–12 PRD (Optimization-Depth and Productization Wave)","link":"/docset/thegent-phase10-12-optimal-design-prd.md"},{"text":"Thegent Phase 10–12 Orchestrator Tooling Stack","link":"/docset/thegent-phase10-12-orchestrator-tooling-stack.md"},{"text":"Thegent Phase 10–12 Policy-as-Code and Automation Contract","link":"/docset/thegent-phase10-12-policy-as-code-and-automation-contract.md"},{"text":"Thegent Phase 10–12 PRD↔WBS Finalization Cross-Map","link":"/docset/thegent-phase10-12-prd-wbs-crossmap-finalization.md"},{"text":"Thegent Phase 10–12 PRD-WBS-DAG-Ticket Validation Framework","link":"/docset/thegent-phase10-12-prd-wbs-dag-ticket-validation.md"},{"text":"Thegent Phase 10–12 Release Readiness and Delta Pack","link":"/docset/thegent-phase10-12-release-readiness-and-delta-pack.md"},{"text":"Thegent Phase 10–12 Test and Readiness Pack","link":"/docset/thegent-phase10-12-test-readiness-pack.md"},{"text":"Thegent Phase 11 Sprint Playbook (Bundles C and D)","link":"/docset/thegent-phase11-control-and-adaptation-sprint-playbook.md"},{"text":"Thegent Phase 12 Sprint Playbook (Bundles E and F)","link":"/docset/thegent-phase12-explainability-and-closure-sprint-playbook.md"},{"text":"Thegent Phase 13+ Extension Boundary Proposal","link":"/docset/thegent-phase13-plus-extension-proposal.md"},{"text":"Thegent Phase 3–6 Closure Acceptance Contract Schema","link":"/docset/thegent-phase3-6-closure-acceptance-contract-schema.md"},{"text":"Thegent Phase 3–6 Closure Acceptance Pack Template","link":"/docset/thegent-phase3-6-closure-acceptance-pack-template.md"},{"text":"Thegent Phase 3–6 Closure Validator Automation Package","link":"/docset/thegent-phase3-6-closure-validator-automation-package.md"},{"text":"Thegent Phase 3–6 Closure Validation Event and Waiver Contract v1","link":"/docset/thegent-phase3-6-closure-validator-event-and-waiver-contract-v1.md"},{"text":"Thegent Phase 3–6 Closure Validator Fault Injection and Chaos Tests","link":"/docset/thegent-phase3-6-closure-validator-fault-injection-and-chaos-tests.md"},{"text":"Thegent Phase 3–6 Closure Validator Implementation Blueprint","link":"/docset/thegent-phase3-6-closure-validator-implementation-blueprint.md"},{"text":"Thegent Phase 3–6 Closure Validator Python Implementation Blueprint","link":"/docset/thegent-phase3-6-closure-validator-python-implementation-blueprint.md"},{"text":"Thegent Phase 3-6 Closure Validator Runtime CLI and Adapter Playbook","link":"/docset/thegent-phase3-6-closure-validator-runtime-cli-and-adapter-playbook.md"},{"text":"Thegent Phase 3–6 Cross-Wave Bridge and Continuity Plan","link":"/docset/thegent-phase3-6-crosswave-bridge-and-continuity-plan.md"},{"text":"Thegent — Phase 3–6 Full-Depth Execution Chunk","link":"/docset/thegent-phase3-6-full-depth-execution-prd.md"},{"text":"Thegent Phase 7–9 Next-Wave PRD (Post-Closure Optimization)","link":"/docset/thegent-phase7-9-next-wave-prd.md"},{"text":"Thegent Phase 7–9 Test and Readiness Pack","link":"/docset/thegent-phase7-9-test-readiness-pack.md"},{"text":"Thegent Orchestration Final Plan Index","link":"/docset/thegent-plan-final-index.md"},{"text":"Thegent Production Orchestration PRD (Final)","link":"/docset/thegent-prd-final.md"},{"text":"Thegent Research Validation Addendum (Zen + Task Tools)","link":"/docset/thegent-research-validation-2026-02-14.md"},{"text":"thegent Third-Party Bundle Manifest","link":"/docset/thegent-third-party-bundle-manifest.md"},{"text":"Thegent Final WBS (Comprehensive)","link":"/docset/thegent-wbs-final.md"},{"text":"Thegent WBS — Phase 10 to Phase 12 (Optimization-Depth and Productization)","link":"/docset/thegent-wbs-phase10-12.md"},{"text":"Thegent WBS — Phase 7 to Phase 9 (Next-Wave Execution)","link":"/docset/thegent-wbs-phase7-9.md"}],"/enterprise/":[{"text":"Decommissioning and Sunset Plan","link":"/enterprise/DECOMMISSIONING_PLAN.md"},{"text":"Program Operating Model and Ownership Map","link":"/enterprise/OPERATING_MODEL.md"},{"text":"Security and Compliance Signoff Package","link":"/enterprise/SECURITY_COMPLIANCE_SIGNOFF.md"}],"/plans/":[{"text":"Fragments","collapsed":false,"items":[{"text":"Lane Strategy Matrix for Hybrid Hook Runtime","link":"/fragments/LANE_STRATEGY_MATRIX.md"},{"text":"No-Regression Enforcement for Hybrid Sync/Async Checks","link":"/fragments/NO_REGRESSION_ENFORCEMENT.md"},{"text":"Performance Optimization Playbook for Hybrid Hook Runtime","link":"/fragments/PERF_OPTIMIZATION_PLAYBOOK.md"},{"text":"Rollout and Operations Runbook for Hybrid Lane System","link":"/fragments/ROLLOUT_AND_OPERATIONS.md"}]},{"text":"Thegent Unified Plan — Master Index","link":"/plans/00-MASTER-INDEX.md"},{"text":"01 — Project State","link":"/plans/01-PROJECT-STATE.md"},{"text":"02 — Unified Work Breakdown Structure","link":"/plans/02-UNIFIED-WBS.md"},{"text":"03 — Unified DAG Specifications","link":"/plans/03-UNIFIED-DAG.md"},{"text":"04 — Unified Requirements","link":"/plans/04-REQUIREMENTS.md"},{"text":"05 — Architecture & Patterns","link":"/plans/05-ARCHITECTURE.md"},{"text":"06 — Implementation Guide","link":"/plans/06-IMPLEMENTATION-GUIDE.md"},{"text":"07 — Test Strategy","link":"/plans/07-TEST-STRATEGY.md"},{"text":"08 — Optimization, Polish, Enhancement & Robustness Catalog","link":"/plans/08-OPTIMIZATION-CATALOG.md"},{"text":"09 — Risk Registry & Anti-Patterns","link":"/plans/09-RISK-REGISTRY.md"},{"text":"10 — Subagent Dispatch Plan","link":"/plans/10-SUBAGENT-DISPATCH.md"},{"text":"12 — Cycleloop Loops & Checker Agent Design","link":"/plans/12-LIFECYCLE-LOOP-DESIGN.md"},{"text":"Design: thegent install CLI Command","link":"/plans/2026-02-14-thegent-install-design.md"},{"text":"thegent install Implementation Plan","link":"/plans/2026-02-14-thegent-install-implementation-plan.md"},{"text":"Research and Elicitation Plan — 2026-02-15","link":"/plans/2026-02-15-RESEARCH-AND-ELICITATION-PLAN.md"},{"text":"thegent sitback — Design & Implementation Plan","link":"/plans/2026-02-15-thegent-sitback-design.md"},{"text":"Tray Application Design - Plugin-Based Architecture","link":"/plans/2026-02-15-tray-application-design.md"},{"text":"AgentDeployer + LifecycleController Integration Review","link":"/plans/2026-02-16-AGENT_DEPLOYER_REVIEW.md"},{"text":"Cycleloop + AgilePlus Integration Plan","link":"/plans/2026-02-16-CYCLELOOP_AGILEPLUS_INTEGRATION.md"},{"text":"Full LiteLLM Feature Integration Plan","link":"/plans/2026-02-16-litellm-full-features-plan.md"},{"text":"LiteLLM Integration Design","link":"/plans/2026-02-16-litellm-integration-design.md"},{"text":"LiteLLM Router Integration Implementation Plan","link":"/plans/2026-02-16-litellm-integration-plan.md"},{"text":"Supermemory.ai Integration Plan (WP-5001-SM)","link":"/plans/2026-02-16-supermemory-integration-plan.md"},{"text":"Design Doc: Agent-Accelerated Production Readiness Optimization","link":"/plans/2026-02-18-production-readiness-optimization-design.md"},{"text":"Agent-Accelerated Production Readiness Implementation Plan","link":"/plans/2026-02-18-production-readiness-optimization-plan.md"},{"text":"Agent Sandboxing Implementation Plan","link":"/plans/AGENT_SANDBOXING_IMPLEMENTATION_PLAN.md"},{"text":"Catalog ↔ CLIProxyAPIPlus Fork Alignment","link":"/plans/CATALOG_CLIPROXY_FORK_ALIGNMENT.md"},{"text":"CLIProxyAPI & Thegent Work Plan – Unified Phased WBS","link":"/plans/CLIPROXY_API_AND_THGENT_UNIFIED_PLAN.md"},{"text":"Agent Orchestration Harness: Multi-Platform (Extreme-Depth Plan)","link":"/plans/CODEX_DONUT_HARNESS_PLAN.md"},{"text":"Cross-Platform Multi-Tenant Desktop Automation Complete Plan","link":"/plans/CROSS_PLATFORM_COMPLETE_PLAN.md"},{"text":"Cross-Platform Multi-Tenant Desktop Automation Implementation Plan","link":"/plans/CROSS_PLATFORM_MULTI_TENANT_IMPLEMENTATION_PLAN.md"},{"text":"Cursor API Integration Research & Plan","link":"/plans/CURSOR_API_INTEGRATION_RESEARCH.md"},{"text":"Debug Tags and Metrics (Transient Response Tags)","link":"/plans/DEBUG_TAGS_AND_METRICS.md"},{"text":"Distributed Model Routing Plan","link":"/plans/DISTRIBUTED_MODEL_ROUTING_PLAN.md"},{"text":"Documentation Expansion Process","link":"/plans/DOCUMENTATION_EXPANSION_PROCESS.md"},{"text":"Documentation Expansion TODO","link":"/plans/DOCUMENTATION_EXPANSION_TODO.md"},{"text":"Documentation Consolidation & Implementation WBS","link":"/plans/DOC_CONSOLIDATION_AND_IMPLEMENTATION_WBS.md"},{"text":"Factory Droid Harness Integration Plan","link":"/plans/FACTORY_DROID_HARNESS_INTEGRATION_PLAN.md"},{"text":"Full Shell → Rust Where Beneficial","link":"/plans/FULL_SHELL_TO_RUST_WHERE_BENEFICIAL.md"},{"text":"Holistic + Harmonious Design & Full Integration Plan","link":"/plans/HOLISTIC_HARMONIOUS_DESIGN_AND_INTEGRATION_PLAN.md"},{"text":"Hook Point Hybrid Latency Expanded Plan","link":"/plans/HOOK_POINT_HYBRID_LATENCY_EXPANDED_PLAN.md"},{"text":"Hook Point Hybrid Latency Master Plan","link":"/plans/HOOK_POINT_HYBRID_LATENCY_MASTER_PLAN.md"},{"text":"Hook Runtime Rust Migration Complete Guide","link":"/plans/HOOK_RUNTIME_RUST_COMPLETE.md"},{"text":"Hook Runtime: Full Rust Migration Design (Deep & Wide)","link":"/plans/HOOK_RUNTIME_RUST_DESIGN.md"},{"text":"Hybrid Mac/Windows Environment Implementation Plan","link":"/plans/HYBRID_ENV_IMPLEMENTATION_PLAN.md"},{"text":"LiteLLM + CLIProxyAPIPlus + Bifrost Harmony","link":"/plans/LITELLM_CLIPROXY_BIFROST_HARMONY.md"},{"text":"MCP Bundle: thegent + Browser Tools (Replace Manual Playwright)","link":"/plans/MCP_BUNDLE_PLAYWRIGHT_REPLACEMENT.md"},{"text":"MCP Tool Optimization, Polish & Enhancement Plan","link":"/plans/MCP_TOOL_OPTIMIZATION_PLAN.md"},{"text":"Multi-Platform Parity Master Plan & Matrix","link":"/plans/MULTI_PLATFORM_PARITY_MASTER_PLAN.md"},{"text":"New Providers Auth Research & Plan","link":"/plans/NEW_PROVIDERS_AUTH_RESEARCH.md"},{"text":"OpenRouter-Style Routing + CLIProxyAPIPlus Integration","link":"/plans/OPENROUTER_STYLE_ROUTING_AND_CLIPROXY.md"},{"text":"Process & Tool Optimization Complete Plan","link":"/plans/PROCESS_OPTIMIZATION_COMPLETE_PLAN.md"},{"text":"Process and Tool Optimization Plan","link":"/plans/PROCESS_OPTIMIZATION_PLAN.md"},{"text":"Prompt History Collection & Audit System: Comprehensive Plan","link":"/plans/PROMPT_HISTORY_COLLECTION_AND_AUDIT_SYSTEM.md"},{"text":"Prompt History Collection & Audit System Complete Guide","link":"/plans/PROMPT_HISTORY_COLLECTION_COMPLETE.md"},{"text":"Remote Compute Implementation Detail","link":"/plans/REMOTE_COMPUTE_IMPLEMENTATION_DETAIL.md"},{"text":"thegent Setup: Proposed Hooks, Plugins, Skills, MCP & Docs","link":"/plans/SETUP_PROPOSED_ITEMS.md"},{"text":"Shell Environment Advanced Enhancement Plan","link":"/plans/SHELL_ENVIRONMENT_ADVANCED_ENHANCEMENT_PLAN.md"},{"text":"Shell Environment Advanced Enhancement - Implementation Summary","link":"/plans/SHELL_ENVIRONMENT_ADVANCED_IMPLEMENTATION_SUMMARY.md"},{"text":"Shell Environment Complete Plan","link":"/plans/SHELL_ENVIRONMENT_COMPLETE_PLAN.md"},{"text":"Shell Environment Implementation Summary","link":"/plans/SHELL_ENVIRONMENT_IMPLEMENTATION_SUMMARY.md"},{"text":"Shell Environment Optimization & Enhancement Plan","link":"/plans/SHELL_ENVIRONMENT_OPTIMIZATION_PLAN.md"},{"text":"Sync/Update Command & Full System Audit Plan","link":"/plans/SYNC_UPDATE_COMMAND_AND_SYSTEM_AUDIT_PLAN.md"},{"text":"Thegent FastMCP 3.0 Implementation Plan","link":"/plans/THGENT_FASTMCP_IMPLEMENTATION_PLAN.md"},{"text":"Runtime Dispatch Consolidation & Fork Fix: Complete","link":"/plans/ULTRA_SHIM_CONSOLIDATION_COMPLETE.md"},{"text":"Ultra-Shim Fork Failure Fix: Root Cause Analysis & Solution","link":"/plans/ULTRA_SHIM_FORK_FAILURE_FIX.md"},{"text":"Unified Login Flow: Open URL + Prompt for Key","link":"/plans/UNIFIED_LOGIN_FLOW.md"},{"text":"Unified System Application Plan","link":"/plans/UNIFIED_SYSTEM_APPLICATION_PLAN.md"}],"/changes/":[{"text":"Hexagonal Migration","collapsed":false,"items":[{"text":"Hexagonal Architecture Migration -- thegent","link":"/hexagonal-migration/proposal.md"}]}],"/checklists/":[{"text":"Hybrid Mac/Windows Environment Setup Checklist","link":"/checklists/HYBRID_ENV_SETUP_CHECKLIST.md"}],"/contracts/":[{"text":"Contract Authority","link":"/contracts/CONTRACT_AUTHORITY.md"},{"text":"Fallback Control Plane","link":"/contracts/FALLBACK_POLICY.md"},{"text":"Provider Adapter Contracts (G-RV-05)","link":"/contracts/PROVIDER_ADAPTER_CONTRACTS.md"},{"text":"Contract Upgrade Playbook","link":"/contracts/UPGRADE_PLAYBOOK.md"}],"/scratchpad/":[{"text":"Session Scratch Board & Optimization Plan","link":"/scratchpad/session_review.md"}],"/architecture/":[{"text":"Diagrams","collapsed":false,"items":[{"text":"Module Dependencies","link":"/diagrams/module-dependencies.md"},{"text":"Package Structure","link":"/diagrams/package-structure.md"}]},{"text":"Agent Sandboxing Architecture: WASM/Containers/VMs (No Docker)","link":"/architecture/AGENT_SANDBOXING_ARCHITECTURE.md"},{"text":"Python Frontmatter + Native Backmatter Architecture","link":"/architecture/FRONTMATTER_BACKMATTER_ARCHITECTURE.md"},{"text":"Hybrid Mac/Windows Development Environment Architecture","link":"/architecture/HYBRID_MAC_WIN_DEV_ENVIRONMENT.md"}],"/guides/":[{"text":"Agent Debugging and Remediation Guide","link":"/guides/AGENT_DEBUGGING_AND_REMEDIATION_GUIDE.md"},{"text":"Agent Instructions: thegent Deep-Dive","link":"/guides/AGENT_INSTRUCTIONS_THEGENT.md"},{"text":"Automated Documentation Demos","link":"/guides/AUTOMATED_DEMOS.md"},{"text":"BKM Implementation Guides","link":"/guides/BKM_IMPLEMENTATION_GUIDES.md"},{"text":"Content Tabs Component","link":"/guides/CONTENT_TABS_GUIDE.md"},{"text":"Cross-Platform Desktop Automation — Complete Guide","link":"/guides/CROSS_PLATFORM_COMPLETE.md"},{"text":"Cross-Platform Desktop Automation: Developer Cookbook","link":"/guides/CROSS_PLATFORM_DEVELOPER_COOKBOOK.md"},{"text":"Cross-Platform Desktop Automation: Implementation Templates","link":"/guides/CROSS_PLATFORM_IMPLEMENTATION_TEMPLATES.md"},{"text":"Cross-Platform Desktop Automation: Migration Guide","link":"/guides/CROSS_PLATFORM_MIGRATION_GUIDE.md"},{"text":"Cross-Platform Desktop Automation: Quick Start Guide","link":"/guides/CROSS_PLATFORM_QUICK_START.md"},{"text":"Cross-Platform Desktop Automation: Implementation Roadmap","link":"/guides/CROSS_PLATFORM_ROADMAP.md"},{"text":"Doctor Command Fixes","link":"/guides/DOCTOR_FIXES.md"},{"text":"Fix Shell Corruption Issue","link":"/guides/FIX_SHELL_CORRUPTION.md"},{"text":"Fix Shell Fork Errors: Quick Guide","link":"/guides/FIX_SHELL_FORK_ERRORS.md"},{"text":"Guides Index","link":"/guides/GUIDES_INDEX.md"},{"text":"Hook Rust Benchmark Harness Guide","link":"/guides/HOOK_RUST_BENCHMARK_HARNESS_GUIDE.md"},{"text":"Hybrid Mac/Windows Environment Quick Start Guide","link":"/guides/HYBRID_ENV_QUICK_START.md"},{"text":"Implementation Patterns Guide","link":"/guides/IMPLEMENTATION_PATTERNS.md"},{"text":"Job Pool System - Usage Guide","link":"/guides/JOB_POOL_USAGE.md"},{"text":"OAuth-Only Authentication Policy","link":"/guides/OAUTH_ONLY_AUTHENTICATION.md"},{"text":"Operational Learning Assets (WP-12008)","link":"/guides/OPERATIONAL_LEARNING.md"},{"text":"oxlint Integration Guide (Phase 4)","link":"/guides/OXLINT_INTEGRATION_GUIDE.md"},{"text":"Thegent Phase 10 Summary and Migration Guide (WP-10010)","link":"/guides/PHASE_10_GUIDE.md"},{"text":"Thegent Phase 11 Summary and Evidence Pack (WP-11010)","link":"/guides/PHASE_11_GUIDE.md"},{"text":"Phase 4 Quick Start: ESLint → oxlint Migration","link":"/guides/PHASE_4_QUICK_START.md"},{"text":"Thegent Phase 7-9 Summary and Training Guide (WP-9010)","link":"/guides/PHASE_7_9_GUIDE.md"},{"text":"Prompts Tooling — Cursor / Codex / Claude Aggregate","link":"/guides/PROMPTS_TOOLING.md"},{"text":"Provider Setup Guide","link":"/guides/PROVIDER_SETUP_GUIDE.md"},{"text":"Quality Assurance Guide","link":"/guides/QUALITY_ASSURANCE.md"},{"text":"Quick Fix: Shell Setup Issues","link":"/guides/QUICK_FIX_SHELL_SETUP.md"},{"text":"Runtime Optimization Guide","link":"/guides/RUNTIME_OPTIMIZATION.md"},{"text":"Runtime Resource Management Guide","link":"/guides/RUNTIME_RESOURCE_MANAGEMENT.md"},{"text":"Shell Advanced Features Guide","link":"/guides/SHELL_ADVANCED_FEATURES.md"},{"text":"Shell Corruption Fix - Complete Solution","link":"/guides/SHELL_CORRUPTION_FIX_COMPLETE.md"},{"text":"Complete Shell Environment System","link":"/guides/SHELL_ENVIRONMENT_COMPLETE.md"},{"text":"Shell Environment Management","link":"/guides/SHELL_ENVIRONMENT_MANAGEMENT.md"},{"text":"Shell Optimization Guide","link":"/guides/SHELL_OPTIMIZATION_GUIDE.md"},{"text":"Shell & Zsh Plugin Setup — Long-Term Fix","link":"/guides/SHELL_ZSH_PLUGIN_SETUP.md"},{"text":"Sitback Plugin API","link":"/guides/SITBACK_PLUGINS.md"},{"text":"Starship + direnv Setup Complete","link":"/guides/STARSHIP_DIRENV_SETUP.md"},{"text":"🚀 Hooks Optimization Initiative - START HERE","link":"/guides/START_HERE.md"},{"text":"Task Routing Quick Reference Guide","link":"/guides/TASK_ROUTING_QUICK_REF.md"},{"text":"thegent Testing Guide","link":"/guides/TESTING.md"},{"text":"Thegent CLI Reference Guide","link":"/guides/THGENT_CLI_REFERENCE.md"},{"text":"Troubleshooting Guide","link":"/guides/TROUBLESHOOTING.md"},{"text":"Creating Terminal Recordings with VHS","link":"/guides/VHS_RECORDINGS.md"},{"text":"VitePress Docsite Setup","link":"/guides/VITEPPRESS_SETUP.md"},{"text":"VitePress Rich Documentation — Usage Guide","link":"/guides/VITEPRESS_USAGE_GUIDE.md"},{"text":"Anti-Pattern Detection Guide","link":"/guides/anti-patterns.md"},{"text":"Architecture Enforcement Guide","link":"/guides/architecture-enforcement.md"},{"text":"Guides","link":"/guides/index.md"}],"/examples/":[{"text":"VitePress Examples","link":"/examples/README.md"},{"text":"CodePlayground Examples","link":"/examples/code-playground-example.md"},{"text":"Demo GIF Examples","link":"/examples/demo-gif-example.md"},{"text":"Math & Emoji Examples","link":"/examples/math-emoji-example.md"},{"text":"Mermaid Diagram Examples","link":"/examples/mermaid-example.md"},{"text":"Tooltip Component Examples","link":"/examples/tooltip-example.md"}],"/governance/":[{"text":"Cost Governance Design (G-GP-06)","link":"/governance/COST_GOVERNANCE_DESIGN.md"},{"text":"HITL (Human-in-the-Loop) Design (G-GP-05)","link":"/governance/HITL_DESIGN.md"},{"text":"NeMo Guardrails Design (G-GP-02)","link":"/governance/NEMO_GUARDRAILS_DESIGN.md"},{"text":"OPA Integration Design (G-GP-01)","link":"/governance/OPA_INTEGRATION_DESIGN.md"},{"text":"Retention Policy Design (G-GP-07)","link":"/governance/RETENTION_POLICY_DESIGN.md"},{"text":"Sandboxing Design (G-GP-08)","link":"/governance/SANDBOXING_DESIGN.md"}],"/migration/":[{"text":"Advanced Performance Patterns & Best Practices","link":"/migration/ADVANCED_PATTERNS.md"},{"text":"Complete Solution: Polished, Optimized, Production-Ready","link":"/migration/COMPLETE_SOLUTION.md"},{"text":"Comprehensive Benchmarking Strategy","link":"/migration/COMPREHENSIVE_BENCHMARKING.md"},{"text":"Comprehensive Performance Analysis & Migration Strategy","link":"/migration/COMPREHENSIVE_PERFORMANCE_ANALYSIS.md"},{"text":"Design Principles","link":"/migration/DESIGN_PRINCIPLES.md"},{"text":"Usage Examples","link":"/migration/EXAMPLES.md"},{"text":"Fork Failure (EAGAIN) Analysis & Solutions","link":"/migration/FORK_FAILURE_ANALYSIS.md"},{"text":"Comprehensive Implementation Roadmap","link":"/migration/IMPLEMENTATION_ROADMAP.md"},{"text":"Production Readiness Checklist","link":"/migration/PRODUCTION_READINESS.md"},{"text":"Quick Start Guide","link":"/migration/QUICK_START.md"},{"text":"Shell to Rust/Go Migration Plan","link":"/migration/RUST_GO_MIGRATION_PLAN.md"},{"text":"Performance Optimization Summary","link":"/migration/SUMMARY.md"},{"text":"The Ultimate Guide: Comprehensive Performance Optimization & Migration","link":"/migration/ULTIMATE_GUIDE.md"},{"text":"User Guide: thegent Performance Optimizations","link":"/migration/USER_GUIDE.md"}],"/demos/":[{"text":"Demo Scripts for VitePress Documentation","link":"/demos/README.md"}],"/reference/":[{"text":"Api","collapsed":false,"items":[{"text":"adapter_policy API Reference","link":"/api/adapter_policy_api.md"},{"text":"adapters API Reference","link":"/api/adapters_api.md"},{"text":"agent_deployer API Reference","link":"/api/agent_deployer_api.md"},{"text":"agents API Reference","link":"/api/agents_api.md"},{"text":"agileplus API Reference","link":"/api/agileplus_api.md"},{"text":"alerting API Reference","link":"/api/alerting_api.md"},{"text":"alerts API Reference","link":"/api/alerts_api.md"},{"text":"analyzer API Reference","link":"/api/analyzer_api.md"},{"text":"api_evolution API Reference","link":"/api/api_evolution_api.md"},{"text":"arbitrage API Reference","link":"/api/arbitrage_api.md"},{"text":"attestation API Reference","link":"/api/attestation_api.md"},{"text":"audit API Reference","link":"/api/audit_api.md"},{"text":"auth_bridge API Reference","link":"/api/auth_bridge_api.md"},{"text":"autopoiesis API Reference","link":"/api/autopoiesis_api.md"},{"text":"backlog API Reference","link":"/api/backlog_api.md"},{"text":"base API Reference","link":"/api/base_api.md"},{"text":"billing API Reference","link":"/api/billing_api.md"},{"text":"black_box_proxy API Reference","link":"/api/black_box_proxy_api.md"},{"text":"breakers API Reference","link":"/api/breakers_api.md"},{"text":"cache API Reference","link":"/api/cache_api.md"},{"text":"cage API Reference","link":"/api/cage_api.md"},{"text":"calibration API Reference","link":"/api/calibration_api.md"},{"text":"capability_registry API Reference","link":"/api/capability_registry_api.md"},{"text":"catalog API Reference","link":"/api/catalog_api.md"},{"text":"checker API Reference","link":"/api/checker_api.md"},{"text":"checkpoint API Reference","link":"/api/checkpoint_api.md"},{"text":"circuit_breaker API Reference","link":"/api/circuit_breaker_api.md"},{"text":"cli API Reference","link":"/api/cli_api.md"},{"text":"cli_document_queue API Reference","link":"/api/cli_document_queue_api.md"},{"text":"cli_impl API Reference","link":"/api/cli_impl_api.md"},{"text":"cliproxy_adapter API Reference","link":"/api/cliproxy_adapter_api.md"},{"text":"cliproxy_data API Reference","link":"/api/cliproxy_data_api.md"},{"text":"cliproxy_manager API Reference","link":"/api/cliproxy_manager_api.md"},{"text":"clode_main API Reference","link":"/api/clode_main_api.md"},{"text":"codex_proxy API Reference","link":"/api/codex_proxy_api.md"},{"text":"collaboration API Reference","link":"/api/collaboration_api.md"},{"text":"compliance API Reference","link":"/api/compliance_api.md"},{"text":"config API Reference","link":"/api/config_api.md"},{"text":"conformance API Reference","link":"/api/conformance_api.md"},{"text":"consistency_checker API Reference","link":"/api/consistency_checker_api.md"},{"text":"constitution API Reference","link":"/api/constitution_api.md"},{"text":"context API Reference","link":"/api/context_api.md"},{"text":"contracts API Reference","link":"/api/contracts_api.md"},{"text":"control_vectors API Reference","link":"/api/control_vectors_api.md"},{"text":"coordination API Reference","link":"/api/coordination_api.md"},{"text":"cost API Reference","link":"/api/cost_api.md"},{"text":"cost_controller API Reference","link":"/api/cost_controller_api.md"},{"text":"cost_tracker API Reference","link":"/api/cost_tracker_api.md"},{"text":"cost_values API Reference","link":"/api/cost_values_api.md"},{"text":"csm API Reference","link":"/api/csm_api.md"},{"text":"cursor_api_runner API Reference","link":"/api/cursor_api_runner_api.md"},{"text":"deferral API Reference","link":"/api/deferral_api.md"},{"text":"design API Reference","link":"/api/design_api.md"},{"text":"design_language API Reference","link":"/api/design_language_api.md"},{"text":"dex_main API Reference","link":"/api/dex_main_api.md"},{"text":"digital_twin API Reference","link":"/api/digital_twin_api.md"},{"text":"direct_agents API Reference","link":"/api/direct_agents_api.md"},{"text":"discovery API Reference","link":"/api/discovery_api.md"},{"text":"dispatch_graph API Reference","link":"/api/dispatch_graph_api.md"},{"text":"dlq API Reference","link":"/api/dlq_api.md"},{"text":"dna_storage API Reference","link":"/api/dna_storage_api.md"},{"text":"doctor API Reference","link":"/api/doctor_api.md"},{"text":"donut_adapter API Reference","link":"/api/donut_adapter_api.md"},{"text":"drift API Reference","link":"/api/drift_api.md"},{"text":"drift_corrector API Reference","link":"/api/drift_corrector_api.md"},{"text":"droid API Reference","link":"/api/droid_api.md"},{"text":"edge_sync API Reference","link":"/api/edge_sync_api.md"},{"text":"egress API Reference","link":"/api/egress_api.md"},{"text":"escalation API Reference","link":"/api/escalation_api.md"},{"text":"ethics_proof API Reference","link":"/api/ethics_proof_api.md"},{"text":"events API Reference","link":"/api/events_api.md"},{"text":"evidence API Reference","link":"/api/evidence_api.md"},{"text":"evidence_graph API Reference","link":"/api/evidence_graph_api.md"},{"text":"evidence_ledger API Reference","link":"/api/evidence_ledger_api.md"},{"text":"evolution API Reference","link":"/api/evolution_api.md"},{"text":"execution API Reference","link":"/api/execution_api.md"},{"text":"exit_codes API Reference","link":"/api/exit_codes_api.md"},{"text":"explainability API Reference","link":"/api/explainability_api.md"},{"text":"explanations API Reference","link":"/api/explanations_api.md"},{"text":"failure_modes API Reference","link":"/api/failure_modes_api.md"},{"text":"fallback_ui API Reference","link":"/api/fallback_ui_api.md"},{"text":"federation API Reference","link":"/api/federation_api.md"},{"text":"fork_guard API Reference","link":"/api/fork_guard_api.md"},{"text":"formal_loop API Reference","link":"/api/formal_loop_api.md"},{"text":"galactic API Reference","link":"/api/galactic_api.md"},{"text":"gardener API Reference","link":"/api/gardener_api.md"},{"text":"gardening API Reference","link":"/api/gardening_api.md"},{"text":"geo_guard API Reference","link":"/api/geo_guard_api.md"},{"text":"governance API Reference","link":"/api/governance_api.md"},{"text":"graph API Reference","link":"/api/graph_api.md"},{"text":"handoff API Reference","link":"/api/handoff_api.md"},{"text":"hardware_id API Reference","link":"/api/hardware_id_api.md"},{"text":"harmonized_paths API Reference","link":"/api/harmonized_paths_api.md"},{"text":"harness API Reference","link":"/api/harness_api.md"},{"text":"health_score API Reference","link":"/api/health_score_api.md"},{"text":"homomorphic API Reference","link":"/api/homomorphic_api.md"},{"text":"human API Reference","link":"/api/human_api.md"},{"text":"hybrid_router API Reference","link":"/api/hybrid_router_api.md"},{"text":"identity API Reference","link":"/api/identity_api.md"},{"text":"information_life API Reference","link":"/api/information_life_api.md"},{"text":"infra API Reference","link":"/api/infra_api.md"},{"text":"input_guardrails API Reference","link":"/api/input_guardrails_api.md"},{"text":"install API Reference","link":"/api/install_api.md"},{"text":"integration API Reference","link":"/api/integration_api.md"},{"text":"kill_switch API Reference","link":"/api/kill_switch_api.md"},{"text":"kpis API Reference","link":"/api/kpis_api.md"},{"text":"lanes API Reference","link":"/api/lanes_api.md"},{"text":"launch API Reference","link":"/api/launch_api.md"},{"text":"learning API Reference","link":"/api/learning_api.md"},{"text":"leasing API Reference","link":"/api/leasing_api.md"},{"text":"ledger API Reference","link":"/api/ledger_api.md"},{"text":"litellm_router API Reference","link":"/api/litellm_router_api.md"},{"text":"liveness API Reference","link":"/api/liveness_api.md"},{"text":"load_based_limits API Reference","link":"/api/load_based_limits_api.md"},{"text":"lock_free API Reference","link":"/api/lock_free_api.md"},{"text":"loop_controller API Reference","link":"/api/loop_controller_api.md"},{"text":"main API Reference","link":"/api/main_api.md"},{"text":"manage_devkit API Reference","link":"/api/manage_devkit_api.md"},{"text":"manager API Reference","link":"/api/manager_api.md"},{"text":"market API Reference","link":"/api/market_api.md"},{"text":"marketplace API Reference","link":"/api/marketplace_api.md"},{"text":"mcp_manage API Reference","link":"/api/mcp_manage_api.md"},{"text":"mcp_server API Reference","link":"/api/mcp_server_api.md"},{"text":"mcp_sitback API Reference","link":"/api/mcp_sitback_api.md"},{"text":"mcp_tools_modes API Reference","link":"/api/mcp_tools_modes_api.md"},{"text":"memory API Reference","link":"/api/memory_api.md"},{"text":"mesh API Reference","link":"/api/mesh_api.md"},{"text":"meta API Reference","link":"/api/meta_api.md"},{"text":"mgmt_manage API Reference","link":"/api/mgmt_manage_api.md"},{"text":"migration API Reference","link":"/api/migration_api.md"},{"text":"models API Reference","link":"/api/models_api.md"},{"text":"models_meta API Reference","link":"/api/models_meta_api.md"},{"text":"modes API Reference","link":"/api/modes_api.md"},{"text":"moral_ui API Reference","link":"/api/moral_ui_api.md"},{"text":"multiverse API Reference","link":"/api/multiverse_api.md"},{"text":"naming API Reference","link":"/api/naming_api.md"},{"text":"never_idle API Reference","link":"/api/never_idle_api.md"},{"text":"omega API Reference","link":"/api/omega_api.md"},{"text":"omega_consensus API Reference","link":"/api/omega_consensus_api.md"},{"text":"omega_safety API Reference","link":"/api/omega_safety_api.md"},{"text":"operations API Reference","link":"/api/operations_api.md"},{"text":"optimizer API Reference","link":"/api/optimizer_api.md"},{"text":"orchestration API Reference","link":"/api/orchestration_api.md"},{"text":"orchestration_modes API Reference","link":"/api/orchestration_modes_api.md"},{"text":"otel_instrumentation API Reference","link":"/api/otel_instrumentation_api.md"},{"text":"output_parser API Reference","link":"/api/output_parser_api.md"},{"text":"overrides API Reference","link":"/api/overrides_api.md"},{"text":"oversight API Reference","link":"/api/oversight_api.md"},{"text":"pareto_viz API Reference","link":"/api/pareto_viz_api.md"},{"text":"parser API Reference","link":"/api/parser_api.md"},{"text":"payments API Reference","link":"/api/payments_api.md"},{"text":"personas API Reference","link":"/api/personas_api.md"},{"text":"phases API Reference","link":"/api/phases_api.md"},{"text":"physical API Reference","link":"/api/physical_api.md"},{"text":"plan_system API Reference","link":"/api/plan_system_api.md"},{"text":"planning API Reference","link":"/api/planning_api.md"},{"text":"platform_paths API Reference","link":"/api/platform_paths_api.md"},{"text":"playbooks API Reference","link":"/api/playbooks_api.md"},{"text":"plugin_lifecycle API Reference","link":"/api/plugin_lifecycle_api.md"},{"text":"policy API Reference","link":"/api/policy_api.md"},{"text":"policy_evolver API Reference","link":"/api/policy_evolver_api.md"},{"text":"preemption API Reference","link":"/api/preemption_api.md"},{"text":"presets API Reference","link":"/api/presets_api.md"},{"text":"probes API Reference","link":"/api/probes_api.md"},{"text":"probing API Reference","link":"/api/probing_api.md"},{"text":"process_registry API Reference","link":"/api/process_registry_api.md"},{"text":"projects API Reference","link":"/api/projects_api.md"},{"text":"promotion API Reference","link":"/api/promotion_api.md"},{"text":"prompts API Reference","link":"/api/prompts_api.md"},{"text":"proof_carrying API Reference","link":"/api/proof_carrying_api.md"},{"text":"protocol API Reference","link":"/api/protocol_api.md"},{"text":"provider_types API Reference","link":"/api/provider_types_api.md"},{"text":"provisioner API Reference","link":"/api/provisioner_api.md"},{"text":"prune_utils API Reference","link":"/api/prune_utils_api.md"},{"text":"quality_values API Reference","link":"/api/quality_values_api.md"},{"text":"quantum_safe API Reference","link":"/api/quantum_safe_api.md"},{"text":"queue_tui API Reference","link":"/api/queue_tui_api.md"},{"text":"rbac API Reference","link":"/api/rbac_api.md"},{"text":"red_team API Reference","link":"/api/red_team_api.md"},{"text":"refactoring API Reference","link":"/api/refactoring_api.md"},{"text":"registry API Reference","link":"/api/registry_api.md"},{"text":"relativistic API Reference","link":"/api/relativistic_api.md"},{"text":"release_packager API Reference","link":"/api/release_packager_api.md"},{"text":"remediation_planner API Reference","link":"/api/remediation_planner_api.md"},{"text":"reputation API Reference","link":"/api/reputation_api.md"},{"text":"research API Reference","link":"/api/research_api.md"},{"text":"resilience API Reference","link":"/api/resilience_api.md"},{"text":"retention API Reference","link":"/api/retention_api.md"},{"text":"role_agent API Reference","link":"/api/role_agent_api.md"},{"text":"router API Reference","link":"/api/router_api.md"},{"text":"routing API Reference","link":"/api/routing_api.md"},{"text":"routing_contracts API Reference","link":"/api/routing_contracts_api.md"},{"text":"sandbox API Reference","link":"/api/sandbox_api.md"},{"text":"scanner API Reference","link":"/api/scanner_api.md"},{"text":"schema_formal API Reference","link":"/api/schema_formal_api.md"},{"text":"scoring API Reference","link":"/api/scoring_api.md"},{"text":"scrapers API Reference","link":"/api/scrapers_api.md"},{"text":"selector API Reference","link":"/api/selector_api.md"},{"text":"self_healing API Reference","link":"/api/self_healing_api.md"},{"text":"semantic_firewall API Reference","link":"/api/semantic_firewall_api.md"},{"text":"session_scraper API Reference","link":"/api/session_scraper_api.md"},{"text":"shadow API Reference","link":"/api/shadow_api.md"},{"text":"heliosShield_bridge API Reference","link":"/api/heliosShield_bridge_api.md"},{"text":"shell_cli API Reference","link":"/api/shell_cli_api.md"},{"text":"shm API Reference","link":"/api/shm_api.md"},{"text":"shm_context API Reference","link":"/api/shm_context_api.md"},{"text":"signatures API Reference","link":"/api/signatures_api.md"},{"text":"simulation API Reference","link":"/api/simulation_api.md"},{"text":"sitback API Reference","link":"/api/sitback_api.md"},{"text":"sitback_plugins API Reference","link":"/api/sitback_plugins_api.md"},{"text":"slack API Reference","link":"/api/slack_api.md"},{"text":"slo_regulator API Reference","link":"/api/slo_regulator_api.md"},{"text":"snapshot API Reference","link":"/api/snapshot_api.md"},{"text":"speed_values API Reference","link":"/api/speed_values_api.md"},{"text":"state_machine API Reference","link":"/api/state_machine_api.md"},{"text":"storage API Reference","link":"/api/storage_api.md"},{"text":"subprocess_manager API Reference","link":"/api/subprocess_manager_api.md"},{"text":"summary API Reference","link":"/api/summary_api.md"},{"text":"support API Reference","link":"/api/support_api.md"},{"text":"swarm API Reference","link":"/api/swarm_api.md"},{"text":"swarm_consensus API Reference","link":"/api/swarm_consensus_api.md"},{"text":"swarm_memory API Reference","link":"/api/swarm_memory_api.md"},{"text":"symbolic API Reference","link":"/api/symbolic_api.md"},{"text":"sync API Reference","link":"/api/sync_api.md"},{"text":"synthesis API Reference","link":"/api/synthesis_api.md"},{"text":"task_router API Reference","link":"/api/task_router_api.md"},{"text":"tasks API Reference","link":"/api/tasks_api.md"},{"text":"teammates API Reference","link":"/api/teammates_api.md"},{"text":"tee_check API Reference","link":"/api/tee_check_api.md"},{"text":"telemetry API Reference","link":"/api/telemetry_api.md"},{"text":"tenancy API Reference","link":"/api/tenancy_api.md"},{"text":"terminal API Reference","link":"/api/terminal_api.md"},{"text":"terminal_cli API Reference","link":"/api/terminal_cli_api.md"},{"text":"thegent API Reference","link":"/api/thegent_api.md"},{"text":"thg_platform API Reference","link":"/api/thg_platform_api.md"},{"text":"tool_adapter API Reference","link":"/api/tool_adapter_api.md"},{"text":"tool_safety API Reference","link":"/api/tool_safety_api.md"},{"text":"traceability API Reference","link":"/api/traceability_api.md"},{"text":"transactions API Reference","link":"/api/transactions_api.md"},{"text":"triggers API Reference","link":"/api/triggers_api.md"},{"text":"trust API Reference","link":"/api/trust_api.md"},{"text":"tui API Reference","link":"/api/tui_api.md"},{"text":"tuning API Reference","link":"/api/tuning_api.md"},{"text":"unified_config API Reference","link":"/api/unified_config_api.md"},{"text":"universal_adapter API Reference","link":"/api/universal_adapter_api.md"},{"text":"utils API Reference","link":"/api/utils_api.md"},{"text":"v1 API Reference","link":"/api/v1_api.md"},{"text":"v2 API Reference","link":"/api/v2_api.md"},{"text":"validation API Reference","link":"/api/validation_api.md"},{"text":"value_lock API Reference","link":"/api/value_lock_api.md"},{"text":"verification API Reference","link":"/api/verification_api.md"},{"text":"verification_gate API Reference","link":"/api/verification_gate_api.md"},{"text":"watchdog API Reference","link":"/api/watchdog_api.md"},{"text":"work_stream API Reference","link":"/api/work_stream_api.md"},{"text":"worker_pool API Reference","link":"/api/worker_pool_api.md"},{"text":"xml_repair API Reference","link":"/api/xml_repair_api.md"},{"text":"zkp API Reference","link":"/api/zkp_api.md"}]},{"text":"Routing System: Project Complete Summary","link":"/reference/00_ROUTING_PROJECT_COMPLETE.md"},{"text":"Agent Identity & Sovereignty Depth (WP-6004)","link":"/reference/AGENT_IDENTITY_SOVEREIGNTY_DEPTH.md"},{"text":"Agent Communication Language (JSON-ACL) & Negotiation (WP-1006)","link":"/reference/AGENT_NEGOTIATION_ACL_DEPTH.md"},{"text":"Agent OS Principals — Depth Document","link":"/reference/AGENT_OS_PRINCIPALS_DEPTH.md"},{"text":"Benchmark Comparison: SWE-Bench vs Terminal Bench 2.0","link":"/reference/BENCHMARK_COMPARISON_SWE_BENCH_VS_TERMINAL_BENCH_2_0.md"},{"text":"Global Claude Code Instructions","link":"/reference/CLAUDE_CORE_GUIDELINES.md"},{"text":"CLAUDE Appendix: thegent-specific and domain workflow rules","link":"/reference/CLAUDE_THEGENT_RUNTIME_APPENDIX.md"},{"text":"Complete Provider Routing Map (All 12+ Providers)","link":"/reference/COMPLETE_PROVIDER_ROUTING_MAP.md"},{"text":"Constitutional Enforcement & Proof of Alignment (WP-3001)","link":"/reference/CONSTITUTIONAL_ENFORCEMENT_DEPTH.md"},{"text":"Context Management & Semantic Compression Depth (WP-5001)","link":"/reference/CONTEXT_MANAGEMENT_DEPTH.md"},{"text":"Cost Enforcement Policy: 2x Limit & Escalation Framework","link":"/reference/COST_ENFORCEMENT_POLICY.md"},{"text":"Cross-Platform Desktop Automation: API Reference","link":"/reference/CROSS_PLATFORM_API_REFERENCE.md"},{"text":"Cross-Platform Multi-Tenant Desktop Automation Quick Reference","link":"/reference/CROSS_PLATFORM_MULTI_TENANT_QUICK_REFERENCE.md"},{"text":"Dominance Proof Reference","link":"/reference/DOMINANCE_PROOF_REFERENCE.md"},{"text":"Economic Governance & Token ROI Modeling (WP-5003)","link":"/reference/ECONOMIC_GOVERNANCE_DEPTH.md"},{"text":"Frontmatter/Backmatter Integration Points","link":"/reference/FRONTMATTER_BACKMATTER_INTEGRATION_POINTS.md"},{"text":"FR Tracker: thegent","link":"/reference/FR_TRACKER.md"},{"text":"Gardener Architecture","link":"/reference/GARDENER_ARCHITECTURE.md"},{"text":"Human-Agent Collaboration (HAC) & HITL Patterns (WP-4001..4009)","link":"/reference/HAC_AND_HITL_PATTERNS.md"},{"text":"Hook Optimization Strategy","link":"/reference/HOOK_OPTIMIZATION_STRATEGY.md"},{"text":"Hybrid Mac/Windows Development Environment - Summary","link":"/reference/HYBRID_ENV_SUMMARY.md"},{"text":"Indexing and Optimization Systems — Reference","link":"/reference/INDEXING_AND_OPTIMIZATION_SYSTEMS.md"},{"text":"TaskRouter + Pareto Routing Integration Architecture","link":"/reference/INTEGRATION_ARCHITECTURE.md"},{"text":"TaskRouter + Pareto Routing Integration — Document Index","link":"/reference/INTEGRATION_INDEX.md"},{"text":"TaskRouter Integration Quick Start","link":"/reference/INTEGRATION_QUICK_START.md"},{"text":"MAIF Artifact Specification & Provenance Depth (WP-3002)","link":"/reference/MAIF_ARTIFACT_SPEC_DEPTH.md"},{"text":"MCP Tool Retry Policy","link":"/reference/MCP_RETRY_POLICY.md"},{"text":"Corrected Model Ranking Using Pareto Frontier","link":"/reference/MODEL_RANKING_CORRECTED.md"},{"text":"Model Routing Decision Tree","link":"/reference/MODEL_ROUTING_DECISION_TREE.md"},{"text":"Model Routing & Cost Governance: Complete Index","link":"/reference/MODEL_ROUTING_INDEX.md"},{"text":"Model Routing & Cost Governance: Quick Reference","link":"/reference/MODEL_ROUTING_SUMMARY.md"},{"text":"Model Routing: Terminal Bench 2.0 Quick Reference","link":"/reference/MODEL_ROUTING_TERMINAL_BENCH_2_0_QUICK_REF.md"},{"text":"Model Selection Documentation Index","link":"/reference/MODEL_SELECTION_INDEX.md"},{"text":"Monitoring Alert Rules","link":"/reference/MONITORING_ALERT_RULES.md"},{"text":"Monitoring Dashboard Specifications","link":"/reference/MONITORING_DASHBOARD_SPEC.md"},{"text":"Monitoring Metrics Reference","link":"/reference/MONITORING_METRICS_REFERENCE.md"},{"text":"Monitoring System Documentation","link":"/reference/MONITORING_README.md"},{"text":"Monitoring Setup Guide","link":"/reference/MONITORING_SETUP_GUIDE.md"},{"text":"Civilizational Multi-Swarm Hierarchy (WP-1006, WP-5004)","link":"/reference/MULTI_SWARM_HIERARCHY_DEPTH.md"},{"text":"OpenTelemetry GenAI & Observability Depth (WP-Y6)","link":"/reference/OTEL_GENAI_AND_HYSTERESIS_DEPTH.md"},{"text":"oxlint Rule Mapping Reference","link":"/reference/OXLINT_RULE_MAPPING.md"},{"text":"Pareto Frontier Algorithm: Pseudocode & Implementation Guide","link":"/reference/PARETO_ALGORITHM_PSEUDOCODE.md"},{"text":"Pareto Frontier: Executive Summary","link":"/reference/PARETO_EXECUTIVE_SUMMARY.md"},{"text":"Pareto Frontier Analysis & Model Ranking Algorithm","link":"/reference/PARETO_FRONTIER_ANALYSIS.md"},{"text":"Pareto Frontier Analysis: Complete Model Evaluation","link":"/reference/PARETO_FRONTIER_COMPLETE_ANALYSIS.md"},{"text":"Pareto Frontier Matrix: Model Selection Guide","link":"/reference/PARETO_FRONTIER_MATRIX.md"},{"text":"Pareto Frontier Quick Reference","link":"/reference/PARETO_FRONTIER_QUICK_REFERENCE.md"},{"text":"Pareto Frontier Analysis: Complete Data Table","link":"/reference/PARETO_FRONTIER_TABLE.md"},{"text":"Pareto Frontier Analysis: Terminal Bench 2.0 (Corrected)","link":"/reference/PARETO_FRONTIER_TERMINAL_BENCH_2_0.md"},{"text":"Pareto Frontier Analysis: Complete Index","link":"/reference/PARETO_INDEX.md"},{"text":"Multi-Objective Provider Routing & Pareto Fronts (WP-1004)","link":"/reference/PARETO_ROUTING_DESIGN.md"},{"text":"Pareto Frontier Visualization & Diagrams","link":"/reference/PARETO_VISUALIZATION.md"},{"text":"Phase 3.5 Quick Reference","link":"/reference/PHASE_3_5_QUICK_REFERENCE.md"},{"text":"Phase 4 UX: Operator Cockpit & Rationale Depth (WP-4001)","link":"/reference/PHASE_4_COCKPIT_UX_DEPTH.md"},{"text":"Phase 5 Scale: Redis & Distributed Robustness (WP-5004)","link":"/reference/PHASE_5_SCALE_ROBUSTNESS_DEPTH.md"},{"text":"POSIX + pwsh Shell Strategy","link":"/reference/POSIX_PWSH_SHELL_STRATEGY.md"},{"text":"Provider Limits and Auto-Fallback","link":"/reference/PROVIDER_LIMITS_AND_FALLBACK.md"},{"text":"Provider Model Behavior Constraints","link":"/reference/PROVIDER_MODEL_BEHAVIOR.md"},{"text":"Provider Model Reference","link":"/reference/PROVIDER_MODEL_REFERENCE.md"},{"text":"Robustness, Breadth, and Depth — Phase Evolution","link":"/reference/ROBUSTNESS_AND_FUTURE_DEPTH.md"},{"text":"Routing Decision Matrix: Task Category Logic","link":"/reference/ROUTING_DECISION_MATRIX.md"},{"text":"Final Routing Recommendation (Terminal Bench 2.0)","link":"/reference/ROUTING_FINAL_RECOMMENDATION.md"},{"text":"Task Routing Implementation Architecture","link":"/reference/ROUTING_IMPLEMENTATION_ARCHITECTURE.md"},{"text":"Model Routing Quick Card (Pocket Reference)","link":"/reference/ROUTING_QUICK_CARD.md"},{"text":"Routing System: Master Summary & Implementation Roadmap","link":"/reference/ROUTING_SYSTEM_MASTER_SUMMARY.md"},{"text":"Rust-Based CLI Tooling","link":"/reference/RUST_TOOLING.md"},{"text":"Agentic CI/CD & Self-Healing Loops (WP-2004)","link":"/reference/SELF_HEALING_AGENTIC_CICD_DEPTH.md"},{"text":"Planning Simulation & Replay Sandbox Depth (WP-4007, WP-12004)","link":"/reference/SIMULATION_AND_SANDBOX_DEPTH.md"},{"text":"MCP Tool SLO Targets (G-OP-08)","link":"/reference/SLO_TARGETS.md"},{"text":"Speed & Quality Index Implementation Plan","link":"/reference/SPEED_QUALITY_INDEX_IMPLEMENTATION_PLAN.md"},{"text":"Starship Prompt — Long-Term Fix for Scan Timeout","link":"/reference/STARSHIP_SETUP.md"},{"text":"Swarm Memory & Multi-Agent Coordination (WP-1006)","link":"/reference/SWARM_MEMORY_COORDINATION_DEPTH.md"},{"text":"Swarm Process Optimizations (Multi-Agent / Multi-Tenant / Multi-Project)","link":"/reference/SWARM_PROCESS_OPTIMIZATIONS.md"},{"text":"Task Categorization & AI Agent Dispatch Routing Design","link":"/reference/TASK_ROUTING_DESIGN.md"},{"text":"Terminal Bench 2.0: Corrected Pareto Frontier & Routing","link":"/reference/TERMINAL_BENCH_2_0_CORRECTED_FRONTIER.md"},{"text":"Tooling & Global Optimizations Audit (In-Depth)","link":"/reference/TOOLING_AND_GLOBAL_OPTIMIZATIONS_AUDIT.md"},{"text":"Tooling and Global Optimizations Audit","link":"/reference/TOOLING_AND_OPTIMIZATION_AUDIT.md"},{"text":"Touchpoint Integration — Deep Dive","link":"/reference/TOUCHPOINT_INTEGRATION_DEEP_DIVE.md"},{"text":"Touchpoint Integration Evaluation","link":"/reference/TOUCHPOINT_INTEGRATION_EVALUATION.md"},{"text":"Unified Work Stream — Design","link":"/reference/UNIFIED_WORK_STREAM_DESIGN.md"},{"text":"WBS Agent Progress — Claim & Coordination","link":"/reference/WBS_AGENT_PROGRESS.md"},{"text":"Unified Work Stream — Canonical","link":"/reference/WORK_STREAM.md"},{"text":"Zen (OpenCode) Integration Analysis","link":"/reference/ZEN_INTEGRATION.md"},{"text":"Reference","link":"/reference/index.md"}],"/reports/":[{"text":"BKM Phase 1 Completion Report","link":"/reports/BKM_PHASE_1_COMPLETION_REPORT.md"},{"text":"Critical Issue #2: Git Cache Invalidation Fix - Complete Report","link":"/reports/CACHE_INVALIDATION_FIX_REPORT.md"},{"text":"Critical Issues Fixes - Completion Report","link":"/reports/CRITICAL_FIXES_COMPLETION_REPORT.md"},{"text":"Critical Issue #2: Unsafe Git Cache Invalidation - Executive Summary","link":"/reports/CRITICAL_ISSUE_2_SUMMARY.md"},{"text":"Phase 10-12 Closure and Final Handoff Note (WP-12010)","link":"/reports/FINAL_CLOSURE_NOTE.md"},{"text":"Holistic + Harmonious Design & Integration — Implementation Complete ✅","link":"/reports/HOLISTIC_DESIGN_IMPLEMENTATION_COMPLETE.md"},{"text":"Holistic + Harmonious Design & Integration — Implementation Progress","link":"/reports/HOLISTIC_DESIGN_IMPLEMENTATION_PROGRESS.md"},{"text":"Thegent Implementation Status Report","link":"/reports/IMPLEMENTATION_STATUS.md"},{"text":"Thegent Implementation Summary","link":"/reports/IMPLEMENTATION_SUMMARY.md"},{"text":"P7.1 Verification Report: Per-Project Quality Gate Checks","link":"/reports/P7.1_VERIFICATION_REPORT.md"},{"text":"P7.2 Cross-Project Consistency Report","link":"/reports/P7.2_CROSS_PROJECT_CONSISTENCY.md"},{"text":"Phase 10-12 Closure and Handoff Note (WP-12010)","link":"/reports/PHASE_10_12_CLOSURE.md"},{"text":"Phase 13: Policy Federation Progress Report","link":"/reports/PHASE_13_PROGRESS_REPORT.md"},{"text":"Phase 14: Autonomous Learning and Cost Sensing Progress Report","link":"/reports/PHASE_14_PROGRESS_REPORT.md"},{"text":"Phase 15: Enterprise Lifecycle and Compliance Progress Report","link":"/reports/PHASE_15_PROGRESS_REPORT.md"},{"text":"Phase 3.5 Optimization Summary","link":"/reports/PHASE_3_5_SUMMARY.md"},{"text":"Phase 3.5 Optimization Validation Report","link":"/reports/PHASE_3_5_VALIDATION.md"},{"text":"Phase 3: Job Pool Implementation - Completion Summary","link":"/reports/PHASE_3_COMPLETION_SUMMARY.md"},{"text":"Phase 3 - Job Pool Implementation Report","link":"/reports/PHASE_3_JOB_POOL_IMPLEMENTATION.md"},{"text":"Phase 4: Advanced Bash Optimizations Report","link":"/reports/PHASE_4_ADVANCED_OPTIMIZATIONS.md"},{"text":"Phase 4 Implementation Summary: ESLint → oxlint Migration","link":"/reports/PHASE_4_IMPLEMENTATION_SUMMARY.md"},{"text":"Phase 4: Advanced Bash Optimizations - Implementation Summary","link":"/reports/PHASE_4_SUMMARY.md"},{"text":"🏁 Project Completion Report: thegent","link":"/reports/PROJECT_COMPLETION_REPORT.md"}]},"socialLinks":[],"outline":"deep","editLink":{"pattern":"https://github.com/kooshapari/temp-PRODVERCEL/485/kush/thegent/edit/main/docs/:path","text":"Edit this page on GitHub"}},"locales":{},"scrollOffset":134,"cleanUrls":false}'));
const __vite_import_meta_env__ = {};
const EXTERNAL_URL_RE = /^(?:[a-z]+:|\/\/)/i;
const APPEARANCE_KEY = "vitepress-theme-appearance";
const HASH_RE = /#.*$/;
const HASH_OR_QUERY_RE = /[?#].*$/;
const INDEX_OR_EXT_RE = /(?:(^|\/)index)?\.(?:md|html)$/;
const inBrowser = typeof document !== "undefined";
const notFoundPageData = {
  relativePath: "404.md",
  filePath: "",
  title: "404",
  description: "Not Found",
  headers: [],
  frontmatter: { sidebar: false, layout: "page" },
  lastUpdated: 0,
  isNotFound: true
};
function isActive(currentPath, matchPath, asRegex = false) {
  if (matchPath === void 0) {
    return false;
  }
  currentPath = normalize(`/${currentPath}`);
  if (asRegex) {
    return new RegExp(matchPath).test(currentPath);
  }
  if (normalize(matchPath) !== currentPath) {
    return false;
  }
  const hashMatch = matchPath.match(HASH_RE);
  if (hashMatch) {
    return (inBrowser ? location.hash : "") === hashMatch[0];
  }
  return true;
}
function normalize(path) {
  return decodeURI(path).replace(HASH_OR_QUERY_RE, "").replace(INDEX_OR_EXT_RE, "$1");
}
function isExternal(path) {
  return EXTERNAL_URL_RE.test(path);
}
function getLocaleForPath(siteData2, relativePath) {
  return Object.keys((siteData2 == null ? void 0 : siteData2.locales) || {}).find((key) => key !== "root" && !isExternal(key) && isActive(relativePath, `/${key}/`, true)) || "root";
}
function resolveSiteDataByRoute(siteData2, relativePath) {
  var _a, _b, _c, _d, _e, _f, _g;
  const localeIndex = getLocaleForPath(siteData2, relativePath);
  return Object.assign({}, siteData2, {
    localeIndex,
    lang: ((_a = siteData2.locales[localeIndex]) == null ? void 0 : _a.lang) ?? siteData2.lang,
    dir: ((_b = siteData2.locales[localeIndex]) == null ? void 0 : _b.dir) ?? siteData2.dir,
    title: ((_c = siteData2.locales[localeIndex]) == null ? void 0 : _c.title) ?? siteData2.title,
    titleTemplate: ((_d = siteData2.locales[localeIndex]) == null ? void 0 : _d.titleTemplate) ?? siteData2.titleTemplate,
    description: ((_e = siteData2.locales[localeIndex]) == null ? void 0 : _e.description) ?? siteData2.description,
    head: mergeHead(siteData2.head, ((_f = siteData2.locales[localeIndex]) == null ? void 0 : _f.head) ?? []),
    themeConfig: {
      ...siteData2.themeConfig,
      ...(_g = siteData2.locales[localeIndex]) == null ? void 0 : _g.themeConfig
    }
  });
}
function createTitle(siteData2, pageData) {
  const title = pageData.title || siteData2.title;
  const template = pageData.titleTemplate ?? siteData2.titleTemplate;
  if (typeof template === "string" && template.includes(":title")) {
    return template.replace(/:title/g, title);
  }
  const templateString = createTitleTemplate(siteData2.title, template);
  if (title === templateString.slice(3)) {
    return title;
  }
  return `${title}${templateString}`;
}
function createTitleTemplate(siteTitle, template) {
  if (template === false) {
    return "";
  }
  if (template === true || template === void 0) {
    return ` | ${siteTitle}`;
  }
  if (siteTitle === template) {
    return "";
  }
  return ` | ${template}`;
}
function hasTag(head, tag) {
  const [tagType, tagAttrs] = tag;
  if (tagType !== "meta")
    return false;
  const keyAttr = Object.entries(tagAttrs)[0];
  if (keyAttr == null)
    return false;
  return head.some(([type, attrs]) => type === tagType && attrs[keyAttr[0]] === keyAttr[1]);
}
function mergeHead(prev, curr) {
  return [...prev.filter((tagAttrs) => !hasTag(curr, tagAttrs)), ...curr];
}
const INVALID_CHAR_REGEX = /[\u0000-\u001F"#$&*+,:;<=>?[\]^`{|}\u007F]/g;
const DRIVE_LETTER_REGEX = /^[a-z]:/i;
function sanitizeFileName(name) {
  const match = DRIVE_LETTER_REGEX.exec(name);
  const driveLetter = match ? match[0] : "";
  return driveLetter + name.slice(driveLetter.length).replace(INVALID_CHAR_REGEX, "_").replace(/(^|\/)_+(?=[^/]*$)/, "$1");
}
const KNOWN_EXTENSIONS = /* @__PURE__ */ new Set();
function treatAsHtml(filename) {
  var _a;
  if (KNOWN_EXTENSIONS.size === 0) {
    const extraExts = typeof process === "object" && ((_a = process.env) == null ? void 0 : _a.VITE_EXTRA_EXTENSIONS) || (__vite_import_meta_env__ == null ? void 0 : __vite_import_meta_env__.VITE_EXTRA_EXTENSIONS) || "";
    ("3g2,3gp,aac,ai,apng,au,avif,bin,bmp,cer,class,conf,crl,css,csv,dll,doc,eps,epub,exe,gif,gz,ics,ief,jar,jpe,jpeg,jpg,js,json,jsonld,m4a,man,mid,midi,mjs,mov,mp2,mp3,mp4,mpe,mpeg,mpg,mpp,oga,ogg,ogv,ogx,opus,otf,p10,p7c,p7m,p7s,pdf,png,ps,qt,roff,rtf,rtx,ser,svg,t,tif,tiff,tr,ts,tsv,ttf,txt,vtt,wav,weba,webm,webp,woff,woff2,xhtml,xml,yaml,yml,zip" + (extraExts && typeof extraExts === "string" ? "," + extraExts : "")).split(",").forEach((ext2) => KNOWN_EXTENSIONS.add(ext2));
  }
  const ext = filename.split(".").pop();
  return ext == null || !KNOWN_EXTENSIONS.has(ext.toLowerCase());
}
const dataSymbol = Symbol();
const siteDataRef = shallowRef(siteData);
function initData(route) {
  const site = computed(() => resolveSiteDataByRoute(siteDataRef.value, route.data.relativePath));
  const appearance = site.value.appearance;
  const isDark = appearance === "force-dark" ? ref(true) : appearance === "force-auto" ? usePreferredDark() : appearance ? useDark({
    storageKey: APPEARANCE_KEY,
    initialValue: () => appearance === "dark" ? "dark" : "auto",
    ...typeof appearance === "object" ? appearance : {}
  }) : ref(false);
  const hashRef = ref(inBrowser ? location.hash : "");
  if (inBrowser) {
    window.addEventListener("hashchange", () => {
      hashRef.value = location.hash;
    });
  }
  watch(() => route.data, () => {
    hashRef.value = inBrowser ? location.hash : "";
  });
  return {
    site,
    theme: computed(() => site.value.themeConfig),
    page: computed(() => route.data),
    frontmatter: computed(() => route.data.frontmatter),
    params: computed(() => route.data.params),
    lang: computed(() => site.value.lang),
    dir: computed(() => route.data.frontmatter.dir || site.value.dir),
    localeIndex: computed(() => site.value.localeIndex || "root"),
    title: computed(() => createTitle(site.value, route.data)),
    description: computed(() => route.data.description || site.value.description),
    isDark,
    hash: computed(() => hashRef.value)
  };
}
function useData$1() {
  const data = inject(dataSymbol);
  if (!data) {
    throw new Error("vitepress data not properly injected in app");
  }
  return data;
}
function joinPath(base, path) {
  return `${base}${path}`.replace(/\/+/g, "/");
}
function withBase(path) {
  return EXTERNAL_URL_RE.test(path) || !path.startsWith("/") ? path : joinPath(siteDataRef.value.base, path);
}
function pathToFile(path) {
  let pagePath = path.replace(/\.html$/, "");
  pagePath = decodeURIComponent(pagePath);
  pagePath = pagePath.replace(/\/$/, "/index");
  {
    if (inBrowser) {
      const base = "/";
      pagePath = sanitizeFileName(pagePath.slice(base.length).replace(/\//g, "_") || "index") + ".md";
      let pageHash = __VP_HASH_MAP__[pagePath.toLowerCase()];
      if (!pageHash) {
        pagePath = pagePath.endsWith("_index.md") ? pagePath.slice(0, -9) + ".md" : pagePath.slice(0, -3) + "_index.md";
        pageHash = __VP_HASH_MAP__[pagePath.toLowerCase()];
      }
      if (!pageHash)
        return null;
      pagePath = `${base}${"assets"}/${pagePath}.${pageHash}.js`;
    } else {
      pagePath = `./${sanitizeFileName(pagePath.slice(1).replace(/\//g, "_"))}.md.js`;
    }
  }
  return pagePath;
}
let contentUpdatedCallbacks = [];
function onContentUpdated(fn) {
  contentUpdatedCallbacks.push(fn);
  onUnmounted(() => {
    contentUpdatedCallbacks = contentUpdatedCallbacks.filter((f) => f !== fn);
  });
}
function getScrollOffset() {
  let scrollOffset = siteDataRef.value.scrollOffset;
  let offset = 0;
  let padding = 24;
  if (typeof scrollOffset === "object" && "padding" in scrollOffset) {
    padding = scrollOffset.padding;
    scrollOffset = scrollOffset.selector;
  }
  if (typeof scrollOffset === "number") {
    offset = scrollOffset;
  } else if (typeof scrollOffset === "string") {
    offset = tryOffsetSelector(scrollOffset, padding);
  } else if (Array.isArray(scrollOffset)) {
    for (const selector of scrollOffset) {
      const res = tryOffsetSelector(selector, padding);
      if (res) {
        offset = res;
        break;
      }
    }
  }
  return offset;
}
function tryOffsetSelector(selector, padding) {
  const el = document.querySelector(selector);
  if (!el)
    return 0;
  const bot = el.getBoundingClientRect().bottom;
  if (bot < 0)
    return 0;
  return bot + padding;
}
const RouterSymbol = Symbol();
const fakeHost = "http://a.com";
const getDefaultRoute = () => ({
  path: "/",
  component: null,
  data: notFoundPageData
});
function createRouter(loadPageModule, fallbackComponent) {
  const route = reactive(getDefaultRoute());
  const router = {
    route,
    go
  };
  async function go(href = inBrowser ? location.href : "/") {
    var _a, _b;
    href = normalizeHref(href);
    if (await ((_a = router.onBeforeRouteChange) == null ? void 0 : _a.call(router, href)) === false)
      return;
    if (inBrowser && href !== normalizeHref(location.href)) {
      history.replaceState({ scrollPosition: window.scrollY }, "");
      history.pushState({}, "", href);
    }
    await loadPage(href);
    await ((_b = router.onAfterRouteChange ?? router.onAfterRouteChanged) == null ? void 0 : _b(href));
  }
  let latestPendingPath = null;
  async function loadPage(href, scrollPosition = 0, isRetry = false) {
    var _a, _b;
    if (await ((_a = router.onBeforePageLoad) == null ? void 0 : _a.call(router, href)) === false)
      return;
    const targetLoc = new URL(href, fakeHost);
    const pendingPath = latestPendingPath = targetLoc.pathname;
    try {
      let page = await loadPageModule(pendingPath);
      if (!page) {
        throw new Error(`Page not found: ${pendingPath}`);
      }
      if (latestPendingPath === pendingPath) {
        latestPendingPath = null;
        const { default: comp, __pageData } = page;
        if (!comp) {
          throw new Error(`Invalid route component: ${comp}`);
        }
        await ((_b = router.onAfterPageLoad) == null ? void 0 : _b.call(router, href));
        route.path = inBrowser ? pendingPath : withBase(pendingPath);
        route.component = markRaw(comp);
        route.data = true ? markRaw(__pageData) : readonly(__pageData);
        if (inBrowser) {
          nextTick(() => {
            let actualPathname = siteDataRef.value.base + __pageData.relativePath.replace(/(?:(^|\/)index)?\.md$/, "$1");
            if (!siteDataRef.value.cleanUrls && !actualPathname.endsWith("/")) {
              actualPathname += ".html";
            }
            if (actualPathname !== targetLoc.pathname) {
              targetLoc.pathname = actualPathname;
              href = actualPathname + targetLoc.search + targetLoc.hash;
              history.replaceState({}, "", href);
            }
            if (targetLoc.hash && !scrollPosition) {
              let target = null;
              try {
                target = document.getElementById(decodeURIComponent(targetLoc.hash).slice(1));
              } catch (e) {
                console.warn(e);
              }
              if (target) {
                scrollTo(target, targetLoc.hash);
                return;
              }
            }
            window.scrollTo(0, scrollPosition);
          });
        }
      }
    } catch (err) {
      if (!/fetch|Page not found/.test(err.message) && !/^\/404(\.html|\/)?$/.test(href)) {
        console.error(err);
      }
      if (!isRetry) {
        try {
          const res = await fetch(siteDataRef.value.base + "hashmap.json");
          window.__VP_HASH_MAP__ = await res.json();
          await loadPage(href, scrollPosition, true);
          return;
        } catch (e) {
        }
      }
      if (latestPendingPath === pendingPath) {
        latestPendingPath = null;
        route.path = inBrowser ? pendingPath : withBase(pendingPath);
        route.component = fallbackComponent ? markRaw(fallbackComponent) : null;
        const relativePath = inBrowser ? pendingPath.replace(/(^|\/)$/, "$1index").replace(/(\.html)?$/, ".md").replace(/^\//, "") : "404.md";
        route.data = { ...notFoundPageData, relativePath };
      }
    }
  }
  if (inBrowser) {
    if (history.state === null) {
      history.replaceState({}, "");
    }
    window.addEventListener("click", (e) => {
      if (e.defaultPrevented || !(e.target instanceof Element) || e.target.closest("button") || // temporary fix for docsearch action buttons
      e.button !== 0 || e.ctrlKey || e.shiftKey || e.altKey || e.metaKey)
        return;
      const link2 = e.target.closest("a");
      if (!link2 || link2.closest(".vp-raw") || link2.hasAttribute("download") || link2.hasAttribute("target"))
        return;
      const linkHref = link2.getAttribute("href") ?? (link2 instanceof SVGAElement ? link2.getAttribute("xlink:href") : null);
      if (linkHref == null)
        return;
      const { href, origin, pathname, hash, search } = new URL(linkHref, link2.baseURI);
      const currentUrl = new URL(location.href);
      if (origin === currentUrl.origin && treatAsHtml(pathname)) {
        e.preventDefault();
        if (pathname === currentUrl.pathname && search === currentUrl.search) {
          if (hash !== currentUrl.hash) {
            history.pushState({}, "", href);
            window.dispatchEvent(new HashChangeEvent("hashchange", {
              oldURL: currentUrl.href,
              newURL: href
            }));
          }
          if (hash) {
            scrollTo(link2, hash, link2.classList.contains("header-anchor"));
          } else {
            window.scrollTo(0, 0);
          }
        } else {
          go(href);
        }
      }
    }, { capture: true });
    window.addEventListener("popstate", async (e) => {
      var _a;
      if (e.state === null)
        return;
      const href = normalizeHref(location.href);
      await loadPage(href, e.state && e.state.scrollPosition || 0);
      await ((_a = router.onAfterRouteChange ?? router.onAfterRouteChanged) == null ? void 0 : _a(href));
    });
    window.addEventListener("hashchange", (e) => {
      e.preventDefault();
    });
  }
  return router;
}
function useRouter() {
  const router = inject(RouterSymbol);
  if (!router) {
    throw new Error("useRouter() is called without provider.");
  }
  return router;
}
function useRoute() {
  return useRouter().route;
}
function scrollTo(el, hash, smooth = false) {
  let target = null;
  try {
    target = el.classList.contains("header-anchor") ? el : document.getElementById(decodeURIComponent(hash).slice(1));
  } catch (e) {
    console.warn(e);
  }
  if (target) {
    let scrollToTarget = function() {
      if (!smooth || Math.abs(targetTop - window.scrollY) > window.innerHeight)
        window.scrollTo(0, targetTop);
      else
        window.scrollTo({ left: 0, top: targetTop, behavior: "smooth" });
    };
    const targetPadding = parseInt(window.getComputedStyle(target).paddingTop, 10);
    const targetTop = window.scrollY + target.getBoundingClientRect().top - getScrollOffset() + targetPadding;
    requestAnimationFrame(scrollToTarget);
  }
}
function normalizeHref(href) {
  const url = new URL(href, fakeHost);
  url.pathname = url.pathname.replace(/(^|\/)index(\.html)?$/, "$1");
  if (siteDataRef.value.cleanUrls)
    url.pathname = url.pathname.replace(/\.html$/, "");
  else if (!url.pathname.endsWith("/") && !url.pathname.endsWith(".html"))
    url.pathname += ".html";
  return url.pathname + url.search + url.hash;
}
const runCbs = () => contentUpdatedCallbacks.forEach((fn) => fn());
const Content = defineComponent({
  name: "VitePressContent",
  props: {
    as: { type: [Object, String], default: "div" }
  },
  setup(props) {
    const route = useRoute();
    const { frontmatter, site } = useData$1();
    watch(frontmatter, runCbs, { deep: true, flush: "post" });
    return () => h(props.as, site.value.contentProps ?? { style: { position: "relative" } }, [
      route.component ? h(route.component, {
        onVnodeMounted: runCbs,
        onVnodeUpdated: runCbs,
        onVnodeUnmounted: runCbs
      }) : "404 Page Not Found"
    ]);
  }
});
const useData = useData$1;
function throttleAndDebounce(fn, delay) {
  let timeoutId;
  let called = false;
  return () => {
    if (timeoutId)
      clearTimeout(timeoutId);
    if (!called) {
      fn();
      (called = true) && setTimeout(() => called = false, delay);
    } else
      timeoutId = setTimeout(fn, delay);
  };
}
function ensureStartingSlash(path) {
  return path.startsWith("/") ? path : `/${path}`;
}
function normalizeLink$1(url) {
  const { pathname, search, hash, protocol } = new URL(url, "http://a.com");
  if (isExternal(url) || url.startsWith("#") || !protocol.startsWith("http") || !treatAsHtml(pathname))
    return url;
  const { site } = useData();
  const normalizedPath = pathname.endsWith("/") || pathname.endsWith(".html") ? url : url.replace(/(?:(^\.+)\/)?.*$/, `$1${pathname.replace(/(\.md)?$/, site.value.cleanUrls ? "" : ".html")}${search}${hash}`);
  return withBase(normalizedPath);
}
function useLangs({ correspondingLink = false } = {}) {
  const { site, localeIndex, page, theme: theme2, hash } = useData();
  const currentLang = computed(() => {
    var _a, _b;
    return {
      label: (_a = site.value.locales[localeIndex.value]) == null ? void 0 : _a.label,
      link: ((_b = site.value.locales[localeIndex.value]) == null ? void 0 : _b.link) || (localeIndex.value === "root" ? "/" : `/${localeIndex.value}/`)
    };
  });
  const localeLinks = computed(() => Object.entries(site.value.locales).flatMap(([key, value]) => currentLang.value.label === value.label ? [] : {
    text: value.label,
    link: normalizeLink(value.link || (key === "root" ? "/" : `/${key}/`), theme2.value.i18nRouting !== false && correspondingLink, page.value.relativePath.slice(currentLang.value.link.length - 1), !site.value.cleanUrls) + hash.value
  }));
  return { localeLinks, currentLang };
}
function normalizeLink(link2, addPath, path, addExt) {
  return addPath ? link2.replace(/\/$/, "") + ensureStartingSlash(path.replace(/(^|\/)index\.md$/, "$1").replace(/\.md$/, addExt ? ".html" : "")) : link2;
}
function getSidebar(_sidebar, path) {
  if (Array.isArray(_sidebar))
    return addBase(_sidebar);
  if (_sidebar == null)
    return [];
  path = ensureStartingSlash(path);
  const dir = Object.keys(_sidebar).sort((a, b) => {
    return b.split("/").length - a.split("/").length;
  }).find((dir2) => {
    return path.startsWith(ensureStartingSlash(dir2));
  });
  const sidebar = dir ? _sidebar[dir] : [];
  return Array.isArray(sidebar) ? addBase(sidebar) : addBase(sidebar.items, sidebar.base);
}
function getSidebarGroups(sidebar) {
  const groups = [];
  let lastGroupIndex = 0;
  for (const index in sidebar) {
    const item = sidebar[index];
    if (item.items) {
      lastGroupIndex = groups.push(item);
      continue;
    }
    if (!groups[lastGroupIndex]) {
      groups.push({ items: [] });
    }
    groups[lastGroupIndex].items.push(item);
  }
  return groups;
}
function getFlatSideBarLinks(sidebar) {
  const links = [];
  function recursivelyExtractLinks(items) {
    for (const item of items) {
      if (item.text && item.link) {
        links.push({
          text: item.text,
          link: item.link,
          docFooterText: item.docFooterText
        });
      }
      if (item.items) {
        recursivelyExtractLinks(item.items);
      }
    }
  }
  recursivelyExtractLinks(sidebar);
  return links;
}
function hasActiveLink(path, items) {
  if (Array.isArray(items)) {
    return items.some((item) => hasActiveLink(path, item));
  }
  return isActive(path, items.link) ? true : items.items ? hasActiveLink(path, items.items) : false;
}
function addBase(items, _base) {
  return [...items].map((_item) => {
    const item = { ..._item };
    const base = item.base || _base;
    if (base && item.link)
      item.link = base + item.link;
    if (item.items)
      item.items = addBase(item.items, base);
    return item;
  });
}
function useSidebar() {
  const { frontmatter, page, theme: theme2 } = useData();
  const is960 = useMediaQuery("(min-width: 960px)");
  const isOpen = ref(false);
  const _sidebar = computed(() => {
    const sidebarConfig = theme2.value.sidebar;
    const relativePath = page.value.relativePath;
    return sidebarConfig ? getSidebar(sidebarConfig, relativePath) : [];
  });
  const sidebar = ref(_sidebar.value);
  watch(_sidebar, (next, prev) => {
    if (JSON.stringify(next) !== JSON.stringify(prev))
      sidebar.value = _sidebar.value;
  });
  const hasSidebar = computed(() => {
    return frontmatter.value.sidebar !== false && sidebar.value.length > 0 && frontmatter.value.layout !== "home";
  });
  const leftAside = computed(() => {
    if (hasAside)
      return frontmatter.value.aside == null ? theme2.value.aside === "left" : frontmatter.value.aside === "left";
    return false;
  });
  const hasAside = computed(() => {
    if (frontmatter.value.layout === "home")
      return false;
    if (frontmatter.value.aside != null)
      return !!frontmatter.value.aside;
    return theme2.value.aside !== false;
  });
  const isSidebarEnabled = computed(() => hasSidebar.value && is960.value);
  const sidebarGroups = computed(() => {
    return hasSidebar.value ? getSidebarGroups(sidebar.value) : [];
  });
  function open() {
    isOpen.value = true;
  }
  function close() {
    isOpen.value = false;
  }
  function toggle() {
    isOpen.value ? close() : open();
  }
  return {
    isOpen,
    sidebar,
    sidebarGroups,
    hasSidebar,
    hasAside,
    leftAside,
    isSidebarEnabled,
    open,
    close,
    toggle
  };
}
function useCloseSidebarOnEscape(isOpen, close) {
  let triggerElement;
  watchEffect(() => {
    triggerElement = isOpen.value ? document.activeElement : void 0;
  });
  onMounted(() => {
    window.addEventListener("keyup", onEscape);
  });
  onUnmounted(() => {
    window.removeEventListener("keyup", onEscape);
  });
  function onEscape(e) {
    if (e.key === "Escape" && isOpen.value) {
      close();
      triggerElement == null ? void 0 : triggerElement.focus();
    }
  }
}
function useSidebarControl(item) {
  const { page, hash } = useData();
  const collapsed = ref(false);
  const collapsible = computed(() => {
    return item.value.collapsed != null;
  });
  const isLink = computed(() => {
    return !!item.value.link;
  });
  const isActiveLink = ref(false);
  const updateIsActiveLink = () => {
    isActiveLink.value = isActive(page.value.relativePath, item.value.link);
  };
  watch([page, item, hash], updateIsActiveLink);
  onMounted(updateIsActiveLink);
  const hasActiveLink$1 = computed(() => {
    if (isActiveLink.value) {
      return true;
    }
    return item.value.items ? hasActiveLink(page.value.relativePath, item.value.items) : false;
  });
  const hasChildren = computed(() => {
    return !!(item.value.items && item.value.items.length);
  });
  watchEffect(() => {
    collapsed.value = !!(collapsible.value && item.value.collapsed);
  });
  watchPostEffect(() => {
    (isActiveLink.value || hasActiveLink$1.value) && (collapsed.value = false);
  });
  function toggle() {
    if (collapsible.value) {
      collapsed.value = !collapsed.value;
    }
  }
  return {
    collapsed,
    collapsible,
    isLink,
    isActiveLink,
    hasActiveLink: hasActiveLink$1,
    hasChildren,
    toggle
  };
}
function useAside() {
  const { hasSidebar } = useSidebar();
  const is960 = useMediaQuery("(min-width: 960px)");
  const is1280 = useMediaQuery("(min-width: 1280px)");
  const isAsideEnabled = computed(() => {
    if (!is1280.value && !is960.value) {
      return false;
    }
    return hasSidebar.value ? is1280.value : is960.value;
  });
  return {
    isAsideEnabled
  };
}
const ignoreRE = /\b(?:VPBadge|header-anchor|footnote-ref|ignore-header)\b/;
const resolvedHeaders = [];
function resolveTitle(theme2) {
  return typeof theme2.outline === "object" && !Array.isArray(theme2.outline) && theme2.outline.label || theme2.outlineTitle || "On this page";
}
function getHeaders(range) {
  const headers = [
    ...document.querySelectorAll(".VPDoc :where(h1,h2,h3,h4,h5,h6)")
  ].filter((el) => el.id && el.hasChildNodes()).map((el) => {
    const level = Number(el.tagName[1]);
    return {
      element: el,
      title: serializeHeader(el),
      link: "#" + el.id,
      level
    };
  });
  return resolveHeaders(headers, range);
}
function serializeHeader(h2) {
  let ret = "";
  for (const node of h2.childNodes) {
    if (node.nodeType === 1) {
      if (ignoreRE.test(node.className))
        continue;
      ret += node.textContent;
    } else if (node.nodeType === 3) {
      ret += node.textContent;
    }
  }
  return ret.trim();
}
function resolveHeaders(headers, range) {
  if (range === false) {
    return [];
  }
  const levelsRange = (typeof range === "object" && !Array.isArray(range) ? range.level : range) || 2;
  const [high, low] = typeof levelsRange === "number" ? [levelsRange, levelsRange] : levelsRange === "deep" ? [2, 6] : levelsRange;
  return buildTree(headers, high, low);
}
function useActiveAnchor(container, marker) {
  const { isAsideEnabled } = useAside();
  const onScroll = throttleAndDebounce(setActiveLink, 100);
  let prevActiveLink = null;
  onMounted(() => {
    requestAnimationFrame(setActiveLink);
    window.addEventListener("scroll", onScroll);
  });
  onUpdated(() => {
    activateLink(location.hash);
  });
  onUnmounted(() => {
    window.removeEventListener("scroll", onScroll);
  });
  function setActiveLink() {
    if (!isAsideEnabled.value) {
      return;
    }
    const scrollY = window.scrollY;
    const innerHeight = window.innerHeight;
    const offsetHeight = document.body.offsetHeight;
    const isBottom = Math.abs(scrollY + innerHeight - offsetHeight) < 1;
    const headers = resolvedHeaders.map(({ element, link: link2 }) => ({
      link: link2,
      top: getAbsoluteTop(element)
    })).filter(({ top }) => !Number.isNaN(top)).sort((a, b) => a.top - b.top);
    if (!headers.length) {
      activateLink(null);
      return;
    }
    if (scrollY < 1) {
      activateLink(null);
      return;
    }
    if (isBottom) {
      activateLink(headers[headers.length - 1].link);
      return;
    }
    let activeLink = null;
    for (const { link: link2, top } of headers) {
      if (top > scrollY + getScrollOffset() + 4) {
        break;
      }
      activeLink = link2;
    }
    activateLink(activeLink);
  }
  function activateLink(hash) {
    if (prevActiveLink) {
      prevActiveLink.classList.remove("active");
    }
    if (hash == null) {
      prevActiveLink = null;
    } else {
      prevActiveLink = container.value.querySelector(`a[href="${decodeURIComponent(hash)}"]`);
    }
    const activeLink = prevActiveLink;
    if (activeLink) {
      activeLink.classList.add("active");
      marker.value.style.top = activeLink.offsetTop + 39 + "px";
      marker.value.style.opacity = "1";
    } else {
      marker.value.style.top = "33px";
      marker.value.style.opacity = "0";
    }
  }
}
function getAbsoluteTop(element) {
  let offsetTop = 0;
  while (element !== document.body) {
    if (element === null) {
      return NaN;
    }
    offsetTop += element.offsetTop;
    element = element.offsetParent;
  }
  return offsetTop;
}
function buildTree(data, min, max) {
  resolvedHeaders.length = 0;
  const result = [];
  const stack = [];
  data.forEach((item) => {
    const node = { ...item, children: [] };
    let parent = stack[stack.length - 1];
    while (parent && parent.level >= node.level) {
      stack.pop();
      parent = stack[stack.length - 1];
    }
    if (node.element.classList.contains("ignore-header") || parent && "shouldIgnore" in parent) {
      stack.push({ level: node.level, shouldIgnore: true });
      return;
    }
    if (node.level > max || node.level < min)
      return;
    resolvedHeaders.push({ element: node.element, link: node.link });
    if (parent)
      parent.children.push(node);
    else
      result.push(node);
    stack.push(node);
  });
  return result;
}
function useEditLink() {
  const { theme: theme2, page } = useData();
  return computed(() => {
    const { text = "Edit this page", pattern = "" } = theme2.value.editLink || {};
    let url;
    if (typeof pattern === "function") {
      url = pattern(page.value);
    } else {
      url = pattern.replace(/:path/g, page.value.filePath);
    }
    return { url, text };
  });
}
function usePrevNext() {
  const { page, theme: theme2, frontmatter } = useData();
  return computed(() => {
    var _a, _b, _c, _d, _e, _f, _g, _h;
    const sidebar = getSidebar(theme2.value.sidebar, page.value.relativePath);
    const links = getFlatSideBarLinks(sidebar);
    const candidates = uniqBy(links, (link2) => link2.link.replace(/[?#].*$/, ""));
    const index = candidates.findIndex((link2) => {
      return isActive(page.value.relativePath, link2.link);
    });
    const hidePrev = ((_a = theme2.value.docFooter) == null ? void 0 : _a.prev) === false && !frontmatter.value.prev || frontmatter.value.prev === false;
    const hideNext = ((_b = theme2.value.docFooter) == null ? void 0 : _b.next) === false && !frontmatter.value.next || frontmatter.value.next === false;
    return {
      prev: hidePrev ? void 0 : {
        text: (typeof frontmatter.value.prev === "string" ? frontmatter.value.prev : typeof frontmatter.value.prev === "object" ? frontmatter.value.prev.text : void 0) ?? ((_c = candidates[index - 1]) == null ? void 0 : _c.docFooterText) ?? ((_d = candidates[index - 1]) == null ? void 0 : _d.text),
        link: (typeof frontmatter.value.prev === "object" ? frontmatter.value.prev.link : void 0) ?? ((_e = candidates[index - 1]) == null ? void 0 : _e.link)
      },
      next: hideNext ? void 0 : {
        text: (typeof frontmatter.value.next === "string" ? frontmatter.value.next : typeof frontmatter.value.next === "object" ? frontmatter.value.next.text : void 0) ?? ((_f = candidates[index + 1]) == null ? void 0 : _f.docFooterText) ?? ((_g = candidates[index + 1]) == null ? void 0 : _g.text),
        link: (typeof frontmatter.value.next === "object" ? frontmatter.value.next.link : void 0) ?? ((_h = candidates[index + 1]) == null ? void 0 : _h.link)
      }
    };
  });
}
function uniqBy(array, keyFn) {
  const seen = /* @__PURE__ */ new Set();
  return array.filter((item) => {
    const k = keyFn(item);
    return seen.has(k) ? false : seen.add(k);
  });
}
function useLocalNav() {
  const { theme: theme2, frontmatter } = useData();
  const headers = shallowRef([]);
  const hasLocalNav = computed(() => {
    return headers.value.length > 0;
  });
  onContentUpdated(() => {
    headers.value = getHeaders(frontmatter.value.outline ?? theme2.value.outline);
  });
  return {
    headers,
    hasLocalNav
  };
}
function useNav() {
  const isScreenOpen = ref(false);
  function openScreen() {
    isScreenOpen.value = true;
    window.addEventListener("resize", closeScreenOnTabletWindow);
  }
  function closeScreen() {
    isScreenOpen.value = false;
    window.removeEventListener("resize", closeScreenOnTabletWindow);
  }
  function toggleScreen() {
    isScreenOpen.value ? closeScreen() : openScreen();
  }
  function closeScreenOnTabletWindow() {
    window.outerWidth >= 768 && closeScreen();
  }
  const route = useRoute();
  watch(() => route.path, closeScreen);
  return {
    isScreenOpen,
    openScreen,
    closeScreen,
    toggleScreen
  };
}
const focusedElement = ref();
let active = false;
let listeners = 0;
function useFlyout(options) {
  const focus = ref(false);
  if (inBrowser) {
    !active && activateFocusTracking();
    listeners++;
    const unwatch = watch(focusedElement, (el) => {
      var _a, _b, _c;
      if (el === options.el.value || ((_a = options.el.value) == null ? void 0 : _a.contains(el))) {
        focus.value = true;
        (_b = options.onFocus) == null ? void 0 : _b.call(options);
      } else {
        focus.value = false;
        (_c = options.onBlur) == null ? void 0 : _c.call(options);
      }
    });
    onUnmounted(() => {
      unwatch();
      listeners--;
      if (!listeners) {
        deactivateFocusTracking();
      }
    });
  }
  return readonly(focus);
}
function activateFocusTracking() {
  document.addEventListener("focusin", handleFocusIn);
  active = true;
  focusedElement.value = document.activeElement;
}
function deactivateFocusTracking() {
  document.removeEventListener("focusin", handleFocusIn);
}
function handleFocusIn() {
  focusedElement.value = document.activeElement;
}
function createSearchTranslate(defaultTranslations) {
  const { localeIndex, theme: theme2 } = useData();
  function translate(key) {
    var _a, _b, _c;
    const keyPath = key.split(".");
    const themeObject = (_a = theme2.value.search) == null ? void 0 : _a.options;
    const isObject = themeObject && typeof themeObject === "object";
    const locales = isObject && ((_c = (_b = themeObject.locales) == null ? void 0 : _b[localeIndex.value]) == null ? void 0 : _c.translations) || null;
    const translations = isObject && themeObject.translations || null;
    let localeResult = locales;
    let translationResult = translations;
    let defaultResult = defaultTranslations;
    const lastKey = keyPath.pop();
    for (const k of keyPath) {
      let fallbackResult = null;
      const foundInFallback = defaultResult == null ? void 0 : defaultResult[k];
      if (foundInFallback) {
        fallbackResult = defaultResult = foundInFallback;
      }
      const foundInTranslation = translationResult == null ? void 0 : translationResult[k];
      if (foundInTranslation) {
        fallbackResult = translationResult = foundInTranslation;
      }
      const foundInLocale = localeResult == null ? void 0 : localeResult[k];
      if (foundInLocale) {
        fallbackResult = localeResult = foundInLocale;
      }
      if (!foundInFallback) {
        defaultResult = fallbackResult;
      }
      if (!foundInTranslation) {
        translationResult = fallbackResult;
      }
      if (!foundInLocale) {
        localeResult = fallbackResult;
      }
    }
    return (localeResult == null ? void 0 : localeResult[lastKey]) ?? (translationResult == null ? void 0 : translationResult[lastKey]) ?? (defaultResult == null ? void 0 : defaultResult[lastKey]) ?? "";
  }
  return translate;
}
const GridSettings = {
  xmini: [[0, 2]],
  mini: [],
  small: [
    [920, 6],
    [768, 5],
    [640, 4],
    [480, 3],
    [0, 2]
  ],
  medium: [
    [960, 5],
    [832, 4],
    [640, 3],
    [480, 2]
  ],
  big: [
    [832, 3],
    [640, 2]
  ]
};
function useSponsorsGrid({ el, size = "medium" }) {
  const onResize = throttleAndDebounce(manage, 100);
  onMounted(() => {
    manage();
    window.addEventListener("resize", onResize);
  });
  onUnmounted(() => {
    window.removeEventListener("resize", onResize);
  });
  function manage() {
    adjustSlots(el.value, size);
  }
}
function adjustSlots(el, size) {
  const tsize = el.children.length;
  const asize = el.querySelectorAll(".vp-sponsor-grid-item:not(.empty)").length;
  const grid = setGrid(el, size, asize);
  manageSlots(el, grid, tsize, asize);
}
function setGrid(el, size, items) {
  const settings = GridSettings[size];
  const screen = window.innerWidth;
  let grid = 1;
  settings.some(([breakpoint, value]) => {
    if (screen >= breakpoint) {
      grid = items < value ? items : value;
      return true;
    }
  });
  setGridData(el, grid);
  return grid;
}
function setGridData(el, value) {
  el.dataset.vpGrid = String(value);
}
function manageSlots(el, grid, tsize, asize) {
  const diff = tsize - asize;
  const rem = asize % grid;
  const drem = rem === 0 ? rem : grid - rem;
  neutralizeSlots(el, drem - diff);
}
function neutralizeSlots(el, count) {
  if (count === 0) {
    return;
  }
  count > 0 ? addSlots(el, count) : removeSlots(el, count * -1);
}
function addSlots(el, count) {
  for (let i = 0; i < count; i++) {
    const slot = document.createElement("div");
    slot.classList.add("vp-sponsor-grid-item", "empty");
    el.append(slot);
  }
}
function removeSlots(el, count) {
  for (let i = 0; i < count; i++) {
    el.removeChild(el.lastElementChild);
  }
}
const theme = {
  Layout: Layout$1,
  enhanceApp: ({ app }) => {
    app.component("Badge", _sfc_main$j);
  }
};
const _sfc_main$i = /* @__PURE__ */ defineComponent({
  __name: "StickyHeader",
  __ssrInlineRender: true,
  setup(__props) {
    const { frontmatter } = useData$1();
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<header${ssrRenderAttrs(mergeProps({ class: "sticky-header" }, _attrs))} data-v-2475a8f1>`);
      ssrRenderSlot(_ctx.$slots, "default", {}, null, _push, _parent);
      _push(`</header>`);
    };
  }
});
const _sfc_setup$i = _sfc_main$i.setup;
_sfc_main$i.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add(".vitepress/theme/components/StickyHeader.vue");
  return _sfc_setup$i ? _sfc_setup$i(props, ctx) : void 0;
};
const StickyHeader = /* @__PURE__ */ _export_sfc(_sfc_main$i, [["__scopeId", "data-v-2475a8f1"]]);
const _sfc_main$h = /* @__PURE__ */ defineComponent({
  __name: "StickySidebar",
  __ssrInlineRender: true,
  setup(__props) {
    const { frontmatter, page } = useData$1();
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<aside${ssrRenderAttrs(mergeProps({ class: "sticky-sidebar" }, _attrs))} data-v-7c9dec3a>`);
      ssrRenderSlot(_ctx.$slots, "default", {}, null, _push, _parent);
      _push(`</aside>`);
    };
  }
});
const _sfc_setup$h = _sfc_main$h.setup;
_sfc_main$h.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add(".vitepress/theme/components/StickySidebar.vue");
  return _sfc_setup$h ? _sfc_setup$h(props, ctx) : void 0;
};
const StickySidebar = /* @__PURE__ */ _export_sfc(_sfc_main$h, [["__scopeId", "data-v-7c9dec3a"]]);
const _sfc_main$g = /* @__PURE__ */ defineComponent({
  __name: "Toast",
  __ssrInlineRender: true,
  props: {
    message: {},
    type: { default: "info" },
    duration: { default: 3e3 },
    persistent: { type: Boolean, default: false },
    id: {}
  },
  emits: ["close"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const visible = ref(false);
    const timer = ref(null);
    onMounted(() => {
      requestAnimationFrame(() => {
        visible.value = true;
      });
      if (!props.persistent && props.duration > 0) {
        timer.value = window.setTimeout(() => {
          close();
        }, props.duration);
      }
    });
    onUnmounted(() => {
      if (timer.value) {
        clearTimeout(timer.value);
      }
    });
    function close() {
      visible.value = false;
      setTimeout(() => {
        emit("close", props.id || "");
      }, 300);
    }
    const icons = {
      success: "✓",
      error: "✕",
      warning: "⚠",
      info: "ℹ"
    };
    const iconLabels = {
      success: "Success",
      error: "Error",
      warning: "Warning",
      info: "Info"
    };
    return (_ctx, _push, _parent, _attrs) => {
      if (visible.value) {
        _push(`<div${ssrRenderAttrs(mergeProps({
          class: ["toast", `toast-${__props.type}`],
          role: "alert",
          "aria-live": __props.type === "error" ? "assertive" : "polite",
          "aria-label": iconLabels[__props.type]
        }, _attrs))} data-v-58dce886><div class="toast-content" data-v-58dce886><span class="toast-icon"${ssrRenderAttr("aria-hidden", true)} data-v-58dce886>${ssrInterpolate(icons[__props.type])}</span><span class="toast-message" data-v-58dce886>${ssrInterpolate(__props.message)}</span></div>`);
        if (__props.persistent) {
          _push(`<button class="toast-close" aria-label="Close notification" data-v-58dce886><span aria-hidden="true" data-v-58dce886>×</span></button>`);
        } else {
          _push(`<!---->`);
        }
        _push(`</div>`);
      } else {
        _push(`<!---->`);
      }
    };
  }
});
const _sfc_setup$g = _sfc_main$g.setup;
_sfc_main$g.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add(".vitepress/theme/components/Toast.vue");
  return _sfc_setup$g ? _sfc_setup$g(props, ctx) : void 0;
};
const Toast = /* @__PURE__ */ _export_sfc(_sfc_main$g, [["__scopeId", "data-v-58dce886"]]);
const _sfc_main$f = /* @__PURE__ */ defineComponent({
  __name: "ToastContainer",
  __ssrInlineRender: true,
  setup(__props) {
    const toasts = ref([]);
    let toastIdCounter = 0;
    function showToast(message, options = {}) {
      const id = `toast-${++toastIdCounter}`;
      const toast = {
        id,
        message,
        type: options.type || "info",
        duration: options.duration ?? 3e3,
        persistent: options.persistent ?? false
      };
      toasts.value.push(toast);
      return id;
    }
    function removeToast(id) {
      const index = toasts.value.findIndex((t) => t.id === id);
      if (index > -1) {
        toasts.value.splice(index, 1);
      }
    }
    provide("toast", {
      show: showToast,
      success: (message, options) => showToast(message, { ...options, type: "success" }),
      error: (message, options) => showToast(message, { ...options, type: "error" }),
      warning: (message, options) => showToast(message, { ...options, type: "warning" }),
      info: (message, options) => showToast(message, { ...options, type: "info" })
    });
    return (_ctx, _push, _parent, _attrs) => {
      ssrRenderTeleport(_push, (_push2) => {
        _push2(`<div class="toast-container" role="region" aria-label="Notifications" data-v-6426ca33><!--[-->`);
        ssrRenderList(toasts.value, (toast) => {
          _push2(ssrRenderComponent(Toast, {
            key: toast.id,
            id: toast.id,
            message: toast.message,
            type: toast.type,
            duration: toast.duration,
            persistent: toast.persistent,
            onClose: removeToast
          }, null, _parent));
        });
        _push2(`<!--]--></div>`);
      }, "body", false, _parent);
    };
  }
});
const _sfc_setup$f = _sfc_main$f.setup;
_sfc_main$f.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add(".vitepress/theme/components/ToastContainer.vue");
  return _sfc_setup$f ? _sfc_setup$f(props, ctx) : void 0;
};
const ToastContainer = /* @__PURE__ */ _export_sfc(_sfc_main$f, [["__scopeId", "data-v-6426ca33"]]);
const scrollThreshold = 400;
const _sfc_main$e = /* @__PURE__ */ defineComponent({
  __name: "BackToTop",
  __ssrInlineRender: true,
  setup(__props) {
    const visible = ref(false);
    function handleScroll() {
      visible.value = window.scrollY > scrollThreshold;
    }
    onMounted(() => {
      window.addEventListener("scroll", handleScroll, { passive: true });
      handleScroll();
    });
    onUnmounted(() => {
      window.removeEventListener("scroll", handleScroll);
    });
    return (_ctx, _push, _parent, _attrs) => {
      if (visible.value) {
        _push(`<button${ssrRenderAttrs(mergeProps({
          class: "back-to-top",
          "aria-label": "Back to top",
          title: "Back to top"
        }, _attrs))} data-v-6db41d20><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" data-v-6db41d20><path d="M18 15l-6-6-6 6" data-v-6db41d20></path></svg></button>`);
      } else {
        _push(`<!---->`);
      }
    };
  }
});
const _sfc_setup$e = _sfc_main$e.setup;
_sfc_main$e.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add(".vitepress/theme/components/BackToTop.vue");
  return _sfc_setup$e ? _sfc_setup$e(props, ctx) : void 0;
};
const BackToTop = /* @__PURE__ */ _export_sfc(_sfc_main$e, [["__scopeId", "data-v-6db41d20"]]);
const _sfc_main$d = /* @__PURE__ */ defineComponent({
  __name: "Layout",
  __ssrInlineRender: true,
  setup(__props) {
    const { Layout: Layout2 } = theme;
    const { frontmatter, page } = useData$1();
    return (_ctx, _push, _parent, _attrs) => {
      _push(ssrRenderComponent(unref(Layout2), _attrs, {
        "nav-bar-content-before": withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(ssrRenderComponent(StickyHeader, null, {
              default: withCtx((_2, _push3, _parent3, _scopeId2) => {
                if (_push3) {
                  ssrRenderSlot(_ctx.$slots, "nav-bar-content-before", {}, null, _push3, _parent3, _scopeId2);
                } else {
                  return [
                    renderSlot(_ctx.$slots, "nav-bar-content-before", {}, void 0, true)
                  ];
                }
              }),
              _: 3
            }, _parent2, _scopeId));
          } else {
            return [
              createVNode(StickyHeader, null, {
                default: withCtx(() => [
                  renderSlot(_ctx.$slots, "nav-bar-content-before", {}, void 0, true)
                ]),
                _: 3
              })
            ];
          }
        }),
        "sidebar-nav-before": withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(ssrRenderComponent(StickySidebar, null, {
              default: withCtx((_2, _push3, _parent3, _scopeId2) => {
                if (_push3) {
                  ssrRenderSlot(_ctx.$slots, "sidebar-nav-before", {}, null, _push3, _parent3, _scopeId2);
                } else {
                  return [
                    renderSlot(_ctx.$slots, "sidebar-nav-before", {}, void 0, true)
                  ];
                }
              }),
              _: 3
            }, _parent2, _scopeId));
          } else {
            return [
              createVNode(StickySidebar, null, {
                default: withCtx(() => [
                  renderSlot(_ctx.$slots, "sidebar-nav-before", {}, void 0, true)
                ]),
                _: 3
              })
            ];
          }
        }),
        "sidebar-nav-after": withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(ssrRenderComponent(StickySidebar, null, {
              default: withCtx((_2, _push3, _parent3, _scopeId2) => {
                if (_push3) {
                  ssrRenderSlot(_ctx.$slots, "sidebar-nav-after", {}, null, _push3, _parent3, _scopeId2);
                } else {
                  return [
                    renderSlot(_ctx.$slots, "sidebar-nav-after", {}, void 0, true)
                  ];
                }
              }),
              _: 3
            }, _parent2, _scopeId));
          } else {
            return [
              createVNode(StickySidebar, null, {
                default: withCtx(() => [
                  renderSlot(_ctx.$slots, "sidebar-nav-after", {}, void 0, true)
                ]),
                _: 3
              })
            ];
          }
        }),
        "page-bottom": withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            ssrRenderSlot(_ctx.$slots, "page-bottom", {}, null, _push2, _parent2, _scopeId);
          } else {
            return [
              renderSlot(_ctx.$slots, "page-bottom", {}, void 0, true)
            ];
          }
        }),
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(ssrRenderComponent(ToastContainer, null, null, _parent2, _scopeId));
            _push2(ssrRenderComponent(BackToTop, null, null, _parent2, _scopeId));
          } else {
            return [
              createVNode(ToastContainer),
              createVNode(BackToTop)
            ];
          }
        }),
        _: 3
      }, _parent));
    };
  }
});
const _sfc_setup$d = _sfc_main$d.setup;
_sfc_main$d.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add(".vitepress/theme/Layout.vue");
  return _sfc_setup$d ? _sfc_setup$d(props, ctx) : void 0;
};
const Layout = /* @__PURE__ */ _export_sfc(_sfc_main$d, [["__scopeId", "data-v-e19a51a9"]]);
const _sfc_main$c = /* @__PURE__ */ defineComponent({
  __name: "Callout",
  __ssrInlineRender: true,
  props: {
    type: { default: "note" },
    title: {},
    collapsible: { type: Boolean, default: false }
  },
  setup(__props) {
    const props = __props;
    const collapsed = ref(false);
    const icons = {
      tip: "💡",
      warning: "⚠️",
      danger: "❌",
      note: "📝",
      info: "ℹ️",
      success: "✅",
      question: "❓",
      example: "📚"
    };
    const labels = {
      tip: "Tip",
      warning: "Warning",
      danger: "Danger",
      note: "Note",
      info: "Info",
      success: "Success",
      question: "Question",
      example: "Example"
    };
    const displayTitle = props.title || labels[props.type];
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<div${ssrRenderAttrs(mergeProps({
        class: ["callout", `callout-${__props.type}`, { collapsible: __props.collapsible }],
        role: "alert",
        "aria-live": __props.type === "danger" ? "assertive" : "polite"
      }, _attrs))} data-v-0fcf3fb4>`);
      if (__props.collapsible) {
        _push(`<button class="callout-toggle"${ssrRenderAttr("aria-expanded", !collapsed.value)} aria-controls="callout-content" data-v-0fcf3fb4><span class="callout-icon" aria-hidden="true" data-v-0fcf3fb4>${ssrInterpolate(icons[__props.type])}</span><span class="callout-title" data-v-0fcf3fb4>${ssrInterpolate(unref(displayTitle))}</span><span class="${ssrRenderClass([{ collapsed: collapsed.value }, "callout-arrow"])}" aria-hidden="true" data-v-0fcf3fb4>▼</span></button>`);
      } else {
        _push(`<div class="callout-header" data-v-0fcf3fb4><span class="callout-icon" aria-hidden="true" data-v-0fcf3fb4>${ssrInterpolate(icons[__props.type])}</span><span class="callout-title" data-v-0fcf3fb4>${ssrInterpolate(unref(displayTitle))}</span></div>`);
      }
      _push(`<div id="callout-content" class="callout-content" style="${ssrRenderStyle(!collapsed.value ? null : { display: "none" })}" data-v-0fcf3fb4>`);
      ssrRenderSlot(_ctx.$slots, "default", {}, null, _push, _parent);
      _push(`</div></div>`);
    };
  }
});
const _sfc_setup$c = _sfc_main$c.setup;
_sfc_main$c.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add(".vitepress/theme/components/Callout.vue");
  return _sfc_setup$c ? _sfc_setup$c(props, ctx) : void 0;
};
const Callout = /* @__PURE__ */ _export_sfc(_sfc_main$c, [["__scopeId", "data-v-0fcf3fb4"]]);
const _sfc_main$b = /* @__PURE__ */ defineComponent({
  __name: "LoadingSpinner",
  __ssrInlineRender: true,
  props: {
    size: { default: "md" },
    variant: { default: "spinner" }
  },
  setup(__props) {
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<div${ssrRenderAttrs(mergeProps({
        class: ["loading-spinner", `size-${__props.size}`, `variant-${__props.variant}`],
        role: "status",
        "aria-label": "Loading"
      }, _attrs))} data-v-64c0c962><span class="sr-only" data-v-64c0c962>Loading...</span>`);
      if (__props.variant === "spinner") {
        _push(`<div class="spinner-circle" data-v-64c0c962></div>`);
      } else if (__props.variant === "dots") {
        _push(`<div class="spinner-dots" data-v-64c0c962><span data-v-64c0c962></span><span data-v-64c0c962></span><span data-v-64c0c962></span></div>`);
      } else if (__props.variant === "pulse") {
        _push(`<div class="spinner-pulse" data-v-64c0c962></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</div>`);
    };
  }
});
const _sfc_setup$b = _sfc_main$b.setup;
_sfc_main$b.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add(".vitepress/theme/components/LoadingSpinner.vue");
  return _sfc_setup$b ? _sfc_setup$b(props, ctx) : void 0;
};
const LoadingSpinner = /* @__PURE__ */ _export_sfc(_sfc_main$b, [["__scopeId", "data-v-64c0c962"]]);
const _sfc_main$a = /* @__PURE__ */ defineComponent({
  __name: "DemoGif",
  __ssrInlineRender: true,
  props: {
    src: {
      type: String,
      required: true
    },
    alt: {
      type: String,
      default: "Demo"
    },
    caption: {
      type: String,
      default: ""
    },
    lazy: {
      type: Boolean,
      default: true
    },
    expandable: {
      type: Boolean,
      default: true
    }
  },
  setup(__props) {
    const props = __props;
    const fullSrc = ref("");
    const loading = ref(true);
    const error = ref(false);
    const expanded = ref(false);
    const imageLoaded = ref(false);
    onMounted(() => {
      fullSrc.value = `/assets/demos/${props.src}`;
      if (!props.lazy) {
        preloadImage();
      }
    });
    function preloadImage() {
      const img = new Image();
      img.onload = () => {
        loading.value = false;
        imageLoaded.value = true;
      };
      img.onerror = () => {
        loading.value = false;
        error.value = true;
      };
      img.src = fullSrc.value;
    }
    function handleIntersection(entries) {
      entries.forEach((entry) => {
        if (entry.isIntersecting && props.lazy && loading.value) {
          preloadImage();
        }
      });
    }
    onMounted(() => {
      if (props.lazy && typeof window !== "undefined" && "IntersectionObserver" in window) {
        const observer = new IntersectionObserver(handleIntersection, {
          rootMargin: "50px"
        });
        const container = document.querySelector(`[data-demo-gif="${props.src}"]`);
        if (container) {
          observer.observe(container);
        }
        return () => observer.disconnect();
      }
    });
    onErrorCaptured(() => {
      error.value = true;
      loading.value = false;
      return false;
    });
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<div${ssrRenderAttrs(mergeProps({
        "data-demo-gif": __props.src,
        class: ["demo-gif-container", { expandable: __props.expandable && !error.value, expanded: expanded.value }]
      }, _attrs))} data-v-429082ea><div class="${ssrRenderClass([{ loading: loading.value, error: error.value }, "demo-gif-wrapper"])}" data-v-429082ea>`);
      if (loading.value) {
        _push(`<div class="demo-gif-loading" data-v-429082ea>`);
        _push(ssrRenderComponent(LoadingSpinner, {
          size: "md",
          variant: "spinner"
        }, null, _parent));
        _push(`<span class="loading-text" data-v-429082ea>Loading demo...</span></div>`);
      } else if (error.value) {
        _push(`<div class="demo-gif-error" data-v-429082ea><span class="error-icon" data-v-429082ea>⚠️</span><span class="error-text" data-v-429082ea>Failed to load demo</span><button class="retry-button" aria-label="Retry loading demo" data-v-429082ea> Retry </button></div>`);
      } else {
        _push(`<!---->`);
      }
      if (imageLoaded.value && !error.value) {
        _push(`<img${ssrRenderAttr("src", fullSrc.value)}${ssrRenderAttr("alt", __props.alt)} class="${ssrRenderClass([{ clickable: __props.expandable }, "demo-gif"])}" loading="lazy" data-v-429082ea>`);
      } else {
        _push(`<!---->`);
      }
      if (__props.expandable && imageLoaded.value && !error.value) {
        _push(`<div class="expand-indicator" aria-hidden="true" data-v-429082ea><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-v-429082ea><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3" data-v-429082ea></path></svg></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</div>`);
      if (__props.caption && !loading.value) {
        _push(`<p class="demo-gif-caption" data-v-429082ea>${ssrInterpolate(__props.caption)}</p>`);
      } else {
        _push(`<!---->`);
      }
      if (expanded.value && __props.expandable) {
        _push(`<div class="demo-gif-modal" data-v-429082ea><div class="modal-content" data-v-429082ea><button class="modal-close" aria-label="Close expanded view" data-v-429082ea><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-v-429082ea><line x1="18" y1="6" x2="6" y2="18" data-v-429082ea></line><line x1="6" y1="6" x2="18" y2="18" data-v-429082ea></line></svg></button><img${ssrRenderAttr("src", fullSrc.value)}${ssrRenderAttr("alt", __props.alt)} class="modal-image" data-v-429082ea>`);
        if (__props.caption) {
          _push(`<p class="modal-caption" data-v-429082ea>${ssrInterpolate(__props.caption)}</p>`);
        } else {
          _push(`<!---->`);
        }
        _push(`</div></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</div>`);
    };
  }
});
const _sfc_setup$a = _sfc_main$a.setup;
_sfc_main$a.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add(".vitepress/theme/components/DemoGif.vue");
  return _sfc_setup$a ? _sfc_setup$a(props, ctx) : void 0;
};
const DemoGif = /* @__PURE__ */ _export_sfc(_sfc_main$a, [["__scopeId", "data-v-429082ea"]]);
const _sfc_main$9 = /* @__PURE__ */ defineComponent({
  __name: "CodePlayground",
  __ssrInlineRender: true,
  props: {
    lang: {},
    endpoint: {},
    code: {},
    title: {}
  },
  setup(__props) {
    const props = __props;
    const output = ref("");
    const running = ref(false);
    const error = ref("");
    const showOutput = ref(false);
    const copied = ref(false);
    const outputCollapsed = ref(false);
    const toast = inject("toast", null);
    async function run() {
      running.value = true;
      error.value = "";
      output.value = "";
      showOutput.value = false;
      outputCollapsed.value = false;
      try {
        const timeoutPromise = new Promise(
          (_, reject) => setTimeout(() => reject(new Error("Execution timeout")), 1e4)
        );
        const executionPromise = new Promise((resolve) => {
          setTimeout(() => {
            if (props.lang === "python" || !props.lang) {
              resolve("Execution simulated. Connect to API endpoint for real execution.");
            } else {
              resolve(`Simulated ${props.lang} execution`);
            }
          }, 500);
        });
        const result = await Promise.race([executionPromise, timeoutPromise]);
        output.value = String(result);
        showOutput.value = true;
        if (toast) {
          toast.success("Code executed successfully");
        }
      } catch (e) {
        const errorMessage = e instanceof Error ? e.message : String(e);
        error.value = errorMessage;
        showOutput.value = true;
        if (toast) {
          toast.error(`Execution failed: ${errorMessage}`);
        }
      } finally {
        running.value = false;
      }
    }
    function handleKeydown(event) {
      if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
        event.preventDefault();
        if (!running.value) {
          run();
        }
      }
      if ((event.ctrlKey || event.metaKey) && event.key === "c" && !(event.target instanceof HTMLInputElement)) ;
    }
    onMounted(() => {
      document.addEventListener("keydown", handleKeydown);
    });
    onUnmounted(() => {
      document.removeEventListener("keydown", handleKeydown);
    });
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<div${ssrRenderAttrs(mergeProps({
        class: "code-playground",
        role: "region",
        "aria-label": __props.title || "Code playground"
      }, _attrs))} data-v-e85f2bf6><div class="code-playground-header" data-v-e85f2bf6><div class="header-left" data-v-e85f2bf6>`);
      if (__props.title) {
        _push(`<span class="playground-title" data-v-e85f2bf6>${ssrInterpolate(__props.title)}</span>`);
      } else {
        _push(`<!---->`);
      }
      _push(`<span class="lang-badge"${ssrRenderAttr("aria-label", `Language: ${__props.lang || "python"}`)} data-v-e85f2bf6>${ssrInterpolate(__props.lang || "python")}</span></div><div class="header-right" data-v-e85f2bf6><button class="${ssrRenderClass([{ copied: copied.value }, "action-button copy-button"])}"${ssrRenderAttr("aria-label", copied.value ? "Copied!" : "Copy code")}${ssrRenderAttr("title", copied.value ? "Copied!" : "Copy code (Ctrl+C)")} data-v-e85f2bf6>`);
      if (copied.value) {
        _push(`<span class="icon" data-v-e85f2bf6>✓</span>`);
      } else {
        _push(`<span class="icon" data-v-e85f2bf6>📋</span>`);
      }
      _push(`</button><button${ssrIncludeBooleanAttr(running.value) ? " disabled" : ""} class="action-button run-button"${ssrRenderAttr("aria-label", running.value ? "Running..." : "Run code")}${ssrRenderAttr("title", running.value ? "Running..." : "Run code (Ctrl+Enter)")} data-v-e85f2bf6>`);
      if (running.value) {
        _push(ssrRenderComponent(LoadingSpinner, {
          size: "sm",
          variant: "spinner"
        }, null, _parent));
      } else {
        _push(`<span class="icon" data-v-e85f2bf6>▶</span>`);
      }
      _push(`<span class="button-text" data-v-e85f2bf6>${ssrInterpolate(running.value ? "Running..." : "Run")}</span></button></div></div><div class="code-container" data-v-e85f2bf6><pre data-v-e85f2bf6><code data-v-e85f2bf6>${ssrInterpolate(__props.code)}</code></pre></div>`);
      if (showOutput.value && (output.value || error.value)) {
        _push(`<div class="output-section" data-v-e85f2bf6>`);
        if (output.value || error.value) {
          _push(`<button class="output-toggle"${ssrRenderAttr("aria-expanded", !outputCollapsed.value)} aria-controls="output-content" data-v-e85f2bf6><span class="output-header" data-v-e85f2bf6>${ssrInterpolate(error.value ? "Error" : "Output")}</span><span class="${ssrRenderClass([{ collapsed: outputCollapsed.value }, "toggle-icon"])}" data-v-e85f2bf6>▼</span></button>`);
        } else {
          _push(`<!---->`);
        }
        _push(`<div id="output-content" class="${ssrRenderClass([{ error: error.value }, "output-content"])}" style="${ssrRenderStyle(!outputCollapsed.value ? null : { display: "none" })}" data-v-e85f2bf6>`);
        if (error.value) {
          _push(`<pre class="error-output" data-v-e85f2bf6>${ssrInterpolate(error.value)}</pre>`);
        } else {
          _push(`<pre class="success-output" data-v-e85f2bf6>${ssrInterpolate(output.value)}</pre>`);
        }
        _push(`</div></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</div>`);
    };
  }
});
const _sfc_setup$9 = _sfc_main$9.setup;
_sfc_main$9.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add(".vitepress/theme/components/CodePlayground.vue");
  return _sfc_setup$9 ? _sfc_setup$9(props, ctx) : void 0;
};
const CodePlayground = /* @__PURE__ */ _export_sfc(_sfc_main$9, [["__scopeId", "data-v-e85f2bf6"]]);
const _sfc_main$8 = /* @__PURE__ */ defineComponent({
  __name: "ContentTabs",
  __ssrInlineRender: true,
  props: {
    tabs: {},
    storageKey: {}
  },
  setup(__props) {
    const props = __props;
    const route = useRoute();
    const tabs = ref(props.tabs || []);
    const activeTabId = ref("0");
    const storageKey = computed(
      () => props.storageKey || `content-tabs-${route.path}`
    );
    function loadPersistedTab() {
      if (typeof window === "undefined") return;
      try {
        const saved = localStorage.getItem(storageKey.value);
        if (saved && tabs.value.find((t) => t.id === saved)) {
          activeTabId.value = saved;
        }
      } catch (e) {
      }
    }
    onMounted(() => {
      if (props.tabs && props.tabs.length > 0) {
        tabs.value = props.tabs;
      } else {
        const tabElements = document.querySelectorAll("[data-tab-id]");
        tabElements.forEach((el, index) => {
          const id = el.getAttribute("data-tab-id") || String(index);
          const label = el.getAttribute("data-tab-label") || id;
          if (!tabs.value.find((t) => t.id === id)) {
            tabs.value.push({ id, label });
          }
        });
      }
      if (tabs.value.length > 0 && !tabs.value.find((t) => t.id === activeTabId.value)) {
        activeTabId.value = tabs.value[0].id;
      }
      loadPersistedTab();
    });
    const activeTab = computed(() => {
      return tabs.value.find((t) => t.id === activeTabId.value) || tabs.value[0];
    });
    watch(() => route.path, () => {
      loadPersistedTab();
    });
    return (_ctx, _push, _parent, _attrs) => {
      var _a;
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "content-tabs" }, _attrs))} data-v-43727035><div class="tab-list" role="tablist"${ssrRenderAttr("aria-label", ((_a = activeTab.value) == null ? void 0 : _a.label) || "Content tabs")} data-v-43727035><!--[-->`);
      ssrRenderList(tabs.value, (tab) => {
        _push(`<button${ssrRenderAttr("data-tab-button", tab.id)} class="${ssrRenderClass([{ active: activeTabId.value === tab.id }, "tab-button"])}" role="tab"${ssrRenderAttr("aria-selected", activeTabId.value === tab.id)}${ssrRenderAttr("aria-controls", `tabpanel-${tab.id}`)}${ssrRenderAttr("id", `tab-${tab.id}`)}${ssrRenderAttr("tabindex", activeTabId.value === tab.id ? 0 : -1)} data-v-43727035><span class="tab-label" data-v-43727035>${ssrInterpolate(tab.label)}</span>`);
        if (activeTabId.value === tab.id) {
          _push(`<span class="tab-indicator" aria-hidden="true" data-v-43727035></span>`);
        } else {
          _push(`<!---->`);
        }
        _push(`</button>`);
      });
      _push(`<!--]--></div><!--[-->`);
      ssrRenderList(tabs.value, (tab) => {
        _push(`<div${ssrRenderAttr("id", `tabpanel-${tab.id}`)} class="${ssrRenderClass([{ active: activeTabId.value === tab.id }, "tab-panel"])}" role="tabpanel"${ssrRenderAttr("aria-labelledby", `tab-${tab.id}`)}${ssrIncludeBooleanAttr(activeTabId.value !== tab.id) ? " hidden" : ""} style="${ssrRenderStyle(activeTabId.value === tab.id ? null : { display: "none" })}" data-v-43727035>`);
        ssrRenderSlot(_ctx.$slots, `tab-${tab.id}`, {}, () => {
          ssrRenderSlot(_ctx.$slots, "default", {}, null, _push, _parent);
        }, _push, _parent);
        _push(`</div>`);
      });
      _push(`<!--]--></div>`);
    };
  }
});
const _sfc_setup$8 = _sfc_main$8.setup;
_sfc_main$8.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add(".vitepress/theme/components/ContentTabs.vue");
  return _sfc_setup$8 ? _sfc_setup$8(props, ctx) : void 0;
};
const ContentTabs = /* @__PURE__ */ _export_sfc(_sfc_main$8, [["__scopeId", "data-v-43727035"]]);
const _sfc_main$7 = /* @__PURE__ */ defineComponent({
  __name: "NavTabs",
  __ssrInlineRender: true,
  props: {
    tabs: {}
  },
  setup(__props) {
    const props = __props;
    const { page } = useData$1();
    const activeIndex = computed(() => {
      const currentPath = page.value.relativePath || "";
      return props.tabs.findIndex((tab) => {
        if (tab.link === "/") {
          return currentPath === "index.md" || currentPath === "";
        }
        return currentPath.startsWith(tab.link.replace(/^\//, "").replace(/\/$/, ""));
      });
    });
    function isActive2(tab, index) {
      return activeIndex.value === index;
    }
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "nav-tabs" }, _attrs))} data-v-fd27ee7c><nav class="tabs-nav" role="navigation" aria-label="Section navigation" data-v-fd27ee7c><!--[-->`);
      ssrRenderList(__props.tabs, (tab, index) => {
        _push(`<button class="${ssrRenderClass([{ active: isActive2(tab, index) }, "tab-button"])}"${ssrRenderAttr("aria-current", isActive2(tab, index) ? "page" : void 0)} data-v-fd27ee7c>`);
        if (tab.icon) {
          _push(`<span class="tab-icon" data-v-fd27ee7c>${ssrInterpolate(tab.icon)}</span>`);
        } else {
          _push(`<!---->`);
        }
        _push(`<span class="tab-text" data-v-fd27ee7c>${ssrInterpolate(tab.text)}</span></button>`);
      });
      _push(`<!--]--></nav></div>`);
    };
  }
});
const _sfc_setup$7 = _sfc_main$7.setup;
_sfc_main$7.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add(".vitepress/theme/components/NavTabs.vue");
  return _sfc_setup$7 ? _sfc_setup$7(props, ctx) : void 0;
};
const NavTabs = /* @__PURE__ */ _export_sfc(_sfc_main$7, [["__scopeId", "data-v-fd27ee7c"]]);
const _sfc_main$6 = /* @__PURE__ */ defineComponent({
  __name: "Breadcrumb",
  __ssrInlineRender: true,
  props: {
    items: {},
    separator: {}
  },
  setup(__props) {
    const props = __props;
    const route = useRoute();
    const breadcrumbs = computed(() => {
      if (props.items && props.items.length > 0) {
        return props.items;
      }
      const path = route.path;
      const parts = path.split("/").filter(Boolean);
      const items = [
        { text: "Home", link: "/" }
      ];
      let currentPath = "";
      parts.forEach((part, index) => {
        currentPath += `/${part}`;
        const isLast = index === parts.length - 1;
        items.push({
          text: part.split("-").map((word) => word.charAt(0).toUpperCase() + word.slice(1)).join(" "),
          link: isLast ? void 0 : currentPath
        });
      });
      return items;
    });
    const separator = computed(() => props.separator || "/");
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<nav${ssrRenderAttrs(mergeProps({
        class: "breadcrumb",
        "aria-label": "Breadcrumb"
      }, _attrs))} data-v-af167943><ol class="breadcrumb-list" data-v-af167943><!--[-->`);
      ssrRenderList(breadcrumbs.value, (item, index) => {
        _push(`<li class="breadcrumb-item" data-v-af167943>`);
        ssrRenderVNode(_push, createVNode(resolveDynamicComponent(item.link ? "a" : "span"), {
          href: item.link,
          class: ["breadcrumb-link", { "breadcrumb-current": !item.link }],
          "aria-current": !item.link ? "page" : void 0
        }, {
          default: withCtx((_, _push2, _parent2, _scopeId) => {
            if (_push2) {
              _push2(`${ssrInterpolate(item.text)}`);
            } else {
              return [
                createTextVNode(toDisplayString(item.text), 1)
              ];
            }
          }),
          _: 2
        }), _parent);
        if (index < breadcrumbs.value.length - 1) {
          _push(`<span class="breadcrumb-separator" aria-hidden="true" data-v-af167943>${ssrInterpolate(separator.value)}</span>`);
        } else {
          _push(`<!---->`);
        }
        _push(`</li>`);
      });
      _push(`<!--]--></ol></nav>`);
    };
  }
});
const _sfc_setup$6 = _sfc_main$6.setup;
_sfc_main$6.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add(".vitepress/theme/components/Breadcrumb.vue");
  return _sfc_setup$6 ? _sfc_setup$6(props, ctx) : void 0;
};
const Breadcrumb = /* @__PURE__ */ _export_sfc(_sfc_main$6, [["__scopeId", "data-v-af167943"]]);
const _sfc_main$5 = /* @__PURE__ */ defineComponent({
  __name: "Tooltip",
  __ssrInlineRender: true,
  props: {
    content: {},
    position: { default: "top" },
    delay: { default: 200 }
  },
  setup(__props) {
    const visible = ref(false);
    const timer = ref(null);
    onUnmounted(() => {
      if (timer.value) {
        clearTimeout(timer.value);
      }
    });
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<span${ssrRenderAttrs(mergeProps({ class: "tooltip-wrapper" }, _attrs))} data-v-c934a947>`);
      ssrRenderSlot(_ctx.$slots, "default", {}, null, _push, _parent);
      if (visible.value) {
        _push(`<div class="${ssrRenderClass([`tooltip-${__props.position}`, "tooltip"])}" role="tooltip" data-v-c934a947>${ssrInterpolate(__props.content)}</div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</span>`);
    };
  }
});
const _sfc_setup$5 = _sfc_main$5.setup;
_sfc_main$5.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add(".vitepress/theme/components/Tooltip.vue");
  return _sfc_setup$5 ? _sfc_setup$5(props, ctx) : void 0;
};
const Tooltip = /* @__PURE__ */ _export_sfc(_sfc_main$5, [["__scopeId", "data-v-c934a947"]]);
const _sfc_main$4 = /* @__PURE__ */ defineComponent({
  __name: "CodeAnnotation",
  __ssrInlineRender: true,
  props: {
    code: {},
    language: {},
    annotations: {},
    lineHeight: { default: 24 }
  },
  setup(__props) {
    const props = __props;
    const lineHeightPx = computed(() => `${props.lineHeight}px`);
    return (_ctx, _push, _parent, _attrs) => {
      var _a;
      const _cssVars = { style: {
        ":--v9ff02316": lineHeightPx.value
      } };
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "code-annotation-wrapper" }, _attrs, _cssVars))} data-v-3b4012c3><div class="code-annotation" data-v-3b4012c3><pre class="code-block" data-v-3b4012c3><code data-v-3b4012c3>${ssrInterpolate(__props.code)}</code></pre>`);
      if ((_a = __props.annotations) == null ? void 0 : _a.length) {
        _push(`<div class="annotations" data-v-3b4012c3><!--[-->`);
        ssrRenderList(__props.annotations, (annotation, index) => {
          _push(`<div class="annotation" style="${ssrRenderStyle({ top: `${(annotation.line - 1) * __props.lineHeight}px` })}" data-v-3b4012c3><span class="annotation-line" data-v-3b4012c3>${ssrInterpolate(annotation.line)}</span><span class="annotation-text" data-v-3b4012c3>${ssrInterpolate(annotation.text)}</span></div>`);
        });
        _push(`<!--]--></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</div></div>`);
    };
  }
});
const _sfc_setup$4 = _sfc_main$4.setup;
_sfc_main$4.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add(".vitepress/theme/components/CodeAnnotation.vue");
  return _sfc_setup$4 ? _sfc_setup$4(props, ctx) : void 0;
};
const CodeAnnotation = /* @__PURE__ */ _export_sfc(_sfc_main$4, [["__scopeId", "data-v-3b4012c3"]]);
const _sfc_main$3 = /* @__PURE__ */ defineComponent({
  __name: "OpenAPI",
  __ssrInlineRender: true,
  props: {
    specUrl: {}
  },
  setup(__props) {
    const props = __props;
    const iframeSrc = computed(() => {
      if (!props.specUrl) return "";
      const encoded = encodeURIComponent(props.specUrl);
      return `https://api.scalar.com/request?url=${encoded}`;
    });
    return (_ctx, _push, _parent, _attrs) => {
      if (__props.specUrl) {
        _push(`<div${ssrRenderAttrs(mergeProps({ class: "openapi-wrapper" }, _attrs))} data-v-026a42eb><iframe${ssrRenderAttr("src", iframeSrc.value)} title="OpenAPI Specification" class="openapi-iframe" loading="lazy" data-v-026a42eb></iframe></div>`);
      } else {
        _push(`<!---->`);
      }
    };
  }
});
const _sfc_setup$3 = _sfc_main$3.setup;
_sfc_main$3.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add(".vitepress/theme/components/OpenAPI.vue");
  return _sfc_setup$3 ? _sfc_setup$3(props, ctx) : void 0;
};
const OpenAPI = /* @__PURE__ */ _export_sfc(_sfc_main$3, [["__scopeId", "data-v-026a42eb"]]);
const _sfc_main$2 = /* @__PURE__ */ defineComponent({
  __name: "DocStatusBadge",
  __ssrInlineRender: true,
  props: {
    status: {}
  },
  setup(__props) {
    const props = __props;
    const colorMap = {
      draft: "#888",
      active: "#2a9d8f",
      published: "#264653",
      archived: "#999",
      deprecated: "#e76f51",
      superseded: "#e9c46a"
    };
    const color = colorMap[props.status] ?? "#888";
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<span${ssrRenderAttrs(mergeProps({
        style: { backgroundColor: unref(color), color: "#fff", padding: "2px 8px", borderRadius: "4px", fontSize: "0.8em", fontWeight: 600 }
      }, _attrs))}>${ssrInterpolate(__props.status)}</span>`);
    };
  }
});
const _sfc_setup$2 = _sfc_main$2.setup;
_sfc_main$2.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add(".vitepress/theme/components/DocStatusBadge.vue");
  return _sfc_setup$2 ? _sfc_setup$2(props, ctx) : void 0;
};
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "AuditTimeline",
  __ssrInlineRender: true,
  setup(__props) {
    const entries = ref([]);
    onMounted(async () => {
      try {
        const mod = await import("./audit-log.C_usxXiR.js");
        entries.value = mod.default ?? mod;
      } catch {
        entries.value = [];
      }
    });
    return (_ctx, _push, _parent, _attrs) => {
      const _component_DocStatusBadge = resolveComponent("DocStatusBadge");
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "audit-timeline" }, _attrs))} data-v-416d3da4>`);
      if (entries.value.length === 0) {
        _push(`<div class="empty" data-v-416d3da4>No audit entries yet.</div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`<!--[-->`);
      ssrRenderList(entries.value, (entry) => {
        _push(`<div class="entry" data-v-416d3da4><span class="date" data-v-416d3da4>${ssrInterpolate(entry.date)}</span>`);
        _push(ssrRenderComponent(_component_DocStatusBadge, {
          status: entry.status
        }, null, _parent));
        _push(`<span class="title" data-v-416d3da4>${ssrInterpolate(entry.title)}</span></div>`);
      });
      _push(`<!--]--></div>`);
    };
  }
});
const _sfc_setup$1 = _sfc_main$1.setup;
_sfc_main$1.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add(".vitepress/theme/components/AuditTimeline.vue");
  return _sfc_setup$1 ? _sfc_setup$1(props, ctx) : void 0;
};
const AuditTimeline = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-416d3da4"]]);
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "KBGraph",
  __ssrInlineRender: true,
  setup(__props) {
    const nodes = ref([]);
    onMounted(async () => {
      try {
        const mod = await import("./kb-graph.DD0O49ip.js");
        const data = mod.default ?? mod;
        nodes.value = data.nodes ?? [];
      } catch {
        nodes.value = [];
      }
    });
    return (_ctx, _push, _parent, _attrs) => {
      const _component_DocStatusBadge = resolveComponent("DocStatusBadge");
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "kb-graph" }, _attrs))} data-v-6a48602e>`);
      if (nodes.value.length === 0) {
        _push(`<div class="empty" data-v-6a48602e>No knowledge base entries yet.</div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`<!--[-->`);
      ssrRenderList(nodes.value, (node) => {
        _push(`<div class="node" data-v-6a48602e><span class="title" data-v-6a48602e>${ssrInterpolate(node.title)}</span>`);
        _push(ssrRenderComponent(_component_DocStatusBadge, {
          status: node.status
        }, null, _parent));
        _push(`</div>`);
      });
      _push(`<!--]--></div>`);
    };
  }
});
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add(".vitepress/theme/components/KBGraph.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const KBGraph = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-6a48602e"]]);
const tabsClientScript = `
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.content-tabs-wrapper').forEach(wrapper => {
    const headers = wrapper.querySelectorAll('.tab-header')
    const bodies = wrapper.querySelectorAll('.tab-body')

    headers.forEach(header => {
      header.addEventListener('click', () => {
        const tabId = header.getAttribute('data-tab')

        // Update active state
        headers.forEach(h => h.classList.remove('active'))
        header.classList.add('active')

        // Show/hide bodies
        bodies.forEach(body => {
          if (body.getAttribute('data-tab') === tabId) {
            body.style.display = 'block'
          } else {
            body.style.display = 'none'
          }
        })
      })

      header.addEventListener('keydown', (e) => {
        const currentIndex = Array.from(headers).indexOf(header)

        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
          e.preventDefault()
          const nextIndex = (currentIndex + 1) % headers.length
          headers[nextIndex].click()
          headers[nextIndex].focus()
        } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
          e.preventDefault()
          const prevIndex = (currentIndex - 1 + headers.length) % headers.length
          headers[prevIndex].click()
          headers[prevIndex].focus()
        } else if (e.key === 'Home') {
          e.preventDefault()
          headers[0].click()
          headers[0].focus()
        } else if (e.key === 'End') {
          e.preventDefault()
          headers[headers.length - 1].click()
          headers[headers.length - 1].focus()
        }
      })
    })
  })
})
`;
const RawTheme = {
  extends: theme,
  Layout,
  enhanceApp({ app }) {
    app.component("Callout", Callout);
    app.component("DemoGif", DemoGif);
    app.component("CodePlayground", CodePlayground);
    app.component("ContentTabs", ContentTabs);
    app.component("NavTabs", NavTabs);
    app.component("StickyHeader", StickyHeader);
    app.component("StickySidebar", StickySidebar);
    app.component("ToastContainer", ToastContainer);
    app.component("LoadingSpinner", LoadingSpinner);
    app.component("BackToTop", BackToTop);
    app.component("Breadcrumb", Breadcrumb);
    app.component("Tooltip", Tooltip);
    app.component("CodeAnnotation", CodeAnnotation);
    app.component("OpenAPI", OpenAPI);
    app.component("DocStatusBadge", _sfc_main$2);
    app.component("AuditTimeline", AuditTimeline);
    app.component("KBGraph", KBGraph);
  },
  scripts: [
    {
      src: "data:text/javascript," + encodeURIComponent(tabsClientScript),
      type: "text/javascript"
    }
  ]
};
const ClientOnly = defineComponent({
  setup(_, { slots }) {
    const show = ref(false);
    onMounted(() => {
      show.value = true;
    });
    return () => show.value && slots.default ? slots.default() : null;
  }
});
function useCodeGroups() {
  if (inBrowser) {
    window.addEventListener("click", (e) => {
      var _a;
      const el = e.target;
      if (el.matches(".vp-code-group input")) {
        const group = (_a = el.parentElement) == null ? void 0 : _a.parentElement;
        if (!group)
          return;
        const i = Array.from(group.querySelectorAll("input")).indexOf(el);
        if (i < 0)
          return;
        const blocks = group.querySelector(".blocks");
        if (!blocks)
          return;
        const current = Array.from(blocks.children).find((child) => child.classList.contains("active"));
        if (!current)
          return;
        const next = blocks.children[i];
        if (!next || current === next)
          return;
        current.classList.remove("active");
        next.classList.add("active");
        const label = group == null ? void 0 : group.querySelector(`label[for="${el.id}"]`);
        label == null ? void 0 : label.scrollIntoView({ block: "nearest" });
      }
    });
  }
}
function useCopyCode() {
  if (inBrowser) {
    const timeoutIdMap = /* @__PURE__ */ new WeakMap();
    window.addEventListener("click", (e) => {
      var _a;
      const el = e.target;
      if (el.matches('div[class*="language-"] > button.copy')) {
        const parent = el.parentElement;
        const sibling = (_a = el.nextElementSibling) == null ? void 0 : _a.nextElementSibling;
        if (!parent || !sibling) {
          return;
        }
        const isShell = /language-(shellscript|shell|bash|sh|zsh)/.test(parent.className);
        const ignoredNodes = [".vp-copy-ignore", ".diff.remove"];
        const clone = sibling.cloneNode(true);
        clone.querySelectorAll(ignoredNodes.join(",")).forEach((node) => node.remove());
        let text = clone.textContent || "";
        if (isShell) {
          text = text.replace(/^ *(\$|>) /gm, "").trim();
        }
        copyToClipboard(text).then(() => {
          el.classList.add("copied");
          clearTimeout(timeoutIdMap.get(el));
          const timeoutId = setTimeout(() => {
            el.classList.remove("copied");
            el.blur();
            timeoutIdMap.delete(el);
          }, 2e3);
          timeoutIdMap.set(el, timeoutId);
        });
      }
    });
  }
}
async function copyToClipboard(text) {
  try {
    return navigator.clipboard.writeText(text);
  } catch {
    const element = document.createElement("textarea");
    const previouslyFocusedElement = document.activeElement;
    element.value = text;
    element.setAttribute("readonly", "");
    element.style.contain = "strict";
    element.style.position = "absolute";
    element.style.left = "-9999px";
    element.style.fontSize = "12pt";
    const selection = document.getSelection();
    const originalRange = selection ? selection.rangeCount > 0 && selection.getRangeAt(0) : null;
    document.body.appendChild(element);
    element.select();
    element.selectionStart = 0;
    element.selectionEnd = text.length;
    document.execCommand("copy");
    document.body.removeChild(element);
    if (originalRange) {
      selection.removeAllRanges();
      selection.addRange(originalRange);
    }
    if (previouslyFocusedElement) {
      previouslyFocusedElement.focus();
    }
  }
}
function useUpdateHead(route, siteDataByRouteRef) {
  let isFirstUpdate = true;
  let managedHeadElements = [];
  const updateHeadTags = (newTags) => {
    if (isFirstUpdate) {
      isFirstUpdate = false;
      newTags.forEach((tag) => {
        const headEl = createHeadElement(tag);
        for (const el of document.head.children) {
          if (el.isEqualNode(headEl)) {
            managedHeadElements.push(el);
            return;
          }
        }
      });
      return;
    }
    const newElements = newTags.map(createHeadElement);
    managedHeadElements.forEach((oldEl, oldIndex) => {
      const matchedIndex = newElements.findIndex((newEl) => newEl == null ? void 0 : newEl.isEqualNode(oldEl ?? null));
      if (matchedIndex !== -1) {
        delete newElements[matchedIndex];
      } else {
        oldEl == null ? void 0 : oldEl.remove();
        delete managedHeadElements[oldIndex];
      }
    });
    newElements.forEach((el) => el && document.head.appendChild(el));
    managedHeadElements = [...managedHeadElements, ...newElements].filter(Boolean);
  };
  watchEffect(() => {
    const pageData = route.data;
    const siteData2 = siteDataByRouteRef.value;
    const pageDescription = pageData && pageData.description;
    const frontmatterHead = pageData && pageData.frontmatter.head || [];
    const title = createTitle(siteData2, pageData);
    if (title !== document.title) {
      document.title = title;
    }
    const description = pageDescription || siteData2.description;
    let metaDescriptionElement = document.querySelector(`meta[name=description]`);
    if (metaDescriptionElement) {
      if (metaDescriptionElement.getAttribute("content") !== description) {
        metaDescriptionElement.setAttribute("content", description);
      }
    } else {
      createHeadElement(["meta", { name: "description", content: description }]);
    }
    updateHeadTags(mergeHead(siteData2.head, filterOutHeadDescription(frontmatterHead)));
  });
}
function createHeadElement([tag, attrs, innerHTML]) {
  const el = document.createElement(tag);
  for (const key in attrs) {
    el.setAttribute(key, attrs[key]);
  }
  if (innerHTML) {
    el.innerHTML = innerHTML;
  }
  if (tag === "script" && attrs.async == null) {
    el.async = false;
  }
  return el;
}
function isMetaDescription(headConfig) {
  return headConfig[0] === "meta" && headConfig[1] && headConfig[1].name === "description";
}
function filterOutHeadDescription(head) {
  return head.filter((h2) => !isMetaDescription(h2));
}
const hasFetched = /* @__PURE__ */ new Set();
const createLink = () => document.createElement("link");
const viaDOM = (url) => {
  const link2 = createLink();
  link2.rel = `prefetch`;
  link2.href = url;
  document.head.appendChild(link2);
};
const viaXHR = (url) => {
  const req = new XMLHttpRequest();
  req.open("GET", url, req.withCredentials = true);
  req.send();
};
let link;
const doFetch = inBrowser && (link = createLink()) && link.relList && link.relList.supports && link.relList.supports("prefetch") ? viaDOM : viaXHR;
function usePrefetch() {
  if (!inBrowser) {
    return;
  }
  if (!window.IntersectionObserver) {
    return;
  }
  let conn;
  if ((conn = navigator.connection) && (conn.saveData || /2g/.test(conn.effectiveType))) {
    return;
  }
  const rIC = window.requestIdleCallback || setTimeout;
  let observer = null;
  const observeLinks = () => {
    if (observer) {
      observer.disconnect();
    }
    observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const link2 = entry.target;
          observer.unobserve(link2);
          const { pathname } = link2;
          if (!hasFetched.has(pathname)) {
            hasFetched.add(pathname);
            const pageChunkPath = pathToFile(pathname);
            if (pageChunkPath)
              doFetch(pageChunkPath);
          }
        }
      });
    });
    rIC(() => {
      document.querySelectorAll("#app a").forEach((link2) => {
        const { hostname, pathname } = new URL(link2.href instanceof SVGAnimatedString ? link2.href.animVal : link2.href, link2.baseURI);
        const extMatch = pathname.match(/\.\w+$/);
        if (extMatch && extMatch[0] !== ".html") {
          return;
        }
        if (
          // only prefetch same tab navigation, since a new tab will load
          // the lean js chunk instead.
          link2.target !== "_blank" && // only prefetch inbound links
          hostname === location.hostname
        ) {
          if (pathname !== location.pathname) {
            observer.observe(link2);
          } else {
            hasFetched.add(pathname);
          }
        }
      });
    });
  };
  onMounted(observeLinks);
  const route = useRoute();
  watch(() => route.path, observeLinks);
  onUnmounted(() => {
    observer && observer.disconnect();
  });
}
function resolveThemeExtends(theme2) {
  if (theme2.extends) {
    const base = resolveThemeExtends(theme2.extends);
    return {
      ...base,
      ...theme2,
      async enhanceApp(ctx) {
        if (base.enhanceApp)
          await base.enhanceApp(ctx);
        if (theme2.enhanceApp)
          await theme2.enhanceApp(ctx);
      }
    };
  }
  return theme2;
}
const Theme = resolveThemeExtends(RawTheme);
const VitePressApp = defineComponent({
  name: "VitePressApp",
  setup() {
    const { site, lang, dir } = useData$1();
    onMounted(() => {
      watchEffect(() => {
        document.documentElement.lang = lang.value;
        document.documentElement.dir = dir.value;
      });
    });
    if (site.value.router.prefetchLinks) {
      usePrefetch();
    }
    useCopyCode();
    useCodeGroups();
    if (Theme.setup)
      Theme.setup();
    return () => h(Theme.Layout);
  }
});
async function createApp() {
  globalThis.__VITEPRESS__ = true;
  const router = newRouter();
  const app = newApp();
  app.provide(RouterSymbol, router);
  const data = initData(router.route);
  app.provide(dataSymbol, data);
  app.component("Mermaid", _sfc_main$k);
  app.component("Content", Content);
  app.component("ClientOnly", ClientOnly);
  Object.defineProperties(app.config.globalProperties, {
    $frontmatter: {
      get() {
        return data.frontmatter.value;
      }
    },
    $params: {
      get() {
        return data.page.value.params;
      }
    }
  });
  if (Theme.enhanceApp) {
    await Theme.enhanceApp({
      app,
      router,
      siteData: siteDataRef
    });
  }
  return { app, router, data };
}
function newApp() {
  return createSSRApp(VitePressApp);
}
function newRouter() {
  let isInitialPageLoad = inBrowser;
  return createRouter((path) => {
    let pageFilePath = pathToFile(path);
    let pageModule = null;
    if (pageFilePath) {
      if (isInitialPageLoad) {
        pageFilePath = pageFilePath.replace(/\.js$/, ".lean.js");
      }
      if (false) ;
      else {
        pageModule = import(
          /*@vite-ignore*/
          pageFilePath
        );
      }
    }
    if (inBrowser) {
      isInitialPageLoad = false;
    }
    return pageModule;
  }, Theme.NotFound);
}
if (inBrowser) {
  createApp().then(({ app, router, data }) => {
    router.go().then(() => {
      useUpdateHead(router.route, data.site);
      app.mount("#app");
    });
  });
}
async function render(path) {
  const { app, router } = await createApp();
  await router.go(path);
  const ctx = { content: "", vpSocialIcons: /* @__PURE__ */ new Set() };
  ctx.content = await renderToString(app, ctx);
  return ctx;
}
export {
  EXTERNAL_URL_RE as E,
  useData as a,
  useLangs as b,
  useActiveAnchor as c,
  useEditLink as d,
  usePrevNext as e,
  useRoute as f,
  getHeaders as g,
  useSidebar as h,
  useLocalNav as i,
  isActive as j,
  useFlyout as k,
  createSearchTranslate as l,
  inBrowser as m,
  normalizeLink$1 as n,
  onContentUpdated as o,
  useNav as p,
  useSidebarControl as q,
  resolveTitle as r,
  render,
  useCloseSidebarOnEscape as s,
  useSponsorsGrid as t,
  useData$1 as u,
  withBase as w
};
