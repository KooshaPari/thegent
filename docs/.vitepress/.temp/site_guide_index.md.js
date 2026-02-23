import { ssrRenderAttrs, ssrRenderStyle } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Guide","description":"","frontmatter":{},"headers":[],"relativePath":"site/guide/index.md","filePath":"site/guide/index.md","lastUpdated":1771678191000}');
const _sfc_main = { name: "site/guide/index.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="guide" tabindex="-1">Guide <a class="header-anchor" href="#guide" aria-label="Permalink to &quot;Guide&quot;">​</a></h1><p>This section helps you install, configure, and run <code>thegent</code> day-to-day.</p><h2 id="start-here" tabindex="-1">Start Here <a class="header-anchor" href="#start-here" aria-label="Permalink to &quot;Start Here&quot;">​</a></h2><ul><li><a href="./getting-started.html">Getting Started</a> for a 5-minute first run.</li><li><a href="./installation.html">Installation</a> for bootstrap, pip, and source installs.</li><li><a href="./cli-reference.html">CLI Reference</a> for command syntax and flags.</li><li><a href="./providers.html">Providers</a> for provider/model setup.</li><li><a href="./architecture.html">Architecture</a> for runtime design.</li><li><a href="./governance.html">Governance</a> for policy and quality controls.</li></ul><h2 id="typical-workflow" tabindex="-1">Typical Workflow <a class="header-anchor" href="#typical-workflow" aria-label="Permalink to &quot;Typical Workflow&quot;">​</a></h2><div class="language-bash vp-adaptive-theme line-numbers-mode"><button title="Copy Code" class="copy"></button><span class="lang">bash</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="${ssrRenderStyle({ "--shiki-light": "#6F42C1", "--shiki-dark": "#B392F0" })}">thegent</span><span style="${ssrRenderStyle({ "--shiki-light": "#032F62", "--shiki-dark": "#9ECBFF" })}"> doctor</span></span>
<span class="line"><span style="${ssrRenderStyle({ "--shiki-light": "#6F42C1", "--shiki-dark": "#B392F0" })}">thegent</span><span style="${ssrRenderStyle({ "--shiki-light": "#032F62", "--shiki-dark": "#9ECBFF" })}"> run</span><span style="${ssrRenderStyle({ "--shiki-light": "#032F62", "--shiki-dark": "#9ECBFF" })}"> &quot;summarize current repo status&quot;</span><span style="${ssrRenderStyle({ "--shiki-light": "#032F62", "--shiki-dark": "#9ECBFF" })}"> free</span></span>
<span class="line"><span style="${ssrRenderStyle({ "--shiki-light": "#6F42C1", "--shiki-dark": "#B392F0" })}">thegent</span><span style="${ssrRenderStyle({ "--shiki-light": "#032F62", "--shiki-dark": "#9ECBFF" })}"> plan</span><span style="${ssrRenderStyle({ "--shiki-light": "#032F62", "--shiki-dark": "#9ECBFF" })}"> do-next</span></span>
<span class="line"><span style="${ssrRenderStyle({ "--shiki-light": "#6F42C1", "--shiki-dark": "#B392F0" })}">thegent</span><span style="${ssrRenderStyle({ "--shiki-light": "#032F62", "--shiki-dark": "#9ECBFF" })}"> plan</span><span style="${ssrRenderStyle({ "--shiki-light": "#032F62", "--shiki-dark": "#9ECBFF" })}"> loop</span></span></code></pre><div class="line-numbers-wrapper" aria-hidden="true"><span class="line-number">1</span><br><span class="line-number">2</span><br><span class="line-number">3</span><br><span class="line-number">4</span><br></div></div><p>Use <code>thegent ps</code> to inspect running and completed sessions.</p></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("site/guide/index.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const index = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  index as default
};
