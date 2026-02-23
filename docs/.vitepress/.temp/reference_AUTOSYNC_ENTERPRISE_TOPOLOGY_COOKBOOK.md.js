import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Autosync Enterprise Topology Cookbook","description":"","frontmatter":{},"headers":[],"relativePath":"reference/AUTOSYNC_ENTERPRISE_TOPOLOGY_COOKBOOK.md","filePath":"reference/AUTOSYNC_ENTERPRISE_TOPOLOGY_COOKBOOK.md","lastUpdated":1771803666000}');
const _sfc_main = { name: "reference/AUTOSYNC_ENTERPRISE_TOPOLOGY_COOKBOOK.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="autosync-enterprise-topology-cookbook" tabindex="-1">Autosync Enterprise Topology Cookbook <a class="header-anchor" href="#autosync-enterprise-topology-cookbook" aria-label="Permalink to &quot;Autosync Enterprise Topology Cookbook&quot;">​</a></h1><h2 id="purpose" tabindex="-1">Purpose <a class="header-anchor" href="#purpose" aria-label="Permalink to &quot;Purpose&quot;">​</a></h2><p>Reference deployment patterns for autosync in enterprise environments.</p><h2 id="topology-a-single-team-single-project" tabindex="-1">Topology A: Single Team, Single Project <a class="header-anchor" href="#topology-a-single-team-single-project" aria-label="Permalink to &quot;Topology A: Single Team, Single Project&quot;">​</a></h2><ul><li>Use case: initial adoption, low complexity.</li><li>Components: one local workstream, one GitHub project, one Linear team.</li><li>Notes: fastest path; minimal conflict surface.</li></ul><h2 id="topology-b-multi-team-shared-platform" tabindex="-1">Topology B: Multi-Team Shared Platform <a class="header-anchor" href="#topology-b-multi-team-shared-platform" aria-label="Permalink to &quot;Topology B: Multi-Team Shared Platform&quot;">​</a></h2><ul><li>Use case: multiple feature teams sharing governance baseline.</li><li>Components: per-team project registry entries + shared policy pack.</li><li>Notes: enforce ownership metadata and per-team auth boundaries.</li></ul><h2 id="topology-c-hub-and-spoke-program" tabindex="-1">Topology C: Hub-and-Spoke Program <a class="header-anchor" href="#topology-c-hub-and-spoke-program" aria-label="Permalink to &quot;Topology C: Hub-and-Spoke Program&quot;">​</a></h2><ul><li>Use case: central platform team with many product teams.</li><li>Components: central governance controls + team-level connector mappings.</li><li>Notes: require strict conflict TTL/escalation and incident snapshots.</li></ul><h2 id="topology-d-regulated-environment" tabindex="-1">Topology D: Regulated Environment <a class="header-anchor" href="#topology-d-regulated-environment" aria-label="Permalink to &quot;Topology D: Regulated Environment&quot;">​</a></h2><ul><li>Use case: compliance-heavy workflows.</li><li>Components: immutable cycle manifests, artifact redaction, audit log retention.</li><li>Notes: prioritize reproducibility and restore verification over throughput.</li></ul><h2 id="topology-e-staged-rollout-recommended-default" tabindex="-1">Topology E: Staged Rollout (Recommended Default) <a class="header-anchor" href="#topology-e-staged-rollout-recommended-default" aria-label="Permalink to &quot;Topology E: Staged Rollout (Recommended Default)&quot;">​</a></h2><ul><li>Use case: safe enterprise onboarding.</li><li>Components: observe-only/shadow mode -&gt; limited write mode -&gt; full mode.</li><li>Notes: advance stages only when reliability and conflict metrics are stable.</li></ul><h2 id="pattern-selection-guide" tabindex="-1">Pattern Selection Guide <a class="header-anchor" href="#pattern-selection-guide" aria-label="Permalink to &quot;Pattern Selection Guide&quot;">​</a></h2><ul><li>Choose A for pilot.</li><li>Move to E for structured expansion.</li><li>Use B or C depending on team autonomy model.</li><li>Use D when compliance or legal requirements dominate.</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("reference/AUTOSYNC_ENTERPRISE_TOPOLOGY_COOKBOOK.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const AUTOSYNC_ENTERPRISE_TOPOLOGY_COOKBOOK = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  AUTOSYNC_ENTERPRISE_TOPOLOGY_COOKBOOK as default
};
