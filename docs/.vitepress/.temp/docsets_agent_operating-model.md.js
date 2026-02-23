import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Agent Operating Model","description":"","frontmatter":{},"headers":[],"relativePath":"docsets/agent/operating-model.md","filePath":"docsets/agent/operating-model.md","lastUpdated":1771577582000}');
const _sfc_main = { name: "docsets/agent/operating-model.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="agent-operating-model" tabindex="-1">Agent Operating Model <a class="header-anchor" href="#agent-operating-model" aria-label="Permalink to &quot;Agent Operating Model&quot;">​</a></h1><h2 id="loop-structure" tabindex="-1">Loop Structure <a class="header-anchor" href="#loop-structure" aria-label="Permalink to &quot;Loop Structure&quot;">​</a></h2><ol><li>Intake and classify work</li><li>Route to harness/model lane</li><li>Execute with policy checks</li><li>Verify, audit, and record outcomes</li></ol><h2 id="delegation-controls" tabindex="-1">Delegation Controls <a class="header-anchor" href="#delegation-controls" aria-label="Permalink to &quot;Delegation Controls&quot;">​</a></h2><ul><li>Explicit task IDs</li><li>Run/session tracking</li><li>Failure/defer/paused states propagated to team coordination data</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("docsets/agent/operating-model.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const operatingModel = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  operatingModel as default
};
