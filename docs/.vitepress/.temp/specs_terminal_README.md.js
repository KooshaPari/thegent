import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Terminal & ZMX Specification","description":"","frontmatter":{},"headers":[],"relativePath":"specs/terminal/README.md","filePath":"specs/terminal/README.md","lastUpdated":1771739999000}');
const _sfc_main = { name: "specs/terminal/README.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="terminal-zmx-specification" tabindex="-1">Terminal &amp; ZMX Specification <a class="header-anchor" href="#terminal-zmx-specification" aria-label="Permalink to &quot;Terminal &amp; ZMX Specification&quot;">​</a></h1><h2 id="overview" tabindex="-1">Overview <a class="header-anchor" href="#overview" aria-label="Permalink to &quot;Overview&quot;">​</a></h2><p>Terminal harness for PTY management and session control.</p><h2 id="components" tabindex="-1">Components <a class="header-anchor" href="#components" aria-label="Permalink to &quot;Components&quot;">​</a></h2><h3 id="zmx-integration" tabindex="-1">ZMX Integration <a class="header-anchor" href="#zmx-integration" aria-label="Permalink to &quot;ZMX Integration&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Component</th><th>Purpose</th><th>Path</th></tr></thead><tbody><tr><td>ZmxBackend</td><td>Session management</td><td><code>session/zmx_backend.py</code></td></tr><tr><td>ZmxSession</td><td>Session state</td><td><code>muxless/zmx_session.py</code></td></tr></tbody></table><h3 id="terminal-operations" tabindex="-1">Terminal Operations <a class="header-anchor" href="#terminal-operations" aria-label="Permalink to &quot;Terminal Operations&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Operation</th><th>Implementation</th></tr></thead><tbody><tr><td>Spawn PTY</td><td>Native process</td></tr><tr><td>Capture output</td><td>Streaming</td></tr><tr><td>Send input</td><td>Direct injection</td></tr><tr><td>Resize</td><td>Window change</td></tr></tbody></table><h2 id="architecture" tabindex="-1">Architecture <a class="header-anchor" href="#architecture" aria-label="Permalink to &quot;Architecture&quot;">​</a></h2><div class="language- vp-adaptive-theme line-numbers-mode"><button title="Copy Code" class="copy"></button><span class="lang"></span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span>User → MCP Tool → ZmxBackend → zmx binary → PTY</span></span>
<span class="line"><span>                        ↓</span></span>
<span class="line"><span>                  Terminal session</span></span></code></pre><div class="line-numbers-wrapper" aria-hidden="true"><span class="line-number">1</span><br><span class="line-number">2</span><br><span class="line-number">3</span><br></div></div><h2 id="performance" tabindex="-1">Performance <a class="header-anchor" href="#performance" aria-label="Permalink to &quot;Performance&quot;">​</a></h2><table tabindex="0"><thead><tr><th>Metric</th><th>Target</th></tr></thead><tbody><tr><td>Spawn latency</td><td>&lt;100ms</td></tr><tr><td>Output capture</td><td>Real-time</td></tr><tr><td>Input latency</td><td>&lt;10ms</td></tr></tbody></table><h2 id="security" tabindex="-1">Security <a class="header-anchor" href="#security" aria-label="Permalink to &quot;Security&quot;">​</a></h2><ul><li>Process isolation</li><li>Resource limits</li><li>Audit logging</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("specs/terminal/README.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const README = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  README as default
};
