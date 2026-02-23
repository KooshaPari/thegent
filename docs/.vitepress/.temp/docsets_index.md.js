import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Docsets","description":"","frontmatter":{},"headers":[],"relativePath":"docsets/index.md","filePath":"docsets/index.md","lastUpdated":1771577582000}');
const _sfc_main = { name: "docsets/index.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="docsets" tabindex="-1">Docsets <a class="header-anchor" href="#docsets" aria-label="Permalink to &quot;Docsets&quot;">​</a></h1><p>Purpose-built documentation sets for different technical audiences.</p><h2 id="developer" tabindex="-1">Developer <a class="header-anchor" href="#developer" aria-label="Permalink to &quot;Developer&quot;">​</a></h2><ul><li><a href="./developer/internal/">Internal Developer Docset</a></li><li><a href="./developer/external/">External Developer Docset</a></li></ul><h2 id="user" tabindex="-1">User <a class="header-anchor" href="#user" aria-label="Permalink to &quot;User&quot;">​</a></h2><ul><li><a href="./user/">Technical User Docset</a></li></ul><h2 id="agent" tabindex="-1">Agent <a class="header-anchor" href="#agent" aria-label="Permalink to &quot;Agent&quot;">​</a></h2><ul><li><a href="./agent/">Agent Operator Docset</a></li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("docsets/index.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const index = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  index as default
};
