import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Verification Domain Technical Specification","description":"","frontmatter":{},"headers":[],"relativePath":"specs/verification/README.md","filePath":"specs/verification/README.md","lastUpdated":1771739999000}');
const _sfc_main = { name: "specs/verification/README.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="verification-domain-technical-specification" tabindex="-1">Verification Domain Technical Specification <a class="header-anchor" href="#verification-domain-technical-specification" aria-label="Permalink to &quot;Verification Domain Technical Specification&quot;">​</a></h1><h2 id="overview" tabindex="-1">Overview <a class="header-anchor" href="#overview" aria-label="Permalink to &quot;Overview&quot;">​</a></h2><p>Formal verification, safety checking, and proof generation.</p><h2 id="components" tabindex="-1">Components <a class="header-anchor" href="#components" aria-label="Permalink to &quot;Components&quot;">​</a></h2><h3 id="verification-types" tabindex="-1">Verification Types <a class="header-anchor" href="#verification-types" aria-label="Permalink to &quot;Verification Types&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Type</th><th>Purpose</th><th>Files</th></tr></thead><tbody><tr><td>Symbolic</td><td>Formal methods</td><td><code>verification/symbolic.py</code></td></tr><tr><td>Formal schema</td><td>Type checking</td><td><code>verification/schema_formal.py</code></td></tr><tr><td>Ethics</td><td>Safety</td><td><code>verification/ethics_proof.py</code></td></tr><tr><td>ZKP</td><td>Proofs</td><td><code>verification/zkp.py</code></td></tr><tr><td>Safety</td><td>Tool safety</td><td><code>verification/tool_safety.py</code></td></tr><tr><td>Liveness</td><td>Availability</td><td><code>verification/liveness.py</code></td></tr></tbody></table><h3 id="trust-safety" tabindex="-1">Trust &amp; Safety <a class="header-anchor" href="#trust-safety" aria-label="Permalink to &quot;Trust &amp; Safety&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Component</th><th>Purpose</th></tr></thead><tbody><tr><td>Proof carrying</td><td>Code proofs</td></tr><tr><td>Traceability</td><td>Lineage</td></tr><tr><td>Omega safety</td><td>Safety bounds</td></tr></tbody></table><h2 id="verification-levels" tabindex="-1">Verification Levels <a class="header-anchor" href="#verification-levels" aria-label="Permalink to &quot;Verification Levels&quot;">​</a></h2><table tabindex="0"><thead><tr><th>Level</th><th>Checks</th></tr></thead><tbody><tr><td>Syntax</td><td>Parse errors</td></tr><tr><td>Type</td><td>Type safety</td></tr><tr><td>Semantic</td><td>Logic</td></tr><tr><td>Formal</td><td>Proofs</td></tr></tbody></table><h2 id="performance" tabindex="-1">Performance <a class="header-anchor" href="#performance" aria-label="Permalink to &quot;Performance&quot;">​</a></h2><table tabindex="0"><thead><tr><th>Metric</th><th>Target</th></tr></thead><tbody><tr><td>Syntax check</td><td>&lt;10ms</td></tr><tr><td>Type check</td><td>&lt;100ms</td></tr><tr><td>Formal proof</td><td>&lt;10s</td></tr></tbody></table></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("specs/verification/README.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const README = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  README as default
};
