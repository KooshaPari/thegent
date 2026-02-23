import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Terminology: Layer Vocabulary","description":"","frontmatter":{},"headers":[],"relativePath":"governance/TERMINOLOGY_LAYERS.md","filePath":"governance/TERMINOLOGY_LAYERS.md","lastUpdated":1771574377000}');
const _sfc_main = { name: "governance/TERMINOLOGY_LAYERS.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="terminology-layer-vocabulary" tabindex="-1">Terminology: Layer Vocabulary <a class="header-anchor" href="#terminology-layer-vocabulary" aria-label="Permalink to &quot;Terminology: Layer Vocabulary&quot;">​</a></h1><p>undefined<strong>Purpose:</strong> Establish consistent vocabulary for ease of communication across thegent, harnesses, and LLM infrastructure.</p><p>undefined<strong>Reference:</strong> CLAUDE.md § Terminology (Layer Vocabulary)</p><hr><h2 id="core-terms" tabindex="-1">Core Terms <a class="header-anchor" href="#core-terms" aria-label="Permalink to &quot;Core Terms&quot;">​</a></h2><h3 id="harness" tabindex="-1">Harness <a class="header-anchor" href="#harness" aria-label="Permalink to &quot;Harness&quot;">​</a></h3><p>The <strong>agent layer</strong>. Executes agent logic, tools, and workflows. May or may not come with a CLI, API, or other interface.</p><p>undefined<strong>Examples:</strong>undefined</p><ul><li>Codex CLI</li><li>Claude Code CLI</li><li>Claude Agent SDK</li><li>Factory Droid</li><li>Cursor (agent mode)</li></ul><h3 id="llm" tabindex="-1">LLM <a class="header-anchor" href="#llm" aria-label="Permalink to &quot;LLM&quot;">​</a></h3><p>The <strong>model</strong> (as known). The underlying language model invoked for completions.</p><p>undefined<strong>Examples:</strong> GPT-5, Claude, Gemini, GLM-5, etc.</p><h3 id="presentation-layer" tabindex="-1">Presentation Layer <a class="header-anchor" href="#presentation-layer" aria-label="Permalink to &quot;Presentation Layer&quot;">​</a></h3><p>The <strong>UI layer</strong> of a harness. How the user interacts with the agent.</p><p>undefined<strong>Examples:</strong> Terminal UI, IDE panel, web UI, chat interface.</p><h3 id="various-layers" tabindex="-1">Various Layers <a class="header-anchor" href="#various-layers" aria-label="Permalink to &quot;Various Layers&quot;">​</a></h3><p>Layers <strong>between and around</strong> the harness, LLM, and presentation. Include routing, proxy, auth, orchestration.</p><p>undefined<strong>Examples:</strong>undefined</p><ul><li>CLIProxyAPIPlus (proxy, auth, routing)</li><li>LiteLLM Router (routing, fallback)</li><li>thegent (orchestration, delegation)</li></ul><hr><h2 id="layer-diagram-conceptual" tabindex="-1">Layer Diagram (Conceptual) <a class="header-anchor" href="#layer-diagram-conceptual" aria-label="Permalink to &quot;Layer Diagram (Conceptual)&quot;">​</a></h2><div class="language- vp-adaptive-theme line-numbers-mode"><button title="Copy Code" class="copy"></button><span class="lang"></span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span>┌─────────────────────────────────────────────────────────┐</span></span>
<span class="line"><span>│  Presentation layer  (UI: terminal, IDE, web)           │</span></span>
<span class="line"><span>├─────────────────────────────────────────────────────────┤</span></span>
<span class="line"><span>│  Harness  (agent layer: Codex CLI, Claude Code, Droid)  │</span></span>
<span class="line"><span>├─────────────────────────────────────────────────────────┤</span></span>
<span class="line"><span>│  Various layers  (routing, proxy, auth, orchestration)   │</span></span>
<span class="line"><span>├─────────────────────────────────────────────────────────┤</span></span>
<span class="line"><span>│  LLM  (model: GPT-5, Claude, Gemini, etc.)              │</span></span>
<span class="line"><span>└─────────────────────────────────────────────────────────┘</span></span></code></pre><div class="line-numbers-wrapper" aria-hidden="true"><span class="line-number">1</span><br><span class="line-number">2</span><br><span class="line-number">3</span><br><span class="line-number">4</span><br><span class="line-number">5</span><br><span class="line-number">6</span><br><span class="line-number">7</span><br><span class="line-number">8</span><br><span class="line-number">9</span><br></div></div><hr><h2 id="usage" tabindex="-1">Usage <a class="header-anchor" href="#usage" aria-label="Permalink to &quot;Usage&quot;">​</a></h2><ul><li>Use <strong>harness</strong> when referring to the agent execution layer (Codex, Claude Code, Droid, Cursor).</li><li>Use <strong>LLM</strong> when referring to the model.</li><li>Use <strong>presentation layer</strong> when referring to UI/UX of a harness.</li><li>Use <strong>various layers</strong> when referring to routing, proxy, auth, orchestration between harness and LLM.</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("governance/TERMINOLOGY_LAYERS.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const TERMINOLOGY_LAYERS = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  TERMINOLOGY_LAYERS as default
};
