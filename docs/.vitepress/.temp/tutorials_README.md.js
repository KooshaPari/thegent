import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { a as _export_sfc } from "./vue.DCJT_Tnz.js";
import "./app.js";
import "@vueuse/core";
import "./mermaid.OkLrB7RK.js";
import "mermaid";
const __pageData = JSON.parse('{"title":"Thegent Tutorials","description":"","frontmatter":{},"headers":[],"relativePath":"tutorials/README.md","filePath":"tutorials/README.md","lastUpdated":1771574377000}');
const _sfc_main = { name: "tutorials/README.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="thegent-tutorials" tabindex="-1">Thegent Tutorials <a class="header-anchor" href="#thegent-tutorials" aria-label="Permalink to &quot;Thegent Tutorials&quot;">​</a></h1><p>Step-by-step guides for common tasks and workflows.</p><h2 id="getting-started" tabindex="-1">Getting Started <a class="header-anchor" href="#getting-started" aria-label="Permalink to &quot;Getting Started&quot;">​</a></h2><ol><li><a href="./01-quick-start.html">Quick Start</a> - Get up and running in 5 minutes</li><li><a href="./02-configuration.html">Configuration</a> - Configure thegent for your needs</li><li><a href="./03-first-agent-run.html">First Agent Run</a> - Run your first agent task</li></ol><h2 id="intermediate" tabindex="-1">Intermediate <a class="header-anchor" href="#intermediate" aria-label="Permalink to &quot;Intermediate&quot;">​</a></h2><ol start="4"><li><a href="./04-multi-agent-workflows.html">Multi-Agent Workflows</a> - Orchestrate multiple agents</li><li><a href="./05-background-sessions.html">Background Sessions</a> - Run agents in the background</li><li><a href="./06-work-stream-management.html">Work Stream Management</a> - Manage tasks and plans</li></ol><h2 id="advanced" tabindex="-1">Advanced <a class="header-anchor" href="#advanced" aria-label="Permalink to &quot;Advanced&quot;">​</a></h2><ol start="7"><li><a href="./07-polyglot-runtimes.html">Polyglot Runtimes</a> - Use PyPy, CPython, Rust, Go together</li><li><a href="./08-performance-optimization.html">Performance Optimization</a> - Optimize for speed</li><li><a href="./09-governance-policies.html">Governance &amp; Policies</a> - Set up governance rules</li><li><a href="./10-custom-agents.html">Custom Agents</a> - Create custom agents</li></ol><h2 id="troubleshooting" tabindex="-1">Troubleshooting <a class="header-anchor" href="#troubleshooting" aria-label="Permalink to &quot;Troubleshooting&quot;">​</a></h2><ul><li><a href="./troubleshooting.html">Common Issues</a> - Solutions to common problems</li><li><a href="./performance-tuning.html">Performance Tuning</a> - Optimize performance</li></ul><h2 id="contributing" tabindex="-1">Contributing <a class="header-anchor" href="#contributing" aria-label="Permalink to &quot;Contributing&quot;">​</a></h2><p>To add a new tutorial:</p><ol><li>Create a markdown file following the naming convention <code>NN-topic.md</code></li><li>Include step-by-step instructions with code examples</li><li>Add links from relevant sections</li><li>Update this README</li></ol></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("tutorials/README.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const README = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  README as default
};
