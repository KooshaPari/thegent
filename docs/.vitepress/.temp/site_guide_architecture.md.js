import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Architecture","description":"","frontmatter":{},"headers":[],"relativePath":"site/guide/architecture.md","filePath":"site/guide/architecture.md","lastUpdated":1771678191000}');
const _sfc_main = { name: "site/guide/architecture.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="architecture" tabindex="-1">Architecture <a class="header-anchor" href="#architecture" aria-label="Permalink to &quot;Architecture&quot;">​</a></h1><p><code>thegent</code> is an orchestration runtime with three primary layers: execution, governance, and interface.</p><h2 id="layer-overview" tabindex="-1">Layer Overview <a class="header-anchor" href="#layer-overview" aria-label="Permalink to &quot;Layer Overview&quot;">​</a></h2><table tabindex="0"><thead><tr><th>Layer</th><th>Responsibility</th><th>Typical artifacts</th></tr></thead><tbody><tr><td>Execution</td><td>Run agent personas and workflows</td><td><code>thegent run</code>, <code>thegent bg</code>, loop commands</td></tr><tr><td>Governance</td><td>Apply policy, quality, and budget controls</td><td>contracts, QA hooks, policy engine</td></tr><tr><td>Interface</td><td>Expose CLI + MCP tools</td><td>CLI commands, MCP server resources/tools</td></tr></tbody></table><h2 id="runtime-flow" tabindex="-1">Runtime Flow <a class="header-anchor" href="#runtime-flow" aria-label="Permalink to &quot;Runtime Flow&quot;">​</a></h2><ol><li>A command starts an agent session.</li><li>Hook dispatchers run pre/post checks.</li><li>Policy checks enforce constraints (cost, quality, safety).</li><li>Outputs and status are persisted for later continuation.</li></ol><h2 id="practical-design-patterns" tabindex="-1">Practical Design Patterns <a class="header-anchor" href="#practical-design-patterns" aria-label="Permalink to &quot;Practical Design Patterns&quot;">​</a></h2><ul><li>Keep hooks thin; move shared logic into reusable libraries.</li><li>Keep policies data-driven in contracts, not hardcoded in command handlers.</li><li>Prefer explicit failures over hidden fallback behavior.</li></ul><h2 id="where-to-extend" tabindex="-1">Where To Extend <a class="header-anchor" href="#where-to-extend" aria-label="Permalink to &quot;Where To Extend&quot;">​</a></h2><ul><li>Add new persona: <code>agents/&lt;name&gt;.md</code></li><li>Add new hook: <code>hooks/&lt;event&gt;-&lt;name&gt;.sh</code></li><li>Add new governance policy: <code>contracts/&lt;policy&gt;.json</code></li><li>Add new CLI command: <code>commands/&lt;command&gt;/</code></li></ul><p>Use <a href="/reference/configuration.html">Reference Configuration</a> before changing environment defaults.</p></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("site/guide/architecture.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const architecture = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  architecture as default
};
