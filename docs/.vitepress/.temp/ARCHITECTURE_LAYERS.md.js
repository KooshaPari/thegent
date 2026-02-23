import { ssrRenderAttrs, ssrRenderStyle } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Architecture Layers (G-KD-05)","description":"","frontmatter":{},"headers":[],"relativePath":"ARCHITECTURE_LAYERS.md","filePath":"ARCHITECTURE_LAYERS.md","lastUpdated":1771498270000}');
const _sfc_main = { name: "ARCHITECTURE_LAYERS.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="architecture-layers-g-kd-05" tabindex="-1">Architecture Layers (G-KD-05) <a class="header-anchor" href="#architecture-layers-g-kd-05" aria-label="Permalink to &quot;Architecture Layers (G-KD-05)&quot;">​</a></h1><p>undefined<strong>Purpose:</strong> Import/dependency boundary enforcement. Enforced by <code>scripts/check_boundaries.py</code> in CI.</p><hr><h2 id="layer-dependency-graph" tabindex="-1">Layer Dependency Graph <a class="header-anchor" href="#layer-dependency-graph" aria-label="Permalink to &quot;Layer Dependency Graph&quot;">​</a></h2><div class="language- vp-adaptive-theme line-numbers-mode"><button title="Copy Code" class="copy"></button><span class="lang"></span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span>config          (no deps)</span></span>
<span class="line"><span>output_parser   (no deps)</span></span>
<span class="line"><span>contracts       → config</span></span>
<span class="line"><span>models          → config, contracts</span></span>
<span class="line"><span>execution       → config, contracts, models</span></span>
<span class="line"><span>agents          → config, contracts, models</span></span>
<span class="line"><span>operations      → config</span></span>
<span class="line"><span>orchestration_modes (no deps)</span></span>
<span class="line"><span></span></span>
<span class="line"><span>cli_impl        → config, contracts, models, execution, agents, output_parser, operations, orchestration_modes</span></span>
<span class="line"><span>cli             → config, contracts, models, execution, agents, output_parser, cli_impl, operations, orchestration_modes</span></span>
<span class="line"><span>mcp_server      → config, contracts, models, execution, agents, output_parser, operations, orchestration_modes, cli_impl</span></span>
<span class="line"><span>main            → config, contracts, models, execution, agents, cli_impl, cli</span></span></code></pre><div class="line-numbers-wrapper" aria-hidden="true"><span class="line-number">1</span><br><span class="line-number">2</span><br><span class="line-number">3</span><br><span class="line-number">4</span><br><span class="line-number">5</span><br><span class="line-number">6</span><br><span class="line-number">7</span><br><span class="line-number">8</span><br><span class="line-number">9</span><br><span class="line-number">10</span><br><span class="line-number">11</span><br><span class="line-number">12</span><br><span class="line-number">13</span><br></div></div><hr><h2 id="rules" tabindex="-1">Rules <a class="header-anchor" href="#rules" aria-label="Permalink to &quot;Rules&quot;">​</a></h2><ul><li>undefined<strong>contracts:</strong> Schema, adapters, validation, policy, telemetry. No agents/execution.</li><li>undefined<strong>agents:</strong> Runners, registry, resilience, state_machine. May use contracts.</li><li>undefined<strong>cli_impl:</strong> Implementation shared by CLI and MCP. May use all core layers.</li><li>undefined<strong>mcp_server:</strong> MCP tools/resources. May use cli_impl and core layers.</li></ul><hr><h2 id="verification" tabindex="-1">Verification <a class="header-anchor" href="#verification" aria-label="Permalink to &quot;Verification&quot;">​</a></h2><div class="language-bash vp-adaptive-theme line-numbers-mode"><button title="Copy Code" class="copy"></button><span class="lang">bash</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="${ssrRenderStyle({ "--shiki-light": "#6F42C1", "--shiki-dark": "#B392F0" })}">python</span><span style="${ssrRenderStyle({ "--shiki-light": "#032F62", "--shiki-dark": "#9ECBFF" })}"> scripts/check_boundaries.py</span></span>
<span class="line"><span style="${ssrRenderStyle({ "--shiki-light": "#6A737D", "--shiki-dark": "#6A737D" })}"># or</span></span>
<span class="line"><span style="${ssrRenderStyle({ "--shiki-light": "#6F42C1", "--shiki-dark": "#B392F0" })}">pytest</span><span style="${ssrRenderStyle({ "--shiki-light": "#032F62", "--shiki-dark": "#9ECBFF" })}"> tests/test_ci_architecture.py</span><span style="${ssrRenderStyle({ "--shiki-light": "#005CC5", "--shiki-dark": "#79B8FF" })}"> -v</span></span></code></pre><div class="line-numbers-wrapper" aria-hidden="true"><span class="line-number">1</span><br><span class="line-number">2</span><br><span class="line-number">3</span><br></div></div><hr><h2 id="see-also" tabindex="-1">See also <a class="header-anchor" href="#see-also" aria-label="Permalink to &quot;See also&quot;">​</a></h2><ul><li><a href="./reference/WORK_STREAM.html">WORK_STREAM.md</a> — canonical backlog</li><li><a href="./plans/05-ARCHITECTURE.html">05-ARCHITECTURE.md</a> — architecture overview</li><li><a href="./plans/00-MASTER-INDEX.html">00-MASTER-INDEX.md</a> — plan index</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("ARCHITECTURE_LAYERS.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const ARCHITECTURE_LAYERS = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  ARCHITECTURE_LAYERS as default
};
