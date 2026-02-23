import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Planning Domain Technical Specification","description":"","frontmatter":{},"headers":[],"relativePath":"specs/planning/README.md","filePath":"specs/planning/README.md","lastUpdated":1771739999000}');
const _sfc_main = { name: "specs/planning/README.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="planning-domain-technical-specification" tabindex="-1">Planning Domain Technical Specification <a class="header-anchor" href="#planning-domain-technical-specification" aria-label="Permalink to &quot;Planning Domain Technical Specification&quot;">​</a></h1><h2 id="overview" tabindex="-1">Overview <a class="header-anchor" href="#overview" aria-label="Permalink to &quot;Overview&quot;">​</a></h2><p>Planning handles AI task decomposition, simulation, and remediation.</p><h2 id="components" tabindex="-1">Components <a class="header-anchor" href="#components" aria-label="Permalink to &quot;Components&quot;">​</a></h2><h3 id="planning-types" tabindex="-1">Planning Types <a class="header-anchor" href="#planning-types" aria-label="Permalink to &quot;Planning Types&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Type</th><th>Purpose</th><th>Files</th></tr></thead><tbody><tr><td>Simulation</td><td>Task replay</td><td><code>planning/simulation.py</code></td></tr><tr><td>Self-healing</td><td>Auto-remediation</td><td><code>planning/self_healing.py</code></td></tr><tr><td>Remediation</td><td>Error recovery</td><td><code>planning/remediation_planner.py</code></td></tr><tr><td>Tuning</td><td>Performance</td><td><code>planning/tuning.py</code></td></tr><tr><td>Learning</td><td>Adaptive</td><td><code>planning/learning.py</code></td></tr><tr><td>Multiiverse</td><td>Parallel plans</td><td><code>planning/multiverse.py</code></td></tr></tbody></table><h3 id="work-stream" tabindex="-1">Work Stream <a class="header-anchor" href="#work-stream" aria-label="Permalink to &quot;Work Stream&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Component</th><th>Purpose</th><th>Files</th></tr></thead><tbody><tr><td>WorkStream</td><td>Task tracking</td><td><code>planning/work_stream.py</code></td></tr><tr><td>Evolution</td><td>Plan improvement</td><td><code>planning/evolution.py</code></td></tr><tr><td>Harness</td><td>Testing</td><td><code>planning/harness.py</code></td></tr></tbody></table><h2 id="algorithms" tabindex="-1">Algorithms <a class="header-anchor" href="#algorithms" aria-label="Permalink to &quot;Algorithms&quot;">​</a></h2><table tabindex="0"><thead><tr><th>Algorithm</th><th>Purpose</th></tr></thead><tbody><tr><td>Tree search</td><td>Plan exploration</td></tr><tr><td>Monte Carlo</td><td>Simulation</td></tr><tr><td>Genetic</td><td>Evolution</td></tr></tbody></table><h2 id="performance" tabindex="-1">Performance <a class="header-anchor" href="#performance" aria-label="Permalink to &quot;Performance&quot;">​</a></h2><table tabindex="0"><thead><tr><th>Metric</th><th>Target</th></tr></thead><tbody><tr><td>Plan generation</td><td>&lt;1s</td></tr><tr><td>Simulation</td><td>&lt;10s</td></tr><tr><td>Remediation</td><td>&lt;5s</td></tr></tbody></table></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("specs/planning/README.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const README = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  README as default
};
