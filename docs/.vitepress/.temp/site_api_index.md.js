import { ssrRenderAttrs, ssrRenderStyle } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"API","description":"","frontmatter":{},"headers":[],"relativePath":"site/api/index.md","filePath":"site/api/index.md","lastUpdated":1771678191000}');
const _sfc_main = { name: "site/api/index.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="api" tabindex="-1">API <a class="header-anchor" href="#api" aria-label="Permalink to &quot;API&quot;">​</a></h1><p>The API section is the index for generated and hand-authored API docs.</p><h2 id="current-surface" tabindex="-1">Current Surface <a class="header-anchor" href="#current-surface" aria-label="Permalink to &quot;Current Surface&quot;">​</a></h2><ul><li>CLI-first operations for agent execution and governance</li><li>MCP tools/resources exposed through <code>thegent serve</code></li><li>Optional generated TypeScript reference (when present)</li></ul><h2 id="generate-typescript-api-docs" tabindex="-1">Generate TypeScript API Docs <a class="header-anchor" href="#generate-typescript-api-docs" aria-label="Permalink to &quot;Generate TypeScript API Docs&quot;">​</a></h2><p>From repository root:</p><div class="language-bash vp-adaptive-theme line-numbers-mode"><button title="Copy Code" class="copy"></button><span class="lang">bash</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="${ssrRenderStyle({ "--shiki-light": "#6F42C1", "--shiki-dark": "#B392F0" })}">./scripts/generate-api-docs-ts.sh</span></span></code></pre><div class="line-numbers-wrapper" aria-hidden="true"><span class="line-number">1</span><br></div></div><p>Generated pages (if source files are detected) are written under <code>docs/site/api/</code>.</p><h2 id="practical-next-steps" tabindex="-1">Practical Next Steps <a class="header-anchor" href="#practical-next-steps" aria-label="Permalink to &quot;Practical Next Steps&quot;">​</a></h2><ul><li>Add module-specific API pages as generated docs become available.</li><li>Cross-link API entries to <a href="/reference/">Reference</a> pages for operational context.</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("site/api/index.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const index = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  index as default
};
