import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"thegent Quick Reference","description":"","frontmatter":{},"headers":[],"relativePath":"guides/QUICK_REFERENCE.md","filePath":"guides/QUICK_REFERENCE.md","lastUpdated":1771558125000}');
const _sfc_main = { name: "guides/QUICK_REFERENCE.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="thegent-quick-reference" tabindex="-1">thegent Quick Reference <a class="header-anchor" href="#thegent-quick-reference" aria-label="Permalink to &quot;thegent Quick Reference&quot;">​</a></h1><p>Top commands and common workflows for <code>thegent</code>.</p><hr><h2 id="🚀-common-tasks" tabindex="-1">🚀 Common Tasks <a class="header-anchor" href="#🚀-common-tasks" aria-label="Permalink to &quot;🚀 Common Tasks&quot;">​</a></h2><table tabindex="0"><thead><tr><th>Task</th><th>Command</th></tr></thead><tbody><tr><td>undefined<strong>Run a task</strong>undefined</td><td><code>thegent run &quot;Your prompt&quot; free</code></td></tr><tr><td>undefined<strong>Verify health</strong>undefined</td><td><code>thegent doctor</code></td></tr><tr><td>undefined<strong>Auto-fix issues</strong>undefined</td><td><code>thegent doctor --fix</code></td></tr><tr><td>undefined<strong>Configure providers</strong>undefined</td><td><code>thegent setup</code></td></tr><tr><td>undefined<strong>Check config</strong>undefined</td><td><code>thegent config show</code></td></tr><tr><td>undefined<strong>Next work item</strong>undefined</td><td><code>thegent plan do-next</code></td></tr><tr><td>undefined<strong>Start MCP server</strong>undefined</td><td><code>thegent serve</code></td></tr><tr><td>undefined<strong>List agents</strong>undefined</td><td><code>thegent agents list</code></td></tr><tr><td>undefined<strong>Show sessions</strong>undefined</td><td><code>thegent sessions list</code></td></tr></tbody></table><hr><h2 id="🛠-setup-installation" tabindex="-1">🛠 Setup &amp; Installation <a class="header-anchor" href="#🛠-setup-installation" aria-label="Permalink to &quot;🛠 Setup &amp; Installation&quot;">​</a></h2><ul><li>undefined<strong>Full Bootstrap</strong>: <code>curl -fsSL https://raw.githubusercontent.com/.../bootstrap.sh | sh</code></li><li>undefined<strong>Shell Completion</strong>: <code>thegent --install-completion zsh</code></li><li>undefined<strong>Install Shims</strong>: <code>thegent install-shims --all</code></li><li>undefined<strong>Git Hooks</strong>: <code>thegent setup --hooks</code></li></ul><hr><h2 id="🧪-advanced-usage" tabindex="-1">🧪 Advanced Usage <a class="header-anchor" href="#🧪-advanced-usage" aria-label="Permalink to &quot;🧪 Advanced Usage&quot;">​</a></h2><ul><li>undefined<strong>Headless Mode</strong>: <code>thegent run --headless &quot;Prompt&quot; agent-name</code></li><li>undefined<strong>Remote Compute</strong>: <code>thegent run --remote &quot;Prompt&quot; agent-name</code></li><li>undefined<strong>Plan Verification</strong>: <code>thegent plan verify</code></li><li>undefined<strong>Sync Plans</strong>: <code>thegent plan sync</code></li></ul><hr><h2 id="📁-key-directories" tabindex="-1">📁 Key Directories <a class="header-anchor" href="#📁-key-directories" aria-label="Permalink to &quot;📁 Key Directories&quot;">​</a></h2><ul><li>undefined<strong>Config</strong>: <code>~/.config/thegent/</code></li><li>undefined<strong>Sessions</strong>: <code>~/.cache/thegent/sessions/</code></li><li>undefined<strong>Mesh</strong>: <code>/tmp/agent-mesh/</code></li><li>undefined<strong>Dumps</strong>: <code>docs/dumps/</code></li></ul><hr><p>For more details, run <code>thegent --help</code> or see the <a href="https://github.com/kooshapari/thegent" target="_blank" rel="noreferrer">full documentation</a>.</p></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("guides/QUICK_REFERENCE.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const QUICK_REFERENCE = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  QUICK_REFERENCE as default
};
