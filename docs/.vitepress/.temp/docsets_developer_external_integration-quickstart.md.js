import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Integration Quickstart","description":"","frontmatter":{},"headers":[],"relativePath":"docsets/developer/external/integration-quickstart.md","filePath":"docsets/developer/external/integration-quickstart.md","lastUpdated":1771577582000}');
const _sfc_main = { name: "docsets/developer/external/integration-quickstart.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="integration-quickstart" tabindex="-1">Integration Quickstart <a class="header-anchor" href="#integration-quickstart" aria-label="Permalink to &quot;Integration Quickstart&quot;">​</a></h1><h2 id="typical-integration-flow" tabindex="-1">Typical Integration Flow <a class="header-anchor" href="#typical-integration-flow" aria-label="Permalink to &quot;Typical Integration Flow&quot;">​</a></h2><ol><li>Install <code>thegent</code> and run <code>thegent doctor</code>.</li><li>Configure providers using <code>thegent setup</code>.</li><li>Use foreground tasks with <code>thegent run</code> and scheduled flows with <code>thegent plan loop</code>.</li><li>Integrate MCP workflows via <code>thegent mcp</code> commands.</li></ol><h2 id="recommended-validation" tabindex="-1">Recommended Validation <a class="header-anchor" href="#recommended-validation" aria-label="Permalink to &quot;Recommended Validation&quot;">​</a></h2><ul><li><code>thegent doctor</code></li><li><code>thegent ps</code></li><li><code>thegent plan do-next</code></li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("docsets/developer/external/integration-quickstart.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const integrationQuickstart = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  integrationQuickstart as default
};
