import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Internal Developer Docset","description":"","frontmatter":{},"headers":[],"relativePath":"docsets/developer/internal/index.md","filePath":"docsets/developer/internal/index.md","lastUpdated":1771577582000}');
const _sfc_main = { name: "docsets/developer/internal/index.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="internal-developer-docset" tabindex="-1">Internal Developer Docset <a class="header-anchor" href="#internal-developer-docset" aria-label="Permalink to &quot;Internal Developer Docset&quot;">​</a></h1><p>For maintainers building and evolving thegent internals.</p><h2 id="start-here" tabindex="-1">Start Here <a class="header-anchor" href="#start-here" aria-label="Permalink to &quot;Start Here&quot;">​</a></h2><ol><li><a href="./architecture.html">System Architecture</a></li><li><a href="./../../architecture/">Runtime and Orchestration</a></li><li><a href="./../../governance/">Governance Modules</a></li><li><a href="./../../plans/">Operational Plans</a></li></ol><h2 id="source-anchors" tabindex="-1">Source Anchors <a class="header-anchor" href="#source-anchors" aria-label="Permalink to &quot;Source Anchors&quot;">​</a></h2><ul><li><code>src/thegent/</code></li><li><code>crates/</code></li><li><code>hooks/</code></li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("docsets/developer/internal/index.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const index = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  index as default
};
