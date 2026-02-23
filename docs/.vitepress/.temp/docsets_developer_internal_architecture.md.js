import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Internal Architecture Guide","description":"","frontmatter":{},"headers":[],"relativePath":"docsets/developer/internal/architecture.md","filePath":"docsets/developer/internal/architecture.md","lastUpdated":1771577582000}');
const _sfc_main = { name: "docsets/developer/internal/architecture.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="internal-architecture-guide" tabindex="-1">Internal Architecture Guide <a class="header-anchor" href="#internal-architecture-guide" aria-label="Permalink to &quot;Internal Architecture Guide&quot;">​</a></h1><h2 id="core-layers" tabindex="-1">Core Layers <a class="header-anchor" href="#core-layers" aria-label="Permalink to &quot;Core Layers&quot;">​</a></h2><ol><li>CLI + entrypoints (<code>src/thegent/main.py</code>, <code>src/thegent/cli/</code>)</li><li>Governance + policy (<code>src/thegent/governance/</code>)</li><li>Orchestration + execution (<code>src/thegent/orchestration/</code>, <code>src/thegent/execution.py</code>)</li><li>Performance accelerators (<code>crates/thegent-*</code>)</li><li>Hooks and lifecycle automation (<code>hooks/</code>)</li></ol><h2 id="engineering-priorities" tabindex="-1">Engineering Priorities <a class="header-anchor" href="#engineering-priorities" aria-label="Permalink to &quot;Engineering Priorities&quot;">​</a></h2><ul><li>Deterministic behavior over implicit fallback behavior.</li><li>Explicit governance checks for critical pathways.</li><li>Rust acceleration for hot paths and shell shim dispatch.</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("docsets/developer/internal/architecture.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const architecture = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  architecture as default
};
