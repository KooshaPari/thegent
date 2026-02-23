import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"External Developer Docset","description":"","frontmatter":{},"headers":[],"relativePath":"docsets/developer/external/index.md","filePath":"docsets/developer/external/index.md","lastUpdated":1771577582000}');
const _sfc_main = { name: "docsets/developer/external/index.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="external-developer-docset" tabindex="-1">External Developer Docset <a class="header-anchor" href="#external-developer-docset" aria-label="Permalink to &quot;External Developer Docset&quot;">​</a></h1><p>For teams integrating thegent into their own projects and automations.</p><h2 id="primary-paths" tabindex="-1">Primary Paths <a class="header-anchor" href="#primary-paths" aria-label="Permalink to &quot;Primary Paths&quot;">​</a></h2><ol><li><a href="./integration-quickstart.html">Integration Quickstart</a></li><li><a href="./../../reference/">CLI Reference</a></li><li><a href="./../../guides/">Guides</a></li><li><a href="./../../api/">API and MCP docs</a></li></ol></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("docsets/developer/external/index.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const index = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  index as default
};
