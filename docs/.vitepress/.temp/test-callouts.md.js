import { resolveComponent, withCtx, createTextVNode, useSSRContext } from "vue";
import { ssrRenderAttrs, ssrRenderComponent } from "vue/server-renderer";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Test Callouts","description":"","frontmatter":{},"headers":[],"relativePath":"test-callouts.md","filePath":"test-callouts.md","lastUpdated":1771753292000}');
const _sfc_main = { name: "test-callouts.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  const _component_Callout = resolveComponent("Callout");
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="test-callouts" tabindex="-1">Test Callouts <a class="header-anchor" href="#test-callouts" aria-label="Permalink to &quot;Test Callouts&quot;">​</a></h1>`);
  _push(ssrRenderComponent(_component_Callout, { type: "tip" }, {
    default: withCtx((_, _push2, _parent2, _scopeId) => {
      if (_push2) {
        _push2(` This is a helpful tip! `);
      } else {
        return [
          createTextVNode(" This is a helpful tip! ")
        ];
      }
    }),
    _: 1
  }, _parent));
  _push(ssrRenderComponent(_component_Callout, { type: "warning" }, {
    default: withCtx((_, _push2, _parent2, _scopeId) => {
      if (_push2) {
        _push2(` Be careful with this operation. `);
      } else {
        return [
          createTextVNode(" Be careful with this operation. ")
        ];
      }
    }),
    _: 1
  }, _parent));
  _push(ssrRenderComponent(_component_Callout, { type: "danger" }, {
    default: withCtx((_, _push2, _parent2, _scopeId) => {
      if (_push2) {
        _push2(` This action cannot be undone! `);
      } else {
        return [
          createTextVNode(" This action cannot be undone! ")
        ];
      }
    }),
    _: 1
  }, _parent));
  _push(ssrRenderComponent(_component_Callout, { type: "note" }, {
    default: withCtx((_, _push2, _parent2, _scopeId) => {
      if (_push2) {
        _push2(` This is just an informational note. `);
      } else {
        return [
          createTextVNode(" This is just an informational note. ")
        ];
      }
    }),
    _: 1
  }, _parent));
  _push(`<hr><h2 id="see-also" tabindex="-1">See also <a class="header-anchor" href="#see-also" aria-label="Permalink to &quot;See also&quot;">​</a></h2><ul><li><a href="./reference/WORK_STREAM.html">WORK_STREAM.md</a> — canonical backlog</li><li><a href="./plans/00-MASTER-INDEX.html">00-MASTER-INDEX.md</a> — plan index</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("test-callouts.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const testCallouts = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  testCallouts as default
};
