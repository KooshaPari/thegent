import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Cross-Platform Domain Technical Specification","description":"","frontmatter":{},"headers":[],"relativePath":"specs/cross_platform/README.md","filePath":"specs/cross_platform/README.md","lastUpdated":1771739999000}');
const _sfc_main = { name: "specs/cross_platform/README.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="cross-platform-domain-technical-specification" tabindex="-1">Cross-Platform Domain Technical Specification <a class="header-anchor" href="#cross-platform-domain-technical-specification" aria-label="Permalink to &quot;Cross-Platform Domain Technical Specification&quot;">​</a></h1><h2 id="overview" tabindex="-1">Overview <a class="header-anchor" href="#overview" aria-label="Permalink to &quot;Overview&quot;">​</a></h2><p>Platform abstraction for desktop automation across OSes.</p><h2 id="platforms-supported" tabindex="-1">Platforms Supported <a class="header-anchor" href="#platforms-supported" aria-label="Permalink to &quot;Platforms Supported&quot;">​</a></h2><table tabindex="0"><thead><tr><th>Platform</th><th>Status</th><th>Automation</th></tr></thead><tbody><tr><td>macOS</td><td>✅</td><td>osascript, Accessibility</td></tr><tr><td>Windows</td><td>✅</td><td>Win32, PowerShell</td></tr><tr><td>Linux</td><td>✅</td><td>X11, Wayland</td></tr><tr><td>WSL</td><td>✅</td><td>Interop</td></tr></tbody></table><h3 id="desktop-automation" tabindex="-1">Desktop Automation <a class="header-anchor" href="#desktop-automation" aria-label="Permalink to &quot;Desktop Automation&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Component</th><th>Platform</th><th>Files</th></tr></thead><tbody><tr><td>macOS desktop</td><td>macOS</td><td><code>automation/macos_desktop.py</code></td></tr><tr><td>Windows desktop</td><td>Windows</td><td><code>automation/virtual_desktop.py</code></td></tr><tr><td>Linux desktop</td><td>Linux</td><td><code>providers/linux_virtual_desktop.py</code></td></tr></tbody></table><h3 id="shell-strategy" tabindex="-1">Shell Strategy <a class="header-anchor" href="#shell-strategy" aria-label="Permalink to &quot;Shell Strategy&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Shell</th><th>Platform</th></tr></thead><tbody><tr><td>Zsh</td><td>macOS</td></tr><tr><td>PowerShell</td><td>Windows</td></tr><tr><td>Bash</td><td>Linux</td></tr></tbody></table><h2 id="cross-platform-utilities" tabindex="-1">Cross-Platform Utilities <a class="header-anchor" href="#cross-platform-utilities" aria-label="Permalink to &quot;Cross-Platform Utilities&quot;">​</a></h2><table tabindex="0"><thead><tr><th>Utility</th><th>Purpose</th></tr></thead><tbody><tr><td>Desktop automation</td><td>UI control</td></tr><tr><td>Coordination</td><td>Multi-OS</td></tr><tr><td>Security</td><td>Platform-specific</td></tr><tr><td>Performance</td><td>Metrics</td></tr></tbody></table><h2 id="performance" tabindex="-1">Performance <a class="header-anchor" href="#performance" aria-label="Permalink to &quot;Performance&quot;">​</a></h2><table tabindex="0"><thead><tr><th>Metric</th><th>Target</th></tr></thead><tbody><tr><td>Launch</td><td>&lt;500ms</td></tr><tr><td>Input</td><td>&lt;10ms</td></tr><tr><td>Screenshot</td><td>&lt;100ms</td></tr></tbody></table></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("specs/cross_platform/README.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const README = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  README as default
};
