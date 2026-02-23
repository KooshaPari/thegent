import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Memory Domain Technical Specification","description":"","frontmatter":{},"headers":[],"relativePath":"specs/memory/README.md","filePath":"specs/memory/README.md","lastUpdated":1771739999000}');
const _sfc_main = { name: "specs/memory/README.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="memory-domain-technical-specification" tabindex="-1">Memory Domain Technical Specification <a class="header-anchor" href="#memory-domain-technical-specification" aria-label="Permalink to &quot;Memory Domain Technical Specification&quot;">​</a></h1><h2 id="overview" tabindex="-1">Overview <a class="header-anchor" href="#overview" aria-label="Permalink to &quot;Overview&quot;">​</a></h2><p>Memory systems for caching, context management, and knowledge retrieval.</p><h2 id="components" tabindex="-1">Components <a class="header-anchor" href="#components" aria-label="Permalink to &quot;Components&quot;">​</a></h2><h3 id="memory-types" tabindex="-1">Memory Types <a class="header-anchor" href="#memory-types" aria-label="Permalink to &quot;Memory Types&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Type</th><th>Backend</th><th>Purpose</th></tr></thead><tbody><tr><td>Cache</td><td>Multi-level</td><td>Fast retrieval</td></tr><tr><td>Supermemory</td><td>Vector DB</td><td>Semantic search</td></tr><tr><td>Garden</td><td>Long-term</td><td>Knowledge graph</td></tr><tr><td>Seed</td><td>Immutable</td><td>Provenance</td></tr></tbody></table><h3 id="cache-hierarchy" tabindex="-1">Cache Hierarchy <a class="header-anchor" href="#cache-hierarchy" aria-label="Permalink to &quot;Cache Hierarchy&quot;">​</a></h3><div class="language- vp-adaptive-theme line-numbers-mode"><button title="Copy Code" class="copy"></button><span class="lang"></span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span>L1: In-memory (hot)</span></span>
<span class="line"><span>L2: Disk (warm)</span></span>
<span class="line"><span>L3: Remote (cold)</span></span></code></pre><div class="line-numbers-wrapper" aria-hidden="true"><span class="line-number">1</span><br><span class="line-number">2</span><br><span class="line-number">3</span><br></div></div><h3 id="key-classes" tabindex="-1">Key Classes <a class="header-anchor" href="#key-classes" aria-label="Permalink to &quot;Key Classes&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Class</th><th>Purpose</th><th>Files</th></tr></thead><tbody><tr><td>MemoryManager</td><td>Lifecycle</td><td><code>memory/manager.py</code></td></tr><tr><td>CacheProvider</td><td>Caching</td><td><code>memory/cache_provider.py</code></td></tr><tr><td>SupermemoryClient</td><td>Vector search</td><td><code>memory/supermemory_client.py</code></td></tr><tr><td>Garden</td><td>Knowledge</td><td><code>memory/garden.py</code></td></tr></tbody></table><h2 id="performance" tabindex="-1">Performance <a class="header-anchor" href="#performance" aria-label="Permalink to &quot;Performance&quot;">​</a></h2><table tabindex="0"><thead><tr><th>Metric</th><th>Target</th></tr></thead><tbody><tr><td>L1 lookup</td><td>&lt;1ms</td></tr><tr><td>L2 lookup</td><td>&lt;10ms</td></tr><tr><td>L3 lookup</td><td>&lt;100ms</td></tr><tr><td>Seed detection</td><td>&lt;50ms</td></tr></tbody></table><h2 id="features" tabindex="-1">Features <a class="header-anchor" href="#features" aria-label="Permalink to &quot;Features&quot;">​</a></h2><ul><li>Frecency-based eviction</li><li>Seed preservation</li><li>Cross-session persistence</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("specs/memory/README.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const README = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  README as default
};
