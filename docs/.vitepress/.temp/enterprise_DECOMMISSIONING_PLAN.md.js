import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Decommissioning and Sunset Plan","description":"","frontmatter":{},"headers":[],"relativePath":"enterprise/DECOMMISSIONING_PLAN.md","filePath":"enterprise/DECOMMISSIONING_PLAN.md","lastUpdated":1771753292000}');
const _sfc_main = { name: "enterprise/DECOMMISSIONING_PLAN.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="decommissioning-and-sunset-plan" tabindex="-1">Decommissioning and Sunset Plan <a class="header-anchor" href="#decommissioning-and-sunset-plan" aria-label="Permalink to &quot;Decommissioning and Sunset Plan&quot;">​</a></h1><p>undefined<strong>Scope:</strong> Temporary controls and legacy adapters in thegent undefined<strong>Date:</strong> 2026-02-14 undefined<strong>Related:</strong> WP-6006, <code>docs/RUNBOOK.md</code> §5</p><h2 id="_1-overview" tabindex="-1">1. Overview <a class="header-anchor" href="#_1-overview" aria-label="Permalink to &quot;1. Overview&quot;">​</a></h2><p>This plan identifies temporary architectural shims, legacy adapters, and transitional controls that should be sunset as the platform matures.</p><h2 id="_2-target-components-for-sunset" tabindex="-1">2. Target Components for Sunset <a class="header-anchor" href="#_2-target-components-for-sunset" aria-label="Permalink to &quot;2. Target Components for Sunset&quot;">​</a></h2><table tabindex="0"><thead><tr><th>Component</th><th>Reason</th><th>Sunset Trigger</th><th>Target</th></tr></thead><tbody><tr><td><code>GenericOutputAdapter</code></td><td>Loose normalization</td><td>100% provider coverage with <code>XMLOutputAdapter</code></td><td>v1.2</td></tr><tr><td><code>fallback-plain</code> policy</td><td>Low confidence</td><td>95% normalization success rate over 30 days</td><td>v1.2</td></tr><tr><td><code>--override</code> flag (unlimited)</td><td>Security risk</td><td>Implementation of TTL-based policy overrides</td><td>v1.1</td></tr><tr><td>Static model lists</td><td>Brittle</td><td>Stable <code>ModelScraper</code> performance for all providers</td><td>v1.2</td></tr><tr><td><code>history-legacy</code> command</td><td>Hidden, superseded</td><td>Already hidden</td><td>v1.1</td></tr></tbody></table><h2 id="_3-migration-path" tabindex="-1">3. Migration Path <a class="header-anchor" href="#_3-migration-path" aria-label="Permalink to &quot;3. Migration Path&quot;">​</a></h2><ol><li>undefined<strong>Deprecation Phase:</strong>undefined <ul><li>Emit warnings via <code>ContractTelemetry</code> when sunset components are used.</li><li>Update <code>CONTRACT_AUTHORITY.md</code> to mark versions as <code>deprecated</code>.</li></ul></li><li>undefined<strong>Dual-Run Phase:</strong>undefined <ul><li>Run legacy and new components in parallel where possible.</li><li>Log drift via <code>ContractTelemetry.detect_drift()</code> and <code>thegent govern conformance --check-drift</code>.</li></ul></li><li>undefined<strong>Decommission Phase:</strong>undefined <ul><li>Remove code from <code>src/thegent</code>.</li><li>Update conformance tests to ensure no regressions.</li></ul></li></ol><h2 id="_4-rollback-strategy" tabindex="-1">4. Rollback Strategy <a class="header-anchor" href="#_4-rollback-strategy" aria-label="Permalink to &quot;4. Rollback Strategy&quot;">​</a></h2><p>In case of critical failures after sunset:</p><ul><li>Retain code in git history for rapid revert.</li><li>Maintain <code>v-1</code> version compatibility in <code>ContractRegistry</code> for one major release.</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("enterprise/DECOMMISSIONING_PLAN.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const DECOMMISSIONING_PLAN = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  DECOMMISSIONING_PLAN as default
};
