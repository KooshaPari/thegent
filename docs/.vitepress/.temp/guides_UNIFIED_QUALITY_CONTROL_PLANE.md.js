import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Unified Quality Control Plane","description":"","frontmatter":{},"headers":[],"relativePath":"guides/UNIFIED_QUALITY_CONTROL_PLANE.md","filePath":"guides/UNIFIED_QUALITY_CONTROL_PLANE.md","lastUpdated":1771803666000}');
const _sfc_main = { name: "guides/UNIFIED_QUALITY_CONTROL_PLANE.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="unified-quality-control-plane" tabindex="-1">Unified Quality Control Plane <a class="header-anchor" href="#unified-quality-control-plane" aria-label="Permalink to &quot;Unified Quality Control Plane&quot;">​</a></h1><p>This guide describes the contract-first quality control plane used by <code>thegent</code>.</p><h2 id="default-posture" tabindex="-1">Default posture <a class="header-anchor" href="#default-posture" aria-label="Permalink to &quot;Default posture&quot;">​</a></h2><ul><li>ADR: <code>ADR-017</code></li><li>Default plane: <code>github_sarif_native</code></li><li>Policy contract: <code>contracts/quality-control-plane-v1.json</code></li><li>Contract schema: <code>schemas/quality-control-plane-v1.schema.json</code></li></ul><h2 id="artifact-contracts" tabindex="-1">Artifact contracts <a class="header-anchor" href="#artifact-contracts" aria-label="Permalink to &quot;Artifact contracts&quot;">​</a></h2><ul><li>Hook result envelope: <code>schemas/thegent-hooks-result-v1.schema.json</code></li><li>Hook input contracts: <ul><li><code>schemas/thegent-hooks-quality-gate-input-v1.schema.json</code></li><li><code>schemas/thegent-hooks-security-pipeline-input-v1.schema.json</code></li></ul></li></ul><h2 id="primary-tasks" tabindex="-1">Primary tasks <a class="header-anchor" href="#primary-tasks" aria-label="Permalink to &quot;Primary tasks&quot;">​</a></h2><ul><li><code>task quality:hooks:sarif</code></li><li><code>task quality:generated-python:antipatterns</code></li><li><code>task quality:pilot:mutation-perf</code></li><li><code>task quality:control-plane:validate</code></li><li><code>task quality:control-plane:report</code></li><li><code>task quality:summary</code></li><li><code>task quality:ci:unified</code></li></ul><h2 id="ci-model" tabindex="-1">CI model <a class="header-anchor" href="#ci-model" aria-label="Permalink to &quot;CI model&quot;">​</a></h2><ul><li>PR: run artifact producers in non-blocking mode where appropriate.</li><li>Nightly: enforce contract validation and readiness reporting gates.</li><li>Promotion: move pilots to blocking after stability and flake budget review.</li></ul><p>Current wiring:</p><ul><li><code>.github/workflows/ci.yml</code> includes <code>quality-unified</code> job for <code>pull_request</code> and nightly <code>schedule</code>.</li><li>Gate policy contract: <code>contracts/unified-quality-gate-policy-v1.json</code></li><li>Gate policy schema: <code>schemas/unified-quality-gate-policy-v1.schema.json</code></li><li>Gate task: <code>task quality:gate:unified</code></li><li>PR runs set <code>QUALITY_UNIFIED_MODE=pr</code>.</li><li>Nightly runs set <code>QUALITY_UNIFIED_MODE=nightly</code> (fail-closed on policy-defined warn/fail conditions).</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("guides/UNIFIED_QUALITY_CONTROL_PLANE.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const UNIFIED_QUALITY_CONTROL_PLANE = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  UNIFIED_QUALITY_CONTROL_PLANE as default
};
