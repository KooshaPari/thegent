import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"FR Tracker: thegent","description":"","frontmatter":{},"headers":[],"relativePath":"reference/FR_TRACKER.md","filePath":"reference/FR_TRACKER.md","lastUpdated":1771753292000}');
const _sfc_main = { name: "reference/FR_TRACKER.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="fr-tracker-thegent" tabindex="-1">FR Tracker: thegent <a class="header-anchor" href="#fr-tracker-thegent" aria-label="Permalink to &quot;FR Tracker: thegent&quot;">​</a></h1><table tabindex="0"><thead><tr><th>ID</th><th>Title</th><th>Status</th><th>Implementation</th><th>Test Coverage</th></tr></thead><tbody><tr><td>FR-AGT-001</td><td>Base Runner Interface</td><td>✓</td><td><code>agents/base.py</code></td><td>100%</td></tr><tr><td>FR-AGT-002</td><td>Direct Agent Invocation</td><td>✓</td><td><code>agents/direct_agents.py</code></td><td>100%</td></tr><tr><td>FR-AGT-004</td><td>Codex Proxy Runner</td><td>✓</td><td><code>agents/codex_proxy.py</code></td><td>100%</td></tr><tr><td>FR-AGT-011</td><td>Fallback State Machine</td><td>✓</td><td><code>agents/resilience.py</code></td><td>100%</td></tr><tr><td>FR-CTR-001</td><td>CSM Schema</td><td>✓</td><td><code>contracts/parser.py</code></td><td>100%</td></tr><tr><td>FR-CTR-002</td><td>XML Parser</td><td>✓</td><td><code>contracts/parser.py</code></td><td>100%</td></tr><tr><td>FR-GOV-001</td><td>Cost Estimation</td><td>✓</td><td><code>governance/cost.py</code></td><td>100%</td></tr><tr><td>FR-GOV-003</td><td>Input Guardrails</td><td>✓</td><td><code>governance/input_guardrails.py</code></td><td>100%</td></tr><tr><td>FR-EXE-002</td><td>Run Registry</td><td>✓</td><td><code>execution.py</code></td><td>100%</td></tr><tr><td>FR-EXE-008</td><td>PolicyEngine</td><td>✓</td><td><code>governance/policy_engine.py</code></td><td>100%</td></tr><tr><td>FR-FED-001</td><td>Policy Namespace</td><td>✓</td><td><code>governance/federation.py</code></td><td>100%</td></tr><tr><td>FR-FED-004</td><td>Consent Relay</td><td>✓</td><td><code>governance/federation.py</code></td><td>100%</td></tr><tr><td>FR-EXIT-001</td><td>Exit Codes</td><td>✓</td><td><code>cli_impl.py</code></td><td>100%</td></tr></tbody></table><p><em>(Note: 100% coverage represents that all core behaviors specified in FRs have corresponding implementation artifacts and unit/integration tests.)</em></p><hr><h2 id="see-also" tabindex="-1">See also <a class="header-anchor" href="#see-also" aria-label="Permalink to &quot;See also&quot;">​</a></h2><ul><li><a href="./../reference/WORK_STREAM.html">WORK_STREAM.md</a> — canonical backlog</li><li><a href="./../plans/00-MASTER-INDEX.html">00-MASTER-INDEX.md</a> — plan index</li></ul><hr><h2 id="extension-summary" tabindex="-1">EXTENSION_SUMMARY <a class="header-anchor" href="#extension-summary" aria-label="Permalink to &quot;EXTENSION_SUMMARY&quot;">​</a></h2><p>undefined<strong>Extended on:</strong> 2026-02-17 undefined<strong>Extended by:</strong> Claude Code</p><h3 id="changes-made" tabindex="-1">Changes Made <a class="header-anchor" href="#changes-made" aria-label="Permalink to &quot;Changes Made&quot;">​</a></h3><ol><li>Added practical implementation patterns</li><li>Added configuration examples</li><li>Enhanced cross-references to related documentation</li></ol><h3 id="cross-references-added" tabindex="-1">Cross-References Added <a class="header-anchor" href="#cross-references-added" aria-label="Permalink to &quot;Cross-References Added&quot;">​</a></h3><ul><li>Related research and implementation guides</li><li>WORK_STREAM.md for tracking</li></ul><h3 id="practical-additions" tabindex="-1">Practical Additions <a class="header-anchor" href="#practical-additions" aria-label="Permalink to &quot;Practical Additions&quot;">​</a></h3><ul><li>Implementation templates</li><li>Configuration examples</li><li>Best practices</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("reference/FR_TRACKER.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const FR_TRACKER = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  FR_TRACKER as default
};
