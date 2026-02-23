import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"VitePress Examples","description":"","frontmatter":{},"headers":[],"relativePath":"examples/README.md","filePath":"examples/README.md","lastUpdated":1771498270000}');
const _sfc_main = { name: "examples/README.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="vitepress-examples" tabindex="-1">VitePress Examples <a class="header-anchor" href="#vitepress-examples" aria-label="Permalink to &quot;VitePress Examples&quot;">​</a></h1><p>This directory contains example pages demonstrating VitePress rich documentation features.</p><h2 id="examples" tabindex="-1">Examples <a class="header-anchor" href="#examples" aria-label="Permalink to &quot;Examples&quot;">​</a></h2><ul><li><a href="./mermaid-example.html">mermaid-example.md</a> - Mermaid diagram examples</li><li><a href="./code-playground-example.html">code-playground-example.md</a> - CodePlayground component examples</li><li><a href="./demo-gif-example.html">demo-gif-example.md</a> - DemoGif component examples</li><li><a href="./math-emoji-example.html">math-emoji-example.md</a> - Math rendering and emoji support</li><li><a href="./tooltip-example.html">tooltip-example.md</a> - Tooltip component usage</li></ul><h2 id="usage" tabindex="-1">Usage <a class="header-anchor" href="#usage" aria-label="Permalink to &quot;Usage&quot;">​</a></h2><p>These examples can be referenced when creating new documentation pages. They demonstrate:</p><ul><li>How to use Mermaid diagrams</li><li>How to embed CodePlayground components</li><li>How to display demo GIFs</li><li>How to use math equations (KaTeX)</li><li>How to use emojis</li><li>How to add tooltips</li><li>Best practices for documentation</li></ul><hr><p>undefined<strong>See Also</strong>: <a href="./../guides/VITEPRESS_USAGE_GUIDE.html">VITEPRESS_USAGE_GUIDE.md</a></p></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("examples/README.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const README = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  README as default
};
