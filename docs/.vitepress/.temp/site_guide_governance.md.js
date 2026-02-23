import { ssrRenderAttrs, ssrRenderStyle } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Governance","description":"","frontmatter":{},"headers":[],"relativePath":"site/guide/governance.md","filePath":"site/guide/governance.md","lastUpdated":1771678191000}');
const _sfc_main = { name: "site/guide/governance.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="governance" tabindex="-1">Governance <a class="header-anchor" href="#governance" aria-label="Permalink to &quot;Governance&quot;">​</a></h1><p><code>thegent</code> includes built-in controls so autonomous runs remain auditable and bounded.</p><h2 id="governance-surfaces" tabindex="-1">Governance Surfaces <a class="header-anchor" href="#governance-surfaces" aria-label="Permalink to &quot;Governance Surfaces&quot;">​</a></h2><ul><li>Cost controls: provider/model routing and spend-sensitive policies.</li><li>Quality gates: lint, tests, and policy checks on lifecycle events.</li><li>Security checks: secret scanning and static analysis in validation pipelines.</li><li>Operational safety: explicit session lifecycle and auditable history.</li></ul><h2 id="baseline-policy-workflow" tabindex="-1">Baseline Policy Workflow <a class="header-anchor" href="#baseline-policy-workflow" aria-label="Permalink to &quot;Baseline Policy Workflow&quot;">​</a></h2><div class="language-bash vp-adaptive-theme line-numbers-mode"><button title="Copy Code" class="copy"></button><span class="lang">bash</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="${ssrRenderStyle({ "--shiki-light": "#6A737D", "--shiki-dark": "#6A737D" })}"># 1) Verify runtime health</span></span>
<span class="line"><span style="${ssrRenderStyle({ "--shiki-light": "#6F42C1", "--shiki-dark": "#B392F0" })}">thegent</span><span style="${ssrRenderStyle({ "--shiki-light": "#032F62", "--shiki-dark": "#9ECBFF" })}"> doctor</span></span>
<span class="line"></span>
<span class="line"><span style="${ssrRenderStyle({ "--shiki-light": "#6A737D", "--shiki-dark": "#6A737D" })}"># 2) Execute work</span></span>
<span class="line"><span style="${ssrRenderStyle({ "--shiki-light": "#6F42C1", "--shiki-dark": "#B392F0" })}">thegent</span><span style="${ssrRenderStyle({ "--shiki-light": "#032F62", "--shiki-dark": "#9ECBFF" })}"> run</span><span style="${ssrRenderStyle({ "--shiki-light": "#032F62", "--shiki-dark": "#9ECBFF" })}"> &quot;implement feature and tests&quot;</span><span style="${ssrRenderStyle({ "--shiki-light": "#032F62", "--shiki-dark": "#9ECBFF" })}"> codex</span></span>
<span class="line"></span>
<span class="line"><span style="${ssrRenderStyle({ "--shiki-light": "#6A737D", "--shiki-dark": "#6A737D" })}"># 3) Validate and review state</span></span>
<span class="line"><span style="${ssrRenderStyle({ "--shiki-light": "#6F42C1", "--shiki-dark": "#B392F0" })}">thegent</span><span style="${ssrRenderStyle({ "--shiki-light": "#032F62", "--shiki-dark": "#9ECBFF" })}"> ps</span></span>
<span class="line"><span style="${ssrRenderStyle({ "--shiki-light": "#6F42C1", "--shiki-dark": "#B392F0" })}">thegent</span><span style="${ssrRenderStyle({ "--shiki-light": "#032F62", "--shiki-dark": "#9ECBFF" })}"> plan</span><span style="${ssrRenderStyle({ "--shiki-light": "#032F62", "--shiki-dark": "#9ECBFF" })}"> do-next</span></span></code></pre><div class="line-numbers-wrapper" aria-hidden="true"><span class="line-number">1</span><br><span class="line-number">2</span><br><span class="line-number">3</span><br><span class="line-number">4</span><br><span class="line-number">5</span><br><span class="line-number">6</span><br><span class="line-number">7</span><br><span class="line-number">8</span><br><span class="line-number">9</span><br></div></div><h2 id="recommended-team-defaults" tabindex="-1">Recommended Team Defaults <a class="header-anchor" href="#recommended-team-defaults" aria-label="Permalink to &quot;Recommended Team Defaults&quot;">​</a></h2><table tabindex="0"><thead><tr><th>Area</th><th>Recommendation</th></tr></thead><tbody><tr><td>Routing</td><td>Use explicit provider/model for critical jobs</td></tr><tr><td>Budgets</td><td>Enforce environment-level spend caps</td></tr><tr><td>Validation</td><td>Run quality checks on each merge candidate</td></tr><tr><td>Recovery</td><td>Prefer continuation/takeover over restarting context</td></tr></tbody></table><h2 id="common-pitfalls" tabindex="-1">Common Pitfalls <a class="header-anchor" href="#common-pitfalls" aria-label="Permalink to &quot;Common Pitfalls&quot;">​</a></h2><ul><li>Running long loops without policy or budget constraints.</li><li>Mixing unrelated workstreams in a single session.</li><li>Bypassing hook-based validation.</li></ul><p>See <a href="/operations/runbooks.html">Operations Runbooks</a> for remediation steps.</p></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("site/guide/governance.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const governance = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  governance as default
};
