import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Cross-Project Links Test","description":"","frontmatter":{},"headers":[],"relativePath":"cross-links-test.md","filePath":"cross-links-test.md","lastUpdated":1771753292000}');
const _sfc_main = { name: "cross-links-test.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="cross-project-links-test" tabindex="-1">Cross-Project Links Test <a class="header-anchor" href="#cross-project-links-test" aria-label="Permalink to &quot;Cross-Project Links Test&quot;">​</a></h1><p>This page tests the cross-project link plugin functionality.</p><h2 id="links-to-other-projects" tabindex="-1">Links to Other Projects <a class="header-anchor" href="#links-to-other-projects" aria-label="Permalink to &quot;Links to Other Projects&quot;">​</a></h2><ul><li><a href="file:///Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/docs-dist/main/ARCHITECTURE_LAYERS.html" target="_blank" class="cross-project-link">thegent Architecture</a></li><li><a href="file:///Users/kooshapari/Dev/job-hunter/docs-dist/docs/specs/PRD.html" target="_blank" class="cross-project-link">jobhunter PRD</a></li><li><a href="file:///Users/kooshapari/temp-PRODVERCEL-485/kush/heliosShield/docs-dist/README.html" target="_blank" class="cross-project-link">heliosShield Guide</a></li><li><a href="file:///Users/kooshapari/kush/trace/docs-dist/docs/index.html" target="_blank" class="cross-project-link">trace Overview</a></li></ul><hr><h2 id="see-also" tabindex="-1">See also <a class="header-anchor" href="#see-also" aria-label="Permalink to &quot;See also&quot;">​</a></h2><ul><li><a href="./../reference/WORK_STREAM.html">WORK_STREAM.md</a> — canonical backlog</li><li><a href="./../plans/00-MASTER-INDEX.html">00-MASTER-INDEX.md</a> — plan index</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("cross-links-test.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const crossLinksTest = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  crossLinksTest as default
};
