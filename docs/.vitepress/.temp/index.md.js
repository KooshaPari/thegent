import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"","description":"","frontmatter":{"layout":"home","hero":{"name":"thegent","text":"AI Agent Governance & MCP Server","tagline":"Comprehensive agent lifecycle management and quality governance","actions":[{"theme":"brand","text":"Get Started","link":"/ARCHITECTURE_LAYERS.md"},{"theme":"alt","text":"View on GitHub","link":"https://github.com"}]},"features":[{"title":"Agent Governance","details":"Define agent personas, dispatch hooks, enforce quality gates"},{"title":"MCP Integration","details":"Expose agent capabilities via Model Context Protocol"},{"title":"Hook System","details":"Lifecycle hooks for pre/post tool execution"}]},"headers":[],"relativePath":"index.md","filePath":"index.md","lastUpdated":1771498270000}');
const _sfc_main = { name: "index.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h2 id="see-also" tabindex="-1">See also <a class="header-anchor" href="#see-also" aria-label="Permalink to &quot;See also&quot;">​</a></h2><ul><li><a href="./reference/WORK_STREAM.html">WORK_STREAM.md</a> — canonical backlog</li><li><a href="./plans/00-MASTER-INDEX.html">00-MASTER-INDEX.md</a> — plan index</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("index.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const index = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  index as default
};
