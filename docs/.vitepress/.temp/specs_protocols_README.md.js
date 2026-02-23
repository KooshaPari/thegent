import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Protocols & Adapters Domain Technical Specification","description":"","frontmatter":{},"headers":[],"relativePath":"specs/protocols/README.md","filePath":"specs/protocols/README.md","lastUpdated":1771739999000}');
const _sfc_main = { name: "specs/protocols/README.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="protocols-adapters-domain-technical-specification" tabindex="-1">Protocols &amp; Adapters Domain Technical Specification <a class="header-anchor" href="#protocols-adapters-domain-technical-specification" aria-label="Permalink to &quot;Protocols &amp; Adapters Domain Technical Specification&quot;">​</a></h1><h2 id="overview" tabindex="-1">Overview <a class="header-anchor" href="#overview" aria-label="Permalink to &quot;Overview&quot;">​</a></h2><p>Multi-protocol support and adapter implementations.</p><h2 id="protocols" tabindex="-1">Protocols <a class="header-anchor" href="#protocols" aria-label="Permalink to &quot;Protocols&quot;">​</a></h2><table tabindex="0"><thead><tr><th>Protocol</th><th>Purpose</th><th>Files</th></tr></thead><tbody><tr><td>MCP</td><td>Tool exposure</td><td><code>mcp/</code></td></tr><tr><td>ACP</td><td>Agent communication</td><td><code>adapters/acp_*.py</code></td></tr><tr><td>A2A</td><td>Agent-to-agent</td><td><code>protocols/a2a.py</code></td></tr><tr><td>JSON-RPC</td><td>RPC</td><td><code>protocols/jsonrpc_agent_server.py</code></td></tr></tbody></table><h3 id="mcp-tools" tabindex="-1">MCP Tools <a class="header-anchor" href="#mcp-tools" aria-label="Permalink to &quot;MCP Tools&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Category</th><th>Count</th><th>Files</th></tr></thead><tbody><tr><td>Session</td><td>50+</td><td><code>tools_sessions.py</code></td></tr><tr><td>Terminal</td><td>20+</td><td><code>tools_terminal.py</code></td></tr><tr><td>Governance</td><td>15+</td><td><code>tools_governance.py</code></td></tr></tbody></table><h3 id="adapters" tabindex="-1">Adapters <a class="header-anchor" href="#adapters" aria-label="Permalink to &quot;Adapters&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Adapter</th><th>Protocol</th><th>Purpose</th></tr></thead><tbody><tr><td>ACP Server</td><td>ACP</td><td>Server</td></tr><tr><td>ACP Client</td><td>ACP</td><td>Client</td></tr><tr><td>MCP Bridge</td><td>MCP ↔ ACP</td><td>Bridge</td></tr></tbody></table><h2 id="features" tabindex="-1">Features <a class="header-anchor" href="#features" aria-label="Permalink to &quot;Features&quot;">​</a></h2><ul><li>Protocol negotiation</li><li>Fallback chains</li><li>Version negotiation</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("specs/protocols/README.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const README = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  README as default
};
