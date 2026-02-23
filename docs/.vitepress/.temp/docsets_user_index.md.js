import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Technical User Docset","description":"","frontmatter":{},"headers":[],"relativePath":"docsets/user/index.md","filePath":"docsets/user/index.md","lastUpdated":1771577582000}');
const _sfc_main = { name: "docsets/user/index.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="technical-user-docset" tabindex="-1">Technical User Docset <a class="header-anchor" href="#technical-user-docset" aria-label="Permalink to &quot;Technical User Docset&quot;">​</a></h1><p>For engineers and operators using thegent day-to-day.</p><h2 id="core-workflows" tabindex="-1">Core Workflows <a class="header-anchor" href="#core-workflows" aria-label="Permalink to &quot;Core Workflows&quot;">​</a></h2><ol><li><a href="./quickstart.html">Quickstart</a></li><li>Session management (<code>thegent run</code>, <code>bg</code>, <code>ps</code>, <code>logs</code>, <code>stop</code>)</li><li>Planning lifecycle (<code>thegent plan do-next</code>, <code>plan loop</code>)</li><li>Governance checks (<code>thegent doctor</code>, audit commands)</li></ol></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("docsets/user/index.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const index = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  index as default
};
