import { resolveComponent, withCtx, createTextVNode, useSSRContext } from "vue";
import { ssrRenderAttrs, ssrRenderComponent, ssrRenderStyle } from "vue/server-renderer";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Tooltip Component Examples","description":"","frontmatter":{},"headers":[],"relativePath":"examples/tooltip-example.md","filePath":"examples/tooltip-example.md","lastUpdated":1771498270000}');
const _sfc_main = { name: "examples/tooltip-example.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  const _component_Tooltip = resolveComponent("Tooltip");
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="tooltip-component-examples" tabindex="-1">Tooltip Component Examples <a class="header-anchor" href="#tooltip-component-examples" aria-label="Permalink to &quot;Tooltip Component Examples&quot;">​</a></h1><p>This page demonstrates the Tooltip component usage.</p><hr><h2 id="basic-usage" tabindex="-1">Basic Usage <a class="header-anchor" href="#basic-usage" aria-label="Permalink to &quot;Basic Usage&quot;">​</a></h2><p>Hover over this text: `);
  _push(ssrRenderComponent(_component_Tooltip, { content: "This is a helpful tooltip!" }, {
    default: withCtx((_, _push2, _parent2, _scopeId) => {
      if (_push2) {
        _push2(`tooltip example`);
      } else {
        return [
          createTextVNode("tooltip example")
        ];
      }
    }),
    _: 1
  }, _parent));
  _push(`</p><hr><h2 id="different-positions" tabindex="-1">Different Positions <a class="header-anchor" href="#different-positions" aria-label="Permalink to &quot;Different Positions&quot;">​</a></h2><ul><li>`);
  _push(ssrRenderComponent(_component_Tooltip, {
    content: "Top tooltip",
    position: "top"
  }, {
    default: withCtx((_, _push2, _parent2, _scopeId) => {
      if (_push2) {
        _push2(`Top`);
      } else {
        return [
          createTextVNode("Top")
        ];
      }
    }),
    _: 1
  }, _parent));
  _push(`</li><li>`);
  _push(ssrRenderComponent(_component_Tooltip, {
    content: "Bottom tooltip",
    position: "bottom"
  }, {
    default: withCtx((_, _push2, _parent2, _scopeId) => {
      if (_push2) {
        _push2(`Bottom`);
      } else {
        return [
          createTextVNode("Bottom")
        ];
      }
    }),
    _: 1
  }, _parent));
  _push(`</li><li>`);
  _push(ssrRenderComponent(_component_Tooltip, {
    content: "Left tooltip",
    position: "left"
  }, {
    default: withCtx((_, _push2, _parent2, _scopeId) => {
      if (_push2) {
        _push2(`Left`);
      } else {
        return [
          createTextVNode("Left")
        ];
      }
    }),
    _: 1
  }, _parent));
  _push(`</li><li>`);
  _push(ssrRenderComponent(_component_Tooltip, {
    content: "Right tooltip",
    position: "right"
  }, {
    default: withCtx((_, _push2, _parent2, _scopeId) => {
      if (_push2) {
        _push2(`Right`);
      } else {
        return [
          createTextVNode("Right")
        ];
      }
    }),
    _: 1
  }, _parent));
  _push(`</li></ul><hr><h2 id="technical-terms" tabindex="-1">Technical Terms <a class="header-anchor" href="#technical-terms" aria-label="Permalink to &quot;Technical Terms&quot;">​</a></h2><ul><li>`);
  _push(ssrRenderComponent(_component_Tooltip, { content: "Application Programming Interface" }, {
    default: withCtx((_, _push2, _parent2, _scopeId) => {
      if (_push2) {
        _push2(`API`);
      } else {
        return [
          createTextVNode("API")
        ];
      }
    }),
    _: 1
  }, _parent));
  _push(`</li><li>`);
  _push(ssrRenderComponent(_component_Tooltip, { content: "Model Context Protocol" }, {
    default: withCtx((_, _push2, _parent2, _scopeId) => {
      if (_push2) {
        _push2(`MCP`);
      } else {
        return [
          createTextVNode("MCP")
        ];
      }
    }),
    _: 1
  }, _parent));
  _push(`</li><li>`);
  _push(ssrRenderComponent(_component_Tooltip, { content: "Representational State Transfer" }, {
    default: withCtx((_, _push2, _parent2, _scopeId) => {
      if (_push2) {
        _push2(`REST`);
      } else {
        return [
          createTextVNode("REST")
        ];
      }
    }),
    _: 1
  }, _parent));
  _push(`</li><li>`);
  _push(ssrRenderComponent(_component_Tooltip, { content: "JavaScript Object Notation" }, {
    default: withCtx((_, _push2, _parent2, _scopeId) => {
      if (_push2) {
        _push2(`JSON`);
      } else {
        return [
          createTextVNode("JSON")
        ];
      }
    }),
    _: 1
  }, _parent));
  _push(`</li></ul><hr><h2 id="code-examples" tabindex="-1">Code Examples <a class="header-anchor" href="#code-examples" aria-label="Permalink to &quot;Code Examples&quot;">​</a></h2><div class="language-python vp-adaptive-theme line-numbers-mode"><button title="Copy Code" class="copy"></button><span class="lang">python</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="${ssrRenderStyle({ "--shiki-light": "#6A737D", "--shiki-dark": "#6A737D" })}"># Hover over the function name</span></span>
<span class="line"><span style="${ssrRenderStyle({ "--shiki-light": "#D73A49", "--shiki-dark": "#F97583" })}">def</span><span style="${ssrRenderStyle({ "--shiki-light": "#D73A49", "--shiki-dark": "#F97583" })}"> &lt;</span><span style="${ssrRenderStyle({ "--shiki-light": "#24292E", "--shiki-dark": "#E1E4E8" })}">Tooltip content</span><span style="${ssrRenderStyle({ "--shiki-light": "#D73A49", "--shiki-dark": "#F97583" })}">=</span><span style="${ssrRenderStyle({ "--shiki-light": "#032F62", "--shiki-dark": "#9ECBFF" })}">&quot;This function calculates the sum of two numbers&quot;</span><span style="${ssrRenderStyle({ "--shiki-light": "#D73A49", "--shiki-dark": "#F97583" })}">&gt;</span><span style="${ssrRenderStyle({ "--shiki-light": "#24292E", "--shiki-dark": "#E1E4E8" })}">add</span><span style="${ssrRenderStyle({ "--shiki-light": "#D73A49", "--shiki-dark": "#F97583" })}">&lt;/</span><span style="${ssrRenderStyle({ "--shiki-light": "#24292E", "--shiki-dark": "#E1E4E8" })}">Tooltip</span><span style="${ssrRenderStyle({ "--shiki-light": "#D73A49", "--shiki-dark": "#F97583" })}">&gt;</span><span style="${ssrRenderStyle({ "--shiki-light": "#24292E", "--shiki-dark": "#E1E4E8" })}">(a: </span><span style="${ssrRenderStyle({ "--shiki-light": "#005CC5", "--shiki-dark": "#79B8FF" })}">int</span><span style="${ssrRenderStyle({ "--shiki-light": "#24292E", "--shiki-dark": "#E1E4E8" })}">, b: </span><span style="${ssrRenderStyle({ "--shiki-light": "#005CC5", "--shiki-dark": "#79B8FF" })}">int</span><span style="${ssrRenderStyle({ "--shiki-light": "#24292E", "--shiki-dark": "#E1E4E8" })}">) </span><span style="${ssrRenderStyle({ "--shiki-light": "#B31D28", "--shiki-light-font-style": "italic", "--shiki-dark": "#FDAEB7", "--shiki-dark-font-style": "italic" })}">-&gt;</span><span style="${ssrRenderStyle({ "--shiki-light": "#005CC5", "--shiki-dark": "#79B8FF" })}"> int</span><span style="${ssrRenderStyle({ "--shiki-light": "#24292E", "--shiki-dark": "#E1E4E8" })}">:</span></span>
<span class="line"><span style="${ssrRenderStyle({ "--shiki-light": "#D73A49", "--shiki-dark": "#F97583" })}">    return</span><span style="${ssrRenderStyle({ "--shiki-light": "#24292E", "--shiki-dark": "#E1E4E8" })}"> a </span><span style="${ssrRenderStyle({ "--shiki-light": "#D73A49", "--shiki-dark": "#F97583" })}">+</span><span style="${ssrRenderStyle({ "--shiki-light": "#24292E", "--shiki-dark": "#E1E4E8" })}"> b</span></span></code></pre><div class="line-numbers-wrapper" aria-hidden="true"><span class="line-number">1</span><br><span class="line-number">2</span><br><span class="line-number">3</span><br></div></div><hr><h2 id="see-also" tabindex="-1">See Also <a class="header-anchor" href="#see-also" aria-label="Permalink to &quot;See Also&quot;">​</a></h2><ul><li><a href="./math-emoji-example.html">Math &amp; Emoji Examples</a> - Math and emoji support</li><li><a href="./../guides/VITEPRESS_USAGE_GUIDE.html">VitePress Usage Guide</a> - Complete guide</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("examples/tooltip-example.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const tooltipExample = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  tooltipExample as default
};
