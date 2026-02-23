import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"WL-137 Weekly LOC/Refactor Diagnosis Checklist","description":"","frontmatter":{},"headers":[],"relativePath":"checklists/WL-137-WEEKLY-DIAGNOSIS.md","filePath":"checklists/WL-137-WEEKLY-DIAGNOSIS.md","lastUpdated":1771739999000}');
const _sfc_main = { name: "checklists/WL-137-WEEKLY-DIAGNOSIS.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="wl-137-weekly-loc-refactor-diagnosis-checklist" tabindex="-1">WL-137 Weekly LOC/Refactor Diagnosis Checklist <a class="header-anchor" href="#wl-137-weekly-loc-refactor-diagnosis-checklist" aria-label="Permalink to &quot;WL-137 Weekly LOC/Refactor Diagnosis Checklist&quot;">​</a></h1><p>Use this checklist once per week to keep LOC/refactor drift visible across active codebases.</p><h2 id="run" tabindex="-1">Run <a class="header-anchor" href="#run" aria-label="Permalink to &quot;Run&quot;">​</a></h2><ul><li>[ ] Run <code>task diag:wl137</code>.</li><li>[ ] Confirm the command exits zero (or explicitly triage non-zero alerts).</li><li>[ ] Verify <code>var/wl137/history.json</code> has a new run entry.</li><li>[ ] Verify a report exists at <code>docs/reports/WL-137-weekly-YYYY-MM-DD.md</code>.</li><li>[ ] Verify trend artifacts exist at <code>docs/reports/artifacts/wl120-wl136-loc-trend-YYYY-MM-DD.{json,md}</code>.</li></ul><h2 id="review" tabindex="-1">Review <a class="header-anchor" href="#review" aria-label="Permalink to &quot;Review&quot;">​</a></h2><ul><li>[ ] Check total LOC drift by target (<code>thegent</code>, <code>trace</code>).</li><li>[ ] Check hotspot growth (<code>files &gt; 500</code>, <code>files &gt; 1000</code>).</li><li>[ ] Review top-file table for new monolith candidates.</li><li>[ ] Confirm alerts are either addressed or tracked.</li></ul><h2 id="follow-up" tabindex="-1">Follow-up <a class="header-anchor" href="#follow-up" aria-label="Permalink to &quot;Follow-up&quot;">​</a></h2><ul><li>[ ] If thresholds regressed, open or update decomposition work items in <code>docs/reference/WORK_STREAM.md</code>.</li><li>[ ] Link the generated report from the relevant active plan/worklog item.</li><li>[ ] Keep report filenames date-stamped and immutable for trend history.</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("checklists/WL-137-WEEKLY-DIAGNOSIS.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const WL137WEEKLYDIAGNOSIS = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  WL137WEEKLYDIAGNOSIS as default
};
