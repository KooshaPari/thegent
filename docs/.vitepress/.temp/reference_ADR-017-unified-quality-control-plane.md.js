import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"ADR-017: Unified Quality Control Plane","description":"","frontmatter":{},"headers":[],"relativePath":"reference/ADR-017-unified-quality-control-plane.md","filePath":"reference/ADR-017-unified-quality-control-plane.md","lastUpdated":1771803666000}');
const _sfc_main = { name: "reference/ADR-017-unified-quality-control-plane.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="adr-017-unified-quality-control-plane" tabindex="-1">ADR-017: Unified Quality Control Plane <a class="header-anchor" href="#adr-017-unified-quality-control-plane" aria-label="Permalink to &quot;ADR-017: Unified Quality Control Plane&quot;">​</a></h1><ul><li>Status: Accepted</li><li>Date: 2026-02-22</li><li>Owner: quality-platform</li></ul><h2 id="context" tabindex="-1">Context <a class="header-anchor" href="#context" aria-label="Permalink to &quot;Context&quot;">​</a></h2><p><code>thegent</code> now has a growing set of quality signals:</p><ul><li>hook result envelopes (<code>quality-gate</code>, <code>security-pipeline</code>)</li><li>SARIF export bridge</li><li>generated-code anti-pattern checker</li><li>mutation/perf pilot artifacts</li></ul><p>Without one control-plane decision, policy behavior drifts between local lanes and CI.</p><h2 id="decision" tabindex="-1">Decision <a class="header-anchor" href="#decision" aria-label="Permalink to &quot;Decision&quot;">​</a></h2><p>Use <strong>GitHub+SARIF-native</strong> as the default control plane for unified quality in 2026.</p><ul><li>Canonical transport: SARIF + JSON side artifacts</li><li>Canonical policy input: contract-backed artifacts under <code>artifacts/quality</code> and <code>artifacts/hooks</code></li><li>Sonar remains optional as a downstream adapter, not source-of-truth</li></ul><h2 id="rationale" tabindex="-1">Rationale <a class="header-anchor" href="#rationale" aria-label="Permalink to &quot;Rationale&quot;">​</a></h2><ul><li>Lowest integration friction with existing GitHub checks and code-scanning workflows.</li><li>Works with multi-tool and custom checker outputs uniformly.</li><li>Keeps internal contracts explicit and portable, independent of vendor lock-in.</li></ul><h2 id="consequences" tabindex="-1">Consequences <a class="header-anchor" href="#consequences" aria-label="Permalink to &quot;Consequences&quot;">​</a></h2><ul><li>Every new checker must define: <ul><li>JSON artifact contract</li><li>optional SARIF adapter</li><li>deterministic task entry in <code>Taskfile.yml</code></li></ul></li><li>CI promotion gates will consume contract-validated artifacts.</li><li>Future Sonar integration should ingest from these artifacts, not bypass them.</li></ul><h2 id="rollout" tabindex="-1">Rollout <a class="header-anchor" href="#rollout" aria-label="Permalink to &quot;Rollout&quot;">​</a></h2><ol><li>Enforce control-plane policy contract in quality lanes.</li><li>Aggregate hook/checker artifacts into one quality summary artifact.</li><li>Promote non-blocking pilots to required checks after stability windows.</li></ol></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("reference/ADR-017-unified-quality-control-plane.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const ADR017UnifiedQualityControlPlane = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  ADR017UnifiedQualityControlPlane as default
};
