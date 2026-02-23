import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Guides","description":"","frontmatter":{},"headers":[],"relativePath":"guides/index.md","filePath":"guides/index.md","lastUpdated":1771753292000}');
const _sfc_main = { name: "guides/index.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="guides" tabindex="-1">Guides <a class="header-anchor" href="#guides" aria-label="Permalink to &quot;Guides&quot;">​</a></h1><p>Welcome to the thegent guides section.</p><h2 id="available-guides" tabindex="-1">Available Guides <a class="header-anchor" href="#available-guides" aria-label="Permalink to &quot;Available Guides&quot;">​</a></h2><ul><li><a href="/guides/INSTALLATION.html">Installation</a></li><li><a href="/guides/QUICK_REFERENCE.html">Quick Reference</a></li><li><a href="/guides/DOTFILES_INTEGRATION.html">Dotfile Manager Integration</a></li><li><a href="/guides/AGENT_INSTRUCTIONS_THEGENT.html">Agent Instructions</a></li><li><a href="/guides/anti-patterns.html">Anti-Patterns</a></li><li><a href="/guides/architecture-enforcement.html">Architecture Enforcement</a></li><li><a href="/guides/JOB_POOL_USAGE.html">Job Pool Usage</a></li><li><a href="/guides/OXLINT_INTEGRATION_GUIDE.html">OXLINT Integration</a></li><li><a href="/guides/PHASE_4_QUICK_START.html">Phase 4 Quick Start</a></li><li><a href="/guides/PROVIDER_SETUP_GUIDE.html">Provider Setup</a></li><li><a href="/guides/START_HERE.html">Start Here</a></li><li><a href="/guides/TASK_ROUTING_QUICK_REF.html">Task Routing</a></li><li><a href="/guides/TESTING.html">Testing</a></li><li><a href="/guides/TROUBLESHOOTING.html">Troubleshooting</a></li></ul><hr><h2 id="see-also" tabindex="-1">See also <a class="header-anchor" href="#see-also" aria-label="Permalink to &quot;See also&quot;">​</a></h2><ul><li><a href="./../reference/WORK_STREAM.html">WORK_STREAM.md</a> — canonical backlog</li><li><a href="./../plans/00-MASTER-INDEX.html">00-MASTER-INDEX.md</a> — plan index</li></ul><hr><h2 id="extension-summary" tabindex="-1">EXTENSION_SUMMARY <a class="header-anchor" href="#extension-summary" aria-label="Permalink to &quot;EXTENSION_SUMMARY&quot;">​</a></h2><p>undefined<strong>Extended on:</strong> 2026-02-17 undefined<strong>Extended by:</strong> Claude Code</p><h3 id="changes-made" tabindex="-1">Changes Made <a class="header-anchor" href="#changes-made" aria-label="Permalink to &quot;Changes Made&quot;">​</a></h3><ol><li>Added practical implementation patterns</li><li>Added configuration examples</li><li>Enhanced cross-references to related documentation</li></ol><h3 id="cross-references-added" tabindex="-1">Cross-References Added <a class="header-anchor" href="#cross-references-added" aria-label="Permalink to &quot;Cross-References Added&quot;">​</a></h3><ul><li>Related research and implementation guides</li><li>WORK_STREAM.md for tracking</li></ul><h3 id="practical-additions" tabindex="-1">Practical Additions <a class="header-anchor" href="#practical-additions" aria-label="Permalink to &quot;Practical Additions&quot;">​</a></h3><ul><li>Implementation templates</li><li>Configuration examples</li><li>Best practices</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("guides/index.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const index = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  index as default
};
