import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Infrastructure Domain Technical Specification","description":"","frontmatter":{},"headers":[],"relativePath":"specs/infra/README.md","filePath":"specs/infra/README.md","lastUpdated":1771739999000}');
const _sfc_main = { name: "specs/infra/README.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="infrastructure-domain-technical-specification" tabindex="-1">Infrastructure Domain Technical Specification <a class="header-anchor" href="#infrastructure-domain-technical-specification" aria-label="Permalink to &quot;Infrastructure Domain Technical Specification&quot;">​</a></h1><h2 id="overview" tabindex="-1">Overview <a class="header-anchor" href="#overview" aria-label="Permalink to &quot;Overview&quot;">​</a></h2><p>Core infrastructure: process management, I/O, security sandboxing.</p><h2 id="components" tabindex="-1">Components <a class="header-anchor" href="#components" aria-label="Permalink to &quot;Components&quot;">​</a></h2><h3 id="process-management" tabindex="-1">Process Management <a class="header-anchor" href="#process-management" aria-label="Permalink to &quot;Process Management&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Component</th><th>Purpose</th><th>Files</th></tr></thead><tbody><tr><td>Runtime dispatcher</td><td>Process allocation</td><td><code>infra/runtime_dispatcher.py</code></td></tr><tr><td>Subprocess manager</td><td>Spawn/control</td><td><code>infra/subprocess_manager.py</code></td></tr><tr><td>Shell detection</td><td>Environment</td><td><code>infra/shell_detection.py</code></td></tr></tbody></table><h3 id="fast-i-o" tabindex="-1">Fast I/O <a class="header-anchor" href="#fast-i-o" aria-label="Permalink to &quot;Fast I/O&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Component</th><th>Purpose</th><th>Files</th></tr></thead><tbody><tr><td>Fast file ops</td><td>Async I/O</td><td><code>infra/fast_file_ops.py</code></td></tr><tr><td>Fast HTTP</td><td>HTTP client</td><td><code>infra/fast_http_client.py</code></td></tr><tr><td>Fast websocket</td><td>Real-time</td><td><code>infra/fast_websocket.py</code></td></tr><tr><td>Compression</td><td>Data reduction</td><td><code>infra/fast_compression.py</code></td></tr></tbody></table><h3 id="security" tabindex="-1">Security <a class="header-anchor" href="#security" aria-label="Permalink to &quot;Security&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Component</th><th>Purpose</th><th>Files</th></tr></thead><tbody><tr><td>Sandbox</td><td>Isolation</td><td><code>infra/sandbox.py</code></td></tr><tr><td>Cage</td><td>Container</td><td><code>infra/cage.py</code></td></tr><tr><td>Wasm plugin</td><td>Extension</td><td><code>infra/wasm_plugin.py</code></td></tr></tbody></table><h3 id="resource-management" tabindex="-1">Resource Management <a class="header-anchor" href="#resource-management" aria-label="Permalink to &quot;Resource Management&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Component</th><th>Purpose</th><th>Files</th></tr></thead><tbody><tr><td>Resource monitor</td><td>Metrics</td><td><code>infra/resource_monitor.py</code></td></tr><tr><td>Resource limits</td><td>Quotas</td><td><code>infra/resource_limits.py</code></td></tr><tr><td>Memory</td><td>In-memory</td><td><code>infra/memory.py</code></td></tr></tbody></table><h2 id="performance" tabindex="-1">Performance <a class="header-anchor" href="#performance" aria-label="Permalink to &quot;Performance&quot;">​</a></h2><table tabindex="0"><thead><tr><th>Metric</th><th>Target</th></tr></thead><tbody><tr><td>File ops</td><td>&lt;1ms</td></tr><tr><td>HTTP request</td><td>&lt;10ms</td></tr><tr><td>Process spawn</td><td>&lt;50ms</td></tr><tr><td>Sandbox launch</td><td>&lt;100ms</td></tr></tbody></table></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("specs/infra/README.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const README = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  README as default
};
