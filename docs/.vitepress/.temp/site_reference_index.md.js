import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Reference","description":"","frontmatter":{},"headers":[],"relativePath":"site/reference/index.md","filePath":"site/reference/index.md","lastUpdated":1771678191000}');
const _sfc_main = { name: "site/reference/index.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="reference" tabindex="-1">Reference <a class="header-anchor" href="#reference" aria-label="Permalink to &quot;Reference&quot;">​</a></h1><p>Reference material for routing behavior, configuration keys, and operational defaults.</p><h2 id="reference-pages" tabindex="-1">Reference Pages <a class="header-anchor" href="#reference-pages" aria-label="Permalink to &quot;Reference Pages&quot;">​</a></h2><ul><li><a href="./routing.html">Routing</a></li><li><a href="./configuration.html">Configuration</a></li></ul><p>Use the <a href="/guide/">Guide</a> for step-by-step setup and usage.</p></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("site/reference/index.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const index = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  index as default
};
