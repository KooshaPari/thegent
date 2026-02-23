import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"","description":"","frontmatter":{"layout":"home","hero":{"name":"thegent","text":"AI Agent Orchestration & Governance","tagline":"Production CLI for running autonomous agent workflows with policy, quality, and cost controls built in.","actions":[{"theme":"brand","text":"Get Started","link":"/guide/getting-started"},{"theme":"alt","text":"Operations","link":"/operations/"},{"theme":"alt","text":"View on GitHub","link":"https://github.com/kooshapari/thegent"}]},"features":[{"icon":"⚡","title":"Fast Runtime","details":"Optimized command path and runtime startup for daily agent workflows."},{"icon":"🔒","title":"Governance by Default","details":"Policy and quality controls help keep autonomous work bounded and auditable."},{"icon":"🌐","title":"Provider Routing","details":"Route across Claude, OpenAI/Codex, Gemini, and proxy-backed providers."},{"icon":"🧰","title":"MCP Native","details":"First-class MCP tooling and server support for agent ecosystems."},{"icon":"📋","title":"Workstream-Aware","details":"Built-in planning commands for prioritizing and executing queued work."},{"icon":"📚","title":"Structured Docs IA","details":"Clear sections for Guide, Operations, Reference, and API."}]},"headers":[],"relativePath":"site/index.md","filePath":"site/index.md","lastUpdated":1771678191000}');
const _sfc_main = { name: "site/index.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h2 id="documentation-map" tabindex="-1">Documentation Map <a class="header-anchor" href="#documentation-map" aria-label="Permalink to &quot;Documentation Map&quot;">​</a></h2><ul><li><a href="/guide/">Guide</a> for setup and daily usage.</li><li><a href="/operations/">Operations</a> for troubleshooting and runbooks.</li><li><a href="/reference/">Reference</a> for routing/config details.</li><li><a href="/api/">API</a> for generated and curated API docs.</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("site/index.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const index = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  index as default
};
