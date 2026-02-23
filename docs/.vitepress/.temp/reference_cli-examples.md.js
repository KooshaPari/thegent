import { resolveComponent, useSSRContext } from "vue";
import { ssrRenderAttrs, ssrRenderComponent } from "vue/server-renderer";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"CLI Examples","description":"","frontmatter":{},"headers":[],"relativePath":"reference/cli-examples.md","filePath":"reference/cli-examples.md","lastUpdated":1771678191000}');
const _sfc_main = { name: "reference/cli-examples.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  const _component_CodePlayground = resolveComponent("CodePlayground");
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="cli-examples" tabindex="-1">CLI Examples <a class="header-anchor" href="#cli-examples" aria-label="Permalink to &quot;CLI Examples&quot;">​</a></h1><p>Interactive examples of thegent CLI commands.</p><hr><h2 id="thegent-archive" tabindex="-1"><code>thegent archive</code> <a class="header-anchor" href="#thegent-archive" aria-label="Permalink to &quot;\`thegent archive\`&quot;">​</a></h2><p>Archive old sessions (WP-6005). WP-3006: tiered retention (hot 30d, cold 1yr).</p><details><summary>Full documentation</summary><p>Archive old sessions (WP-6005). WP-3006: tiered retention (hot 30d, cold 1yr).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent archive --days VALUE --domain VALUE --tier VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-audit-verify" tabindex="-1"><code>thegent audit-verify</code> <a class="header-anchor" href="#thegent-audit-verify" aria-label="Permalink to &quot;\`thegent audit-verify\`&quot;">​</a></h2><p>Verify the integrity of the execution run registry.</p><details><summary>Full documentation</summary><p>Verify the integrity of the execution run registry.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent audit-verify --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-benchmark" tabindex="-1"><code>thegent benchmark</code> <a class="header-anchor" href="#thegent-benchmark" aria-label="Permalink to &quot;\`thegent benchmark\`&quot;">​</a></h2><p>Report orchestration performance metrics (WP-6001).</p><details><summary>Full documentation</summary><p>Report orchestration performance metrics (WP-6001).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent benchmark"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-bg" tabindex="-1"><code>thegent bg</code> <a class="header-anchor" href="#thegent-bg" aria-label="Permalink to &quot;\`thegent bg\`&quot;">​</a></h2>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent bg"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-cliproxy-login" tabindex="-1"><code>thegent cliproxy-login</code> <a class="header-anchor" href="#thegent-cliproxy-login" aria-label="Permalink to &quot;\`thegent cliproxy-login\`&quot;">​</a></h2><p>Run login for provider. Unified flow: open URL + prompt for API key. Preflight checks existing credentials.</p><details><summary>Full documentation</summary><p>Run login for provider. Unified flow: open URL + prompt for API key. Preflight checks existing credentials.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent cliproxy-login --provider VALUE --force VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-closure-pack" tabindex="-1"><code>thegent closure-pack</code> <a class="header-anchor" href="#thegent-closure-pack" aria-label="Permalink to &quot;\`thegent closure-pack\`&quot;">​</a></h2><p>Generate a formal closure pack for the current DAG session (WP-6002/6008/FR-024).</p><details><summary>Full documentation</summary><p>Generate a formal closure pack for the current DAG session (WP-6002/6008/FR-024).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent closure-pack --cd VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-cockpit" tabindex="-1"><code>thegent cockpit</code> <a class="header-anchor" href="#thegent-cockpit" aria-label="Permalink to &quot;\`thegent cockpit\`&quot;">​</a></h2><p>Show high-level operator cockpit summary.</p><details><summary>Full documentation</summary><p>Show high-level operator cockpit summary.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent cockpit"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-compliance-plugin-check" tabindex="-1"><code>thegent compliance-plugin-check</code> <a class="header-anchor" href="#thegent-compliance-plugin-check" aria-label="Permalink to &quot;\`thegent compliance-plugin-check\`&quot;">​</a></h2><p>Verify a plugin contract (WP-15003).</p><details><summary>Full documentation</summary><p>Verify a plugin contract (WP-15003).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent compliance-plugin-check --plugin-id VALUE --signature VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-compliance-redact" tabindex="-1"><code>thegent compliance-redact</code> <a class="header-anchor" href="#thegent-compliance-redact" aria-label="Permalink to &quot;\`thegent compliance-redact\`&quot;">​</a></h2><p>Test PII/Secret redaction (WP-15005).</p><details><summary>Full documentation</summary><p>Test PII/Secret redaction (WP-15005).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent compliance-redact --text VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-compliance-report" tabindex="-1"><code>thegent compliance-report</code> <a class="header-anchor" href="#thegent-compliance-report" aria-label="Permalink to &quot;\`thegent compliance-report\`&quot;">​</a></h2><p>Generate compliance evidence retention report (WP-3006).</p><details><summary>Full documentation</summary><p>Generate compliance evidence retention report (WP-3006).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent compliance-report --format VALUE --output VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-compliance-siem-test" tabindex="-1"><code>thegent compliance-siem-test</code> <a class="header-anchor" href="#thegent-compliance-siem-test" aria-label="Permalink to &quot;\`thegent compliance-siem-test\`&quot;">​</a></h2><p>Test SIEM event egress (WP-15001).</p><details><summary>Full documentation</summary><p>Test SIEM event egress (WP-15001).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent compliance-siem-test --message VALUE --severity VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-concurrency-set" tabindex="-1"><code>thegent concurrency-set</code> <a class="header-anchor" href="#thegent-concurrency-set" aria-label="Permalink to &quot;\`thegent concurrency-set\`&quot;">​</a></h2><p>Set concurrency limit (updates .env file).</p><details><summary>Full documentation</summary><p>Set concurrency limit (updates .env file).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent concurrency-set --limit VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-concurrency-show" tabindex="-1"><code>thegent concurrency-show</code> <a class="header-anchor" href="#thegent-concurrency-show" aria-label="Permalink to &quot;\`thegent concurrency-show\`&quot;">​</a></h2><p>Show current concurrency limit and utilization (WP-5001).</p><details><summary>Full documentation</summary><p>Show current concurrency limit and utilization (WP-5001).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent concurrency-show --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-config-check" tabindex="-1"><code>thegent config-check</code> <a class="header-anchor" href="#thegent-config-check" aria-label="Permalink to &quot;\`thegent config-check\`&quot;">​</a></h2><p>Validate config and report issues (DX-010, ROB-013).</p><details><summary>Full documentation</summary><p>Validate config and report issues (DX-010, ROB-013).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent config-check --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-contracts-conformance" tabindex="-1"><code>thegent contracts-conformance</code> <a class="header-anchor" href="#thegent-contracts-conformance" aria-label="Permalink to &quot;\`thegent contracts-conformance\`&quot;">​</a></h2><p>Run provider adapter conformance tests.</p><details><summary>Full documentation</summary><p>Run provider adapter conformance tests.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent contracts-conformance --format VALUE --check-drift VALUE --drift-window VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-contracts-registry" tabindex="-1"><code>thegent contracts-registry</code> <a class="header-anchor" href="#thegent-contracts-registry" aria-label="Permalink to &quot;\`thegent contracts-registry\`&quot;">​</a></h2><p>Show the contract registry and compatibility matrix.</p><details><summary>Full documentation</summary><p>Show the contract registry and compatibility matrix.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent contracts-registry --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-cost-status" tabindex="-1"><code>thegent cost-status</code> <a class="header-anchor" href="#thegent-cost-status" aria-label="Permalink to &quot;\`thegent cost-status\`&quot;">​</a></h2><p>Show cost budget utilization and cost-aware routing status (WP-5003).</p><details><summary>Full documentation</summary><p>Show cost budget utilization and cost-aware routing status (WP-5003).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent cost-status --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-cost-values" tabindex="-1"><code>thegent cost-values</code> <a class="header-anchor" href="#thegent-cost-values" aria-label="Permalink to &quot;\`thegent cost-values\`&quot;">​</a></h2><p>Show cost values ($/1k tokens) for all model-provider pairs.</p><details><summary>Full documentation</summary><p>Show cost values ($/1k tokens) for all model-provider pairs.</p><p>Uses CLIProxyAPIPlus metrics when reachable; falls back to static values.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent cost-values --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-dag-add" tabindex="-1"><code>thegent dag-add</code> <a class="header-anchor" href="#thegent-dag-add" aria-label="Permalink to &quot;\`thegent dag-add\`&quot;">​</a></h2><p>Add a task to the DAG. XA4: contract_version in task metadata.</p><details><summary>Full documentation</summary><p>Add a task to the DAG. XA4: contract_version in task metadata.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent dag-add --task-id VALUE --agent VALUE --prompt VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-dag-cancel" tabindex="-1"><code>thegent dag-cancel</code> <a class="header-anchor" href="#thegent-dag-cancel" aria-label="Permalink to &quot;\`thegent dag-cancel\`&quot;">​</a></h2><p>Cancel a task (set status to cancelled).</p><details><summary>Full documentation</summary><p>Cancel a task (set status to cancelled).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent dag-cancel --task-id VALUE --cd VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-dag-checkpoint" tabindex="-1"><code>thegent dag-checkpoint</code> <a class="header-anchor" href="#thegent-dag-checkpoint" aria-label="Permalink to &quot;\`thegent dag-checkpoint\`&quot;">​</a></h2><p>Create a point-in-time checkpoint of the DAG state.</p><details><summary>Full documentation</summary><p>Create a point-in-time checkpoint of the DAG state.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent dag-checkpoint --cd VALUE --reason VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-dag-checkpoints" tabindex="-1"><code>thegent dag-checkpoints</code> <a class="header-anchor" href="#thegent-dag-checkpoints" aria-label="Permalink to &quot;\`thegent dag-checkpoints\`&quot;">​</a></h2><p>List recent DAG checkpoints.</p><details><summary>Full documentation</summary><p>List recent DAG checkpoints.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent dag-checkpoints --limit VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-dag-list" tabindex="-1"><code>thegent dag-list</code> <a class="header-anchor" href="#thegent-dag-list" aria-label="Permalink to &quot;\`thegent dag-list\`&quot;">​</a></h2><p>Parse and display DAG session from .factory/dag-session.md.</p><details><summary>Full documentation</summary><p>Parse and display DAG session from .factory/dag-session.md.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent dag-list --cd VALUE --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-dag-probe" tabindex="-1"><code>thegent dag-probe</code> <a class="header-anchor" href="#thegent-dag-probe" aria-label="Permalink to &quot;\`thegent dag-probe\`&quot;">​</a></h2><p>Compare current DAG state with a baseline checkpoint to detect regressions.</p><details><summary>Full documentation</summary><p>Compare current DAG state with a baseline checkpoint to detect regressions.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent dag-probe --cd VALUE --baseline-id VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-dag-ready" tabindex="-1"><code>thegent dag-ready</code> <a class="header-anchor" href="#thegent-dag-ready" aria-label="Permalink to &quot;\`thegent dag-ready\`&quot;">​</a></h2><p>List task ids that are ready (pending with all deps done|cancelled|skipped).</p><details><summary>Full documentation</summary><p>List task ids that are ready (pending with all deps done|cancelled|skipped).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent dag-ready --cd VALUE --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-dag-reconcile" tabindex="-1"><code>thegent dag-reconcile</code> <a class="header-anchor" href="#thegent-dag-reconcile" aria-label="Permalink to &quot;\`thegent dag-reconcile\`&quot;">​</a></h2><p>Reconcile DAG state with reality (clean up stuck &#39;running&#39; tasks).</p><details><summary>Full documentation</summary><p>Reconcile DAG state with reality (clean up stuck &#39;running&#39; tasks).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent dag-reconcile --cd VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-dag-recover" tabindex="-1"><code>thegent dag-recover</code> <a class="header-anchor" href="#thegent-dag-recover" aria-label="Permalink to &quot;\`thegent dag-recover\`&quot;">​</a></h2><p>Perform recovery playbook actions on the DAG.</p><details><summary>Full documentation</summary><p>Perform recovery playbook actions on the DAG.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent dag-recover --cd VALUE --action VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-dag-remove" tabindex="-1"><code>thegent dag-remove</code> <a class="header-anchor" href="#thegent-dag-remove" aria-label="Permalink to &quot;\`thegent dag-remove\`&quot;">​</a></h2><p>Remove a task from the DAG.</p><details><summary>Full documentation</summary><p>Remove a task from the DAG.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent dag-remove --task-id VALUE --cd VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-dag-rollback" tabindex="-1"><code>thegent dag-rollback</code> <a class="header-anchor" href="#thegent-dag-rollback" aria-label="Permalink to &quot;\`thegent dag-rollback\`&quot;">​</a></h2><p>Rollback DAG state to a specific checkpoint.</p><details><summary>Full documentation</summary><p>Rollback DAG state to a specific checkpoint.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent dag-rollback --checkpoint-id VALUE --cd VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-dag-run" tabindex="-1"><code>thegent dag-run</code> <a class="header-anchor" href="#thegent-dag-run" aria-label="Permalink to &quot;\`thegent dag-run\`&quot;">​</a></h2><p>Spawn thegent bg for each ready task; update status=running and session_id.</p><details><summary>Full documentation</summary><p>Spawn thegent bg for each ready task; update status=running and session_id.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent dag-run --cd VALUE --dry-run VALUE --task VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-dag-status" tabindex="-1"><code>thegent dag-status</code> <a class="header-anchor" href="#thegent-dag-status" aria-label="Permalink to &quot;\`thegent dag-status\`&quot;">​</a></h2><p>For each task with session_id show id, status, session_id, session_status (running/exited:rc).</p><details><summary>Full documentation</summary><p>For each task with session_id show id, status, session_id, session_status (running/exited:rc).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent dag-status --cd VALUE --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-dag-sync" tabindex="-1"><code>thegent dag-sync</code> <a class="header-anchor" href="#thegent-dag-sync" aria-label="Permalink to &quot;\`thegent dag-sync\`&quot;">​</a></h2><p>For tasks with session_id and status=running, if pid not running set status=done or failed from rc.</p><details><summary>Full documentation</summary><p>For tasks with session_id and status=running, if pid not running set status=done or failed from rc. If --auto-run-next, spawn next ready tasks after sync.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent dag-sync --cd VALUE --auto-run-next VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-dag-update" tabindex="-1"><code>thegent dag-update</code> <a class="header-anchor" href="#thegent-dag-update" aria-label="Permalink to &quot;\`thegent dag-update\`&quot;">​</a></h2><p>Update a task in the DAG. XA4: contract_version in task metadata.</p><details><summary>Full documentation</summary><p>Update a task in the DAG. XA4: contract_version in task metadata.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent dag-update --task-id VALUE --cd VALUE --status VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-dag-validate" tabindex="-1"><code>thegent dag-validate</code> <a class="header-anchor" href="#thegent-dag-validate" aria-label="Permalink to &quot;\`thegent dag-validate\`&quot;">​</a></h2><p>Validate DAG session from .factory/dag-session.md. Exit 2 on validation errors.</p><details><summary>Full documentation</summary><p>Validate DAG session from .factory/dag-session.md. Exit 2 on validation errors.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent dag-validate --cd VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-data-protection" tabindex="-1"><code>thegent data-protection</code> <a class="header-anchor" href="#thegent-data-protection" aria-label="Permalink to &quot;\`thegent data-protection\`&quot;">​</a></h2><p>Show status of data protection and privacy controls.</p><details><summary>Full documentation</summary><p>Show status of data protection and privacy controls.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent data-protection --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-deep-research" tabindex="-1"><code>thegent deep-research</code> <a class="header-anchor" href="#thegent-deep-research" aria-label="Permalink to &quot;\`thegent deep-research\`&quot;">​</a></h2><p>Perform deep research using the Deep Research Protocol (DRP).</p><details><summary>Full documentation</summary><p>Perform deep research using the Deep Research Protocol (DRP).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent deep-research --query VALUE --subreddits VALUE --output VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-deferral-list" tabindex="-1"><code>thegent deferral-list</code> <a class="header-anchor" href="#thegent-deferral-list" aria-label="Permalink to &quot;\`thegent deferral-list\`&quot;">​</a></h2><p>List all currently deferred tasks (WP-5004).</p><details><summary>Full documentation</summary><p>List all currently deferred tasks (WP-5004).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent deferral-list"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-deferral-resume" tabindex="-1"><code>thegent deferral-resume</code> <a class="header-anchor" href="#thegent-deferral-resume" aria-label="Permalink to &quot;\`thegent deferral-resume\`&quot;">​</a></h2><p>Manually resume a deferred task (WP-5004).</p><details><summary>Full documentation</summary><p>Manually resume a deferred task (WP-5004).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent deferral-resume --run-id VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-discovery-parse" tabindex="-1"><code>thegent discovery-parse</code> <a class="header-anchor" href="#thegent-discovery-parse" aria-label="Permalink to &quot;\`thegent discovery-parse\`&quot;">​</a></h2><p>Parse CLI output for session information and register them.</p><details><summary>Full documentation</summary><p>Parse CLI output for session information and register them.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent discovery-parse --text VALUE --register VALUE --ppid VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-discovery-register" tabindex="-1"><code>thegent discovery-register</code> <a class="header-anchor" href="#thegent-discovery-register" aria-label="Permalink to &quot;\`thegent discovery-register\`&quot;">​</a></h2><p>Register or update a discovered external agent (WP-4008).</p><details><summary>Full documentation</summary><p>Register or update a discovered external agent (WP-4008).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent discovery-register --agent VALUE --pid VALUE --ppid VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-discovery-scan" tabindex="-1"><code>thegent discovery-scan</code> <a class="header-anchor" href="#thegent-discovery-scan" aria-label="Permalink to &quot;\`thegent discovery-scan\`&quot;">​</a></h2><p>Scan process tree for agent CLI sessions and auto-register them.</p><details><summary>Full documentation</summary><p>Scan process tree for agent CLI sessions and auto-register them.</p><p>Detects running cursor-agent, Claude Code, and Codex processes, extracts session IDs from --resume= when present, and registers them for introspection via thegent ps, terminal takeover, and inbox.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent discovery-scan --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-dlq-list" tabindex="-1"><code>thegent dlq-list</code> <a class="header-anchor" href="#thegent-dlq-list" aria-label="Permalink to &quot;\`thegent dlq-list\`&quot;">​</a></h2><p>List items in the Dead-Letter Queue (WP-Y2/WP-2008).</p><details><summary>Full documentation</summary><p>List items in the Dead-Letter Queue (WP-Y2/WP-2008).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent dlq-list --status VALUE --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-drift" tabindex="-1"><code>thegent drift</code> <a class="header-anchor" href="#thegent-drift" aria-label="Permalink to &quot;\`thegent drift\`&quot;">​</a></h2><p>Detect significant drift in contract performance and check alert budgets (G-RV-07).</p><details><summary>Full documentation</summary><p>Detect significant drift in contract performance and check alert budgets (G-RV-07).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent drift --window VALUE --format VALUE --structural-budget VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-drift-monitor" tabindex="-1"><code>thegent drift-monitor</code> <a class="header-anchor" href="#thegent-drift-monitor" aria-label="Permalink to &quot;\`thegent drift-monitor\`&quot;">​</a></h2><p>Monitor drift across multiple providers for the same prompt (WP-3001).</p><details><summary>Full documentation</summary><p>Monitor drift across multiple providers for the same prompt (WP-3001).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent drift-monitor --prompt VALUE --agents VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-escalate-add" tabindex="-1"><code>thegent escalate-add</code> <a class="header-anchor" href="#thegent-escalate-add" aria-label="Permalink to &quot;\`thegent escalate-add\`&quot;">​</a></h2><p>Add a blocked run to the escalation queue (WP-3008).</p><details><summary>Full documentation</summary><p>Add a blocked run to the escalation queue (WP-3008).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent escalate-add --run-id VALUE --reason VALUE --sla-minutes VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-escalate-approve" tabindex="-1"><code>thegent escalate-approve</code> <a class="header-anchor" href="#thegent-escalate-approve" aria-label="Permalink to &quot;\`thegent escalate-approve\`&quot;">​</a></h2><p>Approve an escalation, recording an override for the owner (G-GP-05).</p><details><summary>Full documentation</summary><p>Approve an escalation, recording an override for the owner (G-GP-05).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent escalate-approve --run-id VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-escalate-list" tabindex="-1"><code>thegent escalate-list</code> <a class="header-anchor" href="#thegent-escalate-list" aria-label="Permalink to &quot;\`thegent escalate-list\`&quot;">​</a></h2><p>List governance escalation queue (WP-3008).</p><details><summary>Full documentation</summary><p>List governance escalation queue (WP-3008).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent escalate-list --past-sla-only VALUE --limit VALUE --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-escalate-resolve" tabindex="-1"><code>thegent escalate-resolve</code> <a class="header-anchor" href="#thegent-escalate-resolve" aria-label="Permalink to &quot;\`thegent escalate-resolve\`&quot;">​</a></h2><p>Mark an escalation item as resolved (WP-3008).</p><details><summary>Full documentation</summary><p>Mark an escalation item as resolved (WP-3008).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent escalate-resolve --run-id VALUE --resolution VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-events" tabindex="-1"><code>thegent events</code> <a class="header-anchor" href="#thegent-events" aria-label="Permalink to &quot;\`thegent events\`&quot;">​</a></h2><p>List raw telemetry events.</p><details><summary>Full documentation</summary><p>List raw telemetry events.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent events --run-id VALUE --limit VALUE --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-explain" tabindex="-1"><code>thegent explain</code> <a class="header-anchor" href="#thegent-explain" aria-label="Permalink to &quot;\`thegent explain\`&quot;">​</a></h2><p>Show detailed explanation for an agent run (WP-4002).</p><details><summary>Full documentation</summary><p>Show detailed explanation for an agent run (WP-4002).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent explain --run-id VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-explorer" tabindex="-1"><code>thegent explorer</code> <a class="header-anchor" href="#thegent-explorer" aria-label="Permalink to &quot;\`thegent explorer\`&quot;">​</a></h2><p>Launch the terminal explorer TUI.</p><details><summary>Full documentation</summary><p>Launch the terminal explorer TUI.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent explorer"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-fallbacks" tabindex="-1"><code>thegent fallbacks</code> <a class="header-anchor" href="#thegent-fallbacks" aria-label="Permalink to &quot;\`thegent fallbacks\`&quot;">​</a></h2><p>Show safe fallback options for a failed or blocked run (WP-4003).</p><details><summary>Full documentation</summary><p>Show safe fallback options for a failed or blocked run (WP-4003).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent fallbacks --run-id VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-feedback" tabindex="-1"><code>thegent feedback</code> <a class="header-anchor" href="#thegent-feedback" aria-label="Permalink to &quot;\`thegent feedback\`&quot;">​</a></h2><p>Provide operator feedback for a specific run.</p><details><summary>Full documentation</summary><p>Provide operator feedback for a specific run.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent feedback --run-id VALUE --score VALUE --note VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-forensics-snapshot" tabindex="-1"><code>thegent forensics-snapshot</code> <a class="header-anchor" href="#thegent-forensics-snapshot" aria-label="Permalink to &quot;\`thegent forensics-snapshot\`&quot;">​</a></h2><p>Take a forensics snapshot of an agent run (WP-3002).</p><details><summary>Full documentation</summary><p>Take a forensics snapshot of an agent run (WP-3002).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent forensics-snapshot --run-id VALUE --phase VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-govern-configure" tabindex="-1"><code>thegent govern-configure</code> <a class="header-anchor" href="#thegent-govern-configure" aria-label="Permalink to &quot;\`thegent govern-configure\`&quot;">​</a></h2><p>Bootstrap governance: create contracts/health-targets.json if missing.</p><details><summary>Full documentation</summary><p>Bootstrap governance: create contracts/health-targets.json if missing.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent govern-configure --cd VALUE --force VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-govern-cost" tabindex="-1"><code>thegent govern-cost</code> <a class="header-anchor" href="#thegent-govern-cost" aria-label="Permalink to &quot;\`thegent govern-cost\`&quot;">​</a></h2><p>Show daily cost aggregation (FR-GOV-002).</p><details><summary>Full documentation</summary><p>Show daily cost aggregation (FR-GOV-002).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent govern-cost --owner VALUE --days VALUE --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-govern-go-cycle" tabindex="-1"><code>thegent govern-go-cycle</code> <a class="header-anchor" href="#thegent-govern-go-cycle" aria-label="Permalink to &quot;\`thegent govern-go-cycle\`&quot;">​</a></h2><p>Run a single governance cycle.</p><details><summary>Full documentation</summary><p>Run a single governance cycle.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent govern-go-cycle --cd VALUE --force VALUE --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-govern-go-health" tabindex="-1"><code>thegent govern-go-health</code> <a class="header-anchor" href="#thegent-govern-go-health" aria-label="Permalink to &quot;\`thegent govern-go-health\`&quot;">​</a></h2><p>Show current health score (composite 0-100, band, per-dimension breakdown).</p><details><summary>Full documentation</summary><p>Show current health score (composite 0-100, band, per-dimension breakdown).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent govern-go-health --cd VALUE --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-govern-go-status" tabindex="-1"><code>thegent govern-go-status</code> <a class="header-anchor" href="#thegent-govern-go-status" aria-label="Permalink to &quot;\`thegent govern-go-status\`&quot;">​</a></h2><p>Show current governance status (state, cycle_id, shutdown_requested).</p><details><summary>Full documentation</summary><p>Show current governance status (state, cycle_id, shutdown_requested).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent govern-go-status --cd VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-govern-go-watch" tabindex="-1"><code>thegent govern-go-watch</code> <a class="header-anchor" href="#thegent-govern-go-watch" aria-label="Permalink to &quot;\`thegent govern-go-watch\`&quot;">​</a></h2><p>Run continuous governance mode.</p><details><summary>Full documentation</summary><p>Run continuous governance mode.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent govern-go-watch --cd VALUE --interval VALUE --max-cycles VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-guardrails-check" tabindex="-1"><code>thegent guardrails-check</code> <a class="header-anchor" href="#thegent-guardrails-check" aria-label="Permalink to &quot;\`thegent guardrails-check\`&quot;">​</a></h2><p>Check a prompt against active guardrails (FR-GOV-003..006).</p><details><summary>Full documentation</summary><p>Check a prompt against active guardrails (FR-GOV-003..006).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent guardrails-check --prompt VALUE --agent VALUE --model VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-guardrails-show" tabindex="-1"><code>thegent guardrails-show</code> <a class="header-anchor" href="#thegent-guardrails-show" aria-label="Permalink to &quot;\`thegent guardrails-show\`&quot;">​</a></h2><p>Show active guardrail configuration (FR-GOV-007).</p><details><summary>Full documentation</summary><p>Show active guardrail configuration (FR-GOV-007).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent guardrails-show"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-handoff" tabindex="-1"><code>thegent handoff</code> <a class="header-anchor" href="#thegent-handoff" aria-label="Permalink to &quot;\`thegent handoff\`&quot;">​</a></h2><p>Create a continuity snapshot for a shift handoff (WP-4006, WP-3008).</p><details><summary>Full documentation</summary><p>Create a continuity snapshot for a shift handoff (WP-4006, WP-3008).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent handoff --owner VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-handoff-confirm" tabindex="-1"><code>thegent handoff-confirm</code> <a class="header-anchor" href="#thegent-handoff-confirm" aria-label="Permalink to &quot;\`thegent handoff-confirm\`&quot;">​</a></h2><p>Incoming owner confirms handoff completeness (WP-3008, WP-4006).</p><details><summary>Full documentation</summary><p>Incoming owner confirms handoff completeness (WP-3008, WP-4006).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent handoff-confirm --snapshot-id VALUE --incoming-owner VALUE --confidence VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-handoff-list" tabindex="-1"><code>thegent handoff-list</code> <a class="header-anchor" href="#thegent-handoff-list" aria-label="Permalink to &quot;\`thegent handoff-list\`&quot;">​</a></h2><p>List pending handoff snapshots (WP-4006).</p><details><summary>Full documentation</summary><p>List pending handoff snapshots (WP-4006).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent handoff-list --limit VALUE --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-handoff-show" tabindex="-1"><code>thegent handoff-show</code> <a class="header-anchor" href="#thegent-handoff-show" aria-label="Permalink to &quot;\`thegent handoff-show\`&quot;">​</a></h2><p>Show full handoff summary (state, evidence, next steps) for a snapshot (WP-4006).</p><details><summary>Full documentation</summary><p>Show full handoff summary (state, evidence, next steps) for a snapshot (WP-4006).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent handoff-show --snapshot-id VALUE --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-history" tabindex="-1"><code>thegent history</code> <a class="header-anchor" href="#thegent-history" aria-label="Permalink to &quot;\`thegent history\`&quot;">​</a></h2><p>List execution run history (sync and background).</p><details><summary>Full documentation</summary><p>List execution run history (sync and background).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent history --limit VALUE --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-inbox-list" tabindex="-1"><code>thegent inbox-list</code> <a class="header-anchor" href="#thegent-inbox-list" aria-label="Permalink to &quot;\`thegent inbox-list\`&quot;">​</a></h2><p>List unified inbox events (run registry + escalation) with optional filters.</p><details><summary>Full documentation</summary><p>List unified inbox events (run registry + escalation) with optional filters.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent inbox-list --owner VALUE --agent VALUE --event-type VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-inbox-wait" tabindex="-1"><code>thegent inbox-wait</code> <a class="header-anchor" href="#thegent-inbox-wait" aria-label="Permalink to &quot;\`thegent inbox-wait\`&quot;">​</a></h2><p>Wait for next inbox event matching filters. Blocks until new event or timeout.</p><details><summary>Full documentation</summary><p>Wait for next inbox event matching filters. Blocks until new event or timeout.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent inbox-wait --owner VALUE --agent VALUE --event-type VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-inspect" tabindex="-1"><code>thegent inspect</code> <a class="header-anchor" href="#thegent-inspect" aria-label="Permalink to &quot;\`thegent inspect\`&quot;">​</a></h2><p>Show status and logs for one or more sessions. No shell loop needed.</p><details><summary>Full documentation</summary><p>Show status and logs for one or more sessions. No shell loop needed.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent inspect --session-ids VALUE --owner VALUE --tail VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-interruption-list" tabindex="-1"><code>thegent interruption-list</code> <a class="header-anchor" href="#thegent-interruption-list" aria-label="Permalink to &quot;\`thegent interruption-list\`&quot;">​</a></h2><p>List recent interruptions (WP-4004).</p><details><summary>Full documentation</summary><p>List recent interruptions (WP-4004).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent interruption-list --limit VALUE --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-interruption-snooze" tabindex="-1"><code>thegent interruption-snooze</code> <a class="header-anchor" href="#thegent-interruption-snooze" aria-label="Permalink to &quot;\`thegent interruption-snooze\`&quot;">​</a></h2><p>Snooze an alert; expires → auto-escalation (WP-4004).</p><details><summary>Full documentation</summary><p>Snooze an alert; expires → auto-escalation (WP-4004).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent interruption-snooze --alert-id VALUE --minutes VALUE --itype VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-list-agents" tabindex="-1"><code>thegent list-agents</code> <a class="header-anchor" href="#thegent-list-agents" aria-label="Permalink to &quot;\`thegent list-agents\`&quot;">​</a></h2><p>List available agents.</p><details><summary>Full documentation</summary><p>List available agents.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent list-agents"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-list-droids" tabindex="-1"><code>thegent list-droids</code> <a class="header-anchor" href="#thegent-list-droids" aria-label="Permalink to &quot;\`thegent list-droids\`&quot;">​</a></h2><p>List available droids.</p><details><summary>Full documentation</summary><p>List available droids.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent list-droids --cd VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-list-model-contract-schema" tabindex="-1"><code>thegent list-model-contract-schema</code> <a class="header-anchor" href="#thegent-list-model-contract-schema" aria-label="Permalink to &quot;\`thegent list-model-contract-schema\`&quot;">​</a></h2><p>Print the route contract schema metadata used by contract views.</p><details><summary>Full documentation</summary><p>Print the route contract schema metadata used by contract views.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent list-model-contract-schema"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-list-models" tabindex="-1"><code>thegent list-models</code> <a class="header-anchor" href="#thegent-list-models" aria-label="Permalink to &quot;\`thegent list-models\`&quot;">​</a></h2><p>List available models (scraped from CLIs/config).</p><details><summary>Full documentation</summary><p>List available models (scraped from CLIs/config).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent list-models --provider VALUE --by-model VALUE --refresh VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-load-status" tabindex="-1"><code>thegent load-status</code> <a class="header-anchor" href="#thegent-load-status" aria-label="Permalink to &quot;\`thegent load-status\`&quot;">​</a></h2><p>Show load classification and safe-mode status (WP-5002).</p><details><summary>Full documentation</summary><p>Show load classification and safe-mode status (WP-5002).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent load-status --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-logs" tabindex="-1"><code>thegent logs</code> <a class="header-anchor" href="#thegent-logs" aria-label="Permalink to &quot;\`thegent logs\`&quot;">​</a></h2>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent logs --session-id VALUE --follow VALUE --stderr VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-loop" tabindex="-1"><code>thegent loop</code> <a class="header-anchor" href="#thegent-loop" aria-label="Permalink to &quot;\`thegent loop\`&quot;">​</a></h2><p>Run a Lifecycle loop with Checker oversight.</p><details><summary>Full documentation</summary><p>Run a Lifecycle loop with Checker oversight.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent loop --prompt VALUE --todo-spec VALUE --agent VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-loop-send" tabindex="-1"><code>thegent loop-send</code> <a class="header-anchor" href="#thegent-loop-send" aria-label="Permalink to &quot;\`thegent loop-send\`&quot;">​</a></h2><p>Send a prompt to a running Lifecycle loop (human or agent takeover).</p><details><summary>Full documentation</summary><p>Send a prompt to a running Lifecycle loop (human or agent takeover).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent loop-send --session-id VALUE --prompt VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-loop-stop" tabindex="-1"><code>thegent loop-stop</code> <a class="header-anchor" href="#thegent-loop-stop" aria-label="Permalink to &quot;\`thegent loop-stop\`&quot;">​</a></h2><p>Send STOP signal to a running Lifecycle loop.</p><details><summary>Full documentation</summary><p>Send STOP signal to a running Lifecycle loop.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent loop-stop --session-id VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-metrics" tabindex="-1"><code>thegent metrics</code> <a class="header-anchor" href="#thegent-metrics" aria-label="Permalink to &quot;\`thegent metrics\`&quot;">​</a></h2><p>Show cost, speed, and quality indices for all model-provider pairs (unified view).</p><details><summary>Full documentation</summary><p>Show cost, speed, and quality indices for all model-provider pairs (unified view).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent metrics --format VALUE --no-cache VALUE --limit VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-migration" tabindex="-1"><code>thegent migration</code> <a class="header-anchor" href="#thegent-migration" aria-label="Permalink to &quot;\`thegent migration\`&quot;">​</a></h2><p>Evaluate migration status for a contract version.</p><details><summary>Full documentation</summary><p>Evaluate migration status for a contract version.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent migration --contract-id VALUE --version VALUE --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-modes" tabindex="-1"><code>thegent modes</code> <a class="header-anchor" href="#thegent-modes" aria-label="Permalink to &quot;\`thegent modes\`&quot;">​</a></h2><p>List multi-agent orchestration modes (sequential_delegation, parallel_consensus, review_loop).</p><details><summary>Full documentation</summary><p>List multi-agent orchestration modes (sequential_delegation, parallel_consensus, review_loop).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent modes --format VALUE --mode VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-monitor" tabindex="-1"><code>thegent monitor</code> <a class="header-anchor" href="#thegent-monitor" aria-label="Permalink to &quot;\`thegent monitor\`&quot;">​</a></h2><p>Monitor sessions and plan progress in real-time (WP-8001).</p><details><summary>Full documentation</summary><p>Monitor sessions and plan progress in real-time (WP-8001).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent monitor --interval VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-observe-summary" tabindex="-1"><code>thegent observe-summary</code> <a class="header-anchor" href="#thegent-observe-summary" aria-label="Permalink to &quot;\`thegent observe-summary\`&quot;">​</a></h2><p>FR-X08: Unified observability summary (KPIs, drift, escalation).</p><details><summary>Full documentation</summary><p>FR-X08: Unified observability summary (KPIs, drift, escalation).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent observe-summary --limit VALUE --drift-window VALUE --structural-budget VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-operations" tabindex="-1"><code>thegent operations</code> <a class="header-anchor" href="#thegent-operations" aria-label="Permalink to &quot;\`thegent operations\`&quot;">​</a></h2><p>List universal operation taxonomy (orchestrate, govern, recover, observe, plan).</p><details><summary>Full documentation</summary><p>List universal operation taxonomy (orchestrate, govern, recover, observe, plan).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent operations --format VALUE --operation VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-pause" tabindex="-1"><code>thegent pause</code> <a class="header-anchor" href="#thegent-pause" aria-label="Permalink to &quot;\`thegent pause\`&quot;">​</a></h2><p>Pause a background session (register pause event).</p><details><summary>Full documentation</summary><p>Pause a background session (register pause event).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent pause --session-id VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-plan-analyze" tabindex="-1"><code>thegent plan-analyze</code> <a class="header-anchor" href="#thegent-plan-analyze" aria-label="Permalink to &quot;\`thegent plan-analyze\`&quot;">​</a></h2><p>Run planning simulation overlays (XD1–XD3): PERT, resource contention, continuity risk.</p><details><summary>Full documentation</summary><p>Run planning simulation overlays (XD1–XD3): PERT, resource contention, continuity risk.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent plan-analyze --cd VALUE --pert VALUE --resources VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-plan-claim" tabindex="-1"><code>thegent plan-claim</code> <a class="header-anchor" href="#thegent-plan-claim" aria-label="Permalink to &quot;\`thegent plan-claim\`&quot;">​</a></h2><p>Claim an item in the unified work stream.</p><details><summary>Full documentation</summary><p>Claim an item in the unified work stream.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent plan-claim --item-id VALUE --agent-id VALUE --cd VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-plan-complete" tabindex="-1"><code>thegent plan-complete</code> <a class="header-anchor" href="#thegent-plan-complete" aria-label="Permalink to &quot;\`thegent plan-complete\`&quot;">​</a></h2><p>Mark an item as complete in the unified work stream.</p><details><summary>Full documentation</summary><p>Mark an item as complete in the unified work stream.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent plan-complete --item-id VALUE --agent-id VALUE --cd VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-plan-do-next" tabindex="-1"><code>thegent plan-do-next</code> <a class="header-anchor" href="#thegent-plan-do-next" aria-label="Permalink to &quot;\`thegent plan-do-next\`&quot;">​</a></h2><p>Find next actionable work items from WORK_STREAM, PLAN_STATUS, FR_TRACKER, docs/plans/, escalation queue.</p><details><summary>Full documentation</summary><p>Find next actionable work items from WORK_STREAM, PLAN_STATUS, FR_TRACKER, docs/plans/, escalation queue.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent plan-do-next --cd VALUE --limit VALUE --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-plan-get-next" tabindex="-1"><code>thegent plan-get-next</code> <a class="header-anchor" href="#thegent-plan-get-next" aria-label="Permalink to &quot;\`thegent plan-get-next\`&quot;">​</a></h2><p>Get first work item prompt for scripting. Use: PROMPT=$(thegent plan get-next)</p><details><summary>Full documentation</summary><p>Get first work item prompt for scripting. Use: PROMPT=$(thegent plan get-next)</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent plan-get-next --cd VALUE --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-plan-incorporate" tabindex="-1"><code>thegent plan-incorporate</code> <a class="header-anchor" href="#thegent-plan-incorporate" aria-label="Permalink to &quot;\`thegent plan-incorporate\`&quot;">​</a></h2><p>Merge fragments from 02-UNIFIED-WBS into WORK_STREAM.md. Preserves CLAIMED and COMPLETED.</p><details><summary>Full documentation</summary><p>Merge fragments from 02-UNIFIED-WBS into WORK_STREAM.md. Preserves CLAIMED and COMPLETED.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent plan-incorporate --cd VALUE --dry-run VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-plan-loop" tabindex="-1"><code>thegent plan-loop</code> <a class="header-anchor" href="#thegent-plan-loop" aria-label="Permalink to &quot;\`thegent plan-loop\`&quot;">​</a></h2><p>Loop: get next item -&gt; run bg -&gt; repeat until no items or --max reached.</p><details><summary>Full documentation</summary><p>Loop: get next item -&gt; run bg -&gt; repeat until no items or --max reached.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent plan-loop --cd VALUE --max-iterations VALUE --sleep-seconds VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-plan-progress" tabindex="-1"><code>thegent plan-progress</code> <a class="header-anchor" href="#thegent-plan-progress" aria-label="Permalink to &quot;\`thegent plan-progress\`&quot;">​</a></h2><p>Show recent runs (work-package progress). Alias for history --limit N.</p><details><summary>Full documentation</summary><p>Show recent runs (work-package progress). Alias for history --limit N.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent plan-progress --limit VALUE --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-plan-wait-next" tabindex="-1"><code>thegent plan-wait-next</code> <a class="header-anchor" href="#thegent-plan-wait-next" aria-label="Permalink to &quot;\`thegent plan-wait-next\`&quot;">​</a></h2><p>Block until next actionable work exists (DAG ready, do_next, escalation, inbox).</p><details><summary>Full documentation</summary><p>Block until next actionable work exists (DAG ready, do_next, escalation, inbox).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent plan-wait-next --cd VALUE --poll VALUE --timeout VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-policy-check" tabindex="-1"><code>thegent policy-check</code> <a class="header-anchor" href="#thegent-policy-check" aria-label="Permalink to &quot;\`thegent policy-check\`&quot;">​</a></h2><p>Evaluate a hypothetical run against governance policies (WP-3001).</p><details><summary>Full documentation</summary><p>Evaluate a hypothetical run against governance policies (WP-3001).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent policy-check --agent VALUE --model VALUE --lane VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-policy-purge" tabindex="-1"><code>thegent policy-purge</code> <a class="header-anchor" href="#thegent-policy-purge" aria-label="Permalink to &quot;\`thegent policy-purge\`&quot;">​</a></h2><p>Purge expired history based on tiered retention (WP-3006).</p><details><summary>Full documentation</summary><p>Purge expired history based on tiered retention (WP-3006).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent policy-purge --dry-run VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-policy-show" tabindex="-1"><code>thegent policy-show</code> <a class="header-anchor" href="#thegent-policy-show" aria-label="Permalink to &quot;\`thegent policy-show\`&quot;">​</a></h2><p>Show active governance policies and thresholds.</p><details><summary>Full documentation</summary><p>Show active governance policies and thresholds.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent policy-show"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-project-list" tabindex="-1"><code>thegent project-list</code> <a class="header-anchor" href="#thegent-project-list" aria-label="Permalink to &quot;\`thegent project-list\`&quot;">​</a></h2><p>List all registered projects (WP-4008).</p><details><summary>Full documentation</summary><p>List all registered projects (WP-4008).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent project-list"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-project-register" tabindex="-1"><code>thegent project-register</code> <a class="header-anchor" href="#thegent-project-register" aria-label="Permalink to &quot;\`thegent project-register\`&quot;">​</a></h2><p>Register a new project (WP-4008).</p><details><summary>Full documentation</summary><p>Register a new project (WP-4008).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent project-register --path VALUE --name VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-ps" tabindex="-1"><code>thegent ps</code> <a class="header-anchor" href="#thegent-ps" aria-label="Permalink to &quot;\`thegent ps\`&quot;">​</a></h2>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent ps --all-sessions VALUE --owner VALUE --format VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-purge" tabindex="-1"><code>thegent purge</code> <a class="header-anchor" href="#thegent-purge" aria-label="Permalink to &quot;\`thegent purge\`&quot;">​</a></h2><p>WP-3006: Tiered retention purge (G-GP-07).</p><details><summary>Full documentation</summary><p>WP-3006: Tiered retention purge (G-GP-07).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent purge --dry-run VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-quality-index" tabindex="-1"><code>thegent quality-index</code> <a class="header-anchor" href="#thegent-quality-index" aria-label="Permalink to &quot;\`thegent quality-index\`&quot;">​</a></h2><p>Show quality index (0-1) for all models.</p><details><summary>Full documentation</summary><p>Show quality index (0-1) for all models.</p><p>Uses benchmarks.json (Terminal Bench 2.0, SWE-Bench, AIME) when available; falls back to Route.accuracy_score.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent quality-index --format VALUE --no-cache VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-queue-list" tabindex="-1"><code>thegent queue-list</code> <a class="header-anchor" href="#thegent-queue-list" aria-label="Permalink to &quot;\`thegent queue-list\`&quot;">​</a></h2><p>WP-7002: List pending prompts in the queue.</p><details><summary>Full documentation</summary><p>WP-7002: List pending prompts in the queue.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent queue-list --watch VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-recover-status" tabindex="-1"><code>thegent recover-status</code> <a class="header-anchor" href="#thegent-recover-status" aria-label="Permalink to &quot;\`thegent recover-status\`&quot;">​</a></h2><p>Show current recovery status (WP-7001).</p><details><summary>Full documentation</summary><p>Show current recovery status (WP-7001).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent recover-status"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-release-pack" tabindex="-1"><code>thegent release-pack</code> <a class="header-anchor" href="#thegent-release-pack" aria-label="Permalink to &quot;\`thegent release-pack\`&quot;">​</a></h2><p>Automated release documentation packaging (WP-12009).</p><details><summary>Full documentation</summary><p>Automated release documentation packaging (WP-12009).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent release-pack --version VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-replay" tabindex="-1"><code>thegent replay</code> <a class="header-anchor" href="#thegent-replay" aria-label="Permalink to &quot;\`thegent replay\`&quot;">​</a></h2><p>Decision replay and rationale snapshots (WP-4007).</p><details><summary>Full documentation</summary><p>Decision replay and rationale snapshots (WP-4007).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent replay --run-id VALUE --what-if-env VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-resolve-model-route" tabindex="-1"><code>thegent resolve-model-route</code> <a class="header-anchor" href="#thegent-resolve-model-route" aria-label="Permalink to &quot;\`thegent resolve-model-route\`&quot;">​</a></h2><p>Resolve a model to a preferred route and emit contract-style output.</p><details><summary>Full documentation</summary><p>Resolve a model to a preferred route and emit contract-style output.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent resolve-model-route --model VALUE --provider VALUE --policy VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-resume" tabindex="-1"><code>thegent resume</code> <a class="header-anchor" href="#thegent-resume" aria-label="Permalink to &quot;\`thegent resume\`&quot;">​</a></h2><p>Resume a background session (register resume event).</p><details><summary>Full documentation</summary><p>Resume a background session using the stable WL-110 state contract.</p><ul><li>With no <code>--session-id</code>, <code>thegent</code> selects the most recent resumable <code>state.json</code> under <code>~/.thegent/sessions/*/state.json</code>.</li><li>A resumable state contract must include non-empty string values for: <ul><li><code>session_id</code></li><li><code>run_id</code></li></ul></li><li>Malformed state contracts are skipped during auto-selection and rejected when explicitly targeted.</li></ul></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent resume --session-id VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-retry" tabindex="-1"><code>thegent retry</code> <a class="header-anchor" href="#thegent-retry" aria-label="Permalink to &quot;\`thegent retry\`&quot;">​</a></h2><p>Retry a failed run. With no run_id, list recent failed runs.</p><details><summary>Full documentation</summary><p>Retry a failed run. With no run_id, list recent failed runs.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent retry --run-id VALUE --agent VALUE --failover VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-roadmap" tabindex="-1"><code>thegent roadmap</code> <a class="header-anchor" href="#thegent-roadmap" aria-label="Permalink to &quot;\`thegent roadmap\`&quot;">​</a></h2><p>Successor roadmap generation (WP-6004).</p><details><summary>Full documentation</summary><p>Successor roadmap generation (WP-6004).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent roadmap"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-rules-sync" tabindex="-1"><code>thegent rules-sync</code> <a class="header-anchor" href="#thegent-rules-sync" aria-label="Permalink to &quot;\`thegent rules-sync\`&quot;">​</a></h2><p>Sync CLAUDE.md to other platform-specific rule files (AGENTS.md, Cursor, Codex).</p><details><summary>Full documentation</summary><p>Sync CLAUDE.md to other platform-specific rule files (AGENTS.md, Cursor, Codex).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent rules-sync --force VALUE --check VALUE --cd VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-run" tabindex="-1"><code>thegent run</code> <a class="header-anchor" href="#thegent-run" aria-label="Permalink to &quot;\`thegent run\`&quot;">​</a></h2><p>Run an agent or droid with the given prompt. Model-first: agent=None, model set.</p><details><summary>Full documentation</summary><p>Run an agent or droid with the given prompt. Model-first: agent=None, model set.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent run --agent VALUE --prompt VALUE --cd VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-run-diff" tabindex="-1"><code>thegent run-diff</code> <a class="header-anchor" href="#thegent-run-diff" aria-label="Permalink to &quot;\`thegent run-diff\`&quot;">​</a></h2><p>Compare two execution runs (WP-16001).</p><details><summary>Full documentation</summary><p>Compare two execution runs (WP-16001).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent run-diff --run-a VALUE --run-b VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-self-heal-tests" tabindex="-1"><code>thegent self-heal-tests</code> <a class="header-anchor" href="#thegent-self-heal-tests" aria-label="Permalink to &quot;\`thegent self-heal-tests\`&quot;">​</a></h2><p>Self-healing test suite: automated fix recommendations (WP-6006).</p><details><summary>Full documentation</summary><p>Self-healing test suite: automated fix recommendations (WP-6006).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent self-heal-tests --test-output VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-session" tabindex="-1"><code>thegent session</code> <a class="header-anchor" href="#thegent-session" aria-label="Permalink to &quot;\`thegent session\`&quot;">​</a></h2><p>Rich TUI for session management with subagent monitoring (WP-8002).</p><details><summary>Full documentation</summary><p>Rich TUI for session management with subagent monitoring (WP-8002).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent session --session-id VALUE --watch VALUE --action VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-session-contract-health-gate" tabindex="-1"><code>thegent session-contract-health-gate</code> <a class="header-anchor" href="#thegent-session-contract-health-gate" aria-label="Permalink to &quot;\`thegent session-contract-health-gate\`&quot;">​</a></h2>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent session-contract-health-gate --all-sessions VALUE --owner VALUE --strict VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-session-contract-health-report" tabindex="-1"><code>thegent session-contract-health-report</code> <a class="header-anchor" href="#thegent-session-contract-health-report" aria-label="Permalink to &quot;\`thegent session-contract-health-report\`&quot;">​</a></h2>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent session-contract-health-report --all-sessions VALUE --owner VALUE --strict VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-session-contract-health-trend" tabindex="-1"><code>thegent session-contract-health-trend</code> <a class="header-anchor" href="#thegent-session-contract-health-trend" aria-label="Permalink to &quot;\`thegent session-contract-health-trend\`&quot;">​</a></h2>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent session-contract-health-trend --payload-type VALUE --all-sessions VALUE --owner VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-session-contract-negotiate" tabindex="-1"><code>thegent session-contract-negotiate</code> <a class="header-anchor" href="#thegent-session-contract-negotiate" aria-label="Permalink to &quot;\`thegent session-contract-negotiate\`&quot;">​</a></h2><p>Negotiate a contract version (WP-7001).</p><details><summary>Full documentation</summary><p>Negotiate a contract version (WP-7001).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent session-contract-negotiate --contract-id VALUE --supported-versions VALUE --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-session-contract-trend-analysis" tabindex="-1"><code>thegent session-contract-trend-analysis</code> <a class="header-anchor" href="#thegent-session-contract-trend-analysis" aria-label="Permalink to &quot;\`thegent session-contract-trend-analysis\`&quot;">​</a></h2><p>Detailed contract trend analysis (WP-7009/7010).</p><details><summary>Full documentation</summary><p>Detailed contract trend analysis (WP-7009/7010).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent session-contract-trend-analysis"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-session-contracts" tabindex="-1"><code>thegent session-contracts</code> <a class="header-anchor" href="#thegent-session-contracts" aria-label="Permalink to &quot;\`thegent session-contracts\`&quot;">​</a></h2>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent session-contracts --all-sessions VALUE --owner VALUE --format VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-setup" tabindex="-1"><code>thegent setup</code> <a class="header-anchor" href="#thegent-setup" aria-label="Permalink to &quot;\`thegent setup\`&quot;">​</a></h2><p>Unified setup: configure providers (same flow as cliproxy login) and install shortcuts.</p><details><summary>Full documentation</summary><p>Unified setup: configure providers (same flow as cliproxy login) and install shortcuts.</p><p>Examples: thegent setup # Interactive wizard thegent setup --full # Full setup: install, shims, services, harness thegent setup --harness # Install/update heliosShield harness only thegent setup --hooks --skills # Project: git hooks + skills</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent setup --api-key VALUE --model VALUE --openrouter-key VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-sys-setup-project-scaffold" tabindex="-1"><code>thegent sys setup project scaffold</code> <a class="header-anchor" href="#thegent-sys-setup-project-scaffold" aria-label="Permalink to &quot;\`thegent sys setup project scaffold\`&quot;">​</a></h2><p>Bootstrap a new project from initialize-project presets.</p><details><summary>Full documentation</summary><p>Preset scaffold command with profile defaults and optional tenancy/runtime wiring.</p><p>Examples: thegent sys setup project scaffold ./my-service --profile service_api thegent sys setup project scaffold ./my-service --profile service_api --dry-run --json thegent sys setup project scaffold ./my-service --profile service_api --register --install-runtime</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent sys setup project scaffold DESTINATION --profile VALUE --name VALUE --description VALUE --language VALUE --register --install-runtime --dry-run --json"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-sys-setup-project-scaffold-profiles" tabindex="-1"><code>thegent sys setup project scaffold-profiles</code> <a class="header-anchor" href="#thegent-sys-setup-project-scaffold-profiles" aria-label="Permalink to &quot;\`thegent sys setup project scaffold-profiles\`&quot;">​</a></h2><p>List available scaffold preset profiles.</p><details><summary>Full documentation</summary><p>Show supported profile names and optionally emit JSON.</p><p>Examples: thegent sys setup project scaffold-profiles thegent sys setup project scaffold-profiles --json</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent sys setup project scaffold-profiles --json"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-signatures-list" tabindex="-1"><code>thegent signatures-list</code> <a class="header-anchor" href="#thegent-signatures-list" aria-label="Permalink to &quot;\`thegent signatures-list\`&quot;">​</a></h2><p>List signed MAIF artifacts (WP-3002).</p><details><summary>Full documentation</summary><p>List signed MAIF artifacts (WP-3002).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent signatures-list --limit VALUE --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-signatures-verify" tabindex="-1"><code>thegent signatures-verify</code> <a class="header-anchor" href="#thegent-signatures-verify" aria-label="Permalink to &quot;\`thegent signatures-verify\`&quot;">​</a></h2><p>Verify a signed MAIF artifact (WP-3002).</p><details><summary>Full documentation</summary><p>Verify a signed MAIF artifact (WP-3002).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent signatures-verify --run-id VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-sitback-dashboard" tabindex="-1"><code>thegent sitback-dashboard</code> <a class="header-anchor" href="#thegent-sitback-dashboard" aria-label="Permalink to &quot;\`thegent sitback-dashboard\`&quot;">​</a></h2><p>Unified sitback dashboard: sessions, cockpit (circuits, drift, budget), terminals.</p><details><summary>Full documentation</summary><p>Unified sitback dashboard: sessions, cockpit (circuits, drift, budget), terminals. CLI mirror of thegent_sitback_dashboard MCP tool. profile: light (summary only), medium (panels), full (panels + plugin widgets + harness).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent sitback-dashboard --refresh VALUE --format VALUE --profile VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-speed-index" tabindex="-1"><code>thegent speed-index</code> <a class="header-anchor" href="#thegent-speed-index" aria-label="Permalink to &quot;\`thegent speed-index\`&quot;">​</a></h2><p>Show speed index (0-1, higher=faster) for all model-provider pairs.</p><details><summary>Full documentation</summary><p>Show speed index (0-1, higher=faster) for all model-provider pairs.</p><p>Uses CLIProxyAPIPlus metrics (tps_1m, latency_p50_ms, success_rate) when reachable; falls back to Route.latency_ms.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent speed-index --format VALUE --no-cache VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-status" tabindex="-1"><code>thegent status</code> <a class="header-anchor" href="#thegent-status" aria-label="Permalink to &quot;\`thegent status\`&quot;">​</a></h2>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent status --session-id VALUE --format VALUE --include-contract VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-stop" tabindex="-1"><code>thegent stop</code> <a class="header-anchor" href="#thegent-stop" aria-label="Permalink to &quot;\`thegent stop\`&quot;">​</a></h2>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent stop --session-id VALUE --force VALUE --wind-down VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-summary" tabindex="-1"><code>thegent summary</code> <a class="header-anchor" href="#thegent-summary" aria-label="Permalink to &quot;\`thegent summary\`&quot;">​</a></h2><p>FR-X09: Unified summary and audit log across runs, chats, and commits.</p><details><summary>Full documentation</summary><p>FR-X09: Unified summary and audit log across runs, chats, and commits.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent summary --period VALUE --project VALUE --summarize VALUE ..."
  }, null, _parent));
  _push(`<hr><h2 id="thegent-sweep" tabindex="-1"><code>thegent sweep</code> <a class="header-anchor" href="#thegent-sweep" aria-label="Permalink to &quot;\`thegent sweep\`&quot;">​</a></h2><p>WP-3005: Policy drift sweep - runs drift detection, budget check, past-SLA escalations.</p><details><summary>Full documentation</summary><p>WP-3005: Policy drift sweep - runs drift detection, budget check, past-SLA escalations.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent sweep --drift-window VALUE --include-audit VALUE --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-takeover" tabindex="-1"><code>thegent takeover</code> <a class="header-anchor" href="#thegent-takeover" aria-label="Permalink to &quot;\`thegent takeover\`&quot;">​</a></h2><p>Take over an active terminal session via tmux (WP-4008).</p><details><summary>Full documentation</summary><p>Take over an active terminal session via tmux (WP-4008).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent takeover --session-id VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-team-create" tabindex="-1"><code>thegent team-create</code> <a class="header-anchor" href="#thegent-team-create" aria-label="Permalink to &quot;\`thegent team-create\`&quot;">​</a></h2><p>WP-6008: Create a new multi-agent team.</p><details><summary>Full documentation</summary><p>WP-6008: Create a new multi-agent team.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent team-create --name VALUE --leader VALUE --teammates VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-team-task-add" tabindex="-1"><code>thegent team-task-add</code> <a class="header-anchor" href="#thegent-team-task-add" aria-label="Permalink to &quot;\`thegent team-task-add\`&quot;">​</a></h2><p>WP-6008: Add a task to a team&#39;s backlog.</p><details><summary>Full documentation</summary><p>WP-6008: Add a task to a team&#39;s backlog.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent team-task-add --team-id VALUE --title VALUE --description VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-team-task-list" tabindex="-1"><code>thegent team-task-list</code> <a class="header-anchor" href="#thegent-team-task-list" aria-label="Permalink to &quot;\`thegent team-task-list\`&quot;">​</a></h2><p>WP-6008: List all tasks for a team.</p><details><summary>Full documentation</summary><p>WP-6008: List all tasks for a team.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent team-task-list --team-id VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-teammates-delegate" tabindex="-1"><code>thegent teammates-delegate</code> <a class="header-anchor" href="#thegent-teammates-delegate" aria-label="Permalink to &quot;\`thegent teammates-delegate\`&quot;">​</a></h2><p>WP-16002: Delegate a sub-task to a specialized teammate.</p><details><summary>Full documentation</summary><p>WP-16002: Delegate a sub-task to a specialized teammate.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent teammates-delegate --teammate-id VALUE --prompt VALUE --parent-run-id VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-teammates-list" tabindex="-1"><code>thegent teammates-list</code> <a class="header-anchor" href="#thegent-teammates-list" aria-label="Permalink to &quot;\`thegent teammates-list\`&quot;">​</a></h2><p>WP-16001: List all discovered specialized agents available for delegation.</p><details><summary>Full documentation</summary><p>WP-16001: List all discovered specialized agents available for delegation.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent teammates-list"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-teammates-status" tabindex="-1"><code>thegent teammates-status</code> <a class="header-anchor" href="#thegent-teammates-status" aria-label="Permalink to &quot;\`thegent teammates-status\`&quot;">​</a></h2><p>WP-16002: Monitor the status of the teammate swarm.</p><details><summary>Full documentation</summary><p>WP-16002: Monitor the status of the teammate swarm.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent teammates-status --run-id VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-terminal-route" tabindex="-1"><code>thegent terminal-route</code> <a class="header-anchor" href="#thegent-terminal-route" aria-label="Permalink to &quot;\`thegent terminal-route\`&quot;">​</a></h2><p>Automatically route a prompt to an active terminal session if matching.</p><details><summary>Full documentation</summary><p>Automatically route a prompt to an active terminal session if matching.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent terminal-route --prompt VALUE --cd VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-trace-replay" tabindex="-1"><code>thegent trace-replay</code> <a class="header-anchor" href="#thegent-trace-replay" aria-label="Permalink to &quot;\`thegent trace-replay\`&quot;">​</a></h2><p>WP-16001: Replay an execution trace in sandbox mode.</p><details><summary>Full documentation</summary><p>WP-16001: Replay an execution trace in sandbox mode.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent trace-replay --run-id VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-traffic" tabindex="-1"><code>thegent traffic</code> <a class="header-anchor" href="#thegent-traffic" aria-label="Permalink to &quot;\`thegent traffic\`&quot;">​</a></h2><p>TRAFFIC KPI Dashboard (WP-Y7).</p><details><summary>Full documentation</summary><p>TRAFFIC KPI Dashboard (WP-Y7).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent traffic"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-trust-status" tabindex="-1"><code>thegent trust-status</code> <a class="header-anchor" href="#thegent-trust-status" aria-label="Permalink to &quot;\`thegent trust-status\`&quot;">​</a></h2><p>Show last environment and trust boundary status (WP-3007).</p><details><summary>Full documentation</summary><p>Show last environment and trust boundary status (WP-3007).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent trust-status --format VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-usage" tabindex="-1"><code>thegent usage</code> <a class="header-anchor" href="#thegent-usage" aria-label="Permalink to &quot;\`thegent usage\`&quot;">​</a></h2><p>Show plan usage: provider metrics from CLIProxyAPIPlus and cost status (WP-5003).</p><details><summary>Full documentation</summary><p>Show plan usage: provider metrics from CLIProxyAPIPlus and cost status (WP-5003).</p><p>For cross-provider session parsing (OpenCode, Claude Code, Codex, Gemini, Cursor, etc.), use: bunx tokscale@latest</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent usage --format VALUE --include-cost VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-wait" tabindex="-1"><code>thegent wait</code> <a class="header-anchor" href="#thegent-wait" aria-label="Permalink to &quot;\`thegent wait\`&quot;">​</a></h2>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent wait --session-id VALUE --timeout VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-watchdog" tabindex="-1"><code>thegent watchdog</code> <a class="header-anchor" href="#thegent-watchdog" aria-label="Permalink to &quot;\`thegent watchdog\`&quot;">​</a></h2><p>Scan for stale sessions and recommend handoffs (WP-5005).</p><details><summary>Full documentation</summary><p>Scan for stale sessions and recommend handoffs (WP-5005).</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent watchdog --max-idle-s VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-workstream-dashboard" tabindex="-1"><code>thegent workstream-dashboard</code> <a class="header-anchor" href="#thegent-workstream-dashboard" aria-label="Permalink to &quot;\`thegent workstream-dashboard\`&quot;">​</a></h2><p>Launch workstream dashboard TUI.</p><details><summary>Full documentation</summary><p>Launch workstream dashboard TUI.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent workstream-dashboard"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-workstream-dependencies" tabindex="-1"><code>thegent workstream-dependencies</code> <a class="header-anchor" href="#thegent-workstream-dependencies" aria-label="Permalink to &quot;\`thegent workstream-dependencies\`&quot;">​</a></h2><p>Show the workstream dependency graph.</p><details><summary>Full documentation</summary><p>Show the workstream dependency graph.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent workstream-dependencies"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-workstream-launch" tabindex="-1"><code>thegent workstream-launch</code> <a class="header-anchor" href="#thegent-workstream-launch" aria-label="Permalink to &quot;\`thegent workstream-launch\`&quot;">​</a></h2><p>Launch the auto-launch system in the background.</p><details><summary>Full documentation</summary><p>Launch the auto-launch system in the background.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent workstream-launch"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-workstream-query" tabindex="-1"><code>thegent workstream-query</code> <a class="header-anchor" href="#thegent-workstream-query" aria-label="Permalink to &quot;\`thegent workstream-query\`&quot;">​</a></h2><p>Execute SQL query on workstream database.</p><details><summary>Full documentation</summary><p>Execute SQL query on workstream database.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent workstream-query --query VALUE"
  }, null, _parent));
  _push(`<hr><h2 id="thegent-workstream-stats" tabindex="-1"><code>thegent workstream-stats</code> <a class="header-anchor" href="#thegent-workstream-stats" aria-label="Permalink to &quot;\`thegent workstream-stats\`&quot;">​</a></h2><p>Get workstream statistics.</p><details><summary>Full documentation</summary><p>Get workstream statistics.</p></details>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    code: "thegent workstream-stats"
  }, null, _parent));
  _push(`<hr></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("reference/cli-examples.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const cliExamples = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  cliExamples as default
};
