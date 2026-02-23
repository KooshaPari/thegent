import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Agent Operator Docset","description":"","frontmatter":{},"headers":[],"relativePath":"docsets/agent/index.md","filePath":"docsets/agent/index.md","lastUpdated":1771577582000}');
const _sfc_main = { name: "docsets/agent/index.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="agent-operator-docset" tabindex="-1">Agent Operator Docset <a class="header-anchor" href="#agent-operator-docset" aria-label="Permalink to &quot;Agent Operator Docset&quot;">​</a></h1><p>For teams running agent fleets, delegation, and governance-intensive workflows.</p><h2 id="operating-surfaces" tabindex="-1">Operating Surfaces <a class="header-anchor" href="#operating-surfaces" aria-label="Permalink to &quot;Operating Surfaces&quot;">​</a></h2><ol><li><a href="./operating-model.html">Operating Model</a></li><li>Agent routing and harness strategy</li><li>Policy and HITL governance</li><li>Audit and traceability controls</li></ol></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("docsets/agent/index.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const index = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  index as default
};
