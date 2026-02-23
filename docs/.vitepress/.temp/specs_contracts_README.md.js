import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Contracts Domain Technical Specification","description":"","frontmatter":{},"headers":[],"relativePath":"specs/contracts/README.md","filePath":"specs/contracts/README.md","lastUpdated":1771739999000}');
const _sfc_main = { name: "specs/contracts/README.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="contracts-domain-technical-specification" tabindex="-1">Contracts Domain Technical Specification <a class="header-anchor" href="#contracts-domain-technical-specification" aria-label="Permalink to &quot;Contracts Domain Technical Specification&quot;">​</a></h1><h2 id="overview" tabindex="-1">Overview <a class="header-anchor" href="#overview" aria-label="Permalink to &quot;Overview&quot;">​</a></h2><p>Contract management, capability registry, and conformance validation.</p><h2 id="components" tabindex="-1">Components <a class="header-anchor" href="#components" aria-label="Permalink to &quot;Components&quot;">​</a></h2><h3 id="contract-types" tabindex="-1">Contract Types <a class="header-anchor" href="#contract-types" aria-label="Permalink to &quot;Contract Types&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Type</th><th>Purpose</th><th>Files</th></tr></thead><tbody><tr><td>Capability</td><td>Feature registry</td><td><code>contracts/capability_registry.py</code></td></tr><tr><td>Policy</td><td>Rules engine</td><td><code>contracts/policy.py</code></td></tr><tr><td>Validation</td><td>Conformance</td><td><code>contracts/conformance.py</code></td></tr><tr><td>Migration</td><td>Schema evolution</td><td><code>contracts/migration.py</code></td></tr></tbody></table><h3 id="registry" tabindex="-1">Registry <a class="header-anchor" href="#registry" aria-label="Permalink to &quot;Registry&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Registry</th><th>Purpose</th></tr></thead><tbody><tr><td>Capability</td><td>Features</td></tr><tr><td>Policy</td><td>Rules</td></tr><tr><td>Market</td><td>Marketplace</td></tr></tbody></table><h2 id="conformance" tabindex="-1">Conformance <a class="header-anchor" href="#conformance" aria-label="Permalink to &quot;Conformance&quot;">​</a></h2><ul><li>Schema validation</li><li>Policy enforcement</li><li>Breaking change detection</li><li>Version compatibility</li></ul><h2 id="performance" tabindex="-1">Performance <a class="header-anchor" href="#performance" aria-label="Permalink to &quot;Performance&quot;">​</a></h2><table tabindex="0"><thead><tr><th>Metric</th><th>Target</th></tr></thead><tbody><tr><td>Validation</td><td>&lt;10ms</td></tr><tr><td>Schema check</td><td>&lt;5ms</td></tr><tr><td>Policy eval</td><td>&lt;1ms</td></tr></tbody></table></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("specs/contracts/README.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const README = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  README as default
};
