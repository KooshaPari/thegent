// docs/.vitepress/config.ts
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "file:///Users/kooshapari/CodeProjects/Phenotype/repos/thegent/node_modules/vitepress/dist/node/index.js";
import { withMermaid } from "file:///Users/kooshapari/CodeProjects/Phenotype/repos/thegent/node_modules/vitepress-plugin-mermaid/dist/vitepress-plugin-mermaid.es.mjs";
import { imagetools } from "file:///Users/kooshapari/CodeProjects/Phenotype/repos/thegent/node_modules/vite-imagetools/dist/index.js";

// docs/.vitepress/plugins/cross-project-links.ts
var PROJECT_PATHS = {
  "thegent": "/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/docs-dist/main",
  "jobhunter": "/Users/kooshapari/Dev/job-hunter/docs-dist",
  "heliosShield": "/Users/kooshapari/temp-PRODVERCEL-485/kush/heliosShield/docs-dist",
  "trace": "/Users/kooshapari/kush/trace/docs-dist"
};
function crossProjectLinks(md) {
  const defaultRender = md.renderer.rules.link_open || function(tokens, idx, options, _env, self) {
    return self.renderToken(tokens, idx, options);
  };
  md.renderer.rules.link_open = function(tokens, idx, options, env, self) {
    const href = tokens[idx].attrGet("href");
    if (href && href.startsWith("~")) {
      const match = href.match(/^~([^:]+):(.+)$/);
      if (match) {
        const [, project, path] = match;
        const basePath = PROJECT_PATHS[project];
        if (basePath) {
          const htmlPath = path.replace(/\.md$/, ".html").replace(/^\/+/, "");
          tokens[idx].attrSet("href", `file://${basePath}/${htmlPath}`);
          tokens[idx].attrSet("target", "_blank");
          tokens[idx].attrSet("class", "cross-project-link");
        }
      }
    }
    return defaultRender(tokens, idx, options, env, self);
  };
}

