import { resolveComponent, useSSRContext } from "vue";
import { ssrRenderAttrs, ssrRenderComponent, ssrRenderStyle } from "vue/server-renderer";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Demo GIF Examples","description":"","frontmatter":{},"headers":[],"relativePath":"examples/demo-gif-example.md","filePath":"examples/demo-gif-example.md","lastUpdated":1771753292000}');
const _sfc_main = { name: "examples/demo-gif-example.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  const _component_DemoGif = resolveComponent("DemoGif");
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="demo-gif-examples" tabindex="-1">Demo GIF Examples <a class="header-anchor" href="#demo-gif-examples" aria-label="Permalink to &quot;Demo GIF Examples&quot;">​</a></h1><p>This page demonstrates how to use the DemoGif component.</p><hr><h2 id="cli-demo" tabindex="-1">CLI Demo <a class="header-anchor" href="#cli-demo" aria-label="Permalink to &quot;CLI Demo&quot;">​</a></h2>`);
  _push(ssrRenderComponent(_component_DemoGif, {
    src: "cli-demo.gif",
    alt: "CLI Demo",
    caption: "Running thegent CLI commands"
  }, null, _parent));
  _push(`<hr><h2 id="web-demo" tabindex="-1">Web Demo <a class="header-anchor" href="#web-demo" aria-label="Permalink to &quot;Web Demo&quot;">​</a></h2>`);
  _push(ssrRenderComponent(_component_DemoGif, {
    src: "web-demo.gif",
    alt: "Web Interface Demo",
    caption: "Using thegent web interface"
  }, null, _parent));
  _push(`<hr><h2 id="creating-demo-gifs" tabindex="-1">Creating Demo GIFs <a class="header-anchor" href="#creating-demo-gifs" aria-label="Permalink to &quot;Creating Demo GIFs&quot;">​</a></h2><h3 id="using-vhs-terminal-recordings" tabindex="-1">Using VHS (Terminal Recordings) <a class="header-anchor" href="#using-vhs-terminal-recordings" aria-label="Permalink to &quot;Using VHS (Terminal Recordings)&quot;">​</a></h3><ol><li>Create a <code>.tape</code> file in <code>docs/demos/cli/</code>:</li></ol><div class="language-tape vp-adaptive-theme line-numbers-mode"><button title="Copy Code" class="copy"></button><span class="lang">tape</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span>Output cli-demo.gif</span></span>
<span class="line"><span>Set FontSize 14</span></span>
<span class="line"><span>Set Width 1200</span></span>
<span class="line"><span>Set Height 600</span></span>
<span class="line"><span>Set Theme &quot;Catppuccin Mocha&quot;</span></span>
<span class="line"><span></span></span>
<span class="line"><span>Type &quot;thegent run codex &#39;Hello world&#39;&quot;</span></span>
<span class="line"><span>Sleep 500ms</span></span>
<span class="line"><span>Enter</span></span>
<span class="line"><span>Sleep 2s</span></span></code></pre><div class="line-numbers-wrapper" aria-hidden="true"><span class="line-number">1</span><br><span class="line-number">2</span><br><span class="line-number">3</span><br><span class="line-number">4</span><br><span class="line-number">5</span><br><span class="line-number">6</span><br><span class="line-number">7</span><br><span class="line-number">8</span><br><span class="line-number">9</span><br><span class="line-number">10</span><br></div></div><ol start="2"><li>Generate GIF:</li></ol><div class="language-bash vp-adaptive-theme line-numbers-mode"><button title="Copy Code" class="copy"></button><span class="lang">bash</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="${ssrRenderStyle({ "--shiki-light": "#6F42C1", "--shiki-dark": "#B392F0" })}">./scripts/generate-demo-gifs.sh</span></span></code></pre><div class="line-numbers-wrapper" aria-hidden="true"><span class="line-number">1</span><br></div></div><h3 id="using-playwright-browser-recordings" tabindex="-1">Using Playwright (Browser Recordings) <a class="header-anchor" href="#using-playwright-browser-recordings" aria-label="Permalink to &quot;Using Playwright (Browser Recordings)&quot;">​</a></h3><ol><li>Create a <code>.ts</code> file in <code>docs/demos/web/</code>:</li></ol><div class="language-typescript vp-adaptive-theme line-numbers-mode"><button title="Copy Code" class="copy"></button><span class="lang">typescript</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="${ssrRenderStyle({ "--shiki-light": "#D73A49", "--shiki-dark": "#F97583" })}">import</span><span style="${ssrRenderStyle({ "--shiki-light": "#24292E", "--shiki-dark": "#E1E4E8" })}"> { test } </span><span style="${ssrRenderStyle({ "--shiki-light": "#D73A49", "--shiki-dark": "#F97583" })}">from</span><span style="${ssrRenderStyle({ "--shiki-light": "#032F62", "--shiki-dark": "#9ECBFF" })}"> &#39;@playwright/test&#39;</span></span>
<span class="line"></span>
<span class="line"><span style="${ssrRenderStyle({ "--shiki-light": "#6F42C1", "--shiki-dark": "#B392F0" })}">test</span><span style="${ssrRenderStyle({ "--shiki-light": "#24292E", "--shiki-dark": "#E1E4E8" })}">(</span><span style="${ssrRenderStyle({ "--shiki-light": "#032F62", "--shiki-dark": "#9ECBFF" })}">&#39;demo&#39;</span><span style="${ssrRenderStyle({ "--shiki-light": "#24292E", "--shiki-dark": "#E1E4E8" })}">, </span><span style="${ssrRenderStyle({ "--shiki-light": "#D73A49", "--shiki-dark": "#F97583" })}">async</span><span style="${ssrRenderStyle({ "--shiki-light": "#24292E", "--shiki-dark": "#E1E4E8" })}"> ({ </span><span style="${ssrRenderStyle({ "--shiki-light": "#E36209", "--shiki-dark": "#FFAB70" })}">page</span><span style="${ssrRenderStyle({ "--shiki-light": "#24292E", "--shiki-dark": "#E1E4E8" })}"> }) </span><span style="${ssrRenderStyle({ "--shiki-light": "#D73A49", "--shiki-dark": "#F97583" })}">=&gt;</span><span style="${ssrRenderStyle({ "--shiki-light": "#24292E", "--shiki-dark": "#E1E4E8" })}"> {</span></span>
<span class="line"><span style="${ssrRenderStyle({ "--shiki-light": "#D73A49", "--shiki-dark": "#F97583" })}">  await</span><span style="${ssrRenderStyle({ "--shiki-light": "#24292E", "--shiki-dark": "#E1E4E8" })}"> page.</span><span style="${ssrRenderStyle({ "--shiki-light": "#6F42C1", "--shiki-dark": "#B392F0" })}">goto</span><span style="${ssrRenderStyle({ "--shiki-light": "#24292E", "--shiki-dark": "#E1E4E8" })}">(</span><span style="${ssrRenderStyle({ "--shiki-light": "#032F62", "--shiki-dark": "#9ECBFF" })}">&#39;https://example.com&#39;</span><span style="${ssrRenderStyle({ "--shiki-light": "#24292E", "--shiki-dark": "#E1E4E8" })}">)</span></span>
<span class="line"><span style="${ssrRenderStyle({ "--shiki-light": "#6A737D", "--shiki-dark": "#6A737D" })}">  // ... record interactions</span></span>
<span class="line"><span style="${ssrRenderStyle({ "--shiki-light": "#24292E", "--shiki-dark": "#E1E4E8" })}">})</span></span></code></pre><div class="line-numbers-wrapper" aria-hidden="true"><span class="line-number">1</span><br><span class="line-number">2</span><br><span class="line-number">3</span><br><span class="line-number">4</span><br><span class="line-number">5</span><br><span class="line-number">6</span><br></div></div><ol start="2"><li>Generate GIF:</li></ol><div class="language-bash vp-adaptive-theme line-numbers-mode"><button title="Copy Code" class="copy"></button><span class="lang">bash</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="${ssrRenderStyle({ "--shiki-light": "#6F42C1", "--shiki-dark": "#B392F0" })}">npx</span><span style="${ssrRenderStyle({ "--shiki-light": "#032F62", "--shiki-dark": "#9ECBFF" })}"> playwright</span><span style="${ssrRenderStyle({ "--shiki-light": "#032F62", "--shiki-dark": "#9ECBFF" })}"> test</span><span style="${ssrRenderStyle({ "--shiki-light": "#005CC5", "--shiki-dark": "#79B8FF" })}"> --gif</span></span></code></pre><div class="line-numbers-wrapper" aria-hidden="true"><span class="line-number">1</span><br></div></div><hr><p>undefined<strong>See Also</strong>:</p><ul><li><a href="./../guides/VITEPRESS_USAGE_GUIDE.html">VITEPRESS_USAGE_GUIDE.md</a></li><li><a href="./../guides/AUTOMATED_DEMOS.html">AUTOMATED_DEMOS.md</a></li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("examples/demo-gif-example.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const demoGifExample = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  demoGifExample as default
};
