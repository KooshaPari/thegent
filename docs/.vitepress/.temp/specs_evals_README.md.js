import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Evaluation & Benchmarks Domain Technical Specification","description":"","frontmatter":{},"headers":[],"relativePath":"specs/evals/README.md","filePath":"specs/evals/README.md","lastUpdated":1771739999000}');
const _sfc_main = { name: "specs/evals/README.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="evaluation-benchmarks-domain-technical-specification" tabindex="-1">Evaluation &amp; Benchmarks Domain Technical Specification <a class="header-anchor" href="#evaluation-benchmarks-domain-technical-specification" aria-label="Permalink to &quot;Evaluation &amp; Benchmarks Domain Technical Specification&quot;">​</a></h1><h2 id="overview" tabindex="-1">Overview <a class="header-anchor" href="#overview" aria-label="Permalink to &quot;Overview&quot;">​</a></h2><p>Model evaluation, benchmarking, and quality metrics.</p><h2 id="benchmarks" tabindex="-1">Benchmarks <a class="header-anchor" href="#benchmarks" aria-label="Permalink to &quot;Benchmarks&quot;">​</a></h2><table tabindex="0"><thead><tr><th>Benchmark</th><th>Purpose</th><th>Files</th></tr></thead><tbody><tr><td>Terminal Bench 2.0</td><td>Coding</td><td><code>bench/models.py</code></td></tr><tr><td>SWE-Bench</td><td>Software eng</td><td>External</td></tr><tr><td>Custom evals</td><td>Domain</td><td><code>evals/integration.py</code></td></tr></tbody></table><h3 id="metrics" tabindex="-1">Metrics <a class="header-anchor" href="#metrics" aria-label="Permalink to &quot;Metrics&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Metric</th><th>Purpose</th></tr></thead><tbody><tr><td>Quality score</td><td>Output quality</td></tr><tr><td>Speed score</td><td>Latency</td></tr><tr><td>Cost score</td><td>Token usage</td></tr><tr><td>Pareto frontier</td><td>Multi-objective</td></tr></tbody></table><h2 id="quality-gates" tabindex="-1">Quality Gates <a class="header-anchor" href="#quality-gates" aria-label="Permalink to &quot;Quality Gates&quot;">​</a></h2><ul><li>Benchmarks pass</li><li>Regression detection</li><li>Cost thresholds</li><li>Latency SLAs</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("specs/evals/README.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const README = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  README as default
};
