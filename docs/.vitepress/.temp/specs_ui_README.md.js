import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"UI & TUI Domain Technical Specification","description":"","frontmatter":{},"headers":[],"relativePath":"specs/ui/README.md","filePath":"specs/ui/README.md","lastUpdated":1771739999000}');
const _sfc_main = { name: "specs/ui/README.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="ui-tui-domain-technical-specification" tabindex="-1">UI &amp; TUI Domain Technical Specification <a class="header-anchor" href="#ui-tui-domain-technical-specification" aria-label="Permalink to &quot;UI &amp; TUI Domain Technical Specification&quot;">​</a></h1><h2 id="overview" tabindex="-1">Overview <a class="header-anchor" href="#overview" aria-label="Permalink to &quot;Overview&quot;">​</a></h2><p>Terminal and graphical user interfaces.</p><h2 id="components" tabindex="-1">Components <a class="header-anchor" href="#components" aria-label="Permalink to &quot;Components&quot;">​</a></h2><h3 id="tui-terminal-ui" tabindex="-1">TUI (Terminal UI) <a class="header-anchor" href="#tui-terminal-ui" aria-label="Permalink to &quot;TUI (Terminal UI)&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Component</th><th>Purpose</th><th>Files</th></tr></thead><tbody><tr><td>Compositor</td><td>Layout</td><td><code>tui/compositor.py</code></td></tr><tr><td>Pane manager</td><td>Windows</td><td><code>tui/pane_manager.py</code></td></tr><tr><td>Session</td><td>State</td><td><code>tui/session.py</code></td></tr><tr><td>Themes</td><td>Styling</td><td><code>tui/themes.py</code></td></tr></tbody></table><h3 id="widgets" tabindex="-1">Widgets <a class="header-anchor" href="#widgets" aria-label="Permalink to &quot;Widgets&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Widget</th><th>Purpose</th></tr></thead><tbody><tr><td>Table</td><td>Data display</td></tr><tr><td>Timeline</td><td>History</td></tr><tr><td>StatusBar</td><td>Info</td></tr><tr><td>MenuBar</td><td>Navigation</td></tr><tr><td>TerminalPane</td><td>PTY</td></tr></tbody></table><h3 id="ui-graphical" tabindex="-1">UI (Graphical) <a class="header-anchor" href="#ui-graphical" aria-label="Permalink to &quot;UI (Graphical)&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Component</th><th>Purpose</th></tr></thead><tbody><tr><td>Compositor</td><td>Layout</td></tr><tr><td>Components</td><td>Reusable</td></tr><tr><td>Textual</td><td>App framework</td></tr></tbody></table><h2 id="performance" tabindex="-1">Performance <a class="header-anchor" href="#performance" aria-label="Permalink to &quot;Performance&quot;">​</a></h2><table tabindex="0"><thead><tr><th>Metric</th><th>Target</th></tr></thead><tbody><tr><td>Render</td><td>&lt;16ms (60fps)</td></tr><tr><td>Input</td><td>&lt;10ms</td></tr><tr><td>Resize</td><td>&lt;50ms</td></tr></tbody></table></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("specs/ui/README.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const README = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  README as default
};