// docs/.vitepress/plugins/content-tabs.ts
function parseTabsContent(content) {
  const tabs = [];
  const lines = content.split(/\r?\n/);
  let inTab = false;
  let currentId = "";
  let currentContent = [];
  const tabStart = /^\s*:::\s*tab\s+(.+?)\s*$/;
  const tabEnd = /^\s*:::\s*$/;
  for (const line of lines) {
    const startMatch = line.match(tabStart);
    if (startMatch) {
      if (inTab && currentContent.length > 0) {
        const content2 = currentContent.join("\n").trim();
        tabs.push({ id: currentId, label: currentId, content: content2 });
      }
      inTab = true;
      currentId = startMatch[1].trim();
      currentContent = [];
      continue;
    }
    if (inTab && tabEnd.test(line)) {
      const content2 = currentContent.join("\n").trim();
      tabs.push({ id: currentId, label: currentId, content: content2 });
      inTab = false;
      currentId = "";
      currentContent = [];
      continue;
    }
    if (inTab) {
      currentContent.push(line);
    }
  }
  if (inTab && currentContent.length > 0) {
    const content2 = currentContent.join("\n").trim();
    tabs.push({ id: currentId, label: currentId, content: content2 });
  }
  return { tabs };
}
function normalizeTabId(rawId) {
  return rawId.trim().toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "");
}
function contentTabsPlugin(md) {
  const parseTabsBlock = (state, startLine, endLine) => {
    const tabStart = /^\s*:::\s*tab\s+(.+?)\s*$/;
    const tabsStart = /^\s*:::\s*tabs\s*$/;
    const tabsEnd = /^\s*:::\s*$/;
    let closingLine = -1;
    let line = startLine + 1;
    let depth = 1;
    let inTab = false;
    for (; line <= endLine; line++) {
      const lineStart = state.bMarks[line] + state.tShift[line];
      const lineEnd = state.eMarks[line];
      const lineContent = state.src.slice(lineStart, lineEnd);
      if (tabsStart.test(lineContent) && line !== startLine) {
        depth += 1;
        continue;
      }
      if (tabsEnd.test(lineContent)) {
        if (inTab) {
          inTab = false;
          continue;
        }
        if (depth <= 1) {
          closingLine = line;
          break;
        }
        depth -= 1;
        continue;
      }
      if (tabStart.test(lineContent)) {
        inTab = true;
        continue;
      }
    }
    if (closingLine === -1) {
      return { content: "", tabs: [], closingLine: -1 };
    }
    const rawContent = state.src.slice(
      state.bMarks[startLine + 1],
      state.bMarks[closingLine]
    );
    const { tabs } = parseTabsContent(rawContent);
    return { content: rawContent, tabs, closingLine };
  };
  const tabsContainer = (state, startLine, endLine, silent) => {
    const start = state.bMarks[startLine] + state.tShift[startLine];
    const max = state.eMarks[startLine];
    const line = state.src.slice(start, max);
    if (!line.match(/^\s*:::\s*tabs\s*$/)) {
      return false;
    }
    if (silent) {
      return true;
    }
    const parsed = parseTabsBlock(state, startLine, endLine);
    const closingLine = parsed.closingLine;
    const { tabs } = parsed;
    if (closingLine === -1) {
      const markerToken2 = state.push("tabs_marker", "", 0);
      markerToken2.content = JSON.stringify({ error: "tabs block is missing closing :::", tabs: [] });
      markerToken2.map = [startLine, endLine];
      state.line = endLine + 1;
      return true;
    }
    if (tabs.length === 0) {
      const markerToken2 = state.push("tabs_marker", "", 0);
      markerToken2.content = JSON.stringify({ error: "tabs block has no valid tab sections", tabs: [] });
      markerToken2.map = [startLine, closingLine];
      state.line = closingLine + 1;
      return true;
    }
    const tabsId = `tabs-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const markerToken = state.push("tabs_marker", "", 0);
    markerToken.content = JSON.stringify({ tabs, tabsId });
    markerToken.map = [startLine, closingLine];
    state.line = closingLine + 1;
    return true;
  };
  md.block.ruler.after("fence", "content_tabs", tabsContainer, {
    alt: ["paragraph", "reference", "blockquote", "list"]
  });
  md.renderer.rules.tabs_marker = (tokens, idx, options, env, self) => {
    const token = tokens[idx];
    try {
      const data = JSON.parse(token.content);
      if (data.error) {
        return `<div class="content-tabs-error">${data.error}</div>`;
      }
      const tabs = data.tabs.map((t) => {
        const id = normalizeTabId(t.id);
        return {
          id,
          label: t.label.charAt(0).toUpperCase() + t.label.slice(1)
        };
      });
      let html = `<div class="content-tabs-wrapper" data-tabs-id="${data.tabsId}">`;
      html += `<div class="content-tabs">`;
      html += `<div class="tab-headers">`;
      tabs.forEach((tab, idx2) => {
        const active = idx2 === 0 ? "active" : "";
        html += `<button class="tab-header ${active}" data-tab="${tab.id}">${tab.label}</button>`;
      });
      html += `</div>`;
      html += `<div class="tab-bodies">`;
      data.tabs.forEach((tab, idx2) => {
        const display = idx2 === 0 ? "block" : "none";
        const normalizedId = normalizeTabId(tab.id);
        html += `<div class="tab-body" data-tab="${normalizedId}" style="display: ${display}">`;
        html += md.render(tab.content);
        html += `</div>`;
      });
      html += `</div></div></div>`;
      return html;
    } catch (e) {
      return `<div class="content-tabs-error">Error parsing tabs</div>`;
    }
  };
}

// docs/.vitepress/plugins/video-embed.ts
function parseVideoDirective(md, _options) {
  const videoBlockRule = (state, startLine, endLine) => {
    const pos = state.bMarks[startLine] + state.tShift[startLine];
    const maximum = state.eMarks[startLine];
    if (pos + 3 > maximum) return false;
    if (state.src.slice(pos, pos + 3) !== ":::") return false;
    const markerCount = 3;
    const markup = state.src.slice(pos, pos + markerCount);
    const params = state.src.slice(pos + markerCount, maximum).trim();
    if (!params.startsWith("video ")) return false;
    const videoSrc = params.slice(6).trim();
    if (!videoSrc) return false;
    let nextLine = startLine + 1;
    while (nextLine < endLine) {
      if (state.bMarks[nextLine] + state.tShift[nextLine] + 3 <= state.eMarks[nextLine]) {
        const closePos = state.bMarks[nextLine] + state.tShift[nextLine];
        if (state.src.slice(closePos, closePos + 3) === ":::") {
          break;
        }
      }
      nextLine++;
    }
    const oldParent = state.parentType;
    state.parentType = "paragraph";
    const token = state.push("video_block", "div", 0);
    token.markup = markup;
    token.meta = { src: videoSrc };
    token.map = [startLine, nextLine + 1];
    state.parentType = oldParent;
    state.line = nextLine + 1;
    return true;
  };
  md.block.ruler.before(
    "fence",
    "video_block",
    videoBlockRule
  );
  md.renderer.rules.video_block = (tokens, idx) => {
    const token = tokens[idx];
    const src = token.meta?.src || "";
    return `<video width="100%" controls>
  <source src="${src}" type="video/webm">
  Your browser does not support the video tag.
</video>
`;
  };
}
function enhanceImageRendering(md, options) {
  const originalImageRule = md.renderer.rules.image;
  md.renderer.rules.image = (tokens, idx, _options, env, renderer) => {
    const token = tokens[idx];
    const src = token.attrGet("src") || "";
    if (src.match(/\.(webm|mp4|ogg|mov)$/i)) {
      const alt = token.content || "Video";
      const width = options.width || "100%";
      const controls = options.controls !== false ? "controls" : "";
      const autoplay = options.autoplay ? "autoplay" : "";
      const loop = options.loop ? "loop" : "";
      const muted = options.muted ? "muted" : "";
      const ext = src.split(".").pop()?.toLowerCase();
      let type = "video/webm";
      if (ext === "mp4") type = "video/mp4";
      else if (ext === "ogg") type = "video/ogg";
      else if (ext === "mov") type = "video/quicktime";
      return `<video width="${width}" ${controls} ${autoplay} ${loop} ${muted}>
  <source src="${src}" type="${type}">
  ${alt}
</video>`;
    }
    return originalImageRule?.(tokens, idx, _options, env, renderer) || "";
  };
}
function videoEmbedPlugin(md, options = {}) {
  const defaultOptions = {
    width: "100%",
    height: "auto",
    controls: true,
    autoplay: false,
    loop: false,
    muted: false,
    ...options
  };
  parseVideoDirective(md, defaultOptions);
  enhanceImageRendering(md, defaultOptions);
}

// docs/.vitepress/sidebar-canonical.ts
var sidebar = {
  "/": [
    {
      text: "Getting Started",
      collapsed: false,
      items: [
        { text: "Home", link: "/" },
        { text: "Start Here", link: "/start-here.md" }
      ]
    },
    {
      text: "Tutorials",
      collapsed: false,
      items: [
        { text: "Tutorials Overview", link: "/tutorials/" },
        { text: "Quick Start", link: "/tutorials/01-quick-start.md" },
        { text: "Configuration", link: "/tutorials/02-configuration.md" }
      ]
    },
    {
      text: "How-to Guides",
      collapsed: false,
      items: [
        { text: "How-to Overview", link: "/how-to/" },
        { text: "Installation", link: "/guides/INSTALLATION.md" },
        { text: "Provider Setup", link: "/guides/PROVIDER_SETUP_GUIDE.md" },
        { text: "Testing", link: "/guides/TESTING.md" },
        { text: "Troubleshooting", link: "/guides/TROUBLESHOOTING.md" }
      ]
    },
    {
      text: "Reference",
      collapsed: false,
      items: [
        { text: "Reference Index", link: "/reference/" },
        { text: "Configuration", link: "/reference/configuration.md" },
        { text: "Routing", link: "/reference/routing.md" },
        { text: "CLAUDE Core Guidelines", link: "/reference/CLAUDE_CORE_GUIDELINES.md" },
        { text: "MCP Retry Policy", link: "/reference/MCP_RETRY_POLICY.md" }
      ]
    },
    {
      text: "Explanation",
      collapsed: false,
      items: [
        { text: "Explanation Overview", link: "/explanation/" },
        { text: "Agent Sandboxing", link: "/architecture/AGENT_SANDBOXING_ARCHITECTURE.md" },
        { text: "Cost Governance", link: "/governance/COST_GOVERNANCE_DESIGN.md" },
        { text: "OPA Integration", link: "/governance/OPA_INTEGRATION_DESIGN.md" }
      ]
    },
    {
      text: "Operations",
      collapsed: false,
      items: [
        { text: "Operations Overview", link: "/operations/" },
        { text: "Journey Traceability", link: "/operations/journey-traceability.md" },
        { text: "Runbooks", link: "/operations/runbooks.md" },
        { text: "Troubleshooting", link: "/operations/troubleshooting.md" }
      ]
    },
    {
      text: "Governance",
      collapsed: false,
      items: [
        { text: "Governance Overview", link: "/governance/" },
        { text: "TDD/BDD/SDD", link: "/governance/TDD_BDD_SDD_GOVERNANCE.md" },
        { text: "Test Strategy", link: "/governance/AGENT_ONLY_TEST_STRATEGY.md" },
        { text: "Terminology", link: "/governance/TERMINOLOGY_LAYERS.md" },
        { text: "Context Docs", link: "/governance/CONTEXT_DOCS_PROCESS.md" }
      ]
    },
    {
      text: "Guides",
      collapsed: true,
      items: [
        { text: "Guides Index", link: "/guides/" },
        { text: "Docs Governance", link: "/guides/VITEPRESS_DOCS_GOVERNANCE.md" },
        { text: "VitePress Setup", link: "/guides/VITEPPRESS_SETUP.md" },
        { text: "VitePress Usage", link: "/guides/VITEPRESS_USAGE_GUIDE.md" },
        { text: "Quick Reference", link: "/guides/QUICK_REFERENCE.md" },
        { text: "Shell Environment", link: "/guides/SHELL_ENVIRONMENT_COMPLETE.md" },
        { text: "Cross-Platform", link: "/guides/CROSS_PLATFORM_COMPLETE.md" }
      ]
    },
    {
      text: "API",
      collapsed: false,
      items: [
        { text: "API Overview", link: "/api/" },
        { text: "API README", link: "/api/README.md" }
      ]
    },
    {
      text: "Architecture",
      collapsed: true,
      items: [
        { text: "Module Dependencies", link: "/architecture/diagrams/module-dependencies.md" },
        { text: "Package Structure", link: "/architecture/diagrams/package-structure.md" }
      ]
    },
    {
      text: "Contracts",
      collapsed: true,
      items: [
        { text: "Contract Authority", link: "/contracts/CONTRACT_AUTHORITY.md" },
        { text: "Fallback Policy", link: "/contracts/FALLBACK_POLICY.md" },
        { text: "Provider Adapter Contracts", link: "/contracts/PROVIDER_ADAPTER_CONTRACTS.md" }
      ]
    },
    {
      text: "Enterprise",
      collapsed: true,
      items: [
        { text: "Operating Model", link: "/enterprise/OPERATING_MODEL.md" },
        { text: "Security Compliance", link: "/enterprise/SECURITY_COMPLIANCE_SIGNOFF.md" },
        { text: "Decommissioning Plan", link: "/enterprise/DECOMMISSIONING_PLAN.md" }
      ]
    },
    {
      text: "Examples",
      collapsed: true,
      items: [
        { text: "Examples Overview", link: "/examples/README.md" },
        { text: "Code Playground", link: "/examples/code-playground-example.md" },
        { text: "Mermaid Diagrams", link: "/examples/mermaid-example.md" },
        { text: "Tooltips", link: "/examples/tooltip-example.md" }
      ]
    }
  ]
};

// docs/.vitepress/config.ts
import { createRequire } from "module";
var __vite_injected_original_import_meta_url = "file:///Users/kooshapari/CodeProjects/Phenotype/repos/thegent/docs/.vitepress/config.ts";
var docsDir = dirname(fileURLToPath(__vite_injected_original_import_meta_url));
var phenodocsRoot = resolve(docsDir, "../../../phenodocs");
var phenodocsTheme = resolve(phenodocsRoot, ".vitepress/theme/index.ts");
var require2 = createRequire(__vite_injected_original_import_meta_url);
var markdownItEmoji = require2("markdown-it-emoji").full;
var katex = require2("markdown-it-mathjax3");
var algoliaAppId = process.env.VITEPRESS_ALGOLIA_APP_ID;
var algoliaApiKey = process.env.VITEPRESS_ALGOLIA_API_KEY;
var algoliaIndexName = process.env.VITEPRESS_ALGOLIA_INDEX_NAME;
var hasAlgolia = Boolean(algoliaAppId && algoliaApiKey && algoliaIndexName);
var repoName = process.env.GITHUB_REPOSITORY?.split("/")[1] || "thegent";
var isPagesBuild = process.env.GITHUB_ACTIONS === "true" || process.env.GITHUB_PAGES === "true";
var docsBaseOverride = process.env.VITEPRESS_BASE;
var docsBase = "/thegent/";
var faviconHref = `${docsBase}favicon.ico`;
var locales = {
  root: { label: "English", lang: "en", title: "thegent", description: "AI Agent Governance & MCP Server" },
  "zh-CN": { label: "\u7B80\u4F53\u4E2D\u6587", lang: "zh-CN", title: "thegent", description: "AI \u4EE3\u7406\u6CBB\u7406\u548C MCP \u670D\u52A1\u5668" },
  "zh-TW": { label: "\u7E41\u9AD4\u4E2D\u6587", lang: "zh-TW", title: "thegent", description: "AI \u4EE3\u7406\u6CBB\u7406\u548C MCP \u4F3A\u670D\u5668" },
  fa: { label: "\u0641\u0627\u0631\u0633\u06CC", lang: "fa", title: "thegent", description: "\u062D\u06A9\u0645\u0631\u0627\u0646\u06CC \u0639\u0627\u0645\u0644 \u0647\u0648\u0634 \u0645\u0635\u0646\u0648\u0639\u06CC \u0648 \u0633\u0631\u0648\u0631 MCP" },
  "fa-Latn": { label: "Pinglish", lang: "fa-Latn", title: "thegent", description: "AI Agent Governance (Latin)" }
};
var config = defineConfig({
  title: "thegent",
  description: "AI Agent Governance & MCP Server",
  base: docsBase,
  locales,
  head: [
    ["link", { rel: "icon", href: faviconHref }]
  ],
  appearance: true,
  lastUpdated: true,
  // Exclude problematic directories from the build
  // IMPORTANT: Keep aggressive to avoid build timeouts (7800+ md files total)
  // Only include: index.md, start-here.md, tutorials/, how-to/, reference/, operations/, api/
  srcExclude: [
    // Research/context dumps (566MB+)
    "context/**",
    "diagrams/**",
    "dumps/**",
    "docset/**",
    // Fragmented/in-progress content
    "fragemented/**",
    "plans/**",
    "research/**",
    "reports/**",
    "changes/**",
    "specs/**",
    // Auto-generated API docs (691 files)
    "reference/api/**",
    "reference/WORK_STREAM.md",
    // Archives and legacy
    "archives/**",
    "contracts/**",
    "migration/**",
    "closure/**",
    // Large generated sections
    "governance/**",
    "architecture/**",
    "guides/**",
    "checklists/**",
    "examples/**",
    "security/**",
    "deployment/**",
    "tasks/**",
    "demos/**",
    "concepts/**",
    "projects/**",
    "recordings/**",
    "references/**",
    "site/**",
    // Root-level large files
    "AGENT_*.md",
    "AUDIT_*.md",
    "CROSS_*.md",
    "DISCOVERY.md",
    "DOCUMENT_*.md",
    "FASTMCP_*.md",
    "GAP_*.md",
    "GOVERNANCE_*.md",
    "IMPLEMENTATION_*.md",
    "INSTALL_*.md",
    "LLM_*.md",
    "MAINTENANCE_*.md",
    "MISE_*.md",
    "MONITORING_*.md",
    "MULTI_*.md",
    "NATS_*.md",
    "NEO4J_*.md",
    "NAVIGATION_*.md",
    "NEXT_*.md",
    "ORCHESTRATION_*.md",
    "PATCHES_*.md",
    "PLANNING_*.md",
    "POST_*.md",
    "PYTHON_*.md",
    "QUALITY_*.md",
    "RESUME_*.md",
    "RUNBOOK.md",
    "SETUP-*.md",
    "SHELL_*.md",
    "SPECS_*.md",
    "STATE_*.md",
    "ULTRA_*.md",
    "VERIFICATION_*.md",
    "WHAT_*.md",
    "WORK_*.md",
    "ZSH_*.md"
  ],
  // Disable dead link check (links are external or cross-project)
  ignoreDeadLinks: true,
  vite: {
    resolve: {
      alias: {
        "@phenodocs-theme": phenodocsTheme
      }
    },
    server: {
      fs: {
        allow: [phenodocsRoot]
      }
    },
    plugins: [
      // VitePress bundles its own vite; cast required to resolve dual-vite Plugin type mismatch
      imagetools({
        defaultDirectives: (url) => {
          if (url.searchParams.has("format")) {
            return new URLSearchParams({
              format: url.searchParams.get("format") || "avif",
              as: "picture"
            });
          }
          return new URLSearchParams({
            format: "avif",
            as: "picture"
          });
        }
      })
    ],
    build: {
      assetsDir: "assets",
      rollupOptions: {
        output: {
          manualChunks: (id) => {
            if (id.includes("node_modules")) {
              return "vendor";
            }
          }
        }
      }
    }
  },
  markdown: {
    config: (md) => {
      md.use(crossProjectLinks);
      md.use(contentTabsPlugin);
      md.use(videoEmbedPlugin, {
        controls: true,
        width: "100%"
      });
      md.use(katex, {
        throwOnError: false,
        errorColor: "#cc0000"
      });
      md.use(markdownItEmoji);
    },
    // Enable line numbers for code blocks
    math: true,
    lineNumbers: true,
    // Enable code highlighting
    theme: {
      light: "github-light",
      dark: "github-dark"
    }
  },
  themeConfig: {
    nav: [
      { text: "Home", link: "/" },
      {
        text: "Start Here",
        link: "/start-here.md"
      },
      {
        text: "Tutorials",
        link: "/tutorials/"
      },
      {
        text: "How-to",
        link: "/how-to/"
      },
      {
        text: "Reference",
        link: "/reference/",
        activeMatch: "/reference/"
      },
      {
        text: "Explanation",
        link: "/explanation/"
      },
      {
        text: "Operations",
        link: "/operations/"
      },
      {
        text: "API",
        link: "/api/"
      },
      {
        text: "\u{1F310} Language",
        items: [
          { text: "English", link: "/" },
          { text: "\u7B80\u4F53\u4E2D\u6587", link: "/zh-CN/" },
          { text: "\u7E41\u9AD4\u4E2D\u6587", link: "/zh-TW/" },
          { text: "\u0641\u0627\u0631\u0633\u06CC", link: "/fa/" },
          { text: "Pinglish", link: "/fa-Latn/" }
        ]
      }
    ],
    sidebar,
    socialLinks: [],
    search: hasAlgolia ? {
      provider: "algolia",
      options: {
        appId: algoliaAppId,
        apiKey: algoliaApiKey,
        indexName: algoliaIndexName
      }
    } : void 0,
    outline: "deep",
    editLink: {
      pattern: "https://github.com/kooshapari/temp-PRODVERCEL/485/kush/thegent/edit/main/docs/:path",
      text: "Edit this page on GitHub"
    }
  },
  // Mermaid configuration
  // Note: Mermaid doesn't support CSS variables - use actual color values
  mermaid: {
    theme: "base",
    themeVariables: {
      primaryColor: "#42b883",
      background: "#ffffff",
      primaryTextColor: "#213547",
      primaryBorderColor: "#e0e0e0",
      lineColor: "#666666",
      secondaryColor: "#747bff",
      tertiaryColor: "#f5f5f5"
    },
    flowchart: {
      useMaxWidth: true,
      htmlLabels: true
    },
    sequence: {
      useMaxWidth: true
    },
    gantt: {
      useMaxWidth: true
    }
  }
});
var config_default = withMermaid(config);
export {
  config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsiZG9jcy8udml0ZXByZXNzL2NvbmZpZy50cyIsICJkb2NzLy52aXRlcHJlc3MvcGx1Z2lucy9jcm9zcy1wcm9qZWN0LWxpbmtzLnRzIiwgImRvY3MvLnZpdGVwcmVzcy9wbHVnaW5zL2NvbnRlbnQtdGFicy50cyIsICJkb2NzLy52aXRlcHJlc3MvcGx1Z2lucy92aWRlby1lbWJlZC50cyIsICJkb2NzLy52aXRlcHJlc3Mvc2lkZWJhci1jYW5vbmljYWwudHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCIvVXNlcnMva29vc2hhcGFyaS9Db2RlUHJvamVjdHMvUGhlbm90eXBlL3JlcG9zL3RoZWdlbnQvZG9jcy8udml0ZXByZXNzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCIvVXNlcnMva29vc2hhcGFyaS9Db2RlUHJvamVjdHMvUGhlbm90eXBlL3JlcG9zL3RoZWdlbnQvZG9jcy8udml0ZXByZXNzL2NvbmZpZy50c1wiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9pbXBvcnRfbWV0YV91cmwgPSBcImZpbGU6Ly8vVXNlcnMva29vc2hhcGFyaS9Db2RlUHJvamVjdHMvUGhlbm90eXBlL3JlcG9zL3RoZWdlbnQvZG9jcy8udml0ZXByZXNzL2NvbmZpZy50c1wiO2ltcG9ydCB7IGRpcm5hbWUsIHJlc29sdmUgfSBmcm9tICdub2RlOnBhdGgnXG5pbXBvcnQgeyBmaWxlVVJMVG9QYXRoIH0gZnJvbSAnbm9kZTp1cmwnXG5cbmltcG9ydCB7IGRlZmluZUNvbmZpZyB9IGZyb20gJ3ZpdGVwcmVzcydcbmltcG9ydCB7IHdpdGhNZXJtYWlkIH0gZnJvbSAndml0ZXByZXNzLXBsdWdpbi1tZXJtYWlkJ1xuaW1wb3J0IHsgaW1hZ2V0b29scyB9IGZyb20gJ3ZpdGUtaW1hZ2V0b29scydcbmltcG9ydCB7IGNyb3NzUHJvamVjdExpbmtzIH0gZnJvbSAnLi9wbHVnaW5zL2Nyb3NzLXByb2plY3QtbGlua3MnXG5pbXBvcnQgeyBjb250ZW50VGFic1BsdWdpbiB9IGZyb20gJy4vcGx1Z2lucy9jb250ZW50LXRhYnMnXG5pbXBvcnQgeyB2aWRlb0VtYmVkUGx1Z2luIH0gZnJvbSAnLi9wbHVnaW5zL3ZpZGVvLWVtYmVkJ1xuaW1wb3J0IHsgc2lkZWJhciB9IGZyb20gJy4vc2lkZWJhci1jYW5vbmljYWwnXG5pbXBvcnQgeyBjcmVhdGVSZXF1aXJlIH0gZnJvbSAnbW9kdWxlJ1xuXG5jb25zdCBkb2NzRGlyID0gZGlybmFtZShmaWxlVVJMVG9QYXRoKGltcG9ydC5tZXRhLnVybCkpXG5jb25zdCBwaGVub2RvY3NSb290ID0gcmVzb2x2ZShkb2NzRGlyLCAnLi4vLi4vLi4vcGhlbm9kb2NzJylcbmNvbnN0IHBoZW5vZG9jc1RoZW1lID0gcmVzb2x2ZShwaGVub2RvY3NSb290LCAnLnZpdGVwcmVzcy90aGVtZS9pbmRleC50cycpXG5cbmNvbnN0IHJlcXVpcmUgPSBjcmVhdGVSZXF1aXJlKGltcG9ydC5tZXRhLnVybClcbmNvbnN0IG1hcmtkb3duSXRFbW9qaSA9IHJlcXVpcmUoJ21hcmtkb3duLWl0LWVtb2ppJykuZnVsbFxuY29uc3Qga2F0ZXggPSByZXF1aXJlKCdtYXJrZG93bi1pdC1tYXRoamF4MycpXG5jb25zdCBhbGdvbGlhQXBwSWQgPSBwcm9jZXNzLmVudi5WSVRFUFJFU1NfQUxHT0xJQV9BUFBfSURcbmNvbnN0IGFsZ29saWFBcGlLZXkgPSBwcm9jZXNzLmVudi5WSVRFUFJFU1NfQUxHT0xJQV9BUElfS0VZXG5jb25zdCBhbGdvbGlhSW5kZXhOYW1lID0gcHJvY2Vzcy5lbnYuVklURVBSRVNTX0FMR09MSUFfSU5ERVhfTkFNRVxuY29uc3QgaGFzQWxnb2xpYSA9IEJvb2xlYW4oYWxnb2xpYUFwcElkICYmIGFsZ29saWFBcGlLZXkgJiYgYWxnb2xpYUluZGV4TmFtZSlcbmNvbnN0IHJlcG9OYW1lID0gcHJvY2Vzcy5lbnYuR0lUSFVCX1JFUE9TSVRPUlk/LnNwbGl0KCcvJylbMV0gfHwgJ3RoZWdlbnQnXG5jb25zdCBpc1BhZ2VzQnVpbGQgPSBwcm9jZXNzLmVudi5HSVRIVUJfQUNUSU9OUyA9PT0gJ3RydWUnIHx8IHByb2Nlc3MuZW52LkdJVEhVQl9QQUdFUyA9PT0gJ3RydWUnXG5jb25zdCBkb2NzQmFzZU92ZXJyaWRlID0gcHJvY2Vzcy5lbnYuVklURVBSRVNTX0JBU0Vcbi8vIEhhcmRjb2RlIHRvIC90aGVnZW50LyBmb3IgR2l0SHViIFBhZ2VzIGRlcGxveW1lbnRcbmNvbnN0IGRvY3NCYXNlID0gJy90aGVnZW50LydcbmNvbnN0IGZhdmljb25IcmVmID0gYCR7ZG9jc0Jhc2V9ZmF2aWNvbi5pY29gXG5cbi8vIFN1cHBvcnRlZCBsb2NhbGVzOiBlbiwgemgtQ04sIHpoLVRXLCBmYSwgZmEtTGF0blxuY29uc3QgbG9jYWxlcyA9IHtcbiAgcm9vdDogeyBsYWJlbDogXCJFbmdsaXNoXCIsIGxhbmc6IFwiZW5cIiwgdGl0bGU6ICd0aGVnZW50JywgZGVzY3JpcHRpb246ICdBSSBBZ2VudCBHb3Zlcm5hbmNlICYgTUNQIFNlcnZlcicgfSxcbiAgXCJ6aC1DTlwiOiB7IGxhYmVsOiBcIlx1N0I4MFx1NEY1M1x1NEUyRFx1NjU4N1wiLCBsYW5nOiBcInpoLUNOXCIsIHRpdGxlOiAndGhlZ2VudCcsIGRlc2NyaXB0aW9uOiAnQUkgXHU0RUUzXHU3NDA2XHU2Q0JCXHU3NDA2XHU1NDhDIE1DUCBcdTY3MERcdTUyQTFcdTU2NjgnIH0sXG4gIFwiemgtVFdcIjogeyBsYWJlbDogXCJcdTdFNDFcdTlBRDRcdTRFMkRcdTY1ODdcIiwgbGFuZzogXCJ6aC1UV1wiLCB0aXRsZTogJ3RoZWdlbnQnLCBkZXNjcmlwdGlvbjogJ0FJIFx1NEVFM1x1NzQwNlx1NkNCQlx1NzQwNlx1NTQ4QyBNQ1AgXHU0RjNBXHU2NzBEXHU1NjY4JyB9LFxuICBmYTogeyBsYWJlbDogXCJcdTA2NDFcdTA2MjdcdTA2MzFcdTA2MzNcdTA2Q0NcIiwgbGFuZzogXCJmYVwiLCB0aXRsZTogJ3RoZWdlbnQnLCBkZXNjcmlwdGlvbjogJ1x1MDYyRFx1MDZBOVx1MDY0NVx1MDYzMVx1MDYyN1x1MDY0Nlx1MDZDQyBcdTA2MzlcdTA2MjdcdTA2NDVcdTA2NDQgXHUwNjQ3XHUwNjQ4XHUwNjM0IFx1MDY0NVx1MDYzNVx1MDY0Nlx1MDY0OFx1MDYzOVx1MDZDQyBcdTA2NDggXHUwNjMzXHUwNjMxXHUwNjQ4XHUwNjMxIE1DUCcgfSxcbiAgXCJmYS1MYXRuXCI6IHsgbGFiZWw6IFwiUGluZ2xpc2hcIiwgbGFuZzogXCJmYS1MYXRuXCIsIHRpdGxlOiAndGhlZ2VudCcsIGRlc2NyaXB0aW9uOiAnQUkgQWdlbnQgR292ZXJuYW5jZSAoTGF0aW4pJyB9XG59XG5cbmNvbnN0IGNvbmZpZyA9IGRlZmluZUNvbmZpZyh7XG4gIHRpdGxlOiAndGhlZ2VudCcsXG4gIGRlc2NyaXB0aW9uOiAnQUkgQWdlbnQgR292ZXJuYW5jZSAmIE1DUCBTZXJ2ZXInLFxuICBiYXNlOiBkb2NzQmFzZSxcbiAgbG9jYWxlcyxcbiAgaGVhZDogW1xuICAgIFsnbGluaycsIHsgcmVsOiAnaWNvbicsIGhyZWY6IGZhdmljb25IcmVmIH1dLFxuICBdLFxuICBhcHBlYXJhbmNlOiB0cnVlLFxuICBsYXN0VXBkYXRlZDogdHJ1ZSxcblxuICAvLyBFeGNsdWRlIHByb2JsZW1hdGljIGRpcmVjdG9yaWVzIGZyb20gdGhlIGJ1aWxkXG4gIC8vIElNUE9SVEFOVDogS2VlcCBhZ2dyZXNzaXZlIHRvIGF2b2lkIGJ1aWxkIHRpbWVvdXRzICg3ODAwKyBtZCBmaWxlcyB0b3RhbClcbiAgLy8gT25seSBpbmNsdWRlOiBpbmRleC5tZCwgc3RhcnQtaGVyZS5tZCwgdHV0b3JpYWxzLywgaG93LXRvLywgcmVmZXJlbmNlLywgb3BlcmF0aW9ucy8sIGFwaS9cbiAgc3JjRXhjbHVkZTogW1xuICAgIC8vIFJlc2VhcmNoL2NvbnRleHQgZHVtcHMgKDU2Nk1CKylcbiAgICAnY29udGV4dC8qKicsXG4gICAgJ2RpYWdyYW1zLyoqJyxcbiAgICAnZHVtcHMvKionLFxuICAgICdkb2NzZXQvKionLFxuICAgIC8vIEZyYWdtZW50ZWQvaW4tcHJvZ3Jlc3MgY29udGVudFxuICAgICdmcmFnZW1lbnRlZC8qKicsXG4gICAgJ3BsYW5zLyoqJyxcbiAgICAncmVzZWFyY2gvKionLFxuICAgICdyZXBvcnRzLyoqJyxcbiAgICAnY2hhbmdlcy8qKicsXG4gICAgJ3NwZWNzLyoqJyxcbiAgICAvLyBBdXRvLWdlbmVyYXRlZCBBUEkgZG9jcyAoNjkxIGZpbGVzKVxuICAgICdyZWZlcmVuY2UvYXBpLyoqJyxcbiAgICAncmVmZXJlbmNlL1dPUktfU1RSRUFNLm1kJyxcbiAgICAvLyBBcmNoaXZlcyBhbmQgbGVnYWN5XG4gICAgJ2FyY2hpdmVzLyoqJyxcbiAgICAnY29udHJhY3RzLyoqJyxcbiAgICAnbWlncmF0aW9uLyoqJyxcbiAgICAnY2xvc3VyZS8qKicsXG4gICAgLy8gTGFyZ2UgZ2VuZXJhdGVkIHNlY3Rpb25zXG4gICAgJ2dvdmVybmFuY2UvKionLFxuICAgICdhcmNoaXRlY3R1cmUvKionLFxuICAgICdndWlkZXMvKionLFxuICAgICdjaGVja2xpc3RzLyoqJyxcbiAgICAnZXhhbXBsZXMvKionLFxuICAgICdzZWN1cml0eS8qKicsXG4gICAgJ2RlcGxveW1lbnQvKionLFxuICAgICd0YXNrcy8qKicsXG4gICAgJ2RlbW9zLyoqJyxcbiAgICAnY29uY2VwdHMvKionLFxuICAgICdwcm9qZWN0cy8qKicsXG4gICAgJ3JlY29yZGluZ3MvKionLFxuICAgICdyZWZlcmVuY2VzLyoqJyxcbiAgICAnc2l0ZS8qKicsXG4gICAgLy8gUm9vdC1sZXZlbCBsYXJnZSBmaWxlc1xuICAgICdBR0VOVF8qLm1kJyxcbiAgICAnQVVESVRfKi5tZCcsXG4gICAgJ0NST1NTXyoubWQnLFxuICAgICdESVNDT1ZFUlkubWQnLFxuICAgICdET0NVTUVOVF8qLm1kJyxcbiAgICAnRkFTVE1DUF8qLm1kJyxcbiAgICAnR0FQXyoubWQnLFxuICAgICdHT1ZFUk5BTkNFXyoubWQnLFxuICAgICdJTVBMRU1FTlRBVElPTl8qLm1kJyxcbiAgICAnSU5TVEFMTF8qLm1kJyxcbiAgICAnTExNXyoubWQnLFxuICAgICdNQUlOVEVOQU5DRV8qLm1kJyxcbiAgICAnTUlTRV8qLm1kJyxcbiAgICAnTU9OSVRPUklOR18qLm1kJyxcbiAgICAnTVVMVElfKi5tZCcsXG4gICAgJ05BVFNfKi5tZCcsXG4gICAgJ05FTzRKXyoubWQnLFxuICAgICdOQVZJR0FUSU9OXyoubWQnLFxuICAgICdORVhUXyoubWQnLFxuICAgICdPUkNIRVNUUkFUSU9OXyoubWQnLFxuICAgICdQQVRDSEVTXyoubWQnLFxuICAgICdQTEFOTklOR18qLm1kJyxcbiAgICAnUE9TVF8qLm1kJyxcbiAgICAnUFlUSE9OXyoubWQnLFxuICAgICdRVUFMSVRZXyoubWQnLFxuICAgICdSRVNVTUVfKi5tZCcsXG4gICAgJ1JVTkJPT0subWQnLFxuICAgICdTRVRVUC0qLm1kJyxcbiAgICAnU0hFTExfKi5tZCcsXG4gICAgJ1NQRUNTXyoubWQnLFxuICAgICdTVEFURV8qLm1kJyxcbiAgICAnVUxUUkFfKi5tZCcsXG4gICAgJ1ZFUklGSUNBVElPTl8qLm1kJyxcbiAgICAnV0hBVF8qLm1kJyxcbiAgICAnV09SS18qLm1kJyxcbiAgICAnWlNIXyoubWQnLFxuICBdLFxuXG4gIC8vIERpc2FibGUgZGVhZCBsaW5rIGNoZWNrIChsaW5rcyBhcmUgZXh0ZXJuYWwgb3IgY3Jvc3MtcHJvamVjdClcbiAgaWdub3JlRGVhZExpbmtzOiB0cnVlLFxuXG4gIHZpdGU6IHtcbiAgICByZXNvbHZlOiB7XG4gICAgICBhbGlhczoge1xuICAgICAgICAnQHBoZW5vZG9jcy10aGVtZSc6IHBoZW5vZG9jc1RoZW1lLFxuICAgICAgfSxcbiAgICB9LFxuICAgIHNlcnZlcjoge1xuICAgICAgZnM6IHtcbiAgICAgICAgYWxsb3c6IFtwaGVub2RvY3NSb290XSxcbiAgICAgIH0sXG4gICAgfSxcbiAgICBwbHVnaW5zOiBbXG4gICAgICAvLyBWaXRlUHJlc3MgYnVuZGxlcyBpdHMgb3duIHZpdGU7IGNhc3QgcmVxdWlyZWQgdG8gcmVzb2x2ZSBkdWFsLXZpdGUgUGx1Z2luIHR5cGUgbWlzbWF0Y2hcbiAgICAgIGltYWdldG9vbHMoe1xuICAgICAgICBkZWZhdWx0RGlyZWN0aXZlczogKHVybCkgPT4ge1xuICAgICAgICAgIC8vIEltYWdlIG9wdGltaXphdGlvbjogV2ViUC9BVklGIGNvbnZlcnNpb24sIGxhenkgbG9hZGluZyBoYW5kbGVkIGJ5IGJyb3dzZXJcbiAgICAgICAgICBpZiAodXJsLnNlYXJjaFBhcmFtcy5oYXMoJ2Zvcm1hdCcpKSB7XG4gICAgICAgICAgICByZXR1cm4gbmV3IFVSTFNlYXJjaFBhcmFtcyh7XG4gICAgICAgICAgICAgIGZvcm1hdDogdXJsLnNlYXJjaFBhcmFtcy5nZXQoJ2Zvcm1hdCcpIHx8ICdhdmlmJyxcbiAgICAgICAgICAgICAgYXM6ICdwaWN0dXJlJyxcbiAgICAgICAgICAgIH0pXG4gICAgICAgICAgfVxuICAgICAgICAgIC8vIERlZmF1bHQgdG8gQVZJRiB3aXRoIFdlYlAgZmFsbGJhY2sgZm9yIGJldHRlciBjb21wcmVzc2lvblxuICAgICAgICAgIHJldHVybiBuZXcgVVJMU2VhcmNoUGFyYW1zKHtcbiAgICAgICAgICAgIGZvcm1hdDogJ2F2aWYnLFxuICAgICAgICAgICAgYXM6ICdwaWN0dXJlJyxcbiAgICAgICAgICB9KVxuICAgICAgICB9XG4gICAgICB9KSBhcyBhbnlcbiAgICBdLFxuICAgIGJ1aWxkOiB7XG4gICAgICBhc3NldHNEaXI6ICdhc3NldHMnLFxuICAgICAgcm9sbHVwT3B0aW9uczoge1xuICAgICAgICBvdXRwdXQ6IHtcbiAgICAgICAgICBtYW51YWxDaHVua3M6IChpZCkgPT4ge1xuICAgICAgICAgICAgLy8gS2VlcCBjaHVua2luZyBzaW1wbGUgdG8gYXZvaWQgbWVybWFpZC92dWUgY2lyY3VsYXIgaW5pdCBvcmRlcmluZyBidWdzLlxuICAgICAgICAgICAgaWYgKGlkLmluY2x1ZGVzKCdub2RlX21vZHVsZXMnKSkge1xuICAgICAgICAgICAgICByZXR1cm4gJ3ZlbmRvcidcbiAgICAgICAgICAgIH1cbiAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICB9XG4gIH0sXG5cbiAgbWFya2Rvd246IHtcbiAgICBjb25maWc6IChtZCkgPT4ge1xuICAgICAgbWQudXNlKGNyb3NzUHJvamVjdExpbmtzKVxuICAgICAgbWQudXNlKGNvbnRlbnRUYWJzUGx1Z2luKVxuICAgICAgbWQudXNlKHZpZGVvRW1iZWRQbHVnaW4sIHtcbiAgICAgICAgY29udHJvbHM6IHRydWUsXG4gICAgICAgIHdpZHRoOiAnMTAwJScsXG4gICAgICB9KVxuXG4gICAgICAvLyBNYXRoIHN1cHBvcnQgKEthVGVYKVxuICAgICAgbWQudXNlKGthdGV4LCB7XG4gICAgICAgIHRocm93T25FcnJvcjogZmFsc2UsXG4gICAgICAgIGVycm9yQ29sb3I6ICcjY2MwMDAwJ1xuICAgICAgfSlcblxuICAgICAgLy8gRW1vamkgc3VwcG9ydCAtIHVzZSBkZWZhdWx0cyB0byBhdm9pZCB1bmRlZmluZWQgcmVuZGVyaW5nIGluIHRhYmxlc1xuICAgICAgbWQudXNlKG1hcmtkb3duSXRFbW9qaSlcbiAgICB9LFxuICAgIC8vIEVuYWJsZSBsaW5lIG51bWJlcnMgZm9yIGNvZGUgYmxvY2tzXG4gICAgbWF0aDogdHJ1ZSxcbiAgICBsaW5lTnVtYmVyczogdHJ1ZSxcbiAgICAvLyBFbmFibGUgY29kZSBoaWdobGlnaHRpbmdcbiAgICB0aGVtZToge1xuICAgICAgbGlnaHQ6ICdnaXRodWItbGlnaHQnLFxuICAgICAgZGFyazogJ2dpdGh1Yi1kYXJrJ1xuICAgIH1cbiAgfSxcblxuICB0aGVtZUNvbmZpZzoge1xuICAgIG5hdjogW1xuICAgICAgeyB0ZXh0OiAnSG9tZScsIGxpbms6ICcvJyB9LFxuICAgICAge1xuICAgICAgICB0ZXh0OiAnU3RhcnQgSGVyZScsXG4gICAgICAgIGxpbms6ICcvc3RhcnQtaGVyZS5tZCdcbiAgICAgIH0sXG4gICAgICB7XG4gICAgICAgIHRleHQ6ICdUdXRvcmlhbHMnLFxuICAgICAgICBsaW5rOiAnL3R1dG9yaWFscy8nXG4gICAgICB9LFxuICAgICAge1xuICAgICAgICB0ZXh0OiAnSG93LXRvJyxcbiAgICAgICAgbGluazogJy9ob3ctdG8vJ1xuICAgICAgfSxcbiAgICAgIHtcbiAgICAgICAgdGV4dDogJ1JlZmVyZW5jZScsXG4gICAgICAgIGxpbms6ICcvcmVmZXJlbmNlLycsXG4gICAgICAgIGFjdGl2ZU1hdGNoOiAnL3JlZmVyZW5jZS8nXG4gICAgICB9LFxuICAgICAge1xuICAgICAgICB0ZXh0OiAnRXhwbGFuYXRpb24nLFxuICAgICAgICBsaW5rOiAnL2V4cGxhbmF0aW9uLydcbiAgICAgIH0sXG4gICAgICB7XG4gICAgICAgIHRleHQ6ICdPcGVyYXRpb25zJyxcbiAgICAgICAgbGluazogJy9vcGVyYXRpb25zLydcbiAgICAgIH0sXG4gICAgICB7XG4gICAgICAgIHRleHQ6ICdBUEknLFxuICAgICAgICBsaW5rOiAnL2FwaS8nXG4gICAgICB9LFxuICAgICAge1xuICAgICAgICB0ZXh0OiBcIlx1RDgzQ1x1REYxMCBMYW5ndWFnZVwiLFxuICAgICAgICBpdGVtczogW1xuICAgICAgICAgIHsgdGV4dDogXCJFbmdsaXNoXCIsIGxpbms6IFwiL1wiIH0sXG4gICAgICAgICAgeyB0ZXh0OiBcIlx1N0I4MFx1NEY1M1x1NEUyRFx1NjU4N1wiLCBsaW5rOiBcIi96aC1DTi9cIiB9LFxuICAgICAgICAgIHsgdGV4dDogXCJcdTdFNDFcdTlBRDRcdTRFMkRcdTY1ODdcIiwgbGluazogXCIvemgtVFcvXCIgfSxcbiAgICAgICAgICB7IHRleHQ6IFwiXHUwNjQxXHUwNjI3XHUwNjMxXHUwNjMzXHUwNkNDXCIsIGxpbms6IFwiL2ZhL1wiIH0sXG4gICAgICAgICAgeyB0ZXh0OiBcIlBpbmdsaXNoXCIsIGxpbms6IFwiL2ZhLUxhdG4vXCIgfVxuICAgICAgICBdXG4gICAgICB9XG4gICAgXSxcblxuICAgIHNpZGViYXI6IHNpZGViYXIsXG5cbiAgICBzb2NpYWxMaW5rczogW10sXG4gICAgc2VhcmNoOiBoYXNBbGdvbGlhXG4gICAgICA/IHtcbiAgICAgICAgICBwcm92aWRlcjogJ2FsZ29saWEnLFxuICAgICAgICAgIG9wdGlvbnM6IHtcbiAgICAgICAgICAgIGFwcElkOiBhbGdvbGlhQXBwSWQgYXMgc3RyaW5nLFxuICAgICAgICAgICAgYXBpS2V5OiBhbGdvbGlhQXBpS2V5IGFzIHN0cmluZyxcbiAgICAgICAgICAgIGluZGV4TmFtZTogYWxnb2xpYUluZGV4TmFtZSBhcyBzdHJpbmcsXG4gICAgICAgICAgfSxcbiAgICAgICAgfVxuICAgICAgOiB1bmRlZmluZWQsXG4gICAgb3V0bGluZTogJ2RlZXAnLFxuXG4gICAgZWRpdExpbms6IHtcbiAgICAgIHBhdHRlcm46ICdodHRwczovL2dpdGh1Yi5jb20va29vc2hhcGFyaS90ZW1wLVBST0RWRVJDRUwvNDg1L2t1c2gvdGhlZ2VudC9lZGl0L21haW4vZG9jcy86cGF0aCcsXG4gICAgICB0ZXh0OiAnRWRpdCB0aGlzIHBhZ2Ugb24gR2l0SHViJ1xuICAgIH0sXG4gIH0sXG5cbiAgLy8gTWVybWFpZCBjb25maWd1cmF0aW9uXG4gIC8vIE5vdGU6IE1lcm1haWQgZG9lc24ndCBzdXBwb3J0IENTUyB2YXJpYWJsZXMgLSB1c2UgYWN0dWFsIGNvbG9yIHZhbHVlc1xuICBtZXJtYWlkOiB7XG4gICAgdGhlbWU6ICdiYXNlJyxcbiAgICB0aGVtZVZhcmlhYmxlczoge1xuICAgICAgcHJpbWFyeUNvbG9yOiAnIzQyYjg4MycsXG4gICAgICBiYWNrZ3JvdW5kOiAnI2ZmZmZmZicsXG4gICAgICBwcmltYXJ5VGV4dENvbG9yOiAnIzIxMzU0NycsXG4gICAgICBwcmltYXJ5Qm9yZGVyQ29sb3I6ICcjZTBlMGUwJyxcbiAgICAgIGxpbmVDb2xvcjogJyM2NjY2NjYnLFxuICAgICAgc2Vjb25kYXJ5Q29sb3I6ICcjNzQ3YmZmJyxcbiAgICAgIHRlcnRpYXJ5Q29sb3I6ICcjZjVmNWY1JyxcbiAgICB9LFxuICAgIGZsb3djaGFydDoge1xuICAgICAgdXNlTWF4V2lkdGg6IHRydWUsXG4gICAgICBodG1sTGFiZWxzOiB0cnVlLFxuICAgIH0sXG4gICAgc2VxdWVuY2U6IHtcbiAgICAgIHVzZU1heFdpZHRoOiB0cnVlLFxuICAgIH0sXG4gICAgZ2FudHQ6IHtcbiAgICAgIHVzZU1heFdpZHRoOiB0cnVlLFxuICAgIH0sXG4gIH0sXG5cbn0pXG5cbmV4cG9ydCBkZWZhdWx0IHdpdGhNZXJtYWlkKGNvbmZpZylcbiIsICJjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZGlybmFtZSA9IFwiL1VzZXJzL2tvb3NoYXBhcmkvQ29kZVByb2plY3RzL1BoZW5vdHlwZS9yZXBvcy90aGVnZW50L2RvY3MvLnZpdGVwcmVzcy9wbHVnaW5zXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCIvVXNlcnMva29vc2hhcGFyaS9Db2RlUHJvamVjdHMvUGhlbm90eXBlL3JlcG9zL3RoZWdlbnQvZG9jcy8udml0ZXByZXNzL3BsdWdpbnMvY3Jvc3MtcHJvamVjdC1saW5rcy50c1wiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9pbXBvcnRfbWV0YV91cmwgPSBcImZpbGU6Ly8vVXNlcnMva29vc2hhcGFyaS9Db2RlUHJvamVjdHMvUGhlbm90eXBlL3JlcG9zL3RoZWdlbnQvZG9jcy8udml0ZXByZXNzL3BsdWdpbnMvY3Jvc3MtcHJvamVjdC1saW5rcy50c1wiO2ltcG9ydCB0eXBlIE1hcmtkb3duSXQgZnJvbSAnbWFya2Rvd24taXQnXG5pbXBvcnQgdHlwZSB7IFJlbmRlclJ1bGUgfSBmcm9tICd2aXRlcHJlc3MnXG5cbi8vIE1hcCBwcm9qZWN0IG5hbWVzIHRvIHRoZWlyIGRvY3MtZGlzdCBwYXRoc1xuY29uc3QgUFJPSkVDVF9QQVRIUzogUmVjb3JkPHN0cmluZywgc3RyaW5nPiA9IHtcbiAgJ3RoZWdlbnQnOiAnL1VzZXJzL2tvb3NoYXBhcmkvdGVtcC1QUk9EVkVSQ0VMLzQ4NS9rdXNoL3RoZWdlbnQvZG9jcy1kaXN0L21haW4nLFxuICAnam9iaHVudGVyJzogJy9Vc2Vycy9rb29zaGFwYXJpL0Rldi9qb2ItaHVudGVyL2RvY3MtZGlzdCcsXG4gICdoZWxpb3NTaGllbGQnOiAnL1VzZXJzL2tvb3NoYXBhcmkvdGVtcC1QUk9EVkVSQ0VMLTQ4NS9rdXNoL2hlbGlvc1NoaWVsZC9kb2NzLWRpc3QnLFxuICAndHJhY2UnOiAnL1VzZXJzL2tvb3NoYXBhcmkva3VzaC90cmFjZS9kb2NzLWRpc3QnLFxufVxuXG5leHBvcnQgZnVuY3Rpb24gY3Jvc3NQcm9qZWN0TGlua3MobWQ6IE1hcmtkb3duSXQpIHtcbiAgY29uc3QgZGVmYXVsdFJlbmRlcjogUmVuZGVyUnVsZSA9IG1kLnJlbmRlcmVyLnJ1bGVzLmxpbmtfb3BlbiB8fCBmdW5jdGlvbih0b2tlbnMsIGlkeCwgb3B0aW9ucywgX2Vudiwgc2VsZikge1xuICAgIHJldHVybiBzZWxmLnJlbmRlclRva2VuKHRva2VucywgaWR4LCBvcHRpb25zKVxuICB9XG5cbiAgbWQucmVuZGVyZXIucnVsZXMubGlua19vcGVuID0gZnVuY3Rpb24odG9rZW5zLCBpZHgsIG9wdGlvbnMsIGVudiwgc2VsZikge1xuICAgIGNvbnN0IGhyZWYgPSB0b2tlbnNbaWR4XS5hdHRyR2V0KCdocmVmJylcblxuICAgIC8vIENoZWNrIGZvciB+cHJvamVjdDovcGF0aCBwYXR0ZXJuXG4gICAgaWYgKGhyZWYgJiYgaHJlZi5zdGFydHNXaXRoKCd+JykpIHtcbiAgICAgIGNvbnN0IG1hdGNoID0gaHJlZi5tYXRjaCgvXn4oW146XSspOiguKykkLylcbiAgICAgIGlmIChtYXRjaCkge1xuICAgICAgICBjb25zdCBbLCBwcm9qZWN0LCBwYXRoXSA9IG1hdGNoXG4gICAgICAgIGNvbnN0IGJhc2VQYXRoID0gUFJPSkVDVF9QQVRIU1twcm9qZWN0XVxuXG4gICAgICAgIGlmIChiYXNlUGF0aCkge1xuICAgICAgICAgIC8vIENvbnZlcnQgbWFya2Rvd24gcGF0aCB0byBIVE1MIHBhdGhcbiAgICAgICAgICBjb25zdCBodG1sUGF0aCA9IHBhdGhcbiAgICAgICAgICAgIC5yZXBsYWNlKC9cXC5tZCQvLCAnLmh0bWwnKVxuICAgICAgICAgICAgLnJlcGxhY2UoL15cXC8rLywgJycpXG5cbiAgICAgICAgICB0b2tlbnNbaWR4XS5hdHRyU2V0KCdocmVmJywgYGZpbGU6Ly8ke2Jhc2VQYXRofS8ke2h0bWxQYXRofWApXG4gICAgICAgICAgdG9rZW5zW2lkeF0uYXR0clNldCgndGFyZ2V0JywgJ19ibGFuaycpXG4gICAgICAgICAgdG9rZW5zW2lkeF0uYXR0clNldCgnY2xhc3MnLCAnY3Jvc3MtcHJvamVjdC1saW5rJylcbiAgICAgICAgfVxuICAgICAgfVxuICAgIH1cblxuICAgIHJldHVybiBkZWZhdWx0UmVuZGVyKHRva2VucywgaWR4LCBvcHRpb25zLCBlbnYsIHNlbGYpXG4gIH1cbn1cbiIsICJjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZGlybmFtZSA9IFwiL1VzZXJzL2tvb3NoYXBhcmkvQ29kZVByb2plY3RzL1BoZW5vdHlwZS9yZXBvcy90aGVnZW50L2RvY3MvLnZpdGVwcmVzcy9wbHVnaW5zXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCIvVXNlcnMva29vc2hhcGFyaS9Db2RlUHJvamVjdHMvUGhlbm90eXBlL3JlcG9zL3RoZWdlbnQvZG9jcy8udml0ZXByZXNzL3BsdWdpbnMvY29udGVudC10YWJzLnRzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ltcG9ydF9tZXRhX3VybCA9IFwiZmlsZTovLy9Vc2Vycy9rb29zaGFwYXJpL0NvZGVQcm9qZWN0cy9QaGVub3R5cGUvcmVwb3MvdGhlZ2VudC9kb2NzLy52aXRlcHJlc3MvcGx1Z2lucy9jb250ZW50LXRhYnMudHNcIjtpbXBvcnQgdHlwZSBNYXJrZG93bkl0IGZyb20gJ21hcmtkb3duLWl0J1xuaW1wb3J0IHR5cGUgeyBSdWxlQmxvY2sgfSBmcm9tICdtYXJrZG93bi1pdC9saWIvcGFyc2VyX2Jsb2NrJ1xuXG4vKipcbiAqIFBhcnNlIHRhYiBkZWZpbml0aW9ucyBmcm9tIG1hcmtkb3duIGNvbnRlbnRcbiAqXG4gKiBFeHBlY3RlZCBmb3JtYXQ6XG4gKiA6OjogdGFic1xuICogOjo6IHRhYiBweXRob25cbiAqIGBgYHB5dGhvblxuICogcHJpbnQoXCJoZWxsb1wiKVxuICogYGBgXG4gKiA6OjpcbiAqIDo6OiB0YWIgamF2YXNjcmlwdFxuICogYGBgamF2YXNjcmlwdFxuICogY29uc29sZS5sb2coXCJoZWxsb1wiKVxuICogYGBgXG4gKiA6OjpcbiAqIDo6OlxuICovXG5mdW5jdGlvbiBwYXJzZVRhYnNDb250ZW50KGNvbnRlbnQ6IHN0cmluZyk6IHsgdGFiczogQXJyYXk8e2lkOiBzdHJpbmcsIGxhYmVsOiBzdHJpbmcsIGNvbnRlbnQ6IHN0cmluZ30+IH0ge1xuICBjb25zdCB0YWJzOiBBcnJheTx7aWQ6IHN0cmluZywgbGFiZWw6IHN0cmluZywgY29udGVudDogc3RyaW5nfT4gPSBbXVxuICBjb25zdCBsaW5lcyA9IGNvbnRlbnQuc3BsaXQoL1xccj9cXG4vKVxuICBsZXQgaW5UYWIgPSBmYWxzZVxuICBsZXQgY3VycmVudElkID0gJydcbiAgbGV0IGN1cnJlbnRDb250ZW50OiBzdHJpbmdbXSA9IFtdXG5cbiAgY29uc3QgdGFiU3RhcnQgPSAvXlxccyo6OjpcXHMqdGFiXFxzKyguKz8pXFxzKiQvXG4gIGNvbnN0IHRhYkVuZCA9IC9eXFxzKjo6OlxccyokL1xuXG4gIGZvciAoY29uc3QgbGluZSBvZiBsaW5lcykge1xuICAgIGNvbnN0IHN0YXJ0TWF0Y2ggPSBsaW5lLm1hdGNoKHRhYlN0YXJ0KVxuICAgIGlmIChzdGFydE1hdGNoKSB7XG4gICAgICBpZiAoaW5UYWIgJiYgY3VycmVudENvbnRlbnQubGVuZ3RoID4gMCkge1xuICAgICAgICBjb25zdCBjb250ZW50ID0gY3VycmVudENvbnRlbnQuam9pbignXFxuJykudHJpbSgpXG4gICAgICAgIHRhYnMucHVzaCh7IGlkOiBjdXJyZW50SWQsIGxhYmVsOiBjdXJyZW50SWQsIGNvbnRlbnQgfSlcbiAgICAgIH1cblxuICAgICAgaW5UYWIgPSB0cnVlXG4gICAgICBjdXJyZW50SWQgPSBzdGFydE1hdGNoWzFdLnRyaW0oKVxuICAgICAgY3VycmVudENvbnRlbnQgPSBbXVxuICAgICAgY29udGludWVcbiAgICB9XG5cbiAgICBpZiAoaW5UYWIgJiYgdGFiRW5kLnRlc3QobGluZSkpIHtcbiAgICAgIGNvbnN0IGNvbnRlbnQgPSBjdXJyZW50Q29udGVudC5qb2luKCdcXG4nKS50cmltKClcbiAgICAgIHRhYnMucHVzaCh7IGlkOiBjdXJyZW50SWQsIGxhYmVsOiBjdXJyZW50SWQsIGNvbnRlbnQgfSlcbiAgICAgIGluVGFiID0gZmFsc2VcbiAgICAgIGN1cnJlbnRJZCA9ICcnXG4gICAgICBjdXJyZW50Q29udGVudCA9IFtdXG4gICAgICBjb250aW51ZVxuICAgIH1cblxuICAgIGlmIChpblRhYikge1xuICAgICAgY3VycmVudENvbnRlbnQucHVzaChsaW5lKVxuICAgIH1cbiAgfVxuXG4gIGlmIChpblRhYiAmJiBjdXJyZW50Q29udGVudC5sZW5ndGggPiAwKSB7XG4gICAgY29uc3QgY29udGVudCA9IGN1cnJlbnRDb250ZW50LmpvaW4oJ1xcbicpLnRyaW0oKVxuICAgIHRhYnMucHVzaCh7IGlkOiBjdXJyZW50SWQsIGxhYmVsOiBjdXJyZW50SWQsIGNvbnRlbnQgfSlcbiAgfVxuXG4gIHJldHVybiB7IHRhYnMgfVxufVxuXG5mdW5jdGlvbiBub3JtYWxpemVUYWJJZChyYXdJZDogc3RyaW5nKTogc3RyaW5nIHtcbiAgcmV0dXJuIHJhd0lkXG4gICAgLnRyaW0oKVxuICAgIC50b0xvd2VyQ2FzZSgpXG4gICAgLnJlcGxhY2UoL1xccysvZywgJy0nKVxuICAgIC5yZXBsYWNlKC9bXlxcdy1dL2csICcnKVxufVxuXG5leHBvcnQgZnVuY3Rpb24gY29udGVudFRhYnNQbHVnaW4obWQ6IE1hcmtkb3duSXQpIHtcbiAgY29uc3QgcGFyc2VUYWJzQmxvY2sgPSAoc3RhdGU6IHtcbiAgICBzcmM6IHN0cmluZ1xuICAgIGJNYXJrczogbnVtYmVyW11cbiAgICBlTWFya3M6IG51bWJlcltdXG4gICAgdFNoaWZ0OiBudW1iZXJbXVxuICB9LCBzdGFydExpbmU6IG51bWJlciwgZW5kTGluZTogbnVtYmVyKSA9PiB7XG4gICAgY29uc3QgdGFiU3RhcnQgPSAvXlxccyo6OjpcXHMqdGFiXFxzKyguKz8pXFxzKiQvXG4gICAgY29uc3QgdGFic1N0YXJ0ID0gL15cXHMqOjo6XFxzKnRhYnNcXHMqJC9cbiAgICBjb25zdCB0YWJzRW5kID0gL15cXHMqOjo6XFxzKiQvXG5cbiAgICBsZXQgY2xvc2luZ0xpbmUgPSAtMVxuICAgIGxldCBsaW5lID0gc3RhcnRMaW5lICsgMVxuICAgIGxldCBkZXB0aCA9IDFcbiAgICBsZXQgaW5UYWIgPSBmYWxzZVxuXG4gICAgZm9yICg7IGxpbmUgPD0gZW5kTGluZTsgbGluZSsrKSB7XG4gICAgICBjb25zdCBsaW5lU3RhcnQgPSBzdGF0ZS5iTWFya3NbbGluZV0gKyBzdGF0ZS50U2hpZnRbbGluZV1cbiAgICAgIGNvbnN0IGxpbmVFbmQgPSBzdGF0ZS5lTWFya3NbbGluZV1cbiAgICAgIGNvbnN0IGxpbmVDb250ZW50ID0gc3RhdGUuc3JjLnNsaWNlKGxpbmVTdGFydCwgbGluZUVuZClcblxuICAgICAgaWYgKHRhYnNTdGFydC50ZXN0KGxpbmVDb250ZW50KSAmJiBsaW5lICE9PSBzdGFydExpbmUpIHtcbiAgICAgICAgZGVwdGggKz0gMVxuICAgICAgICBjb250aW51ZVxuICAgICAgfVxuXG4gICAgICBpZiAodGFic0VuZC50ZXN0KGxpbmVDb250ZW50KSkge1xuICAgICAgICBpZiAoaW5UYWIpIHtcbiAgICAgICAgICBpblRhYiA9IGZhbHNlXG4gICAgICAgICAgY29udGludWVcbiAgICAgICAgfVxuXG4gICAgICAgIGlmIChkZXB0aCA8PSAxKSB7XG4gICAgICAgICAgY2xvc2luZ0xpbmUgPSBsaW5lXG4gICAgICAgICAgYnJlYWtcbiAgICAgICAgfVxuXG4gICAgICAgIGRlcHRoIC09IDFcbiAgICAgICAgY29udGludWVcbiAgICAgIH1cblxuICAgICAgaWYgKHRhYlN0YXJ0LnRlc3QobGluZUNvbnRlbnQpKSB7XG4gICAgICAgIGluVGFiID0gdHJ1ZVxuICAgICAgICBjb250aW51ZVxuICAgICAgfVxuICAgIH1cblxuICAgIGlmIChjbG9zaW5nTGluZSA9PT0gLTEpIHtcbiAgICAgIHJldHVybiB7IGNvbnRlbnQ6ICcnLCB0YWJzOiBbXSwgY2xvc2luZ0xpbmU6IC0xIH1cbiAgICB9XG5cbiAgICBjb25zdCByYXdDb250ZW50ID0gc3RhdGUuc3JjLnNsaWNlKFxuICAgICAgc3RhdGUuYk1hcmtzW3N0YXJ0TGluZSArIDFdLFxuICAgICAgc3RhdGUuYk1hcmtzW2Nsb3NpbmdMaW5lXVxuICAgIClcbiAgICBjb25zdCB7IHRhYnMgfSA9IHBhcnNlVGFic0NvbnRlbnQocmF3Q29udGVudClcblxuICAgIHJldHVybiB7IGNvbnRlbnQ6IHJhd0NvbnRlbnQsIHRhYnMsIGNsb3NpbmdMaW5lIH1cbiAgfVxuXG4gIC8vIENyZWF0ZSBjdXN0b20gY29udGFpbmVyIGZvciB0YWJzXG4gIGNvbnN0IHRhYnNDb250YWluZXI6IFJ1bGVCbG9jayA9IChzdGF0ZSwgc3RhcnRMaW5lLCBlbmRMaW5lLCBzaWxlbnQpID0+IHtcbiAgICBjb25zdCBzdGFydCA9IHN0YXRlLmJNYXJrc1tzdGFydExpbmVdICsgc3RhdGUudFNoaWZ0W3N0YXJ0TGluZV1cbiAgICBjb25zdCBtYXggPSBzdGF0ZS5lTWFya3Nbc3RhcnRMaW5lXVxuICAgIGNvbnN0IGxpbmUgPSBzdGF0ZS5zcmMuc2xpY2Uoc3RhcnQsIG1heClcblxuICAgIC8vIENoZWNrIGZvciA6OjogdGFicyBvcGVuaW5nXG4gICAgaWYgKCFsaW5lLm1hdGNoKC9eXFxzKjo6Olxccyp0YWJzXFxzKiQvKSkge1xuICAgICAgcmV0dXJuIGZhbHNlXG4gICAgfVxuXG4gICAgaWYgKHNpbGVudCkge1xuICAgICAgcmV0dXJuIHRydWVcbiAgICB9XG5cbiAgICAvLyBGaW5kIHRoZSBjbG9zaW5nIDo6OlxuICAgIGNvbnN0IHBhcnNlZCA9IHBhcnNlVGFic0Jsb2NrKHN0YXRlLCBzdGFydExpbmUsIGVuZExpbmUpXG4gICAgY29uc3QgY2xvc2luZ0xpbmUgPSBwYXJzZWQuY2xvc2luZ0xpbmVcbiAgICBjb25zdCB7IHRhYnMgfSA9IHBhcnNlZFxuXG4gICAgaWYgKGNsb3NpbmdMaW5lID09PSAtMSkge1xuICAgICAgY29uc3QgbWFya2VyVG9rZW4gPSBzdGF0ZS5wdXNoKCd0YWJzX21hcmtlcicsICcnLCAwKVxuICAgICAgbWFya2VyVG9rZW4uY29udGVudCA9IEpTT04uc3RyaW5naWZ5KHsgZXJyb3I6ICd0YWJzIGJsb2NrIGlzIG1pc3NpbmcgY2xvc2luZyA6OjonLCB0YWJzOiBbXSB9KVxuICAgICAgbWFya2VyVG9rZW4ubWFwID0gW3N0YXJ0TGluZSwgZW5kTGluZV1cbiAgICAgIHN0YXRlLmxpbmUgPSBlbmRMaW5lICsgMVxuICAgICAgcmV0dXJuIHRydWVcbiAgICB9XG5cbiAgICAvLyBHZXQgdGhlIGNvbnRlbnQgYmV0d2VlbiBvcGVuaW5nIGFuZCBjbG9zaW5nXG4gICAgaWYgKHRhYnMubGVuZ3RoID09PSAwKSB7XG4gICAgICBjb25zdCBtYXJrZXJUb2tlbiA9IHN0YXRlLnB1c2goJ3RhYnNfbWFya2VyJywgJycsIDApXG4gICAgICBtYXJrZXJUb2tlbi5jb250ZW50ID0gSlNPTi5zdHJpbmdpZnkoeyBlcnJvcjogJ3RhYnMgYmxvY2sgaGFzIG5vIHZhbGlkIHRhYiBzZWN0aW9ucycsIHRhYnM6IFtdIH0pXG4gICAgICBtYXJrZXJUb2tlbi5tYXAgPSBbc3RhcnRMaW5lLCBjbG9zaW5nTGluZV1cbiAgICAgIHN0YXRlLmxpbmUgPSBjbG9zaW5nTGluZSArIDFcbiAgICAgIHJldHVybiB0cnVlXG4gICAgfVxuXG4gICAgLy8gR2VuZXJhdGUgYSB1bmlxdWUgSUQgZm9yIHRoaXMgdGFicyBpbnN0YW5jZVxuICAgIGNvbnN0IHRhYnNJZCA9IGB0YWJzLSR7RGF0ZS5ub3coKX0tJHtNYXRoLnJhbmRvbSgpLnRvU3RyaW5nKDM2KS5zbGljZSgyLCA4KX1gXG5cbiAgICAvLyBSZW1vdmUgdGVtcG9yYXJ5IEhUTUwgdG9rZW4gZnJvbSBvdXRwdXQgYW5kIGVtaXQgbWFya2VyIHRva2VuIG9ubHkuXG5cbiAgICAvLyBXZSBuZWVkIHRvIHJlbmRlciB0aGUgY29tcG9uZW50IGlubGluZSAtIHVzZSBhIHNpbXBsZXIgYXBwcm9hY2hcbiAgICAvLyBKdXN0IG1hcmsgdGhlIHNlY3Rpb24gd2l0aCBzcGVjaWFsIG1hcmtlcnMgdGhhdCBWdWUgY2FuIHBpY2sgdXBcbiAgICBjb25zdCBtYXJrZXJUb2tlbiA9IHN0YXRlLnB1c2goJ3RhYnNfbWFya2VyJywgJycsIDApXG4gICAgbWFya2VyVG9rZW4uY29udGVudCA9IEpTT04uc3RyaW5naWZ5KHsgdGFicywgdGFic0lkIH0pXG4gICAgbWFya2VyVG9rZW4ubWFwID0gW3N0YXJ0TGluZSwgY2xvc2luZ0xpbmVdXG4gICAgc3RhdGUubGluZSA9IGNsb3NpbmdMaW5lICsgMVxuXG4gICAgcmV0dXJuIHRydWVcbiAgfVxuXG4gIC8vIEFkZCB0aGUgcGx1Z2luXG4gIG1kLmJsb2NrLnJ1bGVyLmFmdGVyKCdmZW5jZScsICdjb250ZW50X3RhYnMnLCB0YWJzQ29udGFpbmVyLCB7XG4gICAgYWx0OiBbJ3BhcmFncmFwaCcsICdyZWZlcmVuY2UnLCAnYmxvY2txdW90ZScsICdsaXN0J11cbiAgfSlcblxuICAvLyBDdXN0b20gcmVuZGVyZXIgZm9yIHRoZSBtYXJrZXJcbiAgbWQucmVuZGVyZXIucnVsZXMudGFic19tYXJrZXIgPSAodG9rZW5zLCBpZHgsIG9wdGlvbnMsIGVudiwgc2VsZikgPT4ge1xuICAgIGNvbnN0IHRva2VuID0gdG9rZW5zW2lkeF1cbiAgICB0cnkge1xuICAgICAgY29uc3QgZGF0YSA9IEpTT04ucGFyc2UodG9rZW4uY29udGVudClcbiAgICAgIGlmIChkYXRhLmVycm9yKSB7XG4gICAgICAgIHJldHVybiBgPGRpdiBjbGFzcz1cXFwiY29udGVudC10YWJzLWVycm9yXFxcIj4ke2RhdGEuZXJyb3J9PC9kaXY+YFxuICAgICAgfVxuICAgICAgY29uc3QgdGFicyA9IGRhdGEudGFicy5tYXAoKHQ6IHtpZDogc3RyaW5nLCBsYWJlbDogc3RyaW5nfSkgPT4ge1xuICAgICAgICBjb25zdCBpZCA9IG5vcm1hbGl6ZVRhYklkKHQuaWQpXG4gICAgICAgIHJldHVybiB7XG4gICAgICAgICAgaWQsXG4gICAgICAgICAgbGFiZWw6IHQubGFiZWwuY2hhckF0KDApLnRvVXBwZXJDYXNlKCkgKyB0LmxhYmVsLnNsaWNlKDEpXG4gICAgICAgIH1cbiAgICAgIH0pXG5cbiAgICAgIC8vIEdlbmVyYXRlIHRoZSBWdWUgY29tcG9uZW50IEhUTUwgd2l0aCBwcmUtcmVuZGVyZWQgY29udGVudFxuICAgICAgbGV0IGh0bWwgPSBgPGRpdiBjbGFzcz1cImNvbnRlbnQtdGFicy13cmFwcGVyXCIgZGF0YS10YWJzLWlkPVwiJHtkYXRhLnRhYnNJZH1cIj5gXG4gICAgICBodG1sICs9IGA8ZGl2IGNsYXNzPVwiY29udGVudC10YWJzXCI+YFxuICAgICAgaHRtbCArPSBgPGRpdiBjbGFzcz1cInRhYi1oZWFkZXJzXCI+YFxuXG4gICAgICB0YWJzLmZvckVhY2goKHRhYjoge2lkOiBzdHJpbmcsIGxhYmVsOiBzdHJpbmd9LCBpZHg6IG51bWJlcikgPT4ge1xuICAgICAgICBjb25zdCBhY3RpdmUgPSBpZHggPT09IDAgPyAnYWN0aXZlJyA6ICcnXG4gICAgICAgIGh0bWwgKz0gYDxidXR0b24gY2xhc3M9XCJ0YWItaGVhZGVyICR7YWN0aXZlfVwiIGRhdGEtdGFiPVwiJHt0YWIuaWR9XCI+JHt0YWIubGFiZWx9PC9idXR0b24+YFxuICAgICAgfSlcblxuICAgICAgaHRtbCArPSBgPC9kaXY+YFxuICAgICAgaHRtbCArPSBgPGRpdiBjbGFzcz1cInRhYi1ib2RpZXNcIj5gXG5cbiAgICAgIGRhdGEudGFicy5mb3JFYWNoKCh0YWI6IHtpZDogc3RyaW5nLCBsYWJlbDogc3RyaW5nLCBjb250ZW50OiBzdHJpbmd9LCBpZHg6IG51bWJlcikgPT4ge1xuICAgICAgICBjb25zdCBkaXNwbGF5ID0gaWR4ID09PSAwID8gJ2Jsb2NrJyA6ICdub25lJ1xuICAgICAgICBjb25zdCBub3JtYWxpemVkSWQgPSBub3JtYWxpemVUYWJJZCh0YWIuaWQpXG4gICAgICAgIGh0bWwgKz0gYDxkaXYgY2xhc3M9XCJ0YWItYm9keVwiIGRhdGEtdGFiPVwiJHtub3JtYWxpemVkSWR9XCIgc3R5bGU9XCJkaXNwbGF5OiAke2Rpc3BsYXl9XCI+YFxuICAgICAgICBodG1sICs9IG1kLnJlbmRlcih0YWIuY29udGVudClcbiAgICAgICAgaHRtbCArPSBgPC9kaXY+YFxuICAgICAgfSlcblxuICAgICAgaHRtbCArPSBgPC9kaXY+PC9kaXY+PC9kaXY+YFxuXG4gICAgICByZXR1cm4gaHRtbFxuICAgIH0gY2F0Y2ggKGUpIHtcbiAgICAgIHJldHVybiBgPGRpdiBjbGFzcz1cImNvbnRlbnQtdGFicy1lcnJvclwiPkVycm9yIHBhcnNpbmcgdGFiczwvZGl2PmBcbiAgICB9XG4gIH1cbn1cblxuLy8gQ2xpZW50LXNpZGUgc2NyaXB0IHRvIGluaXRpYWxpemUgdGFiIGJlaGF2aW9yXG5leHBvcnQgY29uc3QgdGFic0NsaWVudFNjcmlwdCA9IGBcbmRvY3VtZW50LmFkZEV2ZW50TGlzdGVuZXIoJ0RPTUNvbnRlbnRMb2FkZWQnLCAoKSA9PiB7XG4gIGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3JBbGwoJy5jb250ZW50LXRhYnMtd3JhcHBlcicpLmZvckVhY2god3JhcHBlciA9PiB7XG4gICAgY29uc3QgaGVhZGVycyA9IHdyYXBwZXIucXVlcnlTZWxlY3RvckFsbCgnLnRhYi1oZWFkZXInKVxuICAgIGNvbnN0IGJvZGllcyA9IHdyYXBwZXIucXVlcnlTZWxlY3RvckFsbCgnLnRhYi1ib2R5JylcblxuICAgIGhlYWRlcnMuZm9yRWFjaChoZWFkZXIgPT4ge1xuICAgICAgaGVhZGVyLmFkZEV2ZW50TGlzdGVuZXIoJ2NsaWNrJywgKCkgPT4ge1xuICAgICAgICBjb25zdCB0YWJJZCA9IGhlYWRlci5nZXRBdHRyaWJ1dGUoJ2RhdGEtdGFiJylcblxuICAgICAgICAvLyBVcGRhdGUgYWN0aXZlIHN0YXRlXG4gICAgICAgIGhlYWRlcnMuZm9yRWFjaChoID0+IGguY2xhc3NMaXN0LnJlbW92ZSgnYWN0aXZlJykpXG4gICAgICAgIGhlYWRlci5jbGFzc0xpc3QuYWRkKCdhY3RpdmUnKVxuXG4gICAgICAgIC8vIFNob3cvaGlkZSBib2RpZXNcbiAgICAgICAgYm9kaWVzLmZvckVhY2goYm9keSA9PiB7XG4gICAgICAgICAgaWYgKGJvZHkuZ2V0QXR0cmlidXRlKCdkYXRhLXRhYicpID09PSB0YWJJZCkge1xuICAgICAgICAgICAgYm9keS5zdHlsZS5kaXNwbGF5ID0gJ2Jsb2NrJ1xuICAgICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICBib2R5LnN0eWxlLmRpc3BsYXkgPSAnbm9uZSdcbiAgICAgICAgICB9XG4gICAgICAgIH0pXG4gICAgICB9KVxuXG4gICAgICBoZWFkZXIuYWRkRXZlbnRMaXN0ZW5lcigna2V5ZG93bicsIChlKSA9PiB7XG4gICAgICAgIGNvbnN0IGN1cnJlbnRJbmRleCA9IEFycmF5LmZyb20oaGVhZGVycykuaW5kZXhPZihoZWFkZXIpXG5cbiAgICAgICAgaWYgKGUua2V5ID09PSAnQXJyb3dSaWdodCcgfHwgZS5rZXkgPT09ICdBcnJvd0Rvd24nKSB7XG4gICAgICAgICAgZS5wcmV2ZW50RGVmYXVsdCgpXG4gICAgICAgICAgY29uc3QgbmV4dEluZGV4ID0gKGN1cnJlbnRJbmRleCArIDEpICUgaGVhZGVycy5sZW5ndGhcbiAgICAgICAgICBoZWFkZXJzW25leHRJbmRleF0uY2xpY2soKVxuICAgICAgICAgIGhlYWRlcnNbbmV4dEluZGV4XS5mb2N1cygpXG4gICAgICAgIH0gZWxzZSBpZiAoZS5rZXkgPT09ICdBcnJvd0xlZnQnIHx8IGUua2V5ID09PSAnQXJyb3dVcCcpIHtcbiAgICAgICAgICBlLnByZXZlbnREZWZhdWx0KClcbiAgICAgICAgICBjb25zdCBwcmV2SW5kZXggPSAoY3VycmVudEluZGV4IC0gMSArIGhlYWRlcnMubGVuZ3RoKSAlIGhlYWRlcnMubGVuZ3RoXG4gICAgICAgICAgaGVhZGVyc1twcmV2SW5kZXhdLmNsaWNrKClcbiAgICAgICAgICBoZWFkZXJzW3ByZXZJbmRleF0uZm9jdXMoKVxuICAgICAgICB9IGVsc2UgaWYgKGUua2V5ID09PSAnSG9tZScpIHtcbiAgICAgICAgICBlLnByZXZlbnREZWZhdWx0KClcbiAgICAgICAgICBoZWFkZXJzWzBdLmNsaWNrKClcbiAgICAgICAgICBoZWFkZXJzWzBdLmZvY3VzKClcbiAgICAgICAgfSBlbHNlIGlmIChlLmtleSA9PT0gJ0VuZCcpIHtcbiAgICAgICAgICBlLnByZXZlbnREZWZhdWx0KClcbiAgICAgICAgICBoZWFkZXJzW2hlYWRlcnMubGVuZ3RoIC0gMV0uY2xpY2soKVxuICAgICAgICAgIGhlYWRlcnNbaGVhZGVycy5sZW5ndGggLSAxXS5mb2N1cygpXG4gICAgICAgIH1cbiAgICAgIH0pXG4gICAgfSlcbiAgfSlcbn0pXG5gXG4iLCAiY29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2Rpcm5hbWUgPSBcIi9Vc2Vycy9rb29zaGFwYXJpL0NvZGVQcm9qZWN0cy9QaGVub3R5cGUvcmVwb3MvdGhlZ2VudC9kb2NzLy52aXRlcHJlc3MvcGx1Z2luc1wiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9maWxlbmFtZSA9IFwiL1VzZXJzL2tvb3NoYXBhcmkvQ29kZVByb2plY3RzL1BoZW5vdHlwZS9yZXBvcy90aGVnZW50L2RvY3MvLnZpdGVwcmVzcy9wbHVnaW5zL3ZpZGVvLWVtYmVkLnRzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ltcG9ydF9tZXRhX3VybCA9IFwiZmlsZTovLy9Vc2Vycy9rb29zaGFwYXJpL0NvZGVQcm9qZWN0cy9QaGVub3R5cGUvcmVwb3MvdGhlZ2VudC9kb2NzLy52aXRlcHJlc3MvcGx1Z2lucy92aWRlby1lbWJlZC50c1wiOy8qKlxuICogVmlkZW8gZW1iZWQgcGx1Z2luIGZvciBWaXRlUHJlc3MgbWFya2Rvd24uXG4gKlxuICogQWxsb3dzIGVtYmVkZGluZyByZWNvcmRlZCBQbGF5d3JpZ2h0IHZpZGVvcyBpbiBkb2N1bWVudGF0aW9uIHVzaW5nOlxuICogICAhW0FsdCB0ZXh0XSgvcGF0aC90by92aWRlby53ZWJtKVxuICogICBvciBjdXN0b20gc3ludGF4OlxuICogICA8dmlkZW8gd2lkdGg9XCIxMDAlXCIgY29udHJvbHM+XG4gKiAgICAgPHNvdXJjZSBzcmM9XCIvcmVjb3JkaW5ncy9kZW1vLndlYm1cIiB0eXBlPVwidmlkZW8vd2VibVwiPlxuICogICA8L3ZpZGVvPlxuICpcbiAqIFN1cHBvcnRzIHdlYm0sIG1wNCwgYW5kIG90aGVyIEhUTUw1IHZpZGVvIGZvcm1hdHMuXG4gKi9cblxuaW1wb3J0IHR5cGUgeyBNYXJrZG93bkl0IH0gZnJvbSAnbWFya2Rvd24taXQnXG5cbmludGVyZmFjZSBWaWRlb0VtYmVkT3B0aW9ucyB7XG4gIHdpZHRoPzogc3RyaW5nXG4gIGhlaWdodD86IHN0cmluZ1xuICBjb250cm9scz86IGJvb2xlYW5cbiAgYXV0b3BsYXk/OiBib29sZWFuXG4gIGxvb3A/OiBib29sZWFuXG4gIG11dGVkPzogYm9vbGVhblxufVxuXG4vKipcbiAqIFBhcnNlIHZpZGVvIGVtYmVkIGRpcmVjdGl2ZSBzeW50YXguXG4gKiBFeGFtcGxlOiA6OjogdmlkZW8gL3BhdGgvdG8vdmlkZW8ud2VibSA6OjpcbiAqL1xuZnVuY3Rpb24gcGFyc2VWaWRlb0RpcmVjdGl2ZShcbiAgbWQ6IE1hcmtkb3duSXQsXG4gIF9vcHRpb25zOiBWaWRlb0VtYmVkT3B0aW9uc1xuKTogdm9pZCB7XG4gIGNvbnN0IHZpZGVvQmxvY2tSdWxlID0gKHN0YXRlOiBhbnksIHN0YXJ0TGluZTogbnVtYmVyLCBlbmRMaW5lOiBudW1iZXIpID0+IHtcbiAgICBjb25zdCBwb3MgPSBzdGF0ZS5iTWFya3Nbc3RhcnRMaW5lXSArIHN0YXRlLnRTaGlmdFtzdGFydExpbmVdXG4gICAgY29uc3QgbWF4aW11bSA9IHN0YXRlLmVNYXJrc1tzdGFydExpbmVdXG5cbiAgICAvLyBDaGVjayBmb3IgOjo6IHZpZGVvIHN5bnRheFxuICAgIGlmIChwb3MgKyAzID4gbWF4aW11bSkgcmV0dXJuIGZhbHNlXG4gICAgaWYgKHN0YXRlLnNyYy5zbGljZShwb3MsIHBvcyArIDMpICE9PSAnOjo6JykgcmV0dXJuIGZhbHNlXG5cbiAgICBjb25zdCBtYXJrZXJDb3VudCA9IDNcbiAgICBjb25zdCBtYXJrdXAgPSBzdGF0ZS5zcmMuc2xpY2UocG9zLCBwb3MgKyBtYXJrZXJDb3VudClcbiAgICBjb25zdCBwYXJhbXMgPSBzdGF0ZS5zcmMuc2xpY2UocG9zICsgbWFya2VyQ291bnQsIG1heGltdW0pLnRyaW0oKVxuXG4gICAgaWYgKCFwYXJhbXMuc3RhcnRzV2l0aCgndmlkZW8gJykpIHJldHVybiBmYWxzZVxuXG4gICAgY29uc3QgdmlkZW9TcmMgPSBwYXJhbXMuc2xpY2UoNikudHJpbSgpXG4gICAgaWYgKCF2aWRlb1NyYykgcmV0dXJuIGZhbHNlXG5cbiAgICBsZXQgbmV4dExpbmUgPSBzdGFydExpbmUgKyAxXG5cbiAgICAvLyBGaW5kIGNsb3NpbmcgbWFya2VyXG4gICAgd2hpbGUgKG5leHRMaW5lIDwgZW5kTGluZSkge1xuICAgICAgaWYgKFxuICAgICAgICBzdGF0ZS5iTWFya3NbbmV4dExpbmVdICsgc3RhdGUudFNoaWZ0W25leHRMaW5lXSArIDMgPD1cbiAgICAgICAgc3RhdGUuZU1hcmtzW25leHRMaW5lXVxuICAgICAgKSB7XG4gICAgICAgIGNvbnN0IGNsb3NlUG9zID1cbiAgICAgICAgICBzdGF0ZS5iTWFya3NbbmV4dExpbmVdICsgc3RhdGUudFNoaWZ0W25leHRMaW5lXVxuICAgICAgICBpZiAoXG4gICAgICAgICAgc3RhdGUuc3JjLnNsaWNlKGNsb3NlUG9zLCBjbG9zZVBvcyArIDMpID09PSAnOjo6J1xuICAgICAgICApIHtcbiAgICAgICAgICBicmVha1xuICAgICAgICB9XG4gICAgICB9XG4gICAgICBuZXh0TGluZSsrXG4gICAgfVxuXG4gICAgY29uc3Qgb2xkUGFyZW50ID0gc3RhdGUucGFyZW50VHlwZVxuICAgIHN0YXRlLnBhcmVudFR5cGUgPSAncGFyYWdyYXBoJ1xuXG4gICAgY29uc3QgdG9rZW4gPSBzdGF0ZS5wdXNoKCd2aWRlb19ibG9jaycsICdkaXYnLCAwKVxuICAgIHRva2VuLm1hcmt1cCA9IG1hcmt1cFxuICAgIHRva2VuLm1ldGEgPSB7IHNyYzogdmlkZW9TcmMgfVxuICAgIHRva2VuLm1hcCA9IFtzdGFydExpbmUsIG5leHRMaW5lICsgMV1cblxuICAgIHN0YXRlLnBhcmVudFR5cGUgPSBvbGRQYXJlbnRcbiAgICBzdGF0ZS5saW5lID0gbmV4dExpbmUgKyAxXG5cbiAgICByZXR1cm4gdHJ1ZVxuICB9XG5cbiAgbWQuYmxvY2sucnVsZXIuYmVmb3JlKFxuICAgICdmZW5jZScsXG4gICAgJ3ZpZGVvX2Jsb2NrJyxcbiAgICB2aWRlb0Jsb2NrUnVsZVxuICApXG5cbiAgbWQucmVuZGVyZXIucnVsZXMudmlkZW9fYmxvY2sgPSAodG9rZW5zLCBpZHgpID0+IHtcbiAgICBjb25zdCB0b2tlbiA9IHRva2Vuc1tpZHhdXG4gICAgY29uc3Qgc3JjID0gdG9rZW4ubWV0YT8uc3JjIHx8ICcnXG5cbiAgICByZXR1cm4gYDx2aWRlbyB3aWR0aD1cIjEwMCVcIiBjb250cm9scz5cbiAgPHNvdXJjZSBzcmM9XCIke3NyY31cIiB0eXBlPVwidmlkZW8vd2VibVwiPlxuICBZb3VyIGJyb3dzZXIgZG9lcyBub3Qgc3VwcG9ydCB0aGUgdmlkZW8gdGFnLlxuPC92aWRlbz5cXG5gXG4gIH1cbn1cblxuLyoqXG4gKiBFbmhhbmNlZCBpbWFnZSByZW5kZXJpbmcgdG8gc3VwcG9ydCB2aWRlbyBmaWxlcy5cbiAqIENvbnZlcnRzICFbdmlkZW9dKGZpbGUud2VibSkgdG8gPHZpZGVvPiB0YWdzLlxuICovXG5mdW5jdGlvbiBlbmhhbmNlSW1hZ2VSZW5kZXJpbmcoXG4gIG1kOiBNYXJrZG93bkl0LFxuICBvcHRpb25zOiBWaWRlb0VtYmVkT3B0aW9uc1xuKTogdm9pZCB7XG4gIGNvbnN0IG9yaWdpbmFsSW1hZ2VSdWxlID0gbWQucmVuZGVyZXIucnVsZXMuaW1hZ2VcblxuICBtZC5yZW5kZXJlci5ydWxlcy5pbWFnZSA9ICh0b2tlbnMsIGlkeCwgX29wdGlvbnMsIGVudiwgcmVuZGVyZXIpID0+IHtcbiAgICBjb25zdCB0b2tlbiA9IHRva2Vuc1tpZHhdXG4gICAgY29uc3Qgc3JjID0gdG9rZW4uYXR0ckdldCgnc3JjJykgfHwgJydcblxuICAgIC8vIENoZWNrIGlmIGl0J3MgYSB2aWRlbyBmaWxlXG4gICAgaWYgKHNyYy5tYXRjaCgvXFwuKHdlYm18bXA0fG9nZ3xtb3YpJC9pKSkge1xuICAgICAgY29uc3QgYWx0ID0gdG9rZW4uY29udGVudCB8fCAnVmlkZW8nXG4gICAgICBjb25zdCB3aWR0aCA9IG9wdGlvbnMud2lkdGggfHwgJzEwMCUnXG4gICAgICBjb25zdCBjb250cm9scyA9IG9wdGlvbnMuY29udHJvbHMgIT09IGZhbHNlID8gJ2NvbnRyb2xzJyA6ICcnXG4gICAgICBjb25zdCBhdXRvcGxheSA9IG9wdGlvbnMuYXV0b3BsYXkgPyAnYXV0b3BsYXknIDogJydcbiAgICAgIGNvbnN0IGxvb3AgPSBvcHRpb25zLmxvb3AgPyAnbG9vcCcgOiAnJ1xuICAgICAgY29uc3QgbXV0ZWQgPSBvcHRpb25zLm11dGVkID8gJ211dGVkJyA6ICcnXG5cbiAgICAgIGNvbnN0IGV4dCA9IHNyYy5zcGxpdCgnLicpLnBvcCgpPy50b0xvd2VyQ2FzZSgpXG4gICAgICBsZXQgdHlwZSA9ICd2aWRlby93ZWJtJ1xuICAgICAgaWYgKGV4dCA9PT0gJ21wNCcpIHR5cGUgPSAndmlkZW8vbXA0J1xuICAgICAgZWxzZSBpZiAoZXh0ID09PSAnb2dnJykgdHlwZSA9ICd2aWRlby9vZ2cnXG4gICAgICBlbHNlIGlmIChleHQgPT09ICdtb3YnKSB0eXBlID0gJ3ZpZGVvL3F1aWNrdGltZSdcblxuICAgICAgcmV0dXJuIGA8dmlkZW8gd2lkdGg9XCIke3dpZHRofVwiICR7Y29udHJvbHN9ICR7YXV0b3BsYXl9ICR7bG9vcH0gJHttdXRlZH0+XG4gIDxzb3VyY2Ugc3JjPVwiJHtzcmN9XCIgdHlwZT1cIiR7dHlwZX1cIj5cbiAgJHthbHR9XG48L3ZpZGVvPmBcbiAgICB9XG5cbiAgICAvLyBGYWxsIGJhY2sgdG8gZGVmYXVsdCBpbWFnZSByZW5kZXJpbmdcbiAgICByZXR1cm4gb3JpZ2luYWxJbWFnZVJ1bGU/Lih0b2tlbnMsIGlkeCwgX29wdGlvbnMsIGVudiwgcmVuZGVyZXIpIHx8ICcnXG4gIH1cbn1cblxuLyoqXG4gKiBWaXRlUHJlc3MgcGx1Z2luIGZvciB2aWRlbyBlbWJlZGRpbmcgaW4gbWFya2Rvd24uXG4gKlxuICogVXNhZ2UgaW4gbWFya2Rvd246XG4gKiAgICFbTXkgVmlkZW9dKC9yZWNvcmRpbmdzL2RlbW8ud2VibSlcbiAqICAgb3I6XG4gKiAgIDo6OiB2aWRlbyAvcmVjb3JkaW5ncy9kZW1vLndlYm0gOjo6XG4gKlxuICogQHBhcmFtIG1kIE1hcmtkb3duSXQgaW5zdGFuY2VcbiAqIEBwYXJhbSBvcHRpb25zIFZpZGVvIGVtYmVkIG9wdGlvbnNcbiAqL1xuZXhwb3J0IGZ1bmN0aW9uIHZpZGVvRW1iZWRQbHVnaW4oXG4gIG1kOiBNYXJrZG93bkl0LFxuICBvcHRpb25zOiBQYXJ0aWFsPFZpZGVvRW1iZWRPcHRpb25zPiA9IHt9XG4pOiB2b2lkIHtcbiAgY29uc3QgZGVmYXVsdE9wdGlvbnM6IFZpZGVvRW1iZWRPcHRpb25zID0ge1xuICAgIHdpZHRoOiAnMTAwJScsXG4gICAgaGVpZ2h0OiAnYXV0bycsXG4gICAgY29udHJvbHM6IHRydWUsXG4gICAgYXV0b3BsYXk6IGZhbHNlLFxuICAgIGxvb3A6IGZhbHNlLFxuICAgIG11dGVkOiBmYWxzZSxcbiAgICAuLi5vcHRpb25zLFxuICB9XG5cbiAgcGFyc2VWaWRlb0RpcmVjdGl2ZShtZCwgZGVmYXVsdE9wdGlvbnMpXG4gIGVuaGFuY2VJbWFnZVJlbmRlcmluZyhtZCwgZGVmYXVsdE9wdGlvbnMpXG59XG5cbmV4cG9ydCB0eXBlIHsgVmlkZW9FbWJlZE9wdGlvbnMgfVxuIiwgImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCIvVXNlcnMva29vc2hhcGFyaS9Db2RlUHJvamVjdHMvUGhlbm90eXBlL3JlcG9zL3RoZWdlbnQvZG9jcy8udml0ZXByZXNzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCIvVXNlcnMva29vc2hhcGFyaS9Db2RlUHJvamVjdHMvUGhlbm90eXBlL3JlcG9zL3RoZWdlbnQvZG9jcy8udml0ZXByZXNzL3NpZGViYXItY2Fub25pY2FsLnRzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ltcG9ydF9tZXRhX3VybCA9IFwiZmlsZTovLy9Vc2Vycy9rb29zaGFwYXJpL0NvZGVQcm9qZWN0cy9QaGVub3R5cGUvcmVwb3MvdGhlZ2VudC9kb2NzLy52aXRlcHJlc3Mvc2lkZWJhci1jYW5vbmljYWwudHNcIjsvLyBDYW5vbmljYWwgc2lkZWJhciAtIGFsaWduZWQgd2l0aCBGYXN0TUNQL3V2L1N2ZWx0ZSBwYXR0ZXJuc1xuLy8gQmFzZWQgb24gcmVzZWFyY2g6IEdldCBTdGFydGVkIFx1MjE5MiBUdXRvcmlhbHMgXHUyMTkyIEhvdy10byBcdTIxOTIgUmVmZXJlbmNlIFx1MjE5MiBFeHBsYW5hdGlvbiBcdTIxOTIgT3BlcmF0aW9ucyBcdTIxOTIgR292ZXJuYW5jZVxuXG5leHBvcnQgY29uc3Qgc2lkZWJhciA9IHtcbiAgJy8nOiBbXG4gICAge1xuICAgICAgdGV4dDogJ0dldHRpbmcgU3RhcnRlZCcsXG4gICAgICBjb2xsYXBzZWQ6IGZhbHNlLFxuICAgICAgaXRlbXM6IFtcbiAgICAgICAgeyB0ZXh0OiAnSG9tZScsIGxpbms6ICcvJyB9LFxuICAgICAgICB7IHRleHQ6ICdTdGFydCBIZXJlJywgbGluazogJy9zdGFydC1oZXJlLm1kJyB9LFxuICAgICAgXVxuICAgIH0sXG4gICAge1xuICAgICAgdGV4dDogJ1R1dG9yaWFscycsXG4gICAgICBjb2xsYXBzZWQ6IGZhbHNlLFxuICAgICAgaXRlbXM6IFtcbiAgICAgICAgeyB0ZXh0OiAnVHV0b3JpYWxzIE92ZXJ2aWV3JywgbGluazogJy90dXRvcmlhbHMvJyB9LFxuICAgICAgICB7IHRleHQ6ICdRdWljayBTdGFydCcsIGxpbms6ICcvdHV0b3JpYWxzLzAxLXF1aWNrLXN0YXJ0Lm1kJyB9LFxuICAgICAgICB7IHRleHQ6ICdDb25maWd1cmF0aW9uJywgbGluazogJy90dXRvcmlhbHMvMDItY29uZmlndXJhdGlvbi5tZCcgfSxcbiAgICAgIF1cbiAgICB9LFxuICAgIHtcbiAgICAgIHRleHQ6ICdIb3ctdG8gR3VpZGVzJyxcbiAgICAgIGNvbGxhcHNlZDogZmFsc2UsXG4gICAgICBpdGVtczogW1xuICAgICAgICB7IHRleHQ6ICdIb3ctdG8gT3ZlcnZpZXcnLCBsaW5rOiAnL2hvdy10by8nIH0sXG4gICAgICAgIHsgdGV4dDogJ0luc3RhbGxhdGlvbicsIGxpbms6ICcvZ3VpZGVzL0lOU1RBTExBVElPTi5tZCcgfSxcbiAgICAgICAgeyB0ZXh0OiAnUHJvdmlkZXIgU2V0dXAnLCBsaW5rOiAnL2d1aWRlcy9QUk9WSURFUl9TRVRVUF9HVUlERS5tZCcgfSxcbiAgICAgICAgeyB0ZXh0OiAnVGVzdGluZycsIGxpbms6ICcvZ3VpZGVzL1RFU1RJTkcubWQnIH0sXG4gICAgICAgIHsgdGV4dDogJ1Ryb3VibGVzaG9vdGluZycsIGxpbms6ICcvZ3VpZGVzL1RST1VCTEVTSE9PVElORy5tZCcgfSxcbiAgICAgIF1cbiAgICB9LFxuICAgIHtcbiAgICAgIHRleHQ6ICdSZWZlcmVuY2UnLFxuICAgICAgY29sbGFwc2VkOiBmYWxzZSxcbiAgICAgIGl0ZW1zOiBbXG4gICAgICAgIHsgdGV4dDogJ1JlZmVyZW5jZSBJbmRleCcsIGxpbms6ICcvcmVmZXJlbmNlLycgfSxcbiAgICAgICAgeyB0ZXh0OiAnQ29uZmlndXJhdGlvbicsIGxpbms6ICcvcmVmZXJlbmNlL2NvbmZpZ3VyYXRpb24ubWQnIH0sXG4gICAgICAgIHsgdGV4dDogJ1JvdXRpbmcnLCBsaW5rOiAnL3JlZmVyZW5jZS9yb3V0aW5nLm1kJyB9LFxuICAgICAgICB7IHRleHQ6ICdDTEFVREUgQ29yZSBHdWlkZWxpbmVzJywgbGluazogJy9yZWZlcmVuY2UvQ0xBVURFX0NPUkVfR1VJREVMSU5FUy5tZCcgfSxcbiAgICAgICAgeyB0ZXh0OiAnTUNQIFJldHJ5IFBvbGljeScsIGxpbms6ICcvcmVmZXJlbmNlL01DUF9SRVRSWV9QT0xJQ1kubWQnIH0sXG4gICAgICBdXG4gICAgfSxcbiAgICB7XG4gICAgICB0ZXh0OiAnRXhwbGFuYXRpb24nLFxuICAgICAgY29sbGFwc2VkOiBmYWxzZSxcbiAgICAgIGl0ZW1zOiBbXG4gICAgICAgIHsgdGV4dDogJ0V4cGxhbmF0aW9uIE92ZXJ2aWV3JywgbGluazogJy9leHBsYW5hdGlvbi8nIH0sXG4gICAgICAgIHsgdGV4dDogJ0FnZW50IFNhbmRib3hpbmcnLCBsaW5rOiAnL2FyY2hpdGVjdHVyZS9BR0VOVF9TQU5EQk9YSU5HX0FSQ0hJVEVDVFVSRS5tZCcgfSxcbiAgICAgICAgeyB0ZXh0OiAnQ29zdCBHb3Zlcm5hbmNlJywgbGluazogJy9nb3Zlcm5hbmNlL0NPU1RfR09WRVJOQU5DRV9ERVNJR04ubWQnIH0sXG4gICAgICAgIHsgdGV4dDogJ09QQSBJbnRlZ3JhdGlvbicsIGxpbms6ICcvZ292ZXJuYW5jZS9PUEFfSU5URUdSQVRJT05fREVTSUdOLm1kJyB9LFxuICAgICAgXVxuICAgIH0sXG4gICAge1xuICAgICAgdGV4dDogJ09wZXJhdGlvbnMnLFxuICAgICAgY29sbGFwc2VkOiBmYWxzZSxcbiAgICAgIGl0ZW1zOiBbXG4gICAgICAgIHsgdGV4dDogJ09wZXJhdGlvbnMgT3ZlcnZpZXcnLCBsaW5rOiAnL29wZXJhdGlvbnMvJyB9LFxuICAgICAgICB7IHRleHQ6ICdKb3VybmV5IFRyYWNlYWJpbGl0eScsIGxpbms6ICcvb3BlcmF0aW9ucy9qb3VybmV5LXRyYWNlYWJpbGl0eS5tZCcgfSxcbiAgICAgICAgeyB0ZXh0OiAnUnVuYm9va3MnLCBsaW5rOiAnL29wZXJhdGlvbnMvcnVuYm9va3MubWQnIH0sXG4gICAgICAgIHsgdGV4dDogJ1Ryb3VibGVzaG9vdGluZycsIGxpbms6ICcvb3BlcmF0aW9ucy90cm91Ymxlc2hvb3RpbmcubWQnIH0sXG4gICAgICBdXG4gICAgfSxcbiAgICB7XG4gICAgICB0ZXh0OiAnR292ZXJuYW5jZScsXG4gICAgICBjb2xsYXBzZWQ6IGZhbHNlLFxuICAgICAgaXRlbXM6IFtcbiAgICAgICAgeyB0ZXh0OiAnR292ZXJuYW5jZSBPdmVydmlldycsIGxpbms6ICcvZ292ZXJuYW5jZS8nIH0sXG4gICAgICAgIHsgdGV4dDogJ1RERC9CREQvU0REJywgbGluazogJy9nb3Zlcm5hbmNlL1RERF9CRERfU0REX0dPVkVSTkFOQ0UubWQnIH0sXG4gICAgICAgIHsgdGV4dDogJ1Rlc3QgU3RyYXRlZ3knLCBsaW5rOiAnL2dvdmVybmFuY2UvQUdFTlRfT05MWV9URVNUX1NUUkFURUdZLm1kJyB9LFxuICAgICAgICB7IHRleHQ6ICdUZXJtaW5vbG9neScsIGxpbms6ICcvZ292ZXJuYW5jZS9URVJNSU5PTE9HWV9MQVlFUlMubWQnIH0sXG4gICAgICAgIHsgdGV4dDogJ0NvbnRleHQgRG9jcycsIGxpbms6ICcvZ292ZXJuYW5jZS9DT05URVhUX0RPQ1NfUFJPQ0VTUy5tZCcgfSxcbiAgICAgIF1cbiAgICB9LFxuICAgIHtcbiAgICAgIHRleHQ6ICdHdWlkZXMnLFxuICAgICAgY29sbGFwc2VkOiB0cnVlLFxuICAgICAgaXRlbXM6IFtcbiAgICAgICAgeyB0ZXh0OiAnR3VpZGVzIEluZGV4JywgbGluazogJy9ndWlkZXMvJyB9LFxuICAgICAgICB7IHRleHQ6ICdEb2NzIEdvdmVybmFuY2UnLCBsaW5rOiAnL2d1aWRlcy9WSVRFUFJFU1NfRE9DU19HT1ZFUk5BTkNFLm1kJyB9LFxuICAgICAgICB7IHRleHQ6ICdWaXRlUHJlc3MgU2V0dXAnLCBsaW5rOiAnL2d1aWRlcy9WSVRFUFBSRVNTX1NFVFVQLm1kJyB9LFxuICAgICAgICB7IHRleHQ6ICdWaXRlUHJlc3MgVXNhZ2UnLCBsaW5rOiAnL2d1aWRlcy9WSVRFUFJFU1NfVVNBR0VfR1VJREUubWQnIH0sXG4gICAgICAgIHsgdGV4dDogJ1F1aWNrIFJlZmVyZW5jZScsIGxpbms6ICcvZ3VpZGVzL1FVSUNLX1JFRkVSRU5DRS5tZCcgfSxcbiAgICAgICAgeyB0ZXh0OiAnU2hlbGwgRW52aXJvbm1lbnQnLCBsaW5rOiAnL2d1aWRlcy9TSEVMTF9FTlZJUk9OTUVOVF9DT01QTEVURS5tZCcgfSxcbiAgICAgICAgeyB0ZXh0OiAnQ3Jvc3MtUGxhdGZvcm0nLCBsaW5rOiAnL2d1aWRlcy9DUk9TU19QTEFURk9STV9DT01QTEVURS5tZCcgfSxcbiAgICAgIF1cbiAgICB9LFxuICAgIHtcbiAgICAgIHRleHQ6ICdBUEknLFxuICAgICAgY29sbGFwc2VkOiBmYWxzZSxcbiAgICAgIGl0ZW1zOiBbXG4gICAgICAgIHsgdGV4dDogJ0FQSSBPdmVydmlldycsIGxpbms6ICcvYXBpLycgfSxcbiAgICAgICAgeyB0ZXh0OiAnQVBJIFJFQURNRScsIGxpbms6ICcvYXBpL1JFQURNRS5tZCcgfSxcbiAgICAgIF1cbiAgICB9LFxuICAgIHtcbiAgICAgIHRleHQ6ICdBcmNoaXRlY3R1cmUnLFxuICAgICAgY29sbGFwc2VkOiB0cnVlLFxuICAgICAgaXRlbXM6IFtcbiAgICAgICAgeyB0ZXh0OiAnTW9kdWxlIERlcGVuZGVuY2llcycsIGxpbms6ICcvYXJjaGl0ZWN0dXJlL2RpYWdyYW1zL21vZHVsZS1kZXBlbmRlbmNpZXMubWQnIH0sXG4gICAgICAgIHsgdGV4dDogJ1BhY2thZ2UgU3RydWN0dXJlJywgbGluazogJy9hcmNoaXRlY3R1cmUvZGlhZ3JhbXMvcGFja2FnZS1zdHJ1Y3R1cmUubWQnIH0sXG4gICAgICBdXG4gICAgfSxcbiAgICB7XG4gICAgICB0ZXh0OiAnQ29udHJhY3RzJyxcbiAgICAgIGNvbGxhcHNlZDogdHJ1ZSxcbiAgICAgIGl0ZW1zOiBbXG4gICAgICAgIHsgdGV4dDogJ0NvbnRyYWN0IEF1dGhvcml0eScsIGxpbms6ICcvY29udHJhY3RzL0NPTlRSQUNUX0FVVEhPUklUWS5tZCcgfSxcbiAgICAgICAgeyB0ZXh0OiAnRmFsbGJhY2sgUG9saWN5JywgbGluazogJy9jb250cmFjdHMvRkFMTEJBQ0tfUE9MSUNZLm1kJyB9LFxuICAgICAgICB7IHRleHQ6ICdQcm92aWRlciBBZGFwdGVyIENvbnRyYWN0cycsIGxpbms6ICcvY29udHJhY3RzL1BST1ZJREVSX0FEQVBURVJfQ09OVFJBQ1RTLm1kJyB9LFxuICAgICAgXVxuICAgIH0sXG4gICAge1xuICAgICAgdGV4dDogJ0VudGVycHJpc2UnLFxuICAgICAgY29sbGFwc2VkOiB0cnVlLFxuICAgICAgaXRlbXM6IFtcbiAgICAgICAgeyB0ZXh0OiAnT3BlcmF0aW5nIE1vZGVsJywgbGluazogJy9lbnRlcnByaXNlL09QRVJBVElOR19NT0RFTC5tZCcgfSxcbiAgICAgICAgeyB0ZXh0OiAnU2VjdXJpdHkgQ29tcGxpYW5jZScsIGxpbms6ICcvZW50ZXJwcmlzZS9TRUNVUklUWV9DT01QTElBTkNFX1NJR05PRkYubWQnIH0sXG4gICAgICAgIHsgdGV4dDogJ0RlY29tbWlzc2lvbmluZyBQbGFuJywgbGluazogJy9lbnRlcnByaXNlL0RFQ09NTUlTU0lPTklOR19QTEFOLm1kJyB9LFxuICAgICAgXVxuICAgIH0sXG4gICAge1xuICAgICAgdGV4dDogJ0V4YW1wbGVzJyxcbiAgICAgIGNvbGxhcHNlZDogdHJ1ZSxcbiAgICAgIGl0ZW1zOiBbXG4gICAgICAgIHsgdGV4dDogJ0V4YW1wbGVzIE92ZXJ2aWV3JywgbGluazogJy9leGFtcGxlcy9SRUFETUUubWQnIH0sXG4gICAgICAgIHsgdGV4dDogJ0NvZGUgUGxheWdyb3VuZCcsIGxpbms6ICcvZXhhbXBsZXMvY29kZS1wbGF5Z3JvdW5kLWV4YW1wbGUubWQnIH0sXG4gICAgICAgIHsgdGV4dDogJ01lcm1haWQgRGlhZ3JhbXMnLCBsaW5rOiAnL2V4YW1wbGVzL21lcm1haWQtZXhhbXBsZS5tZCcgfSxcbiAgICAgICAgeyB0ZXh0OiAnVG9vbHRpcHMnLCBsaW5rOiAnL2V4YW1wbGVzL3Rvb2x0aXAtZXhhbXBsZS5tZCcgfSxcbiAgICAgIF1cbiAgICB9LFxuICBdXG59XG4iXSwKICAibWFwcGluZ3MiOiAiO0FBQTBYLFNBQVMsU0FBUyxlQUFlO0FBQzNaLFNBQVMscUJBQXFCO0FBRTlCLFNBQVMsb0JBQW9CO0FBQzdCLFNBQVMsbUJBQW1CO0FBQzVCLFNBQVMsa0JBQWtCOzs7QUNEM0IsSUFBTSxnQkFBd0M7QUFBQSxFQUM1QyxXQUFXO0FBQUEsRUFDWCxhQUFhO0FBQUEsRUFDYixnQkFBZ0I7QUFBQSxFQUNoQixTQUFTO0FBQ1g7QUFFTyxTQUFTLGtCQUFrQixJQUFnQjtBQUNoRCxRQUFNLGdCQUE0QixHQUFHLFNBQVMsTUFBTSxhQUFhLFNBQVMsUUFBUSxLQUFLLFNBQVMsTUFBTSxNQUFNO0FBQzFHLFdBQU8sS0FBSyxZQUFZLFFBQVEsS0FBSyxPQUFPO0FBQUEsRUFDOUM7QUFFQSxLQUFHLFNBQVMsTUFBTSxZQUFZLFNBQVMsUUFBUSxLQUFLLFNBQVMsS0FBSyxNQUFNO0FBQ3RFLFVBQU0sT0FBTyxPQUFPLEdBQUcsRUFBRSxRQUFRLE1BQU07QUFHdkMsUUFBSSxRQUFRLEtBQUssV0FBVyxHQUFHLEdBQUc7QUFDaEMsWUFBTSxRQUFRLEtBQUssTUFBTSxpQkFBaUI7QUFDMUMsVUFBSSxPQUFPO0FBQ1QsY0FBTSxDQUFDLEVBQUUsU0FBUyxJQUFJLElBQUk7QUFDMUIsY0FBTSxXQUFXLGNBQWMsT0FBTztBQUV0QyxZQUFJLFVBQVU7QUFFWixnQkFBTSxXQUFXLEtBQ2QsUUFBUSxTQUFTLE9BQU8sRUFDeEIsUUFBUSxRQUFRLEVBQUU7QUFFckIsaUJBQU8sR0FBRyxFQUFFLFFBQVEsUUFBUSxVQUFVLFFBQVEsSUFBSSxRQUFRLEVBQUU7QUFDNUQsaUJBQU8sR0FBRyxFQUFFLFFBQVEsVUFBVSxRQUFRO0FBQ3RDLGlCQUFPLEdBQUcsRUFBRSxRQUFRLFNBQVMsb0JBQW9CO0FBQUEsUUFDbkQ7QUFBQSxNQUNGO0FBQUEsSUFDRjtBQUVBLFdBQU8sY0FBYyxRQUFRLEtBQUssU0FBUyxLQUFLLElBQUk7QUFBQSxFQUN0RDtBQUNGOzs7QUNyQkEsU0FBUyxpQkFBaUIsU0FBZ0Y7QUFDeEcsUUFBTSxPQUE0RCxDQUFDO0FBQ25FLFFBQU0sUUFBUSxRQUFRLE1BQU0sT0FBTztBQUNuQyxNQUFJLFFBQVE7QUFDWixNQUFJLFlBQVk7QUFDaEIsTUFBSSxpQkFBMkIsQ0FBQztBQUVoQyxRQUFNLFdBQVc7QUFDakIsUUFBTSxTQUFTO0FBRWYsYUFBVyxRQUFRLE9BQU87QUFDeEIsVUFBTSxhQUFhLEtBQUssTUFBTSxRQUFRO0FBQ3RDLFFBQUksWUFBWTtBQUNkLFVBQUksU0FBUyxlQUFlLFNBQVMsR0FBRztBQUN0QyxjQUFNQSxXQUFVLGVBQWUsS0FBSyxJQUFJLEVBQUUsS0FBSztBQUMvQyxhQUFLLEtBQUssRUFBRSxJQUFJLFdBQVcsT0FBTyxXQUFXLFNBQUFBLFNBQVEsQ0FBQztBQUFBLE1BQ3hEO0FBRUEsY0FBUTtBQUNSLGtCQUFZLFdBQVcsQ0FBQyxFQUFFLEtBQUs7QUFDL0IsdUJBQWlCLENBQUM7QUFDbEI7QUFBQSxJQUNGO0FBRUEsUUFBSSxTQUFTLE9BQU8sS0FBSyxJQUFJLEdBQUc7QUFDOUIsWUFBTUEsV0FBVSxlQUFlLEtBQUssSUFBSSxFQUFFLEtBQUs7QUFDL0MsV0FBSyxLQUFLLEVBQUUsSUFBSSxXQUFXLE9BQU8sV0FBVyxTQUFBQSxTQUFRLENBQUM7QUFDdEQsY0FBUTtBQUNSLGtCQUFZO0FBQ1osdUJBQWlCLENBQUM7QUFDbEI7QUFBQSxJQUNGO0FBRUEsUUFBSSxPQUFPO0FBQ1QscUJBQWUsS0FBSyxJQUFJO0FBQUEsSUFDMUI7QUFBQSxFQUNGO0FBRUEsTUFBSSxTQUFTLGVBQWUsU0FBUyxHQUFHO0FBQ3RDLFVBQU1BLFdBQVUsZUFBZSxLQUFLLElBQUksRUFBRSxLQUFLO0FBQy9DLFNBQUssS0FBSyxFQUFFLElBQUksV0FBVyxPQUFPLFdBQVcsU0FBQUEsU0FBUSxDQUFDO0FBQUEsRUFDeEQ7QUFFQSxTQUFPLEVBQUUsS0FBSztBQUNoQjtBQUVBLFNBQVMsZUFBZSxPQUF1QjtBQUM3QyxTQUFPLE1BQ0osS0FBSyxFQUNMLFlBQVksRUFDWixRQUFRLFFBQVEsR0FBRyxFQUNuQixRQUFRLFdBQVcsRUFBRTtBQUMxQjtBQUVPLFNBQVMsa0JBQWtCLElBQWdCO0FBQ2hELFFBQU0saUJBQWlCLENBQUMsT0FLckIsV0FBbUIsWUFBb0I7QUFDeEMsVUFBTSxXQUFXO0FBQ2pCLFVBQU0sWUFBWTtBQUNsQixVQUFNLFVBQVU7QUFFaEIsUUFBSSxjQUFjO0FBQ2xCLFFBQUksT0FBTyxZQUFZO0FBQ3ZCLFFBQUksUUFBUTtBQUNaLFFBQUksUUFBUTtBQUVaLFdBQU8sUUFBUSxTQUFTLFFBQVE7QUFDOUIsWUFBTSxZQUFZLE1BQU0sT0FBTyxJQUFJLElBQUksTUFBTSxPQUFPLElBQUk7QUFDeEQsWUFBTSxVQUFVLE1BQU0sT0FBTyxJQUFJO0FBQ2pDLFlBQU0sY0FBYyxNQUFNLElBQUksTUFBTSxXQUFXLE9BQU87QUFFdEQsVUFBSSxVQUFVLEtBQUssV0FBVyxLQUFLLFNBQVMsV0FBVztBQUNyRCxpQkFBUztBQUNUO0FBQUEsTUFDRjtBQUVBLFVBQUksUUFBUSxLQUFLLFdBQVcsR0FBRztBQUM3QixZQUFJLE9BQU87QUFDVCxrQkFBUTtBQUNSO0FBQUEsUUFDRjtBQUVBLFlBQUksU0FBUyxHQUFHO0FBQ2Qsd0JBQWM7QUFDZDtBQUFBLFFBQ0Y7QUFFQSxpQkFBUztBQUNUO0FBQUEsTUFDRjtBQUVBLFVBQUksU0FBUyxLQUFLLFdBQVcsR0FBRztBQUM5QixnQkFBUTtBQUNSO0FBQUEsTUFDRjtBQUFBLElBQ0Y7QUFFQSxRQUFJLGdCQUFnQixJQUFJO0FBQ3RCLGFBQU8sRUFBRSxTQUFTLElBQUksTUFBTSxDQUFDLEdBQUcsYUFBYSxHQUFHO0FBQUEsSUFDbEQ7QUFFQSxVQUFNLGFBQWEsTUFBTSxJQUFJO0FBQUEsTUFDM0IsTUFBTSxPQUFPLFlBQVksQ0FBQztBQUFBLE1BQzFCLE1BQU0sT0FBTyxXQUFXO0FBQUEsSUFDMUI7QUFDQSxVQUFNLEVBQUUsS0FBSyxJQUFJLGlCQUFpQixVQUFVO0FBRTVDLFdBQU8sRUFBRSxTQUFTLFlBQVksTUFBTSxZQUFZO0FBQUEsRUFDbEQ7QUFHQSxRQUFNLGdCQUEyQixDQUFDLE9BQU8sV0FBVyxTQUFTLFdBQVc7QUFDdEUsVUFBTSxRQUFRLE1BQU0sT0FBTyxTQUFTLElBQUksTUFBTSxPQUFPLFNBQVM7QUFDOUQsVUFBTSxNQUFNLE1BQU0sT0FBTyxTQUFTO0FBQ2xDLFVBQU0sT0FBTyxNQUFNLElBQUksTUFBTSxPQUFPLEdBQUc7QUFHdkMsUUFBSSxDQUFDLEtBQUssTUFBTSxvQkFBb0IsR0FBRztBQUNyQyxhQUFPO0FBQUEsSUFDVDtBQUVBLFFBQUksUUFBUTtBQUNWLGFBQU87QUFBQSxJQUNUO0FBR0EsVUFBTSxTQUFTLGVBQWUsT0FBTyxXQUFXLE9BQU87QUFDdkQsVUFBTSxjQUFjLE9BQU87QUFDM0IsVUFBTSxFQUFFLEtBQUssSUFBSTtBQUVqQixRQUFJLGdCQUFnQixJQUFJO0FBQ3RCLFlBQU1DLGVBQWMsTUFBTSxLQUFLLGVBQWUsSUFBSSxDQUFDO0FBQ25ELE1BQUFBLGFBQVksVUFBVSxLQUFLLFVBQVUsRUFBRSxPQUFPLHFDQUFxQyxNQUFNLENBQUMsRUFBRSxDQUFDO0FBQzdGLE1BQUFBLGFBQVksTUFBTSxDQUFDLFdBQVcsT0FBTztBQUNyQyxZQUFNLE9BQU8sVUFBVTtBQUN2QixhQUFPO0FBQUEsSUFDVDtBQUdBLFFBQUksS0FBSyxXQUFXLEdBQUc7QUFDckIsWUFBTUEsZUFBYyxNQUFNLEtBQUssZUFBZSxJQUFJLENBQUM7QUFDbkQsTUFBQUEsYUFBWSxVQUFVLEtBQUssVUFBVSxFQUFFLE9BQU8sd0NBQXdDLE1BQU0sQ0FBQyxFQUFFLENBQUM7QUFDaEcsTUFBQUEsYUFBWSxNQUFNLENBQUMsV0FBVyxXQUFXO0FBQ3pDLFlBQU0sT0FBTyxjQUFjO0FBQzNCLGFBQU87QUFBQSxJQUNUO0FBR0EsVUFBTSxTQUFTLFFBQVEsS0FBSyxJQUFJLENBQUMsSUFBSSxLQUFLLE9BQU8sRUFBRSxTQUFTLEVBQUUsRUFBRSxNQUFNLEdBQUcsQ0FBQyxDQUFDO0FBTTNFLFVBQU0sY0FBYyxNQUFNLEtBQUssZUFBZSxJQUFJLENBQUM7QUFDbkQsZ0JBQVksVUFBVSxLQUFLLFVBQVUsRUFBRSxNQUFNLE9BQU8sQ0FBQztBQUNyRCxnQkFBWSxNQUFNLENBQUMsV0FBVyxXQUFXO0FBQ3pDLFVBQU0sT0FBTyxjQUFjO0FBRTNCLFdBQU87QUFBQSxFQUNUO0FBR0EsS0FBRyxNQUFNLE1BQU0sTUFBTSxTQUFTLGdCQUFnQixlQUFlO0FBQUEsSUFDM0QsS0FBSyxDQUFDLGFBQWEsYUFBYSxjQUFjLE1BQU07QUFBQSxFQUN0RCxDQUFDO0FBR0QsS0FBRyxTQUFTLE1BQU0sY0FBYyxDQUFDLFFBQVEsS0FBSyxTQUFTLEtBQUssU0FBUztBQUNuRSxVQUFNLFFBQVEsT0FBTyxHQUFHO0FBQ3hCLFFBQUk7QUFDRixZQUFNLE9BQU8sS0FBSyxNQUFNLE1BQU0sT0FBTztBQUNyQyxVQUFJLEtBQUssT0FBTztBQUNkLGVBQU8sbUNBQXFDLEtBQUssS0FBSztBQUFBLE1BQ3hEO0FBQ0EsWUFBTSxPQUFPLEtBQUssS0FBSyxJQUFJLENBQUMsTUFBbUM7QUFDN0QsY0FBTSxLQUFLLGVBQWUsRUFBRSxFQUFFO0FBQzlCLGVBQU87QUFBQSxVQUNMO0FBQUEsVUFDQSxPQUFPLEVBQUUsTUFBTSxPQUFPLENBQUMsRUFBRSxZQUFZLElBQUksRUFBRSxNQUFNLE1BQU0sQ0FBQztBQUFBLFFBQzFEO0FBQUEsTUFDRixDQUFDO0FBR0QsVUFBSSxPQUFPLG1EQUFtRCxLQUFLLE1BQU07QUFDekUsY0FBUTtBQUNSLGNBQVE7QUFFUixXQUFLLFFBQVEsQ0FBQyxLQUFrQ0MsU0FBZ0I7QUFDOUQsY0FBTSxTQUFTQSxTQUFRLElBQUksV0FBVztBQUN0QyxnQkFBUSw2QkFBNkIsTUFBTSxlQUFlLElBQUksRUFBRSxLQUFLLElBQUksS0FBSztBQUFBLE1BQ2hGLENBQUM7QUFFRCxjQUFRO0FBQ1IsY0FBUTtBQUVSLFdBQUssS0FBSyxRQUFRLENBQUMsS0FBbURBLFNBQWdCO0FBQ3BGLGNBQU0sVUFBVUEsU0FBUSxJQUFJLFVBQVU7QUFDdEMsY0FBTSxlQUFlLGVBQWUsSUFBSSxFQUFFO0FBQzFDLGdCQUFRLG1DQUFtQyxZQUFZLHFCQUFxQixPQUFPO0FBQ25GLGdCQUFRLEdBQUcsT0FBTyxJQUFJLE9BQU87QUFDN0IsZ0JBQVE7QUFBQSxNQUNWLENBQUM7QUFFRCxjQUFRO0FBRVIsYUFBTztBQUFBLElBQ1QsU0FBUyxHQUFHO0FBQ1YsYUFBTztBQUFBLElBQ1Q7QUFBQSxFQUNGO0FBQ0Y7OztBQy9NQSxTQUFTLG9CQUNQLElBQ0EsVUFDTTtBQUNOLFFBQU0saUJBQWlCLENBQUMsT0FBWSxXQUFtQixZQUFvQjtBQUN6RSxVQUFNLE1BQU0sTUFBTSxPQUFPLFNBQVMsSUFBSSxNQUFNLE9BQU8sU0FBUztBQUM1RCxVQUFNLFVBQVUsTUFBTSxPQUFPLFNBQVM7QUFHdEMsUUFBSSxNQUFNLElBQUksUUFBUyxRQUFPO0FBQzlCLFFBQUksTUFBTSxJQUFJLE1BQU0sS0FBSyxNQUFNLENBQUMsTUFBTSxNQUFPLFFBQU87QUFFcEQsVUFBTSxjQUFjO0FBQ3BCLFVBQU0sU0FBUyxNQUFNLElBQUksTUFBTSxLQUFLLE1BQU0sV0FBVztBQUNyRCxVQUFNLFNBQVMsTUFBTSxJQUFJLE1BQU0sTUFBTSxhQUFhLE9BQU8sRUFBRSxLQUFLO0FBRWhFLFFBQUksQ0FBQyxPQUFPLFdBQVcsUUFBUSxFQUFHLFFBQU87QUFFekMsVUFBTSxXQUFXLE9BQU8sTUFBTSxDQUFDLEVBQUUsS0FBSztBQUN0QyxRQUFJLENBQUMsU0FBVSxRQUFPO0FBRXRCLFFBQUksV0FBVyxZQUFZO0FBRzNCLFdBQU8sV0FBVyxTQUFTO0FBQ3pCLFVBQ0UsTUFBTSxPQUFPLFFBQVEsSUFBSSxNQUFNLE9BQU8sUUFBUSxJQUFJLEtBQ2xELE1BQU0sT0FBTyxRQUFRLEdBQ3JCO0FBQ0EsY0FBTSxXQUNKLE1BQU0sT0FBTyxRQUFRLElBQUksTUFBTSxPQUFPLFFBQVE7QUFDaEQsWUFDRSxNQUFNLElBQUksTUFBTSxVQUFVLFdBQVcsQ0FBQyxNQUFNLE9BQzVDO0FBQ0E7QUFBQSxRQUNGO0FBQUEsTUFDRjtBQUNBO0FBQUEsSUFDRjtBQUVBLFVBQU0sWUFBWSxNQUFNO0FBQ3hCLFVBQU0sYUFBYTtBQUVuQixVQUFNLFFBQVEsTUFBTSxLQUFLLGVBQWUsT0FBTyxDQUFDO0FBQ2hELFVBQU0sU0FBUztBQUNmLFVBQU0sT0FBTyxFQUFFLEtBQUssU0FBUztBQUM3QixVQUFNLE1BQU0sQ0FBQyxXQUFXLFdBQVcsQ0FBQztBQUVwQyxVQUFNLGFBQWE7QUFDbkIsVUFBTSxPQUFPLFdBQVc7QUFFeEIsV0FBTztBQUFBLEVBQ1Q7QUFFQSxLQUFHLE1BQU0sTUFBTTtBQUFBLElBQ2I7QUFBQSxJQUNBO0FBQUEsSUFDQTtBQUFBLEVBQ0Y7QUFFQSxLQUFHLFNBQVMsTUFBTSxjQUFjLENBQUMsUUFBUSxRQUFRO0FBQy9DLFVBQU0sUUFBUSxPQUFPLEdBQUc7QUFDeEIsVUFBTSxNQUFNLE1BQU0sTUFBTSxPQUFPO0FBRS9CLFdBQU87QUFBQSxpQkFDTSxHQUFHO0FBQUE7QUFBQTtBQUFBO0FBQUEsRUFHbEI7QUFDRjtBQU1BLFNBQVMsc0JBQ1AsSUFDQSxTQUNNO0FBQ04sUUFBTSxvQkFBb0IsR0FBRyxTQUFTLE1BQU07QUFFNUMsS0FBRyxTQUFTLE1BQU0sUUFBUSxDQUFDLFFBQVEsS0FBSyxVQUFVLEtBQUssYUFBYTtBQUNsRSxVQUFNLFFBQVEsT0FBTyxHQUFHO0FBQ3hCLFVBQU0sTUFBTSxNQUFNLFFBQVEsS0FBSyxLQUFLO0FBR3BDLFFBQUksSUFBSSxNQUFNLHdCQUF3QixHQUFHO0FBQ3ZDLFlBQU0sTUFBTSxNQUFNLFdBQVc7QUFDN0IsWUFBTSxRQUFRLFFBQVEsU0FBUztBQUMvQixZQUFNLFdBQVcsUUFBUSxhQUFhLFFBQVEsYUFBYTtBQUMzRCxZQUFNLFdBQVcsUUFBUSxXQUFXLGFBQWE7QUFDakQsWUFBTSxPQUFPLFFBQVEsT0FBTyxTQUFTO0FBQ3JDLFlBQU0sUUFBUSxRQUFRLFFBQVEsVUFBVTtBQUV4QyxZQUFNLE1BQU0sSUFBSSxNQUFNLEdBQUcsRUFBRSxJQUFJLEdBQUcsWUFBWTtBQUM5QyxVQUFJLE9BQU87QUFDWCxVQUFJLFFBQVEsTUFBTyxRQUFPO0FBQUEsZUFDakIsUUFBUSxNQUFPLFFBQU87QUFBQSxlQUN0QixRQUFRLE1BQU8sUUFBTztBQUUvQixhQUFPLGlCQUFpQixLQUFLLEtBQUssUUFBUSxJQUFJLFFBQVEsSUFBSSxJQUFJLElBQUksS0FBSztBQUFBLGlCQUM1RCxHQUFHLFdBQVcsSUFBSTtBQUFBLElBQy9CLEdBQUc7QUFBQTtBQUFBLElBRUg7QUFHQSxXQUFPLG9CQUFvQixRQUFRLEtBQUssVUFBVSxLQUFLLFFBQVEsS0FBSztBQUFBLEVBQ3RFO0FBQ0Y7QUFhTyxTQUFTLGlCQUNkLElBQ0EsVUFBc0MsQ0FBQyxHQUNqQztBQUNOLFFBQU0saUJBQW9DO0FBQUEsSUFDeEMsT0FBTztBQUFBLElBQ1AsUUFBUTtBQUFBLElBQ1IsVUFBVTtBQUFBLElBQ1YsVUFBVTtBQUFBLElBQ1YsTUFBTTtBQUFBLElBQ04sT0FBTztBQUFBLElBQ1AsR0FBRztBQUFBLEVBQ0w7QUFFQSxzQkFBb0IsSUFBSSxjQUFjO0FBQ3RDLHdCQUFzQixJQUFJLGNBQWM7QUFDMUM7OztBQ25LTyxJQUFNLFVBQVU7QUFBQSxFQUNyQixLQUFLO0FBQUEsSUFDSDtBQUFBLE1BQ0UsTUFBTTtBQUFBLE1BQ04sV0FBVztBQUFBLE1BQ1gsT0FBTztBQUFBLFFBQ0wsRUFBRSxNQUFNLFFBQVEsTUFBTSxJQUFJO0FBQUEsUUFDMUIsRUFBRSxNQUFNLGNBQWMsTUFBTSxpQkFBaUI7QUFBQSxNQUMvQztBQUFBLElBQ0Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxNQUFNO0FBQUEsTUFDTixXQUFXO0FBQUEsTUFDWCxPQUFPO0FBQUEsUUFDTCxFQUFFLE1BQU0sc0JBQXNCLE1BQU0sY0FBYztBQUFBLFFBQ2xELEVBQUUsTUFBTSxlQUFlLE1BQU0sK0JBQStCO0FBQUEsUUFDNUQsRUFBRSxNQUFNLGlCQUFpQixNQUFNLGlDQUFpQztBQUFBLE1BQ2xFO0FBQUEsSUFDRjtBQUFBLElBQ0E7QUFBQSxNQUNFLE1BQU07QUFBQSxNQUNOLFdBQVc7QUFBQSxNQUNYLE9BQU87QUFBQSxRQUNMLEVBQUUsTUFBTSxtQkFBbUIsTUFBTSxXQUFXO0FBQUEsUUFDNUMsRUFBRSxNQUFNLGdCQUFnQixNQUFNLDBCQUEwQjtBQUFBLFFBQ3hELEVBQUUsTUFBTSxrQkFBa0IsTUFBTSxrQ0FBa0M7QUFBQSxRQUNsRSxFQUFFLE1BQU0sV0FBVyxNQUFNLHFCQUFxQjtBQUFBLFFBQzlDLEVBQUUsTUFBTSxtQkFBbUIsTUFBTSw2QkFBNkI7QUFBQSxNQUNoRTtBQUFBLElBQ0Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxNQUFNO0FBQUEsTUFDTixXQUFXO0FBQUEsTUFDWCxPQUFPO0FBQUEsUUFDTCxFQUFFLE1BQU0sbUJBQW1CLE1BQU0sY0FBYztBQUFBLFFBQy9DLEVBQUUsTUFBTSxpQkFBaUIsTUFBTSw4QkFBOEI7QUFBQSxRQUM3RCxFQUFFLE1BQU0sV0FBVyxNQUFNLHdCQUF3QjtBQUFBLFFBQ2pELEVBQUUsTUFBTSwwQkFBMEIsTUFBTSx1Q0FBdUM7QUFBQSxRQUMvRSxFQUFFLE1BQU0sb0JBQW9CLE1BQU0saUNBQWlDO0FBQUEsTUFDckU7QUFBQSxJQUNGO0FBQUEsSUFDQTtBQUFBLE1BQ0UsTUFBTTtBQUFBLE1BQ04sV0FBVztBQUFBLE1BQ1gsT0FBTztBQUFBLFFBQ0wsRUFBRSxNQUFNLHdCQUF3QixNQUFNLGdCQUFnQjtBQUFBLFFBQ3RELEVBQUUsTUFBTSxvQkFBb0IsTUFBTSxpREFBaUQ7QUFBQSxRQUNuRixFQUFFLE1BQU0sbUJBQW1CLE1BQU0sd0NBQXdDO0FBQUEsUUFDekUsRUFBRSxNQUFNLG1CQUFtQixNQUFNLHdDQUF3QztBQUFBLE1BQzNFO0FBQUEsSUFDRjtBQUFBLElBQ0E7QUFBQSxNQUNFLE1BQU07QUFBQSxNQUNOLFdBQVc7QUFBQSxNQUNYLE9BQU87QUFBQSxRQUNMLEVBQUUsTUFBTSx1QkFBdUIsTUFBTSxlQUFlO0FBQUEsUUFDcEQsRUFBRSxNQUFNLHdCQUF3QixNQUFNLHNDQUFzQztBQUFBLFFBQzVFLEVBQUUsTUFBTSxZQUFZLE1BQU0sMEJBQTBCO0FBQUEsUUFDcEQsRUFBRSxNQUFNLG1CQUFtQixNQUFNLGlDQUFpQztBQUFBLE1BQ3BFO0FBQUEsSUFDRjtBQUFBLElBQ0E7QUFBQSxNQUNFLE1BQU07QUFBQSxNQUNOLFdBQVc7QUFBQSxNQUNYLE9BQU87QUFBQSxRQUNMLEVBQUUsTUFBTSx1QkFBdUIsTUFBTSxlQUFlO0FBQUEsUUFDcEQsRUFBRSxNQUFNLGVBQWUsTUFBTSx3Q0FBd0M7QUFBQSxRQUNyRSxFQUFFLE1BQU0saUJBQWlCLE1BQU0sMENBQTBDO0FBQUEsUUFDekUsRUFBRSxNQUFNLGVBQWUsTUFBTSxvQ0FBb0M7QUFBQSxRQUNqRSxFQUFFLE1BQU0sZ0JBQWdCLE1BQU0sc0NBQXNDO0FBQUEsTUFDdEU7QUFBQSxJQUNGO0FBQUEsSUFDQTtBQUFBLE1BQ0UsTUFBTTtBQUFBLE1BQ04sV0FBVztBQUFBLE1BQ1gsT0FBTztBQUFBLFFBQ0wsRUFBRSxNQUFNLGdCQUFnQixNQUFNLFdBQVc7QUFBQSxRQUN6QyxFQUFFLE1BQU0sbUJBQW1CLE1BQU0sdUNBQXVDO0FBQUEsUUFDeEUsRUFBRSxNQUFNLG1CQUFtQixNQUFNLDhCQUE4QjtBQUFBLFFBQy9ELEVBQUUsTUFBTSxtQkFBbUIsTUFBTSxtQ0FBbUM7QUFBQSxRQUNwRSxFQUFFLE1BQU0sbUJBQW1CLE1BQU0sNkJBQTZCO0FBQUEsUUFDOUQsRUFBRSxNQUFNLHFCQUFxQixNQUFNLHdDQUF3QztBQUFBLFFBQzNFLEVBQUUsTUFBTSxrQkFBa0IsTUFBTSxxQ0FBcUM7QUFBQSxNQUN2RTtBQUFBLElBQ0Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxNQUFNO0FBQUEsTUFDTixXQUFXO0FBQUEsTUFDWCxPQUFPO0FBQUEsUUFDTCxFQUFFLE1BQU0sZ0JBQWdCLE1BQU0sUUFBUTtBQUFBLFFBQ3RDLEVBQUUsTUFBTSxjQUFjLE1BQU0saUJBQWlCO0FBQUEsTUFDL0M7QUFBQSxJQUNGO0FBQUEsSUFDQTtBQUFBLE1BQ0UsTUFBTTtBQUFBLE1BQ04sV0FBVztBQUFBLE1BQ1gsT0FBTztBQUFBLFFBQ0wsRUFBRSxNQUFNLHVCQUF1QixNQUFNLGdEQUFnRDtBQUFBLFFBQ3JGLEVBQUUsTUFBTSxxQkFBcUIsTUFBTSw4Q0FBOEM7QUFBQSxNQUNuRjtBQUFBLElBQ0Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxNQUFNO0FBQUEsTUFDTixXQUFXO0FBQUEsTUFDWCxPQUFPO0FBQUEsUUFDTCxFQUFFLE1BQU0sc0JBQXNCLE1BQU0sbUNBQW1DO0FBQUEsUUFDdkUsRUFBRSxNQUFNLG1CQUFtQixNQUFNLGdDQUFnQztBQUFBLFFBQ2pFLEVBQUUsTUFBTSw4QkFBOEIsTUFBTSwyQ0FBMkM7QUFBQSxNQUN6RjtBQUFBLElBQ0Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxNQUFNO0FBQUEsTUFDTixXQUFXO0FBQUEsTUFDWCxPQUFPO0FBQUEsUUFDTCxFQUFFLE1BQU0sbUJBQW1CLE1BQU0saUNBQWlDO0FBQUEsUUFDbEUsRUFBRSxNQUFNLHVCQUF1QixNQUFNLDZDQUE2QztBQUFBLFFBQ2xGLEVBQUUsTUFBTSx3QkFBd0IsTUFBTSxzQ0FBc0M7QUFBQSxNQUM5RTtBQUFBLElBQ0Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxNQUFNO0FBQUEsTUFDTixXQUFXO0FBQUEsTUFDWCxPQUFPO0FBQUEsUUFDTCxFQUFFLE1BQU0scUJBQXFCLE1BQU0sc0JBQXNCO0FBQUEsUUFDekQsRUFBRSxNQUFNLG1CQUFtQixNQUFNLHVDQUF1QztBQUFBLFFBQ3hFLEVBQUUsTUFBTSxvQkFBb0IsTUFBTSwrQkFBK0I7QUFBQSxRQUNqRSxFQUFFLE1BQU0sWUFBWSxNQUFNLCtCQUErQjtBQUFBLE1BQzNEO0FBQUEsSUFDRjtBQUFBLEVBQ0Y7QUFDRjs7O0FKM0hBLFNBQVMscUJBQXFCO0FBVmlOLElBQU0sMkNBQTJDO0FBWWhTLElBQU0sVUFBVSxRQUFRLGNBQWMsd0NBQWUsQ0FBQztBQUN0RCxJQUFNLGdCQUFnQixRQUFRLFNBQVMsb0JBQW9CO0FBQzNELElBQU0saUJBQWlCLFFBQVEsZUFBZSwyQkFBMkI7QUFFekUsSUFBTUMsV0FBVSxjQUFjLHdDQUFlO0FBQzdDLElBQU0sa0JBQWtCQSxTQUFRLG1CQUFtQixFQUFFO0FBQ3JELElBQU0sUUFBUUEsU0FBUSxzQkFBc0I7QUFDNUMsSUFBTSxlQUFlLFFBQVEsSUFBSTtBQUNqQyxJQUFNLGdCQUFnQixRQUFRLElBQUk7QUFDbEMsSUFBTSxtQkFBbUIsUUFBUSxJQUFJO0FBQ3JDLElBQU0sYUFBYSxRQUFRLGdCQUFnQixpQkFBaUIsZ0JBQWdCO0FBQzVFLElBQU0sV0FBVyxRQUFRLElBQUksbUJBQW1CLE1BQU0sR0FBRyxFQUFFLENBQUMsS0FBSztBQUNqRSxJQUFNLGVBQWUsUUFBUSxJQUFJLG1CQUFtQixVQUFVLFFBQVEsSUFBSSxpQkFBaUI7QUFDM0YsSUFBTSxtQkFBbUIsUUFBUSxJQUFJO0FBRXJDLElBQU0sV0FBVztBQUNqQixJQUFNLGNBQWMsR0FBRyxRQUFRO0FBRy9CLElBQU0sVUFBVTtBQUFBLEVBQ2QsTUFBTSxFQUFFLE9BQU8sV0FBVyxNQUFNLE1BQU0sT0FBTyxXQUFXLGFBQWEsbUNBQW1DO0FBQUEsRUFDeEcsU0FBUyxFQUFFLE9BQU8sNEJBQVEsTUFBTSxTQUFTLE9BQU8sV0FBVyxhQUFhLDJEQUFtQjtBQUFBLEVBQzNGLFNBQVMsRUFBRSxPQUFPLDRCQUFRLE1BQU0sU0FBUyxPQUFPLFdBQVcsYUFBYSwyREFBbUI7QUFBQSxFQUMzRixJQUFJLEVBQUUsT0FBTyxrQ0FBUyxNQUFNLE1BQU0sT0FBTyxXQUFXLGFBQWEsa0tBQXFDO0FBQUEsRUFDdEcsV0FBVyxFQUFFLE9BQU8sWUFBWSxNQUFNLFdBQVcsT0FBTyxXQUFXLGFBQWEsOEJBQThCO0FBQ2hIO0FBRUEsSUFBTSxTQUFTLGFBQWE7QUFBQSxFQUMxQixPQUFPO0FBQUEsRUFDUCxhQUFhO0FBQUEsRUFDYixNQUFNO0FBQUEsRUFDTjtBQUFBLEVBQ0EsTUFBTTtBQUFBLElBQ0osQ0FBQyxRQUFRLEVBQUUsS0FBSyxRQUFRLE1BQU0sWUFBWSxDQUFDO0FBQUEsRUFDN0M7QUFBQSxFQUNBLFlBQVk7QUFBQSxFQUNaLGFBQWE7QUFBQTtBQUFBO0FBQUE7QUFBQSxFQUtiLFlBQVk7QUFBQTtBQUFBLElBRVY7QUFBQSxJQUNBO0FBQUEsSUFDQTtBQUFBLElBQ0E7QUFBQTtBQUFBLElBRUE7QUFBQSxJQUNBO0FBQUEsSUFDQTtBQUFBLElBQ0E7QUFBQSxJQUNBO0FBQUEsSUFDQTtBQUFBO0FBQUEsSUFFQTtBQUFBLElBQ0E7QUFBQTtBQUFBLElBRUE7QUFBQSxJQUNBO0FBQUEsSUFDQTtBQUFBLElBQ0E7QUFBQTtBQUFBLElBRUE7QUFBQSxJQUNBO0FBQUEsSUFDQTtBQUFBLElBQ0E7QUFBQSxJQUNBO0FBQUEsSUFDQTtBQUFBLElBQ0E7QUFBQSxJQUNBO0FBQUEsSUFDQTtBQUFBLElBQ0E7QUFBQSxJQUNBO0FBQUEsSUFDQTtBQUFBLElBQ0E7QUFBQSxJQUNBO0FBQUE7QUFBQSxJQUVBO0FBQUEsSUFDQTtBQUFBLElBQ0E7QUFBQSxJQUNBO0FBQUEsSUFDQTtBQUFBLElBQ0E7QUFBQSxJQUNBO0FBQUEsSUFDQTtBQUFBLElBQ0E7QUFBQSxJQUNBO0FBQUEsSUFDQTtBQUFBLElBQ0E7QUFBQSxJQUNBO0FBQUEsSUFDQTtBQUFBLElBQ0E7QUFBQSxJQUNBO0FBQUEsSUFDQTtBQUFBLElBQ0E7QUFBQSxJQUNBO0FBQUEsSUFDQTtBQUFBLElBQ0E7QUFBQSxJQUNBO0FBQUEsSUFDQTtBQUFBLElBQ0E7QUFBQSxJQUNBO0FBQUEsSUFDQTtBQUFBLElBQ0E7QUFBQSxJQUNBO0FBQUEsSUFDQTtBQUFBLElBQ0E7QUFBQSxJQUNBO0FBQUEsSUFDQTtBQUFBLElBQ0E7QUFBQSxJQUNBO0FBQUEsSUFDQTtBQUFBLElBQ0E7QUFBQSxFQUNGO0FBQUE7QUFBQSxFQUdBLGlCQUFpQjtBQUFBLEVBRWpCLE1BQU07QUFBQSxJQUNKLFNBQVM7QUFBQSxNQUNQLE9BQU87QUFBQSxRQUNMLG9CQUFvQjtBQUFBLE1BQ3RCO0FBQUEsSUFDRjtBQUFBLElBQ0EsUUFBUTtBQUFBLE1BQ04sSUFBSTtBQUFBLFFBQ0YsT0FBTyxDQUFDLGFBQWE7QUFBQSxNQUN2QjtBQUFBLElBQ0Y7QUFBQSxJQUNBLFNBQVM7QUFBQTtBQUFBLE1BRVAsV0FBVztBQUFBLFFBQ1QsbUJBQW1CLENBQUMsUUFBUTtBQUUxQixjQUFJLElBQUksYUFBYSxJQUFJLFFBQVEsR0FBRztBQUNsQyxtQkFBTyxJQUFJLGdCQUFnQjtBQUFBLGNBQ3pCLFFBQVEsSUFBSSxhQUFhLElBQUksUUFBUSxLQUFLO0FBQUEsY0FDMUMsSUFBSTtBQUFBLFlBQ04sQ0FBQztBQUFBLFVBQ0g7QUFFQSxpQkFBTyxJQUFJLGdCQUFnQjtBQUFBLFlBQ3pCLFFBQVE7QUFBQSxZQUNSLElBQUk7QUFBQSxVQUNOLENBQUM7QUFBQSxRQUNIO0FBQUEsTUFDRixDQUFDO0FBQUEsSUFDSDtBQUFBLElBQ0EsT0FBTztBQUFBLE1BQ0wsV0FBVztBQUFBLE1BQ1gsZUFBZTtBQUFBLFFBQ2IsUUFBUTtBQUFBLFVBQ04sY0FBYyxDQUFDLE9BQU87QUFFcEIsZ0JBQUksR0FBRyxTQUFTLGNBQWMsR0FBRztBQUMvQixxQkFBTztBQUFBLFlBQ1Q7QUFBQSxVQUNGO0FBQUEsUUFDRjtBQUFBLE1BQ0Y7QUFBQSxJQUNGO0FBQUEsRUFDRjtBQUFBLEVBRUEsVUFBVTtBQUFBLElBQ1IsUUFBUSxDQUFDLE9BQU87QUFDZCxTQUFHLElBQUksaUJBQWlCO0FBQ3hCLFNBQUcsSUFBSSxpQkFBaUI7QUFDeEIsU0FBRyxJQUFJLGtCQUFrQjtBQUFBLFFBQ3ZCLFVBQVU7QUFBQSxRQUNWLE9BQU87QUFBQSxNQUNULENBQUM7QUFHRCxTQUFHLElBQUksT0FBTztBQUFBLFFBQ1osY0FBYztBQUFBLFFBQ2QsWUFBWTtBQUFBLE1BQ2QsQ0FBQztBQUdELFNBQUcsSUFBSSxlQUFlO0FBQUEsSUFDeEI7QUFBQTtBQUFBLElBRUEsTUFBTTtBQUFBLElBQ04sYUFBYTtBQUFBO0FBQUEsSUFFYixPQUFPO0FBQUEsTUFDTCxPQUFPO0FBQUEsTUFDUCxNQUFNO0FBQUEsSUFDUjtBQUFBLEVBQ0Y7QUFBQSxFQUVBLGFBQWE7QUFBQSxJQUNYLEtBQUs7QUFBQSxNQUNILEVBQUUsTUFBTSxRQUFRLE1BQU0sSUFBSTtBQUFBLE1BQzFCO0FBQUEsUUFDRSxNQUFNO0FBQUEsUUFDTixNQUFNO0FBQUEsTUFDUjtBQUFBLE1BQ0E7QUFBQSxRQUNFLE1BQU07QUFBQSxRQUNOLE1BQU07QUFBQSxNQUNSO0FBQUEsTUFDQTtBQUFBLFFBQ0UsTUFBTTtBQUFBLFFBQ04sTUFBTTtBQUFBLE1BQ1I7QUFBQSxNQUNBO0FBQUEsUUFDRSxNQUFNO0FBQUEsUUFDTixNQUFNO0FBQUEsUUFDTixhQUFhO0FBQUEsTUFDZjtBQUFBLE1BQ0E7QUFBQSxRQUNFLE1BQU07QUFBQSxRQUNOLE1BQU07QUFBQSxNQUNSO0FBQUEsTUFDQTtBQUFBLFFBQ0UsTUFBTTtBQUFBLFFBQ04sTUFBTTtBQUFBLE1BQ1I7QUFBQSxNQUNBO0FBQUEsUUFDRSxNQUFNO0FBQUEsUUFDTixNQUFNO0FBQUEsTUFDUjtBQUFBLE1BQ0E7QUFBQSxRQUNFLE1BQU07QUFBQSxRQUNOLE9BQU87QUFBQSxVQUNMLEVBQUUsTUFBTSxXQUFXLE1BQU0sSUFBSTtBQUFBLFVBQzdCLEVBQUUsTUFBTSw0QkFBUSxNQUFNLFVBQVU7QUFBQSxVQUNoQyxFQUFFLE1BQU0sNEJBQVEsTUFBTSxVQUFVO0FBQUEsVUFDaEMsRUFBRSxNQUFNLGtDQUFTLE1BQU0sT0FBTztBQUFBLFVBQzlCLEVBQUUsTUFBTSxZQUFZLE1BQU0sWUFBWTtBQUFBLFFBQ3hDO0FBQUEsTUFDRjtBQUFBLElBQ0Y7QUFBQSxJQUVBO0FBQUEsSUFFQSxhQUFhLENBQUM7QUFBQSxJQUNkLFFBQVEsYUFDSjtBQUFBLE1BQ0UsVUFBVTtBQUFBLE1BQ1YsU0FBUztBQUFBLFFBQ1AsT0FBTztBQUFBLFFBQ1AsUUFBUTtBQUFBLFFBQ1IsV0FBVztBQUFBLE1BQ2I7QUFBQSxJQUNGLElBQ0E7QUFBQSxJQUNKLFNBQVM7QUFBQSxJQUVULFVBQVU7QUFBQSxNQUNSLFNBQVM7QUFBQSxNQUNULE1BQU07QUFBQSxJQUNSO0FBQUEsRUFDRjtBQUFBO0FBQUE7QUFBQSxFQUlBLFNBQVM7QUFBQSxJQUNQLE9BQU87QUFBQSxJQUNQLGdCQUFnQjtBQUFBLE1BQ2QsY0FBYztBQUFBLE1BQ2QsWUFBWTtBQUFBLE1BQ1osa0JBQWtCO0FBQUEsTUFDbEIsb0JBQW9CO0FBQUEsTUFDcEIsV0FBVztBQUFBLE1BQ1gsZ0JBQWdCO0FBQUEsTUFDaEIsZUFBZTtBQUFBLElBQ2pCO0FBQUEsSUFDQSxXQUFXO0FBQUEsTUFDVCxhQUFhO0FBQUEsTUFDYixZQUFZO0FBQUEsSUFDZDtBQUFBLElBQ0EsVUFBVTtBQUFBLE1BQ1IsYUFBYTtBQUFBLElBQ2Y7QUFBQSxJQUNBLE9BQU87QUFBQSxNQUNMLGFBQWE7QUFBQSxJQUNmO0FBQUEsRUFDRjtBQUVGLENBQUM7QUFFRCxJQUFPLGlCQUFRLFlBQVksTUFBTTsiLAogICJuYW1lcyI6IFsiY29udGVudCIsICJtYXJrZXJUb2tlbiIsICJpZHgiLCAicmVxdWlyZSJdCn0K
