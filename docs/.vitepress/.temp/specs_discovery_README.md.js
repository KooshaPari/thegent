import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Discovery Domain Technical Specification","description":"","frontmatter":{},"headers":[],"relativePath":"specs/discovery/README.md","filePath":"specs/discovery/README.md","lastUpdated":1771739999000}');
const _sfc_main = { name: "specs/discovery/README.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="discovery-domain-technical-specification" tabindex="-1">Discovery Domain Technical Specification <a class="header-anchor" href="#discovery-domain-technical-specification" aria-label="Permalink to &quot;Discovery Domain Technical Specification&quot;">​</a></h1><h2 id="overview" tabindex="-1">Overview <a class="header-anchor" href="#overview" aria-label="Permalink to &quot;Overview&quot;">​</a></h2><p>Project discovery, federation, and edge synchronization.</p><h2 id="components" tabindex="-1">Components <a class="header-anchor" href="#components" aria-label="Permalink to &quot;Components&quot;">​</a></h2><h3 id="discovery-types" tabindex="-1">Discovery Types <a class="header-anchor" href="#discovery-types" aria-label="Permalink to &quot;Discovery Types&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Type</th><th>Purpose</th><th>Files</th></tr></thead><tbody><tr><td>Projects</td><td>Workspace</td><td><code>discovery/projects.py</code></td></tr><tr><td>Federation</td><td>Cross-org</td><td><code>discovery/federation.py</code></td></tr><tr><td>Edge sync</td><td>Offline</td><td><code>discovery/edge_sync.py</code></td></tr><tr><td>Mesh</td><td>P2P</td><td><code>discovery/mesh.py</code></td></tr><tr><td>Galactic</td><td>Global</td><td><code>discovery/galactic.py</code></td></tr></tbody></table><h3 id="sync" tabindex="-1">Sync <a class="header-anchor" href="#sync" aria-label="Permalink to &quot;Sync&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Component</th><th>Purpose</th><th>Files</th></tr></thead><tbody><tr><td>Relativistic</td><td>Time sync</td><td><code>discovery/relativistic.py</code></td></tr><tr><td>Market</td><td>Discovery</td><td><code>discovery/market.py</code></td></tr></tbody></table><h2 id="features" tabindex="-1">Features <a class="header-anchor" href="#features" aria-label="Permalink to &quot;Features&quot;">​</a></h2><ul><li>Automatic project detection</li><li>Cross-project references</li><li>Offline capability</li><li>Federation protocols</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("specs/discovery/README.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const README = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  README as default
};
