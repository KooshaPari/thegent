import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Observability Domain Technical Specification","description":"","frontmatter":{},"headers":[],"relativePath":"specs/observability/README.md","filePath":"specs/observability/README.md","lastUpdated":1771739999000}');
const _sfc_main = { name: "specs/observability/README.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="observability-domain-technical-specification" tabindex="-1">Observability Domain Technical Specification <a class="header-anchor" href="#observability-domain-technical-specification" aria-label="Permalink to &quot;Observability Domain Technical Specification&quot;">​</a></h1><h2 id="overview" tabindex="-1">Overview <a class="header-anchor" href="#overview" aria-label="Permalink to &quot;Overview&quot;">​</a></h2><p>Observability for metrics, tracing, logging, and AI explainability.</p><h2 id="components" tabindex="-1">Components <a class="header-anchor" href="#components" aria-label="Permalink to &quot;Components&quot;">​</a></h2><h3 id="metrics" tabindex="-1">Metrics <a class="header-anchor" href="#metrics" aria-label="Permalink to &quot;Metrics&quot;">​</a></h3><table tabindex="0"><thead><tr><th>System</th><th>Backend</th><th>Files</th></tr></thead><tbody><tr><td>Prometheus</td><td>Pull</td><td><code>observability/prometheus.py</code></td></tr><tr><td>OpenTelemetry</td><td>Export</td><td><code>observability/otel.py</code></td></tr><tr><td>Custom</td><td>In-memory</td><td><code>observability/metrics.py</code></td></tr></tbody></table><h3 id="tracing" tabindex="-1">Tracing <a class="header-anchor" href="#tracing" aria-label="Permalink to &quot;Tracing&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Type</th><th>Implementation</th></tr></thead><tbody><tr><td>Distributed</td><td>OpenTelemetry</td></tr><tr><td>AI spans</td><td>Custom</td></tr><tr><td>Performance</td><td>Timing hooks</td></tr></tbody></table><h3 id="logging" tabindex="-1">Logging <a class="header-anchor" href="#logging" aria-label="Permalink to &quot;Logging&quot;">​</a></h3><table tabindex="0"><thead><tr><th>Handler</th><th>Purpose</th></tr></thead><tbody><tr><td>AsyncLogger</td><td>Non-blocking</td></tr><tr><td>Structured</td><td>JSON output</td></tr><tr><td>Alerting</td><td>PagerDuty</td></tr></tbody></table><h2 id="ai-explainability" tabindex="-1">AI Explainability <a class="header-anchor" href="#ai-explainability" aria-label="Permalink to &quot;AI Explainability&quot;">​</a></h2><table tabindex="0"><thead><tr><th>Feature</th><th>Implementation</th></tr></thead><tbody><tr><td>Decision trace</td><td><code>explainability.py</code></td></tr><tr><td>Cost attribution</td><td>Cost aggregation</td></tr><tr><td>Quality scoring</td><td>Evaluation</td></tr></tbody></table><h2 id="metrics-exposed" tabindex="-1">Metrics Exposed <a class="header-anchor" href="#metrics-exposed" aria-label="Permalink to &quot;Metrics Exposed&quot;">​</a></h2><table tabindex="0"><thead><tr><th>Metric</th><th>Type</th><th>Target</th></tr></thead><tbody><tr><td>Request latency</td><td>Histogram</td><td>p99 &lt; 100ms</td></tr><tr><td>Token usage</td><td>Counter</td><td>Budget tracking</td></tr><tr><td>Error rate</td><td>Gauge</td><td>&lt; 1%</td></tr><tr><td>Cost</td><td>Counter</td><td>Per-provider</td></tr></tbody></table><h2 id="integration" tabindex="-1">Integration <a class="header-anchor" href="#integration" aria-label="Permalink to &quot;Integration&quot;">​</a></h2><ul><li>OpenTelemetry collector</li><li>Prometheus scrape</li><li>Grafana dashboard</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("specs/observability/README.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const README = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  README as default
};
