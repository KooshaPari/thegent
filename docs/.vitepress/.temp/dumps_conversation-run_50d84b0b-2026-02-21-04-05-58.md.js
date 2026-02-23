import { resolveComponent, withCtx, createTextVNode, useSSRContext } from "vue";
import { ssrRenderAttrs, ssrRenderComponent } from "vue/server-renderer";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"","description":"","frontmatter":{},"headers":[],"relativePath":"dumps/conversation-run_50d84b0b-2026-02-21-04-05-58.md","filePath":"dumps/conversation-run_50d84b0b-2026-02-21-04-05-58.md","lastUpdated":1771753292000}');
const _sfc_main = { name: "dumps/conversation-run_50d84b0b-2026-02-21-04-05-58.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  const _component_STATUS = resolveComponent("STATUS");
  _push(`<div${ssrRenderAttrs(_attrs)}><p>{&#39;stdout&#39;: &#39;`);
  _push(ssrRenderComponent(_component_STATUS, null, {
    default: withCtx((_, _push2, _parent2, _scopeId) => {
      if (_push2) {
        _push2(`completed`);
      } else {
        return [
          createTextVNode("completed")
        ];
      }
    }),
    _: 1
  }, _parent));
  _push(`&#39;, &#39;stderr&#39;: &#39;&#39;, &#39;exit_code&#39;: 0}</p></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("dumps/conversation-run_50d84b0b-2026-02-21-04-05-58.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const conversationRun_50d84b0b20260221040558 = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  conversationRun_50d84b0b20260221040558 as default
};
