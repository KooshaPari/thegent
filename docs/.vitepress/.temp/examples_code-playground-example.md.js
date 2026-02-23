import { resolveComponent, useSSRContext } from "vue";
import { ssrRenderAttrs, ssrRenderComponent } from "vue/server-renderer";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"CodePlayground Examples","description":"","frontmatter":{},"headers":[],"relativePath":"examples/code-playground-example.md","filePath":"examples/code-playground-example.md","lastUpdated":1771753292000}');
const _sfc_main = { name: "examples/code-playground-example.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  const _component_CodePlayground = resolveComponent("CodePlayground");
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="codeplayground-examples" tabindex="-1">CodePlayground Examples <a class="header-anchor" href="#codeplayground-examples" aria-label="Permalink to &quot;CodePlayground Examples&quot;">​</a></h1><p>This page demonstrates the CodePlayground component for interactive code examples.</p><hr><h2 id="python-example" tabindex="-1">Python Example <a class="header-anchor" href="#python-example" aria-label="Permalink to &quot;Python Example&quot;">​</a></h2>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "python",
    title: "Agent Example",
    code: "from thegent import Agent\\n\\nagent = Agent('codex')\\nresult = agent.run('Hello world')\\nprint(result)"
  }, null, _parent));
  _push(`<hr><h2 id="bash-example" tabindex="-1">Bash Example <a class="header-anchor" href="#bash-example" aria-label="Permalink to &quot;Bash Example&quot;">​</a></h2>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "bash",
    title: "CLI Example",
    code: "thegent run codex 'Fix this bug'\\nthegent list agents\\nthegent status"
  }, null, _parent));
  _push(`<hr><h2 id="javascript-example" tabindex="-1">JavaScript Example <a class="header-anchor" href="#javascript-example" aria-label="Permalink to &quot;JavaScript Example&quot;">​</a></h2>`);
  _push(ssrRenderComponent(_component_CodePlayground, {
    lang: "javascript",
    title: "API Example",
    code: "const agent = new Agent('codex');\\nconst result = await agent.run('Hello world');\\nconsole.log(result);"
  }, null, _parent));
  _push(`<hr><h2 id="features" tabindex="-1">Features <a class="header-anchor" href="#features" aria-label="Permalink to &quot;Features&quot;">​</a></h2><ul><li>undefined<strong>Copy Code</strong>: Click the 📋 button to copy code</li><li>undefined<strong>Run Code</strong>: Click ▶ Run to execute (ready for API integration)</li><li>undefined<strong>Language Badge</strong>: Shows the programming language</li><li>undefined<strong>Output Display</strong>: Shows execution results or errors</li><li>undefined<strong>Dark Mode</strong>: Automatically adapts to theme</li></ul><hr><p>undefined<strong>See Also</strong>: <a href="./../guides/VITEPRESS_USAGE_GUIDE.html">VITEPRESS_USAGE_GUIDE.md</a></p></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("examples/code-playground-example.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const codePlaygroundExample = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  codePlaygroundExample as default
};
