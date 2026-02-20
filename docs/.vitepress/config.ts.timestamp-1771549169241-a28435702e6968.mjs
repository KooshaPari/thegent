// docs/.vitepress/config.ts
import { defineConfig } from "file:///Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/node_modules/.pnpm/vitepress@1.6.4_@algolia+client-search@5.48.1_@types+node@25.2.3_postcss@8.5.6_search-insights@2.17.3/node_modules/vitepress/dist/node/index.js";
import { withMermaid } from "file:///Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/node_modules/vitepress-plugin-mermaid/dist/vitepress-plugin-mermaid.es.mjs";
import { OramaPlugin } from "file:///Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/node_modules/@orama/plugin-vitepress/dist/index.js";
import { imagetools } from "file:///Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/node_modules/vite-imagetools/dist/index.js";

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

// docs/.vitepress/sidebar.ts
var sidebar = {
  "/": [
    {
      "text": "Architecture",
      "collapsed": false,
      "items": [
        {
          "text": "Agent Sandboxing Architecture: WASM/Containers/VMs (No Docker)",
          "link": "/architecture/AGENT_SANDBOXING_ARCHITECTURE.md"
        },
        {
          "text": "Python Frontmatter + Native Backmatter Architecture",
          "link": "/architecture/FRONTMATTER_BACKMATTER_ARCHITECTURE.md"
        },
        {
          "text": "Hybrid Mac/Windows Development Environment Architecture",
          "link": "/architecture/HYBRID_MAC_WIN_DEV_ENVIRONMENT.md"
        }
      ]
    },
    {
      "text": "Changes",
      "collapsed": false,
      "items": [
        {
          "text": "Hexagonal Migration",
          "collapsed": false,
          "items": [
            {
              "text": "Hexagonal Architecture Migration -- thegent",
              "link": "/hexagonal-migration/proposal.md"
            }
          ]
        }
      ]
    },
    {
      "text": "Checklists",
      "collapsed": false,
      "items": [
        {
          "text": "Hybrid Mac/Windows Environment Setup Checklist",
          "link": "/checklists/HYBRID_ENV_SETUP_CHECKLIST.md"
        }
      ]
    },
    {
      "text": "Closure",
      "collapsed": false,
      "items": [
        {
          "text": "DR Rehearsal Report",
          "link": "/closure/DR_REHEARSAL_REPORT.md"
        },
        {
          "text": "Governance & Compliance Bundle",
          "link": "/closure/GOVERNANCE_COMPLIANCE_BUNDLE.md"
        },
        {
          "text": "Phase 6 Readiness Report",
          "link": "/closure/PHASE6_READINESS_REPORT.md"
        },
        {
          "text": "Post-Launch 28-Day Observation Plan",
          "link": "/closure/POST_LAUNCH_28DAY_OBSERVATION.md"
        },
        {
          "text": "Rollback Reserve Plan",
          "link": "/closure/ROLLBACK_RESERVE_PLAN.md"
        },
        {
          "text": "SLO Certification Matrix",
          "link": "/closure/SLO_CERTIFICATION_MATRIX.md"
        }
      ]
    },
    {
      "text": "Contracts",
      "collapsed": false,
      "items": [
        {
          "text": "Contract Authority",
          "link": "/contracts/CONTRACT_AUTHORITY.md"
        },
        {
          "text": "Fallback Control Plane",
          "link": "/contracts/FALLBACK_POLICY.md"
        },
        {
          "text": "Provider Adapter Contracts (G-RV-05)",
          "link": "/contracts/PROVIDER_ADAPTER_CONTRACTS.md"
        },
        {
          "text": "Contract Upgrade Playbook",
          "link": "/contracts/UPGRADE_PLAYBOOK.md"
        }
      ]
    },
    {
      "text": "Demos",
      "collapsed": false,
      "items": [
        {
          "text": "Demo Scripts for VitePress Documentation",
          "link": "/demos/README.md"
        }
      ]
    },
    {
      "text": "Docset",
      "collapsed": false,
      "items": [
        {
          "text": "DAG Node-to-Service Contract Checklist",
          "link": "/docset/DAG_NODE_SERVICE_CONTRACT_CHECKLIST.md"
        },
        {
          "text": "DAG Node-to-Service Contract Checklist",
          "link": "/docset/DAG_NODE_TO_SERVICE_CONTRACT_CHECKLIST.md"
        },
        {
          "text": "E2E Next Chunk Plan \u2014 Full-Phase Mega Chunk",
          "link": "/docset/E2E_NEXT_CHUNK_PLAN.md"
        },
        {
          "text": "E2E Remaining Full-Depth Plan",
          "link": "/docset/E2E_REMAINING_FULL_DEPTH_PLAN.md"
        },
        {
          "text": "FastMCP 3.0 Integration Reference for Thegent",
          "link": "/docset/FASTMCP_INTEGRATION.md"
        },
        {
          "text": "Thegent Implementation Status Tracker",
          "link": "/docset/IMPLEMENTATION_STATUS.md"
        },
        {
          "text": "Thegent Optimization, Polish, and Robustness Addendum",
          "link": "/docset/OPTIMIZATION_POLISH_ADDENDUM.md"
        },
        {
          "text": "Thegent Pattern Catalog",
          "link": "/docset/PATTERNS.md"
        },
        {
          "text": "Comprehensive Test Plan Matrix",
          "link": "/docset/PRD_TEST_PLAN_MATRIX.md"
        },
        {
          "text": "Remaining Gaps \u2014 Full Depth Analysis",
          "link": "/docset/REMAINING_GAPS_DEEP_DIVE.md"
        },
        {
          "text": "Remaining Gaps \u2014 Full Depth Analysis",
          "link": "/docset/REMAINING_GAPS_FULL_DEPTH.md"
        },
        {
          "text": "Thegent Risks and Anti-Patterns Catalog",
          "link": "/docset/RISKS_AND_ANTIPATTERNS.md"
        },
        {
          "text": "WBS-to-Issue Import Matrix",
          "link": "/docset/WBS_TO_ISSUE_IMPORT_MATRIX.md"
        },
        {
          "text": "Thegent CLI Single Source of Truth Audit",
          "link": "/docset/thegent-cli-single-source-of-truth-audit-2026-02-14.md"
        },
        {
          "text": "Thegent Cross-Analysis Matrix (Deep)",
          "link": "/docset/thegent-cross-analysis-matrix-2026-02-14.md"
        },
        {
          "text": "Thegent Final DAG Specification",
          "link": "/docset/thegent-dag-final.md"
        },
        {
          "text": "Thegent DAG Extension \u2014 Phases 10 to 12",
          "link": "/docset/thegent-dag-phase10-12-extension.md"
        },
        {
          "text": "thegent DAG Extension \u2014 Phases 7, 8, 9",
          "link": "/docset/thegent-dag-phase7-9-extension.md"
        },
        {
          "text": "Thegent Gaps and Discovery Report",
          "link": "/docset/thegent-gaps-and-discovery-2026-02-14.md"
        },
        {
          "text": "Thegent Implementation Log",
          "link": "/docset/thegent-implementation-log-2026-02-14.md"
        },
        {
          "text": "Thegent Kush Docs Deep Dive (Zen + Adjacent Projects)",
          "link": "/docset/thegent-kush-docs-deep-dive-2026-02-14.md"
        },
        {
          "text": "Thegent Mega Research Synthesis",
          "link": "/docset/thegent-mega-research-synthesis-2026-02-14.md"
        },
        {
          "text": "Thegent Orchestration Optimization & Expansion PRD (Living Document)",
          "link": "/docset/thegent-orchestration-optimization-prd.md"
        },
        {
          "text": "Thegent Pattern Enhancement Synthesis",
          "link": "/docset/thegent-patterns-enhancement-synthesis.md"
        },
        {
          "text": "Thegent Phase 10\u201312 Bundle B Sprint Playbook",
          "link": "/docset/thegent-phase10-12-bundle-b-sprint-playbook.md"
        },
        {
          "text": "Thegent Phase 10\u201312 Bundle Signoff and Handoff Packages",
          "link": "/docset/thegent-phase10-12-bundle-signoff-and-handoff-packages.md"
        },
        {
          "text": "Thegent Phase 10\u201312 Closure Readiness Pack Template",
          "link": "/docset/thegent-phase10-12-closure-readiness-pack-template.md"
        },
        {
          "text": "Thegent Phase 10\u201312 Compact Execution Dashboard",
          "link": "/docset/thegent-phase10-12-compact-execution-dashboard.md"
        },
        {
          "text": "Thegent Phase 10\u201312 Drift Reconciliation Playbook",
          "link": "/docset/thegent-phase10-12-drift-reconciliation-playbook.md"
        },
        {
          "text": "Thegent Phase 10\u201312 Execution Bundles Playbook",
          "link": "/docset/thegent-phase10-12-execution-bundles-playbook.md"
        },
        {
          "text": "Thegent Phase 10\u201312 Execution Synthesis Playbook",
          "link": "/docset/thegent-phase10-12-execution-synthesis-playbook.md"
        },
        {
          "text": "Thegent Phase 10\u201312 Execution Workboard (Chunk 4)",
          "link": "/docset/thegent-phase10-12-execution-workboard.md"
        },
        {
          "text": "Thegent Phase 10\u201312 Hard-Stop, Rollback, and Stability Matrix",
          "link": "/docset/thegent-phase10-12-hard-stop-and-rollback-matrix.md"
        },
        {
          "text": "Thegent Phase 10\u201312 Implementation Chunk Plan",
          "link": "/docset/thegent-phase10-12-implementation-chunk-plan.md"
        },
        {
          "text": "Thegent Phase 10\u201312 Implementation Issue Queue",
          "link": "/docset/thegent-phase10-12-implementation-issue-queue.md"
        },
        {
          "text": "Thegent Phase 10\u201312 Implementation Ticket Templates (Chunk 3)",
          "link": "/docset/thegent-phase10-12-implementation-ticket-templates.md"
        },
        {
          "text": "Thegent Phase 10\u201312 Issue Board Automation Playbook",
          "link": "/docset/thegent-phase10-12-issue-board-automation.md"
        },
        {
          "text": "Thegent Phase 10\u201312 Issue Board Import Notes",
          "link": "/docset/thegent-phase10-12-issue-board-import-notes.md"
        },
        {
          "text": "Thegent Phase 10\u201312 Launch Schedule (Day-by-Day Execution Plan)",
          "link": "/docset/thegent-phase10-12-launch-schedule.md"
        },
        {
          "text": "Thegent Phase 10\u201312 Master Traceability Ledger",
          "link": "/docset/thegent-phase10-12-master-traceability-ledger.md"
        },
        {
          "text": "Thegent \u2014 Phase 10\u201312 PRD (Optimization-Depth and Productization Wave)",
          "link": "/docset/thegent-phase10-12-optimal-design-prd.md"
        },
        {
          "text": "Thegent Phase 10\u201312 Orchestrator Tooling Stack",
          "link": "/docset/thegent-phase10-12-orchestrator-tooling-stack.md"
        },
        {
          "text": "Thegent Phase 10\u201312 Policy-as-Code and Automation Contract",
          "link": "/docset/thegent-phase10-12-policy-as-code-and-automation-contract.md"
        },
        {
          "text": "Thegent Phase 10\u201312 PRD\u2194WBS Finalization Cross-Map",
          "link": "/docset/thegent-phase10-12-prd-wbs-crossmap-finalization.md"
        },
        {
          "text": "Thegent Phase 10\u201312 PRD-WBS-DAG-Ticket Validation Framework",
          "link": "/docset/thegent-phase10-12-prd-wbs-dag-ticket-validation.md"
        },
        {
          "text": "Thegent Phase 10\u201312 Release Readiness and Delta Pack",
          "link": "/docset/thegent-phase10-12-release-readiness-and-delta-pack.md"
        },
        {
          "text": "Thegent Phase 10\u201312 Test and Readiness Pack",
          "link": "/docset/thegent-phase10-12-test-readiness-pack.md"
        },
        {
          "text": "Thegent Phase 11 Sprint Playbook (Bundles C and D)",
          "link": "/docset/thegent-phase11-control-and-adaptation-sprint-playbook.md"
        },
        {
          "text": "Thegent Phase 12 Sprint Playbook (Bundles E and F)",
          "link": "/docset/thegent-phase12-explainability-and-closure-sprint-playbook.md"
        },
        {
          "text": "Thegent Phase 13+ Extension Boundary Proposal",
          "link": "/docset/thegent-phase13-plus-extension-proposal.md"
        },
        {
          "text": "Thegent Phase 3\u20136 Closure Acceptance Contract Schema",
          "link": "/docset/thegent-phase3-6-closure-acceptance-contract-schema.md"
        },
        {
          "text": "Thegent Phase 3\u20136 Closure Acceptance Pack Template",
          "link": "/docset/thegent-phase3-6-closure-acceptance-pack-template.md"
        },
        {
          "text": "Thegent Phase 3\u20136 Closure Validator Automation Package",
          "link": "/docset/thegent-phase3-6-closure-validator-automation-package.md"
        },
        {
          "text": "Thegent Phase 3\u20136 Closure Validation Event and Waiver Contract v1",
          "link": "/docset/thegent-phase3-6-closure-validator-event-and-waiver-contract-v1.md"
        },
        {
          "text": "Thegent Phase 3\u20136 Closure Validator Fault Injection and Chaos Tests",
          "link": "/docset/thegent-phase3-6-closure-validator-fault-injection-and-chaos-tests.md"
        },
        {
          "text": "Thegent Phase 3\u20136 Closure Validator Implementation Blueprint",
          "link": "/docset/thegent-phase3-6-closure-validator-implementation-blueprint.md"
        },
        {
          "text": "Thegent Phase 3\u20136 Closure Validator Python Implementation Blueprint",
          "link": "/docset/thegent-phase3-6-closure-validator-python-implementation-blueprint.md"
        },
        {
          "text": "Thegent Phase 3-6 Closure Validator Runtime CLI and Adapter Playbook",
          "link": "/docset/thegent-phase3-6-closure-validator-runtime-cli-and-adapter-playbook.md"
        },
        {
          "text": "Thegent Phase 3\u20136 Cross-Wave Bridge and Continuity Plan",
          "link": "/docset/thegent-phase3-6-crosswave-bridge-and-continuity-plan.md"
        },
        {
          "text": "Thegent \u2014 Phase 3\u20136 Full-Depth Execution Chunk",
          "link": "/docset/thegent-phase3-6-full-depth-execution-prd.md"
        },
        {
          "text": "Thegent Phase 7\u20139 Next-Wave PRD (Post-Closure Optimization)",
          "link": "/docset/thegent-phase7-9-next-wave-prd.md"
        },
        {
          "text": "Thegent Phase 7\u20139 Test and Readiness Pack",
          "link": "/docset/thegent-phase7-9-test-readiness-pack.md"
        },
        {
          "text": "Thegent Orchestration Final Plan Index",
          "link": "/docset/thegent-plan-final-index.md"
        },
        {
          "text": "Thegent Production Orchestration PRD (Final)",
          "link": "/docset/thegent-prd-final.md"
        },
        {
          "text": "Thegent Research Validation Addendum (Zen + Task Tools)",
          "link": "/docset/thegent-research-validation-2026-02-14.md"
        },
        {
          "text": "thegent Third-Party Bundle Manifest",
          "link": "/docset/thegent-third-party-bundle-manifest.md"
        },
        {
          "text": "Thegent Final WBS (Comprehensive)",
          "link": "/docset/thegent-wbs-final.md"
        },
        {
          "text": "Thegent WBS \u2014 Phase 10 to Phase 12 (Optimization-Depth and Productization)",
          "link": "/docset/thegent-wbs-phase10-12.md"
        },
        {
          "text": "Thegent WBS \u2014 Phase 7 to Phase 9 (Next-Wave Execution)",
          "link": "/docset/thegent-wbs-phase7-9.md"
        }
      ]
    },
    {
      "text": "Enterprise",
      "collapsed": false,
      "items": [
        {
          "text": "Decommissioning and Sunset Plan",
          "link": "/enterprise/DECOMMISSIONING_PLAN.md"
        },
        {
          "text": "Program Operating Model and Ownership Map",
          "link": "/enterprise/OPERATING_MODEL.md"
        },
        {
          "text": "Security and Compliance Signoff Package",
          "link": "/enterprise/SECURITY_COMPLIANCE_SIGNOFF.md"
        }
      ]
    },
    {
      "text": "Governance",
      "collapsed": false,
      "items": [
        {
          "text": "Cost Governance Design (G-GP-06)",
          "link": "/governance/COST_GOVERNANCE_DESIGN.md"
        },
        {
          "text": "HITL (Human-in-the-Loop) Design (G-GP-05)",
          "link": "/governance/HITL_DESIGN.md"
        },
        {
          "text": "NeMo Guardrails Design (G-GP-02)",
          "link": "/governance/NEMO_GUARDRAILS_DESIGN.md"
        },
        {
          "text": "OPA Integration Design (G-GP-01)",
          "link": "/governance/OPA_INTEGRATION_DESIGN.md"
        },
        {
          "text": "Retention Policy Design (G-GP-07)",
          "link": "/governance/RETENTION_POLICY_DESIGN.md"
        },
        {
          "text": "Sandboxing Design (G-GP-08)",
          "link": "/governance/SANDBOXING_DESIGN.md"
        }
      ]
    },
    {
      "text": "Guides",
      "collapsed": false,
      "items": [
        {
          "text": "Agent Debugging and Remediation Guide",
          "link": "/guides/AGENT_DEBUGGING_AND_REMEDIATION_GUIDE.md"
        },
        {
          "text": "Agent Instructions: thegent Deep-Dive",
          "link": "/guides/AGENT_INSTRUCTIONS_THEGENT.md"
        },
        {
          "text": "Automated Documentation Demos",
          "link": "/guides/AUTOMATED_DEMOS.md"
        },
        {
          "text": "BKM Implementation Guides",
          "link": "/guides/BKM_IMPLEMENTATION_GUIDES.md"
        },
        {
          "text": "Cross-Platform Desktop Automation \u2014 Complete Guide",
          "link": "/guides/CROSS_PLATFORM_COMPLETE.md"
        },
        {
          "text": "Cross-Platform Desktop Automation: Developer Cookbook",
          "link": "/guides/CROSS_PLATFORM_DEVELOPER_COOKBOOK.md"
        },
        {
          "text": "Cross-Platform Desktop Automation: Implementation Templates",
          "link": "/guides/CROSS_PLATFORM_IMPLEMENTATION_TEMPLATES.md"
        },
        {
          "text": "Cross-Platform Desktop Automation: Migration Guide",
          "link": "/guides/CROSS_PLATFORM_MIGRATION_GUIDE.md"
        },
        {
          "text": "Cross-Platform Desktop Automation: Quick Start Guide",
          "link": "/guides/CROSS_PLATFORM_QUICK_START.md"
        },
        {
          "text": "Cross-Platform Desktop Automation: Implementation Roadmap",
          "link": "/guides/CROSS_PLATFORM_ROADMAP.md"
        },
        {
          "text": "Doctor Command Fixes",
          "link": "/guides/DOCTOR_FIXES.md"
        },
        {
          "text": "Fix Shell Corruption Issue",
          "link": "/guides/FIX_SHELL_CORRUPTION.md"
        },
        {
          "text": "Fix Shell Fork Errors: Quick Guide",
          "link": "/guides/FIX_SHELL_FORK_ERRORS.md"
        },
        {
          "text": "Guides Index",
          "link": "/guides/GUIDES_INDEX.md"
        },
        {
          "text": "Hybrid Mac/Windows Environment Quick Start Guide",
          "link": "/guides/HYBRID_ENV_QUICK_START.md"
        },
        {
          "text": "Implementation Patterns Guide",
          "link": "/guides/IMPLEMENTATION_PATTERNS.md"
        },
        {
          "text": "Job Pool System - Usage Guide",
          "link": "/guides/JOB_POOL_USAGE.md"
        },
        {
          "text": "OAuth-Only Authentication Policy",
          "link": "/guides/OAUTH_ONLY_AUTHENTICATION.md"
        },
        {
          "text": "Operational Learning Assets (WP-12008)",
          "link": "/guides/OPERATIONAL_LEARNING.md"
        },
        {
          "text": "oxlint Integration Guide (Phase 4)",
          "link": "/guides/OXLINT_INTEGRATION_GUIDE.md"
        },
        {
          "text": "Thegent Phase 10 Summary and Migration Guide (WP-10010)",
          "link": "/guides/PHASE_10_GUIDE.md"
        },
        {
          "text": "Thegent Phase 11 Summary and Evidence Pack (WP-11010)",
          "link": "/guides/PHASE_11_GUIDE.md"
        },
        {
          "text": "Phase 4 Quick Start: ESLint \u2192 oxlint Migration",
          "link": "/guides/PHASE_4_QUICK_START.md"
        },
        {
          "text": "Thegent Phase 7-9 Summary and Training Guide (WP-9010)",
          "link": "/guides/PHASE_7_9_GUIDE.md"
        },
        {
          "text": "Prompts Tooling \u2014 Cursor / Codex / Claude Aggregate",
          "link": "/guides/PROMPTS_TOOLING.md"
        },
        {
          "text": "Provider Setup Guide",
          "link": "/guides/PROVIDER_SETUP_GUIDE.md"
        },
        {
          "text": "Quality Assurance Guide",
          "link": "/guides/QUALITY_ASSURANCE.md"
        },
        {
          "text": "Quick Fix: Shell Setup Issues",
          "link": "/guides/QUICK_FIX_SHELL_SETUP.md"
        },
        {
          "text": "Runtime Optimization Guide",
          "link": "/guides/RUNTIME_OPTIMIZATION.md"
        },
        {
          "text": "Shell Advanced Features Guide",
          "link": "/guides/SHELL_ADVANCED_FEATURES.md"
        },
        {
          "text": "Shell Corruption Fix - Complete Solution",
          "link": "/guides/SHELL_CORRUPTION_FIX_COMPLETE.md"
        },
        {
          "text": "Complete Shell Environment System",
          "link": "/guides/SHELL_ENVIRONMENT_COMPLETE.md"
        },
        {
          "text": "Shell Environment Management",
          "link": "/guides/SHELL_ENVIRONMENT_MANAGEMENT.md"
        },
        {
          "text": "Shell Optimization Guide",
          "link": "/guides/SHELL_OPTIMIZATION_GUIDE.md"
        },
        {
          "text": "Shell & Zsh Plugin Setup \u2014 Long-Term Fix",
          "link": "/guides/SHELL_ZSH_PLUGIN_SETUP.md"
        },
        {
          "text": "Sitback Plugin API",
          "link": "/guides/SITBACK_PLUGINS.md"
        },
        {
          "text": "Starship + direnv Setup Complete",
          "link": "/guides/STARSHIP_DIRENV_SETUP.md"
        },
        {
          "text": "\u{1F680} Hooks Optimization Initiative - START HERE",
          "link": "/guides/START_HERE.md"
        },
        {
          "text": "Task Routing Quick Reference Guide",
          "link": "/guides/TASK_ROUTING_QUICK_REF.md"
        },
        {
          "text": "thegent Testing Guide",
          "link": "/guides/TESTING.md"
        },
        {
          "text": "Troubleshooting Guide",
          "link": "/guides/TROUBLESHOOTING.md"
        },
        {
          "text": "VitePress Docsite Setup",
          "link": "/guides/VITEPPRESS_SETUP.md"
        },
        {
          "text": "Anti-Pattern Detection Guide",
          "link": "/guides/anti-patterns.md"
        },
        {
          "text": "Architecture Enforcement Guide",
          "link": "/guides/architecture-enforcement.md"
        },
        {
          "text": "Guides",
          "link": "/guides/index.md"
        }
      ]
    },
    {
      "text": "Migration",
      "collapsed": false,
      "items": [
        {
          "text": "Advanced Performance Patterns & Best Practices",
          "link": "/migration/ADVANCED_PATTERNS.md"
        },
        {
          "text": "Complete Solution: Polished, Optimized, Production-Ready",
          "link": "/migration/COMPLETE_SOLUTION.md"
        },
        {
          "text": "Comprehensive Benchmarking Strategy",
          "link": "/migration/COMPREHENSIVE_BENCHMARKING.md"
        },
        {
          "text": "Comprehensive Performance Analysis & Migration Strategy",
          "link": "/migration/COMPREHENSIVE_PERFORMANCE_ANALYSIS.md"
        },
        {
          "text": "Design Principles",
          "link": "/migration/DESIGN_PRINCIPLES.md"
        },
        {
          "text": "Usage Examples",
          "link": "/migration/EXAMPLES.md"
        },
        {
          "text": "Fork Failure (EAGAIN) Analysis & Solutions",
          "link": "/migration/FORK_FAILURE_ANALYSIS.md"
        },
        {
          "text": "Comprehensive Implementation Roadmap",
          "link": "/migration/IMPLEMENTATION_ROADMAP.md"
        },
        {
          "text": "Production Readiness Checklist",
          "link": "/migration/PRODUCTION_READINESS.md"
        },
        {
          "text": "Quick Start Guide",
          "link": "/migration/QUICK_START.md"
        },
        {
          "text": "Shell to Rust/Go Migration Plan",
          "link": "/migration/RUST_GO_MIGRATION_PLAN.md"
        },
        {
          "text": "Performance Optimization Summary",
          "link": "/migration/SUMMARY.md"
        },
        {
          "text": "The Ultimate Guide: Comprehensive Performance Optimization & Migration",
          "link": "/migration/ULTIMATE_GUIDE.md"
        },
        {
          "text": "User Guide: thegent Performance Optimizations",
          "link": "/migration/USER_GUIDE.md"
        }
      ]
    },
    {
      "text": "Plans",
      "collapsed": false,
      "items": [
        {
          "text": "Thegent Unified Plan \u2014 Master Index",
          "link": "/plans/00-MASTER-INDEX.md"
        },
        {
          "text": "01 \u2014 Project State",
          "link": "/plans/01-PROJECT-STATE.md"
        },
        {
          "text": "02 \u2014 Unified Work Breakdown Structure",
          "link": "/plans/02-UNIFIED-WBS.md"
        },
        {
          "text": "03 \u2014 Unified DAG Specifications",
          "link": "/plans/03-UNIFIED-DAG.md"
        },
        {
          "text": "04 \u2014 Unified Requirements",
          "link": "/plans/04-REQUIREMENTS.md"
        },
        {
          "text": "05 \u2014 Architecture & Patterns",
          "link": "/plans/05-ARCHITECTURE.md"
        },
        {
          "text": "06 \u2014 Implementation Guide",
          "link": "/plans/06-IMPLEMENTATION-GUIDE.md"
        },
        {
          "text": "07 \u2014 Test Strategy",
          "link": "/plans/07-TEST-STRATEGY.md"
        },
        {
          "text": "08 \u2014 Optimization, Polish, Enhancement & Robustness Catalog",
          "link": "/plans/08-OPTIMIZATION-CATALOG.md"
        },
        {
          "text": "09 \u2014 Risk Registry & Anti-Patterns",
          "link": "/plans/09-RISK-REGISTRY.md"
        },
        {
          "text": "10 \u2014 Subagent Dispatch Plan",
          "link": "/plans/10-SUBAGENT-DISPATCH.md"
        },
        {
          "text": "12 \u2014 Cycleloop Loops & Checker Agent Design",
          "link": "/plans/12-LIFECYCLE-LOOP-DESIGN.md"
        },
        {
          "text": "Design: thegent install CLI Command",
          "link": "/plans/2026-02-14-thegent-install-design.md"
        },
        {
          "text": "thegent install Implementation Plan",
          "link": "/plans/2026-02-14-thegent-install-implementation-plan.md"
        },
        {
          "text": "Research and Elicitation Plan \u2014 2026-02-15",
          "link": "/plans/2026-02-15-RESEARCH-AND-ELICITATION-PLAN.md"
        },
        {
          "text": "thegent sitback \u2014 Design & Implementation Plan",
          "link": "/plans/2026-02-15-thegent-sitback-design.md"
        },
        {
          "text": "Tray Application Design - Plugin-Based Architecture",
          "link": "/plans/2026-02-15-tray-application-design.md"
        },
        {
          "text": "AgentDeployer + LifecycleController Integration Review",
          "link": "/plans/2026-02-16-AGENT_DEPLOYER_REVIEW.md"
        },
        {
          "text": "Cycleloop + AgilePlus Integration Plan",
          "link": "/plans/2026-02-16-CYCLELOOP_AGILEPLUS_INTEGRATION.md"
        },
        {
          "text": "Full LiteLLM Feature Integration Plan",
          "link": "/plans/2026-02-16-litellm-full-features-plan.md"
        },
        {
          "text": "LiteLLM Integration Design",
          "link": "/plans/2026-02-16-litellm-integration-design.md"
        },
        {
          "text": "LiteLLM Router Integration Implementation Plan",
          "link": "/plans/2026-02-16-litellm-integration-plan.md"
        },
        {
          "text": "Supermemory.ai Integration Plan (WP-5001-SM)",
          "link": "/plans/2026-02-16-supermemory-integration-plan.md"
        },
        {
          "text": "Agent Sandboxing Implementation Plan",
          "link": "/plans/AGENT_SANDBOXING_IMPLEMENTATION_PLAN.md"
        },
        {
          "text": "Catalog \u2194 CLIProxyAPIPlus Fork Alignment",
          "link": "/plans/CATALOG_CLIPROXY_FORK_ALIGNMENT.md"
        },
        {
          "text": "CLIProxyAPI & Thegent Work Plan \u2013 Unified Phased WBS",
          "link": "/plans/CLIPROXY_API_AND_THGENT_UNIFIED_PLAN.md"
        },
        {
          "text": "Agent Orchestration Harness: Multi-Platform (Extreme-Depth Plan)",
          "link": "/plans/CODEX_DONUT_HARNESS_PLAN.md"
        },
        {
          "text": "Cross-Platform Multi-Tenant Desktop Automation Complete Plan",
          "link": "/plans/CROSS_PLATFORM_COMPLETE_PLAN.md"
        },
        {
          "text": "Cross-Platform Multi-Tenant Desktop Automation Implementation Plan",
          "link": "/plans/CROSS_PLATFORM_MULTI_TENANT_IMPLEMENTATION_PLAN.md"
        },
        {
          "text": "Cursor API Integration Research & Plan",
          "link": "/plans/CURSOR_API_INTEGRATION_RESEARCH.md"
        },
        {
          "text": "Debug Tags and Metrics (Transient Response Tags)",
          "link": "/plans/DEBUG_TAGS_AND_METRICS.md"
        },
        {
          "text": "Distributed Model Routing Plan",
          "link": "/plans/DISTRIBUTED_MODEL_ROUTING_PLAN.md"
        },
        {
          "text": "Documentation Expansion Process",
          "link": "/plans/DOCUMENTATION_EXPANSION_PROCESS.md"
        },
        {
          "text": "Documentation Expansion TODO",
          "link": "/plans/DOCUMENTATION_EXPANSION_TODO.md"
        },
        {
          "text": "Documentation Consolidation & Implementation WBS",
          "link": "/plans/DOC_CONSOLIDATION_AND_IMPLEMENTATION_WBS.md"
        },
        {
          "text": "Factory Droid Harness Integration Plan",
          "link": "/plans/FACTORY_DROID_HARNESS_INTEGRATION_PLAN.md"
        },
        {
          "text": "Full Shell \u2192 Rust Where Beneficial",
          "link": "/plans/FULL_SHELL_TO_RUST_WHERE_BENEFICIAL.md"
        },
        {
          "text": "Holistic + Harmonious Design & Full Integration Plan",
          "link": "/plans/HOLISTIC_HARMONIOUS_DESIGN_AND_INTEGRATION_PLAN.md"
        },
        {
          "text": "Hook Runtime Rust Migration Complete Guide",
          "link": "/plans/HOOK_RUNTIME_RUST_COMPLETE.md"
        },
        {
          "text": "Hook Runtime: Full Rust Migration Design (Deep & Wide)",
          "link": "/plans/HOOK_RUNTIME_RUST_DESIGN.md"
        },
        {
          "text": "Hybrid Mac/Windows Environment Implementation Plan",
          "link": "/plans/HYBRID_ENV_IMPLEMENTATION_PLAN.md"
        },
        {
          "text": "LiteLLM + CLIProxyAPIPlus + Bifrost Harmony",
          "link": "/plans/LITELLM_CLIPROXY_BIFROST_HARMONY.md"
        },
        {
          "text": "MCP Bundle: thegent + Browser Tools (Replace Manual Playwright)",
          "link": "/plans/MCP_BUNDLE_PLAYWRIGHT_REPLACEMENT.md"
        },
        {
          "text": "MCP Tool Optimization, Polish & Enhancement Plan",
          "link": "/plans/MCP_TOOL_OPTIMIZATION_PLAN.md"
        },
        {
          "text": "Multi-Platform Parity Master Plan & Matrix",
          "link": "/plans/MULTI_PLATFORM_PARITY_MASTER_PLAN.md"
        },
        {
          "text": "New Providers Auth Research & Plan",
          "link": "/plans/NEW_PROVIDERS_AUTH_RESEARCH.md"
        },
        {
          "text": "OpenRouter-Style Routing + CLIProxyAPIPlus Integration",
          "link": "/plans/OPENROUTER_STYLE_ROUTING_AND_CLIPROXY.md"
        },
        {
          "text": "Process & Tool Optimization Complete Plan",
          "link": "/plans/PROCESS_OPTIMIZATION_COMPLETE_PLAN.md"
        },
        {
          "text": "Process and Tool Optimization Plan",
          "link": "/plans/PROCESS_OPTIMIZATION_PLAN.md"
        },
        {
          "text": "Prompt History Collection & Audit System: Comprehensive Plan",
          "link": "/plans/PROMPT_HISTORY_COLLECTION_AND_AUDIT_SYSTEM.md"
        },
        {
          "text": "Prompt History Collection & Audit System Complete Guide",
          "link": "/plans/PROMPT_HISTORY_COLLECTION_COMPLETE.md"
        },
        {
          "text": "Remote Compute Implementation Detail",
          "link": "/plans/REMOTE_COMPUTE_IMPLEMENTATION_DETAIL.md"
        },
        {
          "text": "thegent Setup: Proposed Hooks, Plugins, Skills, MCP & Docs",
          "link": "/plans/SETUP_PROPOSED_ITEMS.md"
        },
        {
          "text": "Shell Environment Advanced Enhancement Plan",
          "link": "/plans/SHELL_ENVIRONMENT_ADVANCED_ENHANCEMENT_PLAN.md"
        },
        {
          "text": "Shell Environment Advanced Enhancement - Implementation Summary",
          "link": "/plans/SHELL_ENVIRONMENT_ADVANCED_IMPLEMENTATION_SUMMARY.md"
        },
        {
          "text": "Shell Environment Complete Plan",
          "link": "/plans/SHELL_ENVIRONMENT_COMPLETE_PLAN.md"
        },
        {
          "text": "Shell Environment Implementation Summary",
          "link": "/plans/SHELL_ENVIRONMENT_IMPLEMENTATION_SUMMARY.md"
        },
        {
          "text": "Shell Environment Optimization & Enhancement Plan",
          "link": "/plans/SHELL_ENVIRONMENT_OPTIMIZATION_PLAN.md"
        },
        {
          "text": "Sync/Update Command & Full System Audit Plan",
          "link": "/plans/SYNC_UPDATE_COMMAND_AND_SYSTEM_AUDIT_PLAN.md"
        },
        {
          "text": "Thegent FastMCP 3.0 Implementation Plan",
          "link": "/plans/THGENT_FASTMCP_IMPLEMENTATION_PLAN.md"
        },
        {
          "text": "Runtime Dispatch Consolidation & Fork Fix: Complete",
          "link": "/plans/ULTRA_SHIM_CONSOLIDATION_COMPLETE.md"
        },
        {
          "text": "Ultra-Shim Fork Failure Fix: Root Cause Analysis & Solution",
          "link": "/plans/ULTRA_SHIM_FORK_FAILURE_FIX.md"
        },
        {
          "text": "Unified Login Flow: Open URL + Prompt for Key",
          "link": "/plans/UNIFIED_LOGIN_FLOW.md"
        },
        {
          "text": "Unified System Application Plan",
          "link": "/plans/UNIFIED_SYSTEM_APPLICATION_PLAN.md"
        }
      ]
    },
    {
      "text": "Reference",
      "collapsed": false,
      "items": [
        {
          "text": "Routing System: Project Complete Summary",
          "link": "/reference/00_ROUTING_PROJECT_COMPLETE.md"
        },
        {
          "text": "Agent Identity & Sovereignty Depth (WP-6004)",
          "link": "/reference/AGENT_IDENTITY_SOVEREIGNTY_DEPTH.md"
        },
        {
          "text": "Agent Communication Language (JSON-ACL) & Negotiation (WP-1006)",
          "link": "/reference/AGENT_NEGOTIATION_ACL_DEPTH.md"
        },
        {
          "text": "Agent OS Principals \u2014 Depth Document",
          "link": "/reference/AGENT_OS_PRINCIPALS_DEPTH.md"
        },
        {
          "text": "Benchmark Comparison: SWE-Bench vs Terminal Bench 2.0",
          "link": "/reference/BENCHMARK_COMPARISON_SWE_BENCH_VS_TERMINAL_BENCH_2_0.md"
        },
        {
          "text": "Global Claude Code Instructions",
          "link": "/reference/CLAUDE_CORE_GUIDELINES.md"
        },
        {
          "text": "CLAUDE Appendix: thegent-specific and domain workflow rules",
          "link": "/reference/CLAUDE_THEGENT_RUNTIME_APPENDIX.md"
        },
        {
          "text": "Complete Provider Routing Map (All 12+ Providers)",
          "link": "/reference/COMPLETE_PROVIDER_ROUTING_MAP.md"
        },
        {
          "text": "Constitutional Enforcement & Proof of Alignment (WP-3001)",
          "link": "/reference/CONSTITUTIONAL_ENFORCEMENT_DEPTH.md"
        },
        {
          "text": "Context Management & Semantic Compression Depth (WP-5001)",
          "link": "/reference/CONTEXT_MANAGEMENT_DEPTH.md"
        },
        {
          "text": "Cost Enforcement Policy: 2x Limit & Escalation Framework",
          "link": "/reference/COST_ENFORCEMENT_POLICY.md"
        },
        {
          "text": "Cross-Platform Desktop Automation: API Reference",
          "link": "/reference/CROSS_PLATFORM_API_REFERENCE.md"
        },
        {
          "text": "Cross-Platform Multi-Tenant Desktop Automation Quick Reference",
          "link": "/reference/CROSS_PLATFORM_MULTI_TENANT_QUICK_REFERENCE.md"
        },
        {
          "text": "Dominance Proof Reference",
          "link": "/reference/DOMINANCE_PROOF_REFERENCE.md"
        },
        {
          "text": "Economic Governance & Token ROI Modeling (WP-5003)",
          "link": "/reference/ECONOMIC_GOVERNANCE_DEPTH.md"
        },
        {
          "text": "Frontmatter/Backmatter Integration Points",
          "link": "/reference/FRONTMATTER_BACKMATTER_INTEGRATION_POINTS.md"
        },
        {
          "text": "FR Tracker: thegent",
          "link": "/reference/FR_TRACKER.md"
        },
        {
          "text": "Gardener Architecture",
          "link": "/reference/GARDENER_ARCHITECTURE.md"
        },
        {
          "text": "Human-Agent Collaboration (HAC) & HITL Patterns (WP-4001..4009)",
          "link": "/reference/HAC_AND_HITL_PATTERNS.md"
        },
        {
          "text": "Hook Optimization Strategy",
          "link": "/reference/HOOK_OPTIMIZATION_STRATEGY.md"
        },
        {
          "text": "Hybrid Mac/Windows Development Environment - Summary",
          "link": "/reference/HYBRID_ENV_SUMMARY.md"
        },
        {
          "text": "Indexing and Optimization Systems \u2014 Reference",
          "link": "/reference/INDEXING_AND_OPTIMIZATION_SYSTEMS.md"
        },
        {
          "text": "TaskRouter + Pareto Routing Integration Architecture",
          "link": "/reference/INTEGRATION_ARCHITECTURE.md"
        },
        {
          "text": "TaskRouter + Pareto Routing Integration \u2014 Document Index",
          "link": "/reference/INTEGRATION_INDEX.md"
        },
        {
          "text": "TaskRouter Integration Quick Start",
          "link": "/reference/INTEGRATION_QUICK_START.md"
        },
        {
          "text": "MAIF Artifact Specification & Provenance Depth (WP-3002)",
          "link": "/reference/MAIF_ARTIFACT_SPEC_DEPTH.md"
        },
        {
          "text": "MCP Tool Retry Policy",
          "link": "/reference/MCP_RETRY_POLICY.md"
        },
        {
          "text": "Corrected Model Ranking Using Pareto Frontier",
          "link": "/reference/MODEL_RANKING_CORRECTED.md"
        },
        {
          "text": "Model Routing Decision Tree",
          "link": "/reference/MODEL_ROUTING_DECISION_TREE.md"
        },
        {
          "text": "Model Routing & Cost Governance: Complete Index",
          "link": "/reference/MODEL_ROUTING_INDEX.md"
        },
        {
          "text": "Model Routing & Cost Governance: Quick Reference",
          "link": "/reference/MODEL_ROUTING_SUMMARY.md"
        },
        {
          "text": "Model Routing: Terminal Bench 2.0 Quick Reference",
          "link": "/reference/MODEL_ROUTING_TERMINAL_BENCH_2_0_QUICK_REF.md"
        },
        {
          "text": "Model Selection Documentation Index",
          "link": "/reference/MODEL_SELECTION_INDEX.md"
        },
        {
          "text": "Monitoring Alert Rules",
          "link": "/reference/MONITORING_ALERT_RULES.md"
        },
        {
          "text": "Monitoring Dashboard Specifications",
          "link": "/reference/MONITORING_DASHBOARD_SPEC.md"
        },
        {
          "text": "Monitoring Metrics Reference",
          "link": "/reference/MONITORING_METRICS_REFERENCE.md"
        },
        {
          "text": "Monitoring System Documentation",
          "link": "/reference/MONITORING_README.md"
        },
        {
          "text": "Monitoring Setup Guide",
          "link": "/reference/MONITORING_SETUP_GUIDE.md"
        },
        {
          "text": "Civilizational Multi-Swarm Hierarchy (WP-1006, WP-5004)",
          "link": "/reference/MULTI_SWARM_HIERARCHY_DEPTH.md"
        },
        {
          "text": "OpenTelemetry GenAI & Observability Depth (WP-Y6)",
          "link": "/reference/OTEL_GENAI_AND_HYSTERESIS_DEPTH.md"
        },
        {
          "text": "oxlint Rule Mapping Reference",
          "link": "/reference/OXLINT_RULE_MAPPING.md"
        },
        {
          "text": "Pareto Frontier Algorithm: Pseudocode & Implementation Guide",
          "link": "/reference/PARETO_ALGORITHM_PSEUDOCODE.md"
        },
        {
          "text": "Pareto Frontier: Executive Summary",
          "link": "/reference/PARETO_EXECUTIVE_SUMMARY.md"
        },
        {
          "text": "Pareto Frontier Analysis & Model Ranking Algorithm",
          "link": "/reference/PARETO_FRONTIER_ANALYSIS.md"
        },
        {
          "text": "Pareto Frontier Analysis: Complete Model Evaluation",
          "link": "/reference/PARETO_FRONTIER_COMPLETE_ANALYSIS.md"
        },
        {
          "text": "Pareto Frontier Matrix: Model Selection Guide",
          "link": "/reference/PARETO_FRONTIER_MATRIX.md"
        },
        {
          "text": "Pareto Frontier Quick Reference",
          "link": "/reference/PARETO_FRONTIER_QUICK_REFERENCE.md"
        },
        {
          "text": "Pareto Frontier Analysis: Complete Data Table",
          "link": "/reference/PARETO_FRONTIER_TABLE.md"
        },
        {
          "text": "Pareto Frontier Analysis: Terminal Bench 2.0 (Corrected)",
          "link": "/reference/PARETO_FRONTIER_TERMINAL_BENCH_2_0.md"
        },
        {
          "text": "Pareto Frontier Analysis: Complete Index",
          "link": "/reference/PARETO_INDEX.md"
        },
        {
          "text": "Multi-Objective Provider Routing & Pareto Fronts (WP-1004)",
          "link": "/reference/PARETO_ROUTING_DESIGN.md"
        },
        {
          "text": "Pareto Frontier Visualization & Diagrams",
          "link": "/reference/PARETO_VISUALIZATION.md"
        },
        {
          "text": "Phase 3.5 Quick Reference",
          "link": "/reference/PHASE_3_5_QUICK_REFERENCE.md"
        },
        {
          "text": "Phase 4 UX: Operator Cockpit & Rationale Depth (WP-4001)",
          "link": "/reference/PHASE_4_COCKPIT_UX_DEPTH.md"
        },
        {
          "text": "Phase 5 Scale: Redis & Distributed Robustness (WP-5004)",
          "link": "/reference/PHASE_5_SCALE_ROBUSTNESS_DEPTH.md"
        },
        {
          "text": "POSIX + pwsh Shell Strategy",
          "link": "/reference/POSIX_PWSH_SHELL_STRATEGY.md"
        },
        {
          "text": "Provider Limits and Auto-Fallback",
          "link": "/reference/PROVIDER_LIMITS_AND_FALLBACK.md"
        },
        {
          "text": "Provider Model Behavior Constraints",
          "link": "/reference/PROVIDER_MODEL_BEHAVIOR.md"
        },
        {
          "text": "Provider Model Reference",
          "link": "/reference/PROVIDER_MODEL_REFERENCE.md"
        },
        {
          "text": "Robustness, Breadth, and Depth \u2014 Phase Evolution",
          "link": "/reference/ROBUSTNESS_AND_FUTURE_DEPTH.md"
        },
        {
          "text": "Routing Decision Matrix: Task Category Logic",
          "link": "/reference/ROUTING_DECISION_MATRIX.md"
        },
        {
          "text": "Final Routing Recommendation (Terminal Bench 2.0)",
          "link": "/reference/ROUTING_FINAL_RECOMMENDATION.md"
        },
        {
          "text": "Task Routing Implementation Architecture",
          "link": "/reference/ROUTING_IMPLEMENTATION_ARCHITECTURE.md"
        },
        {
          "text": "Model Routing Quick Card (Pocket Reference)",
          "link": "/reference/ROUTING_QUICK_CARD.md"
        },
        {
          "text": "Routing System: Master Summary & Implementation Roadmap",
          "link": "/reference/ROUTING_SYSTEM_MASTER_SUMMARY.md"
        },
        {
          "text": "Rust-Based CLI Tooling",
          "link": "/reference/RUST_TOOLING.md"
        },
        {
          "text": "Agentic CI/CD & Self-Healing Loops (WP-2004)",
          "link": "/reference/SELF_HEALING_AGENTIC_CICD_DEPTH.md"
        },
        {
          "text": "Planning Simulation & Replay Sandbox Depth (WP-4007, WP-12004)",
          "link": "/reference/SIMULATION_AND_SANDBOX_DEPTH.md"
        },
        {
          "text": "MCP Tool SLO Targets (G-OP-08)",
          "link": "/reference/SLO_TARGETS.md"
        },
        {
          "text": "Speed & Quality Index Implementation Plan",
          "link": "/reference/SPEED_QUALITY_INDEX_IMPLEMENTATION_PLAN.md"
        },
        {
          "text": "Starship Prompt \u2014 Long-Term Fix for Scan Timeout",
          "link": "/reference/STARSHIP_SETUP.md"
        },
        {
          "text": "Swarm Memory & Multi-Agent Coordination (WP-1006)",
          "link": "/reference/SWARM_MEMORY_COORDINATION_DEPTH.md"
        },
        {
          "text": "Swarm Process Optimizations (Multi-Agent / Multi-Tenant / Multi-Project)",
          "link": "/reference/SWARM_PROCESS_OPTIMIZATIONS.md"
        },
        {
          "text": "Task Categorization & AI Agent Dispatch Routing Design",
          "link": "/reference/TASK_ROUTING_DESIGN.md"
        },
        {
          "text": "Terminal Bench 2.0: Corrected Pareto Frontier & Routing",
          "link": "/reference/TERMINAL_BENCH_2_0_CORRECTED_FRONTIER.md"
        },
        {
          "text": "Tooling & Global Optimizations Audit (In-Depth)",
          "link": "/reference/TOOLING_AND_GLOBAL_OPTIMIZATIONS_AUDIT.md"
        },
        {
          "text": "Tooling and Global Optimizations Audit",
          "link": "/reference/TOOLING_AND_OPTIMIZATION_AUDIT.md"
        },
        {
          "text": "Touchpoint Integration \u2014 Deep Dive",
          "link": "/reference/TOUCHPOINT_INTEGRATION_DEEP_DIVE.md"
        },
        {
          "text": "Touchpoint Integration Evaluation",
          "link": "/reference/TOUCHPOINT_INTEGRATION_EVALUATION.md"
        },
        {
          "text": "Unified Work Stream \u2014 Design",
          "link": "/reference/UNIFIED_WORK_STREAM_DESIGN.md"
        },
        {
          "text": "WBS Agent Progress \u2014 Claim & Coordination",
          "link": "/reference/WBS_AGENT_PROGRESS.md"
        },
        {
          "text": "Unified Work Stream \u2014 Canonical",
          "link": "/reference/WORK_STREAM.md"
        },
        {
          "text": "Zen (OpenCode) Integration Analysis",
          "link": "/reference/ZEN_INTEGRATION.md"
        },
        {
          "text": "Reference",
          "link": "/reference/index.md"
        }
      ]
    },
    {
      "text": "Reports",
      "collapsed": false,
      "items": [
        {
          "text": "BKM Phase 1 Completion Report",
          "link": "/reports/BKM_PHASE_1_COMPLETION_REPORT.md"
        },
        {
          "text": "Critical Issue #2: Git Cache Invalidation Fix - Complete Report",
          "link": "/reports/CACHE_INVALIDATION_FIX_REPORT.md"
        },
        {
          "text": "Critical Issues Fixes - Completion Report",
          "link": "/reports/CRITICAL_FIXES_COMPLETION_REPORT.md"
        },
        {
          "text": "Critical Issue #2: Unsafe Git Cache Invalidation - Executive Summary",
          "link": "/reports/CRITICAL_ISSUE_2_SUMMARY.md"
        },
        {
          "text": "Phase 10-12 Closure and Final Handoff Note (WP-12010)",
          "link": "/reports/FINAL_CLOSURE_NOTE.md"
        },
        {
          "text": "Holistic + Harmonious Design & Integration \u2014 Implementation Complete \u2705",
          "link": "/reports/HOLISTIC_DESIGN_IMPLEMENTATION_COMPLETE.md"
        },
        {
          "text": "Holistic + Harmonious Design & Integration \u2014 Implementation Progress",
          "link": "/reports/HOLISTIC_DESIGN_IMPLEMENTATION_PROGRESS.md"
        },
        {
          "text": "Thegent Implementation Status Report",
          "link": "/reports/IMPLEMENTATION_STATUS.md"
        },
        {
          "text": "Thegent Implementation Summary",
          "link": "/reports/IMPLEMENTATION_SUMMARY.md"
        },
        {
          "text": "P7.1 Verification Report: Per-Project Quality Gate Checks",
          "link": "/reports/P7.1_VERIFICATION_REPORT.md"
        },
        {
          "text": "P7.2 Cross-Project Consistency Report",
          "link": "/reports/P7.2_CROSS_PROJECT_CONSISTENCY.md"
        },
        {
          "text": "Phase 10-12 Closure and Handoff Note (WP-12010)",
          "link": "/reports/PHASE_10_12_CLOSURE.md"
        },
        {
          "text": "Phase 13: Policy Federation Progress Report",
          "link": "/reports/PHASE_13_PROGRESS_REPORT.md"
        },
        {
          "text": "Phase 14: Autonomous Learning and Cost Sensing Progress Report",
          "link": "/reports/PHASE_14_PROGRESS_REPORT.md"
        },
        {
          "text": "Phase 15: Enterprise Lifecycle and Compliance Progress Report",
          "link": "/reports/PHASE_15_PROGRESS_REPORT.md"
        },
        {
          "text": "Phase 3.5 Optimization Summary",
          "link": "/reports/PHASE_3_5_SUMMARY.md"
        },
        {
          "text": "Phase 3.5 Optimization Validation Report",
          "link": "/reports/PHASE_3_5_VALIDATION.md"
        },
        {
          "text": "Phase 3: Job Pool Implementation - Completion Summary",
          "link": "/reports/PHASE_3_COMPLETION_SUMMARY.md"
        },
        {
          "text": "Phase 3 - Job Pool Implementation Report",
          "link": "/reports/PHASE_3_JOB_POOL_IMPLEMENTATION.md"
        },
        {
          "text": "Phase 4: Advanced Bash Optimizations Report",
          "link": "/reports/PHASE_4_ADVANCED_OPTIMIZATIONS.md"
        },
        {
          "text": "Phase 4 Implementation Summary: ESLint \u2192 oxlint Migration",
          "link": "/reports/PHASE_4_IMPLEMENTATION_SUMMARY.md"
        },
        {
          "text": "Phase 4: Advanced Bash Optimizations - Implementation Summary",
          "link": "/reports/PHASE_4_SUMMARY.md"
        },
        {
          "text": "\u{1F3C1} Project Completion Report: thegent",
          "link": "/reports/PROJECT_COMPLETION_REPORT.md"
        }
      ]
    },
    {
      "text": "Research",
      "collapsed": false,
      "items": [
        {
          "text": "Idea Seeds",
          "collapsed": false,
          "items": [
            {
              "text": "Idea Seed Expansion \u2014 Complete",
              "link": "/idea-seeds/IDEA_SEED_EXPANSION_COMPLETE.md"
            },
            {
              "text": "Idea seed: $idea prompt harvesting (Cursor/Codex/Claude)",
              "link": "/idea-seeds/seed_cursor_20260216T103017Z_87c98b2e-9c87-459c-919e-1430c46c5b5b_199.md"
            },
            {
              "text": "Idea seed: $idea prompt harvesting (Cursor/Codex/Claude)",
              "link": "/idea-seeds/seed_cursor_20260216T103017Z_87c98b2e-9c87-459c-919e-1430c46c5b5b_201.md"
            },
            {
              "text": "Idea seed: $idea prompt harvesting (Cursor/Codex/Claude)",
              "link": "/idea-seeds/seed_cursor_20260216T103237Z_87c98b2e-9c87-459c-919e-1430c46c5b5b_199.md"
            },
            {
              "text": "Idea seed: $idea prompt harvesting (Cursor/Codex/Claude)",
              "link": "/idea-seeds/seed_cursor_20260216T103237Z_87c98b2e-9c87-459c-919e-1430c46c5b5b_201.md"
            }
          ]
        },
        {
          "text": "ADR-013: Multi-Org Policy Federation",
          "link": "/research/ADR-013-POLICY-FEDERATION.md"
        },
        {
          "text": "ADR-014: Autonomous Learning and Cost Sensing",
          "link": "/research/ADR-014-AUTONOMOUS-LEARNING.md"
        },
        {
          "text": "ADR-015: Enterprise Lifecycle and Compliance API",
          "link": "/research/ADR-015-ENTERPRISE-COMPLIANCE.md"
        },
        {
          "text": "Advanced Storage, Workflow & AI Systems: Deep Comparison & Optimization Strategies",
          "link": "/research/ADVANCED_STORAGE_WORKFLOW_AI_SYSTEMS_DEEP_COMPARISON.md"
        },
        {
          "text": "Advanced Strategies & Resilience \u2014 Full-Depth Research & Plan",
          "link": "/research/ADVANCED_STRATEGIES_AND_RESILIENCE_RESEARCH.md"
        },
        {
          "text": "Agent Access and Optimization \u2014 Audit and Plan",
          "link": "/research/AGENT_ACCESS_AND_OPTIMIZATION_AUDIT_PLAN.md"
        },
        {
          "text": "Agent File Search \u2014 Unified Tool Research",
          "link": "/research/AGENT_FILE_SEARCH_UNIFIED_TOOL_RESEARCH.md"
        },
        {
          "text": "Agent Platforms Complete Research & Integration Guide",
          "link": "/research/AGENT_PLATFORMS_COMPLETE.md"
        },
        {
          "text": "Agent Platforms: kilo, roo, OpenCode, Zen + CLIProxyAPI \u2014 Research",
          "link": "/research/AGENT_PLATFORMS_KILO_ROO_OPencode_CLIPROXY_RESEARCH.md"
        },
        {
          "text": "Agent Process Architecture \u2014 Research Note",
          "link": "/research/AGENT_PROCESS_ARCHITECTURE_RESEARCH.md"
        },
        {
          "text": "API, CLI, and DevOps Documentation Tools Research Report",
          "link": "/research/API_CLI_DEVOPS_TOOLING.md"
        },
        {
          "text": "Caching, Indexing & Pre-warming Complete Practical Guide",
          "link": "/research/CACHING_COMPLETE.md"
        },
        {
          "text": "Caching, Indexing & Pre-warming: Deep Research & Strategies",
          "link": "/research/CACHING_INDEXING_PREWARMING_DEEP_RESEARCH.md"
        },
        {
          "text": "CI/CD and Developer Experience Tooling Research Report (2025-2026)",
          "link": "/research/CI_CD_DEVX_TOOLING.md"
        },
        {
          "text": "Multi-Agent Feature Parity Audit",
          "link": "/research/CLAUDE_CODE_FEATURE_PARITY_AUDIT.md"
        },
        {
          "text": "Claude Code: Queue Pending & Blocking Messages (Research & Plan)",
          "link": "/research/CLAUDE_CODE_QUEUE_PENDING_BLOCKING.md"
        },
        {
          "text": "Claude Code Plan & Delegate Modes \u2014 Deep Research for thegent Tooling",
          "link": "/research/CLAUDE_PLAN_DELEGATE_MODES_RESEARCH.md"
        },
        {
          "text": "Client-Side Software Package Design & Deployment Research",
          "link": "/research/CLIENT_SIDE_PACKAGE_DESIGN_RESEARCH.md"
        },
        {
          "text": "Codex Hooks, Notifications & Extension Options",
          "link": "/research/CODEX_HOOKS_AND_EXTENSION_OPTIONS.md"
        },
        {
          "text": "Codex + CLIProxyAPIPlus: Research and Plan",
          "link": "/research/CODEX_MINIMAX_CLIPROXY_RESEARCH_AND_PLAN.md"
        },
        {
          "text": "Comprehensive Non-Canonical Audit and Consolidation Plan",
          "link": "/research/COMPREHENSIVE_NON_CANONICAL_AUDIT.md"
        },
        {
          "text": "Conversation Dump \u2014 2026-02-16",
          "link": "/research/CONVERSATION_DUMP_2026-02-16.md"
        },
        {
          "text": "Conversation Dump Complete \u2014 2026-02-16 Structured & Expanded",
          "link": "/research/CONVERSATION_DUMP_2026-02-16_COMPLETE.md"
        },
        {
          "text": "Conversation Dump 2026-02-16 \u2014 Complete Expansion",
          "link": "/research/CONVERSATION_DUMP_2026-02-16_EXPANDED.md"
        },
        {
          "text": "Cost-Based Routing \u2014 Deferred Scope",
          "link": "/research/COST_ROUTING_DEFERRED.md"
        },
        {
          "text": "Cost Routing Deferred \u2014 Formal Decision Record",
          "link": "/research/COST_ROUTING_DEFERRED_EXPANDED.md"
        },
        {
          "text": "Cross-Platform Multi-Tenant Desktop Automation: Advanced Patterns",
          "link": "/research/CROSS_PLATFORM_ADVANCED_PATTERNS.md"
        },
        {
          "text": "Cross-Platform Extensions: Wider, Deeper, Polish & Optimization",
          "link": "/research/CROSS_PLATFORM_EXTENSIONS_WIDER_DEEPER_OPTIMIZATION.md"
        },
        {
          "text": "Cross-Platform Gaps and Extensions \u2014 Research & Plan",
          "link": "/research/CROSS_PLATFORM_GAPS_AND_EXTENSIONS_RESEARCH.md"
        },
        {
          "text": "Cross-Platform Desktop Automation: Integration Guide",
          "link": "/research/CROSS_PLATFORM_INTEGRATION_GUIDE.md"
        },
        {
          "text": "Cross-Platform Multi-Tenant Desktop Automation Research & Plan",
          "link": "/research/CROSS_PLATFORM_MULTI_TENANT_DESKTOP_AUTOMATION_RESEARCH.md"
        },
        {
          "text": "Cross-Platform Desktop Automation: Performance Benchmarks & SLAs",
          "link": "/research/CROSS_PLATFORM_PERFORMANCE_BENCHMARKS.md"
        },
        {
          "text": "Cross-Platform Research Complete \u2014 Comprehensive Consolidated Guide",
          "link": "/research/CROSS_PLATFORM_RESEARCH_COMPLETE.md"
        },
        {
          "text": "Cross-Platform Desktop Automation: Research Completion Summary",
          "link": "/research/CROSS_PLATFORM_RESEARCH_COMPLETION_SUMMARY.md"
        },
        {
          "text": "Cross-Platform Research \u2014 Consolidated Comprehensive Guide",
          "link": "/research/CROSS_PLATFORM_RESEARCH_CONSOLIDATED.md"
        },
        {
          "text": "Cross-Platform Desktop Automation: Research Index",
          "link": "/research/CROSS_PLATFORM_RESEARCH_INDEX.md"
        },
        {
          "text": "Cross-Platform Multi-Tenant Desktop Automation: Research Summary",
          "link": "/research/CROSS_PLATFORM_RESEARCH_SUMMARY.md"
        },
        {
          "text": "Cross-Platform Desktop Automation: Security Deep Dive",
          "link": "/research/CROSS_PLATFORM_SECURITY_DEEP_DIVE.md"
        },
        {
          "text": "Doctor Command: OAuth-Only Authentication Update",
          "link": "/research/DOCTOR_OAUTH_ONLY_UPDATE.md"
        },
        {
          "text": "ESLint \u2192 oxlint Migration Audit (Phase 4)",
          "link": "/research/ESLINT_AUDIT.md"
        },
        {
          "text": "Expansion Complete \u2014 Final Report",
          "link": "/research/EXPANSION_COMPLETE_FINAL.md"
        },
        {
          "text": "Expansion Phase \u2014 Complete Summary",
          "link": "/research/EXPANSION_PHASE_COMPLETE.md"
        },
        {
          "text": "FastMCP Complete \u2014 Comprehensive Implementation Guide",
          "link": "/research/FASTMCP_COMPLETE.md"
        },
        {
          "text": "FastMCP Elicitation & Context API Summary",
          "link": "/research/FASTMCP_ELICITATION_CONTEXT.md"
        },
        {
          "text": "FastMCP Features & MCP Transport Spec Gaps",
          "link": "/research/FASTMCP_FEATURES_AND_TRANSPORT_GAPS.md"
        },
        {
          "text": "FastMCP Implementation Guide for thegent",
          "link": "/research/FASTMCP_IMPLEMENTATION_GUIDE.md"
        },
        {
          "text": "FastMCP Middleware",
          "link": "/research/FASTMCP_MIDDLEWARE.md"
        },
        {
          "text": "FastMCP Progress & Tasks API Summary",
          "link": "/research/FASTMCP_PROGRESS_TASKS.md"
        },
        {
          "text": "FastMCP Sampling & Telemetry",
          "link": "/research/FASTMCP_SAMPLING_TELEMETRY.md"
        },
        {
          "text": "FastMCP Spec Deep Dive",
          "link": "/research/FASTMCP_SPEC_DEEP_DIVE.md"
        },
        {
          "text": "FastMCP Storage Backends & EventStore",
          "link": "/research/FASTMCP_STORAGE_EVENTSTORE.md"
        },
        {
          "text": "FastMCP Transforms & Deployment Summary",
          "link": "/research/FASTMCP_TRANSFORMS_DEPLOYMENT.md"
        },
        {
          "text": "Final Expansion Report \u2014 Complete",
          "link": "/research/FINAL_EXPANSION_REPORT.md"
        },
        {
          "text": "Git Shim Starship Optimization \u2014 Fix for 8+ Minute Prompt Delays",
          "link": "/research/GIT_SHIM_STARSHIP_OPTIMIZATION.md"
        },
        {
          "text": "Git Tooling Audit and Modernization Plan",
          "link": "/research/GIT_TOOLING_AUDIT_AND_PLAN.md"
        },
        {
          "text": "Governance, Policy Enforcement, and Audit Trail Research",
          "link": "/research/GOVERNANCE_POLICY_AUDIT_RESEARCH.md"
        },
        {
          "text": "Governance WP Gaps \u2014 Implementation Notes",
          "link": "/research/GOVERNANCE_WP_GAPS.md"
        },
        {
          "text": "Governance WP Gaps \u2014 Expanded & BACKLOG Items",
          "link": "/research/GOVERNANCE_WP_GAPS_EXPANDED.md"
        },
        {
          "text": "Hook Rust Migration Complete \u2014 Comprehensive Migration Strategy & Timeline",
          "link": "/research/HOOK_RUST_MIGRATION_COMPLETE.md"
        },
        {
          "text": "Hook Runtime Rust Migration: Research Synthesis",
          "link": "/research/HOOK_RUST_MIGRATION_RESEARCH_SYNTHESIS.md"
        },
        {
          "text": "Hook Runtime Rust Migration \u2014 Complete Expansion",
          "link": "/research/HOOK_RUST_MIGRATION_RESEARCH_SYNTHESIS_EXPANDED.md"
        },
        {
          "text": "Idea Seeds & Session Storage",
          "link": "/research/IDEA_SEEDS_SESSION_STORAGE.md"
        },
        {
          "text": "Idea Seed Review Complete \u2014 Consolidation & Rationale",
          "link": "/research/IDEA_SEED_REVIEW_COMPLETE.md"
        },
        {
          "text": "Index Sprawl Status Update \u2014 Complete",
          "link": "/research/INDEX_SPRAWL_STATUS_UPDATE.md"
        },
        {
          "text": "In-Depth Tooling and Global Optimizations Audit (2026-02-15)",
          "link": "/research/IN_DEPTH_TOOLING_AUDIT_2026.md"
        },
        {
          "text": "Library-First Audit and Plan",
          "link": "/research/LIBRARY_FIRST_AUDIT_AND_PLAN.md"
        },
        {
          "text": "Library Replacement Audit \u2014 Deep & Wide",
          "link": "/research/LIBRARY_REPLACEMENT_AUDIT_DEEP.md"
        },
        {
          "text": "Library Replacement Complete \u2014 Comprehensive Audit & Migration Plan",
          "link": "/research/LIBRARY_REPLACEMENT_COMPLETE.md"
        },
        {
          "text": "Library Replacement \u2014 Consolidated Migration Plan",
          "link": "/research/LIBRARY_REPLACEMENT_CONSOLIDATED.md"
        },
        {
          "text": "Library Replacement \u2014 Phase Design Work Breakdowns (DWBs)",
          "link": "/research/LIBRARY_REPLACEMENT_PHASE_DWBS.md"
        },
        {
          "text": "Master Expansion TODO \u2014 Complete Documentation Sprawl",
          "link": "/research/MASTER_EXPANSION_TODO.md"
        },
        {
          "text": "MCP Full Parity & FastMCP Transport Spec Audit",
          "link": "/research/MCP_FULL_PARITY_AND_FASTMCP_AUDIT.md"
        },
        {
          "text": "MCP and Client Features for Session Notifications",
          "link": "/research/MCP_NOTIFICATION_OPTIONS.md"
        },
        {
          "text": "MD Documentation Normalization Guide",
          "link": "/research/MD_NORMALIZATION_GUIDE.md"
        },
        {
          "text": "Memory Optimization \u2014 Long-Term Plan",
          "link": "/research/MEMORY_OPTIMIZATION_LONG_TERM_PLAN.md"
        },
        {
          "text": "Multi-Platform Agent Deep Dive",
          "link": "/research/MULTI_PLATFORM_DEEP_DIVE.md"
        },
        {
          "text": "OpenClaw / Agent Zero as Main Agent \u2014 Research",
          "link": "/research/OPENCLAW_AGENTZERO_AS_MAIN_AGENT_RESEARCH.md"
        },
        {
          "text": "OpenClaw, ClawHub, Agent Zero \u2014 Use Cases for thegent",
          "link": "/research/OPENCLAW_CLAWHUB_AGENTZERO_USE_CASES.md"
        },
        {
          "text": "Priority 1 (P1) Expansion \u2014 Complete",
          "link": "/research/P1_EXPANSION_COMPLETE.md"
        },
        {
          "text": "Priority 1 (P1) Phase \u2014 Complete",
          "link": "/research/P1_PHASE_COMPLETE.md"
        },
        {
          "text": "P3 Polish Complete \u2014 Full Research Docs",
          "link": "/research/P3_POLISH_COMPLETE.md"
        },
        {
          "text": "P4 Normalization \u2014 Complete",
          "link": "/research/P4_NORMALIZATION_COMPLETE.md"
        },
        {
          "text": "P4 Normalization \u2014 Final Status",
          "link": "/research/P4_NORMALIZATION_FINAL.md"
        },
        {
          "text": "P4 Normalization Progress \u2014 All MD Docs",
          "link": "/research/P4_NORMALIZATION_PROGRESS.md"
        },
        {
          "text": "P4 Normalization Summary \u2014 Complete",
          "link": "/research/P4_NORMALIZATION_SUMMARY.md"
        },
        {
          "text": "P4 Normalization Update \u2014 Progress Report",
          "link": "/research/P4_NORMALIZATION_UPDATE.md"
        },
        {
          "text": "Package Design Research Summary",
          "link": "/research/PACKAGE_DESIGN_RESEARCH_SUMMARY.md"
        },
        {
          "text": "Phase Documents \u2014 Complete Expansion",
          "link": "/research/PHASE_DOCUMENTS_EXPANDED.md"
        },
        {
          "text": "Plan Usage and Budget Research",
          "link": "/research/PLAN_USAGE_AND_BUDGET_RESEARCH.md"
        },
        {
          "text": "Proactive Governance Evolution Plan",
          "link": "/research/PROACTIVE_GOVERNANCE_EVOLUTION_PLAN.md"
        },
        {
          "text": "Production Packaging, Polish & Optimization Audit + Plan",
          "link": "/research/PRODUCTION_PACKAGING_POLISH_OPTIMIZATION_AUDIT_AND_PLAN.md"
        },
        {
          "text": "Python Frontmatter + Native Backmatter: Research Audit & Plan",
          "link": "/research/PYTHON_FRONTMATTER_NATIVE_BACKMATTER_AUDIT_PLAN.md"
        },
        {
          "text": "Qwen3.5 Plus 02-15 on OpenRouter \u2014 Pareto Research",
          "link": "/research/QWEN3.5_PLUS_OPENROUTER_PARETO_RESEARCH.md"
        },
        {
          "text": "Remove Directory Dependencies \u2014 Production Installation Optimization",
          "link": "/research/REMOVE_DIRECTORY_DEPENDENCIES_AUDIT_AND_PLAN.md"
        },
        {
          "text": "Research, Seed & Fragment Inventory \u2014 Sprawl Todo & Unified Work Stream",
          "link": "/research/RESEARCH_SEED_FRAGMENT_INVENTORY_AND_SPRAWL_TODO.md"
        },
        {
          "text": '"See Also" Section Template',
          "link": "/research/SEE_ALSO_TEMPLATE.md"
        },
        {
          "text": "Session Research Complete \u2014 Comprehensive Deep-Dive",
          "link": "/research/SESSION_RESEARCH_COMPLETE.md"
        },
        {
          "text": "Session Research Fragments \u2014 2026-02-15",
          "link": "/research/SESSION_RESEARCH_FRAGMENTS.md"
        },
        {
          "text": "Session Research Fragments \u2014 Complete Expansion",
          "link": "/research/SESSION_RESEARCH_FRAGMENTS_EXPANDED.md"
        },
        {
          "text": "Shell Configuration Audit and Consolidation Plan",
          "link": "/research/SHELL_CONFIG_AUDIT_AND_CONSOLIDATION_PLAN.md"
        },
        {
          "text": "Shell Error Fixes \u2014 zsh Bad Substitution",
          "link": "/research/SHELL_ERROR_FIXES.md"
        },
        {
          "text": "Smart & Robust Process Strategies \u2014 Research & Plan",
          "link": "/research/SMART_ROBUST_STRATEGIES_RESEARCH.md"
        },
        {
          "text": "Swarm Management Complete Research & Implementation Guide",
          "link": "/research/SWARM_COMPLETE.md"
        },
        {
          "text": "Swarm Optimization, Management & Scheduling \u2014 Deep Research",
          "link": "/research/SWARM_OPTIMIZATION_SCHEDULING_DEEP_RESEARCH.md"
        },
        {
          "text": "Swarm Process Automation \u2014 Deep Research & Plan",
          "link": "/research/SWARM_PROCESS_AUTOMATION_DEEP_RESEARCH.md"
        },
        {
          "text": "Swarm & Resource Optimization \u2014 Research Index",
          "link": "/research/SWARM_RESEARCH_INDEX.md"
        },
        {
          "text": "System Resources Complete Practical Guide",
          "link": "/research/SYSTEM_RESOURCES_COMPLETE.md"
        },
        {
          "text": "System Resources (FD, CPU, Threads, Ports) \u2014 Full-Depth Research & Plan",
          "link": "/research/SYSTEM_RESOURCES_FD_CPU_DEEP_RESEARCH.md"
        },
        {
          "text": "Thegent Teammates: Research and Implementation Plan (2026-02-15)",
          "link": "/research/TEAMMATES_RESEARCH_AND_PLAN.md"
        },
        {
          "text": "Tenacity vs Custom Retry \u2014 Audit & Plan",
          "link": "/research/TENACITY_RETRY_AUDIT_PLAN.md"
        },
        {
          "text": "Thegent Command Model Options and Agent Features Research",
          "link": "/research/THGENT_COMMAND_MODEL_OPTIONS_AND_AGENT_FEATURES_RESEARCH.md"
        },
        {
          "text": "TUI Compositor Comparison Research",
          "link": "/research/TUI_COMPOSITOR_COMPARISON.md"
        },
        {
          "text": "Unified Work Stream Integration \u2014 Complete",
          "link": "/research/UNIFIED_WORK_STREAM_INTEGRATION.md"
        },
        {
          "text": "User Queue + TUI: Editable Prompts While Agent Runs",
          "link": "/research/USER_QUEUE_TUI_AND_AGENT_POLL.md"
        },
        {
          "text": "VitePress Enhancements Research Report (2025-2026)",
          "link": "/research/VITEPRESS_ENHANCEMENTS.md"
        },
        {
          "text": "VitePress Phase 1 Implementation \u2014 \u2705 COMPLETE",
          "link": "/research/VITEPRESS_PHASE1_COMPLETE.md"
        },
        {
          "text": "VitePress Phase 1 Implementation \u2014 Status",
          "link": "/research/VITEPRESS_PHASE1_IMPLEMENTATION.md"
        },
        {
          "text": "VitePress Phase 2 Implementation \u2014 Status",
          "link": "/research/VITEPRESS_PHASE2_IMPLEMENTATION.md"
        },
        {
          "text": "VitePress Phase 3 Implementation \u2014 \u2705 COMPLETE",
          "link": "/research/VITEPRESS_PHASE3_COMPLETE.md"
        },
        {
          "text": "VitePress Rich Documentation Audit & Implementation Plan",
          "link": "/research/VITEPRESS_RICH_DOCUMENTATION_AUDIT.md"
        },
        {
          "text": "VitePress Rich Documentation \u2014 Implementation Plan",
          "link": "/research/VITEPRESS_RICH_DOCUMENTATION_IMPLEMENTATION_PLAN.md"
        },
        {
          "text": "Phase 13: Compliance Profile Mapping",
          "link": "/research/phase13-compliance-profile-mapping.md"
        },
        {
          "text": "Phase 13: Cost Sensitivity Experiment Plan",
          "link": "/research/phase13-cost-sensitivity-experiment-plan.md"
        },
        {
          "text": "Phase 13: Policy Federation Surface Map",
          "link": "/research/phase13-policy-federation-surface-map.md"
        },
        {
          "text": "Phase 13: Tenant Boundary Test Matrix",
          "link": "/research/phase13-tenant-boundary-test-matrix.md"
        },
        {
          "text": "Phase 14: Autonomous Learning and Cost Sensing Surface Map",
          "link": "/research/phase14-autonomous-learning-surface-map.md"
        },
        {
          "text": "Phase 14: Cost Sensing and Learning Test Matrix",
          "link": "/research/phase14-cost-sensing-test-matrix.md"
        },
        {
          "text": "Phase 15: Enterprise Compliance Test Matrix",
          "link": "/research/phase15-enterprise-compliance-test-matrix.md"
        },
        {
          "text": "Phase 15: Enterprise Lifecycle and Compliance Surface Map",
          "link": "/research/phase15-enterprise-lifecycle-surface-map.md"
        }
      ]
    },
    {
      "text": "Scratchpad",
      "collapsed": false,
      "items": [
        {
          "text": "Session Scratch Board & Optimization Plan",
          "link": "/scratchpad/session_review.md"
        }
      ]
    },
    {
      "text": "Cross-Project Agent Instructions",
      "link": "/docs/AGENT_INSTRUCTIONS.md"
    },
    {
      "text": "Architecture Layers (G-KD-05)",
      "link": "/docs/ARCHITECTURE_LAYERS.md"
    },
    {
      "text": "Cross-Platform Desktop Automation: Master Document Index",
      "link": "/docs/CROSS_PLATFORM_MASTER_INDEX.md"
    },
    {
      "text": "Discovery Surface (G-DS)",
      "link": "/docs/DISCOVERY.md"
    },
    {
      "text": "Document Queue Integration Guide",
      "link": "/docs/DOCUMENT_QUEUE_INTEGRATION.md"
    },
    {
      "text": "FastMCP Deployment Guide (G-FM-01 Phase 5)",
      "link": "/docs/FASTMCP_DEPLOYMENT_GUIDE.md"
    },
    {
      "text": "FastMCP Graceful Shutdown (G-OP-10)",
      "link": "/docs/FASTMCP_GRACEFUL_SHUTDOWN.md"
    },
    {
      "text": "FastMCP Icons and UX Hints (G-FM-04)",
      "link": "/docs/FASTMCP_ICONS_UX_HINTS.md"
    },
    {
      "text": "FastMCP Optimization & Polish Audit (G-OP-04\u2013G-OP-10)",
      "link": "/docs/FASTMCP_OPTIMIZATION_AUDIT.md"
    },
    {
      "text": "FastMCP Phase Checklist Verification (G-FM-06)",
      "link": "/docs/FASTMCP_PHASE_CHECKLIST_VERIFICATION.md"
    },
    {
      "text": "FastMCP Testing Strategy (G-FM-05)",
      "link": "/docs/FASTMCP_TESTING_STRATEGY.md"
    },
    {
      "text": "Thegent Gap Analysis & Remediation Plan",
      "link": "/docs/GAP_ANALYSIS_AND_REMEDIATION.md"
    },
    {
      "text": "Governance WP Implementation Verification (G-GP-01\u201309)",
      "link": "/docs/GOVERNANCE_WP_VERIFICATION.md"
    },
    {
      "text": "Multi-Agent Orchestration Mode Catalog",
      "link": "/docs/MULTI_AGENT_MODE_CATALOG.md"
    },
    {
      "text": "Thegent Orchestration Optimization Program (v1.0)",
      "link": "/docs/ORCHESTRATION.md"
    },
    {
      "text": "Planning Simulation Design (G-CA-04)",
      "link": "/docs/PLANNING_SIMULATION_DESIGN.md"
    },
    {
      "text": "Post-Launch Observation Playbook",
      "link": "/docs/POST_LAUNCH_OBSERVATION_PLAYBOOK.md"
    },
    {
      "text": "Thegent Orchestration Runbook (v1.0)",
      "link": "/docs/RUNBOOK.md"
    },
    {
      "text": "Setup Restore \u2014 Long-term Fixes Applied",
      "link": "/docs/SETUP-RESTORE.md"
    },
    {
      "text": "State-Aware Orchestration Design",
      "link": "/docs/STATE_AWARE_ORCHESTRATION_DESIGN.md"
    },
    {
      "text": "Thegent FastMCP Verification Runbook",
      "link": "/docs/VERIFICATION_RUNBOOK.md"
    },
    {
      "text": "Cross-Project Links Test",
      "link": "/docs/cross-links-test.md"
    },
    {
      "text": "Index",
      "link": "/docs/index.md"
    },
    {
      "text": "Test Callouts",
      "link": "/docs/test-callouts.md"
    }
  ],
  "/research/": [
    {
      "text": "Idea Seeds",
      "collapsed": false,
      "items": [
        {
          "text": "Idea Seed Expansion \u2014 Complete",
          "link": "/idea-seeds/IDEA_SEED_EXPANSION_COMPLETE.md"
        },
        {
          "text": "Idea seed: $idea prompt harvesting (Cursor/Codex/Claude)",
          "link": "/idea-seeds/seed_cursor_20260216T103017Z_87c98b2e-9c87-459c-919e-1430c46c5b5b_199.md"
        },
        {
          "text": "Idea seed: $idea prompt harvesting (Cursor/Codex/Claude)",
          "link": "/idea-seeds/seed_cursor_20260216T103017Z_87c98b2e-9c87-459c-919e-1430c46c5b5b_201.md"
        },
        {
          "text": "Idea seed: $idea prompt harvesting (Cursor/Codex/Claude)",
          "link": "/idea-seeds/seed_cursor_20260216T103237Z_87c98b2e-9c87-459c-919e-1430c46c5b5b_199.md"
        },
        {
          "text": "Idea seed: $idea prompt harvesting (Cursor/Codex/Claude)",
          "link": "/idea-seeds/seed_cursor_20260216T103237Z_87c98b2e-9c87-459c-919e-1430c46c5b5b_201.md"
        }
      ]
    },
    {
      "text": "ADR-013: Multi-Org Policy Federation",
      "link": "/research/ADR-013-POLICY-FEDERATION.md"
    },
    {
      "text": "ADR-014: Autonomous Learning and Cost Sensing",
      "link": "/research/ADR-014-AUTONOMOUS-LEARNING.md"
    },
    {
      "text": "ADR-015: Enterprise Lifecycle and Compliance API",
      "link": "/research/ADR-015-ENTERPRISE-COMPLIANCE.md"
    },
    {
      "text": "Advanced Storage, Workflow & AI Systems: Deep Comparison & Optimization Strategies",
      "link": "/research/ADVANCED_STORAGE_WORKFLOW_AI_SYSTEMS_DEEP_COMPARISON.md"
    },
    {
      "text": "Advanced Strategies & Resilience \u2014 Full-Depth Research & Plan",
      "link": "/research/ADVANCED_STRATEGIES_AND_RESILIENCE_RESEARCH.md"
    },
    {
      "text": "Agent Access and Optimization \u2014 Audit and Plan",
      "link": "/research/AGENT_ACCESS_AND_OPTIMIZATION_AUDIT_PLAN.md"
    },
    {
      "text": "Agent File Search \u2014 Unified Tool Research",
      "link": "/research/AGENT_FILE_SEARCH_UNIFIED_TOOL_RESEARCH.md"
    },
    {
      "text": "Agent Platforms Complete Research & Integration Guide",
      "link": "/research/AGENT_PLATFORMS_COMPLETE.md"
    },
    {
      "text": "Agent Platforms: kilo, roo, OpenCode, Zen + CLIProxyAPI \u2014 Research",
      "link": "/research/AGENT_PLATFORMS_KILO_ROO_OPencode_CLIPROXY_RESEARCH.md"
    },
    {
      "text": "Agent Process Architecture \u2014 Research Note",
      "link": "/research/AGENT_PROCESS_ARCHITECTURE_RESEARCH.md"
    },
    {
      "text": "API, CLI, and DevOps Documentation Tools Research Report",
      "link": "/research/API_CLI_DEVOPS_TOOLING.md"
    },
    {
      "text": "Caching, Indexing & Pre-warming Complete Practical Guide",
      "link": "/research/CACHING_COMPLETE.md"
    },
    {
      "text": "Caching, Indexing & Pre-warming: Deep Research & Strategies",
      "link": "/research/CACHING_INDEXING_PREWARMING_DEEP_RESEARCH.md"
    },
    {
      "text": "CI/CD and Developer Experience Tooling Research Report (2025-2026)",
      "link": "/research/CI_CD_DEVX_TOOLING.md"
    },
    {
      "text": "Multi-Agent Feature Parity Audit",
      "link": "/research/CLAUDE_CODE_FEATURE_PARITY_AUDIT.md"
    },
    {
      "text": "Claude Code: Queue Pending & Blocking Messages (Research & Plan)",
      "link": "/research/CLAUDE_CODE_QUEUE_PENDING_BLOCKING.md"
    },
    {
      "text": "Claude Code Plan & Delegate Modes \u2014 Deep Research for thegent Tooling",
      "link": "/research/CLAUDE_PLAN_DELEGATE_MODES_RESEARCH.md"
    },
    {
      "text": "Client-Side Software Package Design & Deployment Research",
      "link": "/research/CLIENT_SIDE_PACKAGE_DESIGN_RESEARCH.md"
    },
    {
      "text": "Codex Hooks, Notifications & Extension Options",
      "link": "/research/CODEX_HOOKS_AND_EXTENSION_OPTIONS.md"
    },
    {
      "text": "Codex + CLIProxyAPIPlus: Research and Plan",
      "link": "/research/CODEX_MINIMAX_CLIPROXY_RESEARCH_AND_PLAN.md"
    },
    {
      "text": "Comprehensive Non-Canonical Audit and Consolidation Plan",
      "link": "/research/COMPREHENSIVE_NON_CANONICAL_AUDIT.md"
    },
    {
      "text": "Conversation Dump \u2014 2026-02-16",
      "link": "/research/CONVERSATION_DUMP_2026-02-16.md"
    },
    {
      "text": "Conversation Dump Complete \u2014 2026-02-16 Structured & Expanded",
      "link": "/research/CONVERSATION_DUMP_2026-02-16_COMPLETE.md"
    },
    {
      "text": "Conversation Dump 2026-02-16 \u2014 Complete Expansion",
      "link": "/research/CONVERSATION_DUMP_2026-02-16_EXPANDED.md"
    },
    {
      "text": "Cost-Based Routing \u2014 Deferred Scope",
      "link": "/research/COST_ROUTING_DEFERRED.md"
    },
    {
      "text": "Cost Routing Deferred \u2014 Formal Decision Record",
      "link": "/research/COST_ROUTING_DEFERRED_EXPANDED.md"
    },
    {
      "text": "Cross-Platform Multi-Tenant Desktop Automation: Advanced Patterns",
      "link": "/research/CROSS_PLATFORM_ADVANCED_PATTERNS.md"
    },
    {
      "text": "Cross-Platform Extensions: Wider, Deeper, Polish & Optimization",
      "link": "/research/CROSS_PLATFORM_EXTENSIONS_WIDER_DEEPER_OPTIMIZATION.md"
    },
    {
      "text": "Cross-Platform Gaps and Extensions \u2014 Research & Plan",
      "link": "/research/CROSS_PLATFORM_GAPS_AND_EXTENSIONS_RESEARCH.md"
    },
    {
      "text": "Cross-Platform Desktop Automation: Integration Guide",
      "link": "/research/CROSS_PLATFORM_INTEGRATION_GUIDE.md"
    },
    {
      "text": "Cross-Platform Multi-Tenant Desktop Automation Research & Plan",
      "link": "/research/CROSS_PLATFORM_MULTI_TENANT_DESKTOP_AUTOMATION_RESEARCH.md"
    },
    {
      "text": "Cross-Platform Desktop Automation: Performance Benchmarks & SLAs",
      "link": "/research/CROSS_PLATFORM_PERFORMANCE_BENCHMARKS.md"
    },
    {
      "text": "Cross-Platform Research Complete \u2014 Comprehensive Consolidated Guide",
      "link": "/research/CROSS_PLATFORM_RESEARCH_COMPLETE.md"
    },
    {
      "text": "Cross-Platform Desktop Automation: Research Completion Summary",
      "link": "/research/CROSS_PLATFORM_RESEARCH_COMPLETION_SUMMARY.md"
    },
    {
      "text": "Cross-Platform Research \u2014 Consolidated Comprehensive Guide",
      "link": "/research/CROSS_PLATFORM_RESEARCH_CONSOLIDATED.md"
    },
    {
      "text": "Cross-Platform Desktop Automation: Research Index",
      "link": "/research/CROSS_PLATFORM_RESEARCH_INDEX.md"
    },
    {
      "text": "Cross-Platform Multi-Tenant Desktop Automation: Research Summary",
      "link": "/research/CROSS_PLATFORM_RESEARCH_SUMMARY.md"
    },
    {
      "text": "Cross-Platform Desktop Automation: Security Deep Dive",
      "link": "/research/CROSS_PLATFORM_SECURITY_DEEP_DIVE.md"
    },
    {
      "text": "Doctor Command: OAuth-Only Authentication Update",
      "link": "/research/DOCTOR_OAUTH_ONLY_UPDATE.md"
    },
    {
      "text": "ESLint \u2192 oxlint Migration Audit (Phase 4)",
      "link": "/research/ESLINT_AUDIT.md"
    },
    {
      "text": "Expansion Complete \u2014 Final Report",
      "link": "/research/EXPANSION_COMPLETE_FINAL.md"
    },
    {
      "text": "Expansion Phase \u2014 Complete Summary",
      "link": "/research/EXPANSION_PHASE_COMPLETE.md"
    },
    {
      "text": "FastMCP Complete \u2014 Comprehensive Implementation Guide",
      "link": "/research/FASTMCP_COMPLETE.md"
    },
    {
      "text": "FastMCP Elicitation & Context API Summary",
      "link": "/research/FASTMCP_ELICITATION_CONTEXT.md"
    },
    {
      "text": "FastMCP Features & MCP Transport Spec Gaps",
      "link": "/research/FASTMCP_FEATURES_AND_TRANSPORT_GAPS.md"
    },
    {
      "text": "FastMCP Implementation Guide for thegent",
      "link": "/research/FASTMCP_IMPLEMENTATION_GUIDE.md"
    },
    {
      "text": "FastMCP Middleware",
      "link": "/research/FASTMCP_MIDDLEWARE.md"
    },
    {
      "text": "FastMCP Progress & Tasks API Summary",
      "link": "/research/FASTMCP_PROGRESS_TASKS.md"
    },
    {
      "text": "FastMCP Sampling & Telemetry",
      "link": "/research/FASTMCP_SAMPLING_TELEMETRY.md"
    },
    {
      "text": "FastMCP Spec Deep Dive",
      "link": "/research/FASTMCP_SPEC_DEEP_DIVE.md"
    },
    {
      "text": "FastMCP Storage Backends & EventStore",
      "link": "/research/FASTMCP_STORAGE_EVENTSTORE.md"
    },
    {
      "text": "FastMCP Transforms & Deployment Summary",
      "link": "/research/FASTMCP_TRANSFORMS_DEPLOYMENT.md"
    },
    {
      "text": "Final Expansion Report \u2014 Complete",
      "link": "/research/FINAL_EXPANSION_REPORT.md"
    },
    {
      "text": "Git Shim Starship Optimization \u2014 Fix for 8+ Minute Prompt Delays",
      "link": "/research/GIT_SHIM_STARSHIP_OPTIMIZATION.md"
    },
    {
      "text": "Git Tooling Audit and Modernization Plan",
      "link": "/research/GIT_TOOLING_AUDIT_AND_PLAN.md"
    },
    {
      "text": "Governance, Policy Enforcement, and Audit Trail Research",
      "link": "/research/GOVERNANCE_POLICY_AUDIT_RESEARCH.md"
    },
    {
      "text": "Governance WP Gaps \u2014 Implementation Notes",
      "link": "/research/GOVERNANCE_WP_GAPS.md"
    },
    {
      "text": "Governance WP Gaps \u2014 Expanded & BACKLOG Items",
      "link": "/research/GOVERNANCE_WP_GAPS_EXPANDED.md"
    },
    {
      "text": "Hook Rust Migration Complete \u2014 Comprehensive Migration Strategy & Timeline",
      "link": "/research/HOOK_RUST_MIGRATION_COMPLETE.md"
    },
    {
      "text": "Hook Runtime Rust Migration: Research Synthesis",
      "link": "/research/HOOK_RUST_MIGRATION_RESEARCH_SYNTHESIS.md"
    },
    {
      "text": "Hook Runtime Rust Migration \u2014 Complete Expansion",
      "link": "/research/HOOK_RUST_MIGRATION_RESEARCH_SYNTHESIS_EXPANDED.md"
    },
    {
      "text": "Idea Seeds & Session Storage",
      "link": "/research/IDEA_SEEDS_SESSION_STORAGE.md"
    },
    {
      "text": "Idea Seed Review Complete \u2014 Consolidation & Rationale",
      "link": "/research/IDEA_SEED_REVIEW_COMPLETE.md"
    },
    {
      "text": "Index Sprawl Status Update \u2014 Complete",
      "link": "/research/INDEX_SPRAWL_STATUS_UPDATE.md"
    },
    {
      "text": "In-Depth Tooling and Global Optimizations Audit (2026-02-15)",
      "link": "/research/IN_DEPTH_TOOLING_AUDIT_2026.md"
    },
    {
      "text": "Library-First Audit and Plan",
      "link": "/research/LIBRARY_FIRST_AUDIT_AND_PLAN.md"
    },
    {
      "text": "Library Replacement Audit \u2014 Deep & Wide",
      "link": "/research/LIBRARY_REPLACEMENT_AUDIT_DEEP.md"
    },
    {
      "text": "Library Replacement Complete \u2014 Comprehensive Audit & Migration Plan",
      "link": "/research/LIBRARY_REPLACEMENT_COMPLETE.md"
    },
    {
      "text": "Library Replacement \u2014 Consolidated Migration Plan",
      "link": "/research/LIBRARY_REPLACEMENT_CONSOLIDATED.md"
    },
    {
      "text": "Library Replacement \u2014 Phase Design Work Breakdowns (DWBs)",
      "link": "/research/LIBRARY_REPLACEMENT_PHASE_DWBS.md"
    },
    {
      "text": "Master Expansion TODO \u2014 Complete Documentation Sprawl",
      "link": "/research/MASTER_EXPANSION_TODO.md"
    },
    {
      "text": "MCP Full Parity & FastMCP Transport Spec Audit",
      "link": "/research/MCP_FULL_PARITY_AND_FASTMCP_AUDIT.md"
    },
    {
      "text": "MCP and Client Features for Session Notifications",
      "link": "/research/MCP_NOTIFICATION_OPTIONS.md"
    },
    {
      "text": "MD Documentation Normalization Guide",
      "link": "/research/MD_NORMALIZATION_GUIDE.md"
    },
    {
      "text": "Memory Optimization \u2014 Long-Term Plan",
      "link": "/research/MEMORY_OPTIMIZATION_LONG_TERM_PLAN.md"
    },
    {
      "text": "Multi-Platform Agent Deep Dive",
      "link": "/research/MULTI_PLATFORM_DEEP_DIVE.md"
    },
    {
      "text": "OpenClaw / Agent Zero as Main Agent \u2014 Research",
      "link": "/research/OPENCLAW_AGENTZERO_AS_MAIN_AGENT_RESEARCH.md"
    },
    {
      "text": "OpenClaw, ClawHub, Agent Zero \u2014 Use Cases for thegent",
      "link": "/research/OPENCLAW_CLAWHUB_AGENTZERO_USE_CASES.md"
    },
    {
      "text": "Priority 1 (P1) Expansion \u2014 Complete",
      "link": "/research/P1_EXPANSION_COMPLETE.md"
    },
    {
      "text": "Priority 1 (P1) Phase \u2014 Complete",
      "link": "/research/P1_PHASE_COMPLETE.md"
    },
    {
      "text": "P3 Polish Complete \u2014 Full Research Docs",
      "link": "/research/P3_POLISH_COMPLETE.md"
    },
    {
      "text": "P4 Normalization \u2014 Complete",
      "link": "/research/P4_NORMALIZATION_COMPLETE.md"
    },
    {
      "text": "P4 Normalization \u2014 Final Status",
      "link": "/research/P4_NORMALIZATION_FINAL.md"
    },
    {
      "text": "P4 Normalization Progress \u2014 All MD Docs",
      "link": "/research/P4_NORMALIZATION_PROGRESS.md"
    },
    {
      "text": "P4 Normalization Summary \u2014 Complete",
      "link": "/research/P4_NORMALIZATION_SUMMARY.md"
    },
    {
      "text": "P4 Normalization Update \u2014 Progress Report",
      "link": "/research/P4_NORMALIZATION_UPDATE.md"
    },
    {
      "text": "Package Design Research Summary",
      "link": "/research/PACKAGE_DESIGN_RESEARCH_SUMMARY.md"
    },
    {
      "text": "Phase Documents \u2014 Complete Expansion",
      "link": "/research/PHASE_DOCUMENTS_EXPANDED.md"
    },
    {
      "text": "Plan Usage and Budget Research",
      "link": "/research/PLAN_USAGE_AND_BUDGET_RESEARCH.md"
    },
    {
      "text": "Proactive Governance Evolution Plan",
      "link": "/research/PROACTIVE_GOVERNANCE_EVOLUTION_PLAN.md"
    },
    {
      "text": "Production Packaging, Polish & Optimization Audit + Plan",
      "link": "/research/PRODUCTION_PACKAGING_POLISH_OPTIMIZATION_AUDIT_AND_PLAN.md"
    },
    {
      "text": "Python Frontmatter + Native Backmatter: Research Audit & Plan",
      "link": "/research/PYTHON_FRONTMATTER_NATIVE_BACKMATTER_AUDIT_PLAN.md"
    },
    {
      "text": "Qwen3.5 Plus 02-15 on OpenRouter \u2014 Pareto Research",
      "link": "/research/QWEN3.5_PLUS_OPENROUTER_PARETO_RESEARCH.md"
    },
    {
      "text": "Remove Directory Dependencies \u2014 Production Installation Optimization",
      "link": "/research/REMOVE_DIRECTORY_DEPENDENCIES_AUDIT_AND_PLAN.md"
    },
    {
      "text": "Research, Seed & Fragment Inventory \u2014 Sprawl Todo & Unified Work Stream",
      "link": "/research/RESEARCH_SEED_FRAGMENT_INVENTORY_AND_SPRAWL_TODO.md"
    },
    {
      "text": '"See Also" Section Template',
      "link": "/research/SEE_ALSO_TEMPLATE.md"
    },
    {
      "text": "Session Research Complete \u2014 Comprehensive Deep-Dive",
      "link": "/research/SESSION_RESEARCH_COMPLETE.md"
    },
    {
      "text": "Session Research Fragments \u2014 2026-02-15",
      "link": "/research/SESSION_RESEARCH_FRAGMENTS.md"
    },
    {
      "text": "Session Research Fragments \u2014 Complete Expansion",
      "link": "/research/SESSION_RESEARCH_FRAGMENTS_EXPANDED.md"
    },
    {
      "text": "Shell Configuration Audit and Consolidation Plan",
      "link": "/research/SHELL_CONFIG_AUDIT_AND_CONSOLIDATION_PLAN.md"
    },
    {
      "text": "Shell Error Fixes \u2014 zsh Bad Substitution",
      "link": "/research/SHELL_ERROR_FIXES.md"
    },
    {
      "text": "Smart & Robust Process Strategies \u2014 Research & Plan",
      "link": "/research/SMART_ROBUST_STRATEGIES_RESEARCH.md"
    },
    {
      "text": "Swarm Management Complete Research & Implementation Guide",
      "link": "/research/SWARM_COMPLETE.md"
    },
    {
      "text": "Swarm Optimization, Management & Scheduling \u2014 Deep Research",
      "link": "/research/SWARM_OPTIMIZATION_SCHEDULING_DEEP_RESEARCH.md"
    },
    {
      "text": "Swarm Process Automation \u2014 Deep Research & Plan",
      "link": "/research/SWARM_PROCESS_AUTOMATION_DEEP_RESEARCH.md"
    },
    {
      "text": "Swarm & Resource Optimization \u2014 Research Index",
      "link": "/research/SWARM_RESEARCH_INDEX.md"
    },
    {
      "text": "System Resources Complete Practical Guide",
      "link": "/research/SYSTEM_RESOURCES_COMPLETE.md"
    },
    {
      "text": "System Resources (FD, CPU, Threads, Ports) \u2014 Full-Depth Research & Plan",
      "link": "/research/SYSTEM_RESOURCES_FD_CPU_DEEP_RESEARCH.md"
    },
    {
      "text": "Thegent Teammates: Research and Implementation Plan (2026-02-15)",
      "link": "/research/TEAMMATES_RESEARCH_AND_PLAN.md"
    },
    {
      "text": "Tenacity vs Custom Retry \u2014 Audit & Plan",
      "link": "/research/TENACITY_RETRY_AUDIT_PLAN.md"
    },
    {
      "text": "Thegent Command Model Options and Agent Features Research",
      "link": "/research/THGENT_COMMAND_MODEL_OPTIONS_AND_AGENT_FEATURES_RESEARCH.md"
    },
    {
      "text": "TUI Compositor Comparison Research",
      "link": "/research/TUI_COMPOSITOR_COMPARISON.md"
    },
    {
      "text": "Unified Work Stream Integration \u2014 Complete",
      "link": "/research/UNIFIED_WORK_STREAM_INTEGRATION.md"
    },
    {
      "text": "User Queue + TUI: Editable Prompts While Agent Runs",
      "link": "/research/USER_QUEUE_TUI_AND_AGENT_POLL.md"
    },
    {
      "text": "VitePress Enhancements Research Report (2025-2026)",
      "link": "/research/VITEPRESS_ENHANCEMENTS.md"
    },
    {
      "text": "VitePress Phase 1 Implementation \u2014 \u2705 COMPLETE",
      "link": "/research/VITEPRESS_PHASE1_COMPLETE.md"
    },
    {
      "text": "VitePress Phase 1 Implementation \u2014 Status",
      "link": "/research/VITEPRESS_PHASE1_IMPLEMENTATION.md"
    },
    {
      "text": "VitePress Phase 2 Implementation \u2014 Status",
      "link": "/research/VITEPRESS_PHASE2_IMPLEMENTATION.md"
    },
    {
      "text": "VitePress Phase 3 Implementation \u2014 \u2705 COMPLETE",
      "link": "/research/VITEPRESS_PHASE3_COMPLETE.md"
    },
    {
      "text": "VitePress Rich Documentation Audit & Implementation Plan",
      "link": "/research/VITEPRESS_RICH_DOCUMENTATION_AUDIT.md"
    },
    {
      "text": "VitePress Rich Documentation \u2014 Implementation Plan",
      "link": "/research/VITEPRESS_RICH_DOCUMENTATION_IMPLEMENTATION_PLAN.md"
    },
    {
      "text": "Phase 13: Compliance Profile Mapping",
      "link": "/research/phase13-compliance-profile-mapping.md"
    },
    {
      "text": "Phase 13: Cost Sensitivity Experiment Plan",
      "link": "/research/phase13-cost-sensitivity-experiment-plan.md"
    },
    {
      "text": "Phase 13: Policy Federation Surface Map",
      "link": "/research/phase13-policy-federation-surface-map.md"
    },
    {
      "text": "Phase 13: Tenant Boundary Test Matrix",
      "link": "/research/phase13-tenant-boundary-test-matrix.md"
    },
    {
      "text": "Phase 14: Autonomous Learning and Cost Sensing Surface Map",
      "link": "/research/phase14-autonomous-learning-surface-map.md"
    },
    {
      "text": "Phase 14: Cost Sensing and Learning Test Matrix",
      "link": "/research/phase14-cost-sensing-test-matrix.md"
    },
    {
      "text": "Phase 15: Enterprise Compliance Test Matrix",
      "link": "/research/phase15-enterprise-compliance-test-matrix.md"
    },
    {
      "text": "Phase 15: Enterprise Lifecycle and Compliance Surface Map",
      "link": "/research/phase15-enterprise-lifecycle-surface-map.md"
    }
  ],
  "/closure/": [
    {
      "text": "DR Rehearsal Report",
      "link": "/closure/DR_REHEARSAL_REPORT.md"
    },
    {
      "text": "Governance & Compliance Bundle",
      "link": "/closure/GOVERNANCE_COMPLIANCE_BUNDLE.md"
    },
    {
      "text": "Phase 6 Readiness Report",
      "link": "/closure/PHASE6_READINESS_REPORT.md"
    },
    {
      "text": "Post-Launch 28-Day Observation Plan",
      "link": "/closure/POST_LAUNCH_28DAY_OBSERVATION.md"
    },
    {
      "text": "Rollback Reserve Plan",
      "link": "/closure/ROLLBACK_RESERVE_PLAN.md"
    },
    {
      "text": "SLO Certification Matrix",
      "link": "/closure/SLO_CERTIFICATION_MATRIX.md"
    }
  ],
  "/docset/": [
    {
      "text": "DAG Node-to-Service Contract Checklist",
      "link": "/docset/DAG_NODE_SERVICE_CONTRACT_CHECKLIST.md"
    },
    {
      "text": "DAG Node-to-Service Contract Checklist",
      "link": "/docset/DAG_NODE_TO_SERVICE_CONTRACT_CHECKLIST.md"
    },
    {
      "text": "E2E Next Chunk Plan \u2014 Full-Phase Mega Chunk",
      "link": "/docset/E2E_NEXT_CHUNK_PLAN.md"
    },
    {
      "text": "E2E Remaining Full-Depth Plan",
      "link": "/docset/E2E_REMAINING_FULL_DEPTH_PLAN.md"
    },
    {
      "text": "FastMCP 3.0 Integration Reference for Thegent",
      "link": "/docset/FASTMCP_INTEGRATION.md"
    },
    {
      "text": "Thegent Implementation Status Tracker",
      "link": "/docset/IMPLEMENTATION_STATUS.md"
    },
    {
      "text": "Thegent Optimization, Polish, and Robustness Addendum",
      "link": "/docset/OPTIMIZATION_POLISH_ADDENDUM.md"
    },
    {
      "text": "Thegent Pattern Catalog",
      "link": "/docset/PATTERNS.md"
    },
    {
      "text": "Comprehensive Test Plan Matrix",
      "link": "/docset/PRD_TEST_PLAN_MATRIX.md"
    },
    {
      "text": "Remaining Gaps \u2014 Full Depth Analysis",
      "link": "/docset/REMAINING_GAPS_DEEP_DIVE.md"
    },
    {
      "text": "Remaining Gaps \u2014 Full Depth Analysis",
      "link": "/docset/REMAINING_GAPS_FULL_DEPTH.md"
    },
    {
      "text": "Thegent Risks and Anti-Patterns Catalog",
      "link": "/docset/RISKS_AND_ANTIPATTERNS.md"
    },
    {
      "text": "WBS-to-Issue Import Matrix",
      "link": "/docset/WBS_TO_ISSUE_IMPORT_MATRIX.md"
    },
    {
      "text": "Thegent CLI Single Source of Truth Audit",
      "link": "/docset/thegent-cli-single-source-of-truth-audit-2026-02-14.md"
    },
    {
      "text": "Thegent Cross-Analysis Matrix (Deep)",
      "link": "/docset/thegent-cross-analysis-matrix-2026-02-14.md"
    },
    {
      "text": "Thegent Final DAG Specification",
      "link": "/docset/thegent-dag-final.md"
    },
    {
      "text": "Thegent DAG Extension \u2014 Phases 10 to 12",
      "link": "/docset/thegent-dag-phase10-12-extension.md"
    },
    {
      "text": "thegent DAG Extension \u2014 Phases 7, 8, 9",
      "link": "/docset/thegent-dag-phase7-9-extension.md"
    },
    {
      "text": "Thegent Gaps and Discovery Report",
      "link": "/docset/thegent-gaps-and-discovery-2026-02-14.md"
    },
    {
      "text": "Thegent Implementation Log",
      "link": "/docset/thegent-implementation-log-2026-02-14.md"
    },
    {
      "text": "Thegent Kush Docs Deep Dive (Zen + Adjacent Projects)",
      "link": "/docset/thegent-kush-docs-deep-dive-2026-02-14.md"
    },
    {
      "text": "Thegent Mega Research Synthesis",
      "link": "/docset/thegent-mega-research-synthesis-2026-02-14.md"
    },
    {
      "text": "Thegent Orchestration Optimization & Expansion PRD (Living Document)",
      "link": "/docset/thegent-orchestration-optimization-prd.md"
    },
    {
      "text": "Thegent Pattern Enhancement Synthesis",
      "link": "/docset/thegent-patterns-enhancement-synthesis.md"
    },
    {
      "text": "Thegent Phase 10\u201312 Bundle B Sprint Playbook",
      "link": "/docset/thegent-phase10-12-bundle-b-sprint-playbook.md"
    },
    {
      "text": "Thegent Phase 10\u201312 Bundle Signoff and Handoff Packages",
      "link": "/docset/thegent-phase10-12-bundle-signoff-and-handoff-packages.md"
    },
    {
      "text": "Thegent Phase 10\u201312 Closure Readiness Pack Template",
      "link": "/docset/thegent-phase10-12-closure-readiness-pack-template.md"
    },
    {
      "text": "Thegent Phase 10\u201312 Compact Execution Dashboard",
      "link": "/docset/thegent-phase10-12-compact-execution-dashboard.md"
    },
    {
      "text": "Thegent Phase 10\u201312 Drift Reconciliation Playbook",
      "link": "/docset/thegent-phase10-12-drift-reconciliation-playbook.md"
    },
    {
      "text": "Thegent Phase 10\u201312 Execution Bundles Playbook",
      "link": "/docset/thegent-phase10-12-execution-bundles-playbook.md"
    },
    {
      "text": "Thegent Phase 10\u201312 Execution Synthesis Playbook",
      "link": "/docset/thegent-phase10-12-execution-synthesis-playbook.md"
    },
    {
      "text": "Thegent Phase 10\u201312 Execution Workboard (Chunk 4)",
      "link": "/docset/thegent-phase10-12-execution-workboard.md"
    },
    {
      "text": "Thegent Phase 10\u201312 Hard-Stop, Rollback, and Stability Matrix",
      "link": "/docset/thegent-phase10-12-hard-stop-and-rollback-matrix.md"
    },
    {
      "text": "Thegent Phase 10\u201312 Implementation Chunk Plan",
      "link": "/docset/thegent-phase10-12-implementation-chunk-plan.md"
    },
    {
      "text": "Thegent Phase 10\u201312 Implementation Issue Queue",
      "link": "/docset/thegent-phase10-12-implementation-issue-queue.md"
    },
    {
      "text": "Thegent Phase 10\u201312 Implementation Ticket Templates (Chunk 3)",
      "link": "/docset/thegent-phase10-12-implementation-ticket-templates.md"
    },
    {
      "text": "Thegent Phase 10\u201312 Issue Board Automation Playbook",
      "link": "/docset/thegent-phase10-12-issue-board-automation.md"
    },
    {
      "text": "Thegent Phase 10\u201312 Issue Board Import Notes",
      "link": "/docset/thegent-phase10-12-issue-board-import-notes.md"
    },
    {
      "text": "Thegent Phase 10\u201312 Launch Schedule (Day-by-Day Execution Plan)",
      "link": "/docset/thegent-phase10-12-launch-schedule.md"
    },
    {
      "text": "Thegent Phase 10\u201312 Master Traceability Ledger",
      "link": "/docset/thegent-phase10-12-master-traceability-ledger.md"
    },
    {
      "text": "Thegent \u2014 Phase 10\u201312 PRD (Optimization-Depth and Productization Wave)",
      "link": "/docset/thegent-phase10-12-optimal-design-prd.md"
    },
    {
      "text": "Thegent Phase 10\u201312 Orchestrator Tooling Stack",
      "link": "/docset/thegent-phase10-12-orchestrator-tooling-stack.md"
    },
    {
      "text": "Thegent Phase 10\u201312 Policy-as-Code and Automation Contract",
      "link": "/docset/thegent-phase10-12-policy-as-code-and-automation-contract.md"
    },
    {
      "text": "Thegent Phase 10\u201312 PRD\u2194WBS Finalization Cross-Map",
      "link": "/docset/thegent-phase10-12-prd-wbs-crossmap-finalization.md"
    },
    {
      "text": "Thegent Phase 10\u201312 PRD-WBS-DAG-Ticket Validation Framework",
      "link": "/docset/thegent-phase10-12-prd-wbs-dag-ticket-validation.md"
    },
    {
      "text": "Thegent Phase 10\u201312 Release Readiness and Delta Pack",
      "link": "/docset/thegent-phase10-12-release-readiness-and-delta-pack.md"
    },
    {
      "text": "Thegent Phase 10\u201312 Test and Readiness Pack",
      "link": "/docset/thegent-phase10-12-test-readiness-pack.md"
    },
    {
      "text": "Thegent Phase 11 Sprint Playbook (Bundles C and D)",
      "link": "/docset/thegent-phase11-control-and-adaptation-sprint-playbook.md"
    },
    {
      "text": "Thegent Phase 12 Sprint Playbook (Bundles E and F)",
      "link": "/docset/thegent-phase12-explainability-and-closure-sprint-playbook.md"
    },
    {
      "text": "Thegent Phase 13+ Extension Boundary Proposal",
      "link": "/docset/thegent-phase13-plus-extension-proposal.md"
    },
    {
      "text": "Thegent Phase 3\u20136 Closure Acceptance Contract Schema",
      "link": "/docset/thegent-phase3-6-closure-acceptance-contract-schema.md"
    },
    {
      "text": "Thegent Phase 3\u20136 Closure Acceptance Pack Template",
      "link": "/docset/thegent-phase3-6-closure-acceptance-pack-template.md"
    },
    {
      "text": "Thegent Phase 3\u20136 Closure Validator Automation Package",
      "link": "/docset/thegent-phase3-6-closure-validator-automation-package.md"
    },
    {
      "text": "Thegent Phase 3\u20136 Closure Validation Event and Waiver Contract v1",
      "link": "/docset/thegent-phase3-6-closure-validator-event-and-waiver-contract-v1.md"
    },
    {
      "text": "Thegent Phase 3\u20136 Closure Validator Fault Injection and Chaos Tests",
      "link": "/docset/thegent-phase3-6-closure-validator-fault-injection-and-chaos-tests.md"
    },
    {
      "text": "Thegent Phase 3\u20136 Closure Validator Implementation Blueprint",
      "link": "/docset/thegent-phase3-6-closure-validator-implementation-blueprint.md"
    },
    {
      "text": "Thegent Phase 3\u20136 Closure Validator Python Implementation Blueprint",
      "link": "/docset/thegent-phase3-6-closure-validator-python-implementation-blueprint.md"
    },
    {
      "text": "Thegent Phase 3-6 Closure Validator Runtime CLI and Adapter Playbook",
      "link": "/docset/thegent-phase3-6-closure-validator-runtime-cli-and-adapter-playbook.md"
    },
    {
      "text": "Thegent Phase 3\u20136 Cross-Wave Bridge and Continuity Plan",
      "link": "/docset/thegent-phase3-6-crosswave-bridge-and-continuity-plan.md"
    },
    {
      "text": "Thegent \u2014 Phase 3\u20136 Full-Depth Execution Chunk",
      "link": "/docset/thegent-phase3-6-full-depth-execution-prd.md"
    },
    {
      "text": "Thegent Phase 7\u20139 Next-Wave PRD (Post-Closure Optimization)",
      "link": "/docset/thegent-phase7-9-next-wave-prd.md"
    },
    {
      "text": "Thegent Phase 7\u20139 Test and Readiness Pack",
      "link": "/docset/thegent-phase7-9-test-readiness-pack.md"
    },
    {
      "text": "Thegent Orchestration Final Plan Index",
      "link": "/docset/thegent-plan-final-index.md"
    },
    {
      "text": "Thegent Production Orchestration PRD (Final)",
      "link": "/docset/thegent-prd-final.md"
    },
    {
      "text": "Thegent Research Validation Addendum (Zen + Task Tools)",
      "link": "/docset/thegent-research-validation-2026-02-14.md"
    },
    {
      "text": "thegent Third-Party Bundle Manifest",
      "link": "/docset/thegent-third-party-bundle-manifest.md"
    },
    {
      "text": "Thegent Final WBS (Comprehensive)",
      "link": "/docset/thegent-wbs-final.md"
    },
    {
      "text": "Thegent WBS \u2014 Phase 10 to Phase 12 (Optimization-Depth and Productization)",
      "link": "/docset/thegent-wbs-phase10-12.md"
    },
    {
      "text": "Thegent WBS \u2014 Phase 7 to Phase 9 (Next-Wave Execution)",
      "link": "/docset/thegent-wbs-phase7-9.md"
    }
  ],
  "/enterprise/": [
    {
      "text": "Decommissioning and Sunset Plan",
      "link": "/enterprise/DECOMMISSIONING_PLAN.md"
    },
    {
      "text": "Program Operating Model and Ownership Map",
      "link": "/enterprise/OPERATING_MODEL.md"
    },
    {
      "text": "Security and Compliance Signoff Package",
      "link": "/enterprise/SECURITY_COMPLIANCE_SIGNOFF.md"
    }
  ],
  "/plans/": [
    {
      "text": "Thegent Unified Plan \u2014 Master Index",
      "link": "/plans/00-MASTER-INDEX.md"
    },
    {
      "text": "01 \u2014 Project State",
      "link": "/plans/01-PROJECT-STATE.md"
    },
    {
      "text": "02 \u2014 Unified Work Breakdown Structure",
      "link": "/plans/02-UNIFIED-WBS.md"
    },
    {
      "text": "03 \u2014 Unified DAG Specifications",
      "link": "/plans/03-UNIFIED-DAG.md"
    },
    {
      "text": "04 \u2014 Unified Requirements",
      "link": "/plans/04-REQUIREMENTS.md"
    },
    {
      "text": "05 \u2014 Architecture & Patterns",
      "link": "/plans/05-ARCHITECTURE.md"
    },
    {
      "text": "06 \u2014 Implementation Guide",
      "link": "/plans/06-IMPLEMENTATION-GUIDE.md"
    },
    {
      "text": "07 \u2014 Test Strategy",
      "link": "/plans/07-TEST-STRATEGY.md"
    },
    {
      "text": "08 \u2014 Optimization, Polish, Enhancement & Robustness Catalog",
      "link": "/plans/08-OPTIMIZATION-CATALOG.md"
    },
    {
      "text": "09 \u2014 Risk Registry & Anti-Patterns",
      "link": "/plans/09-RISK-REGISTRY.md"
    },
    {
      "text": "10 \u2014 Subagent Dispatch Plan",
      "link": "/plans/10-SUBAGENT-DISPATCH.md"
    },
    {
      "text": "12 \u2014 Cycleloop Loops & Checker Agent Design",
      "link": "/plans/12-LIFECYCLE-LOOP-DESIGN.md"
    },
    {
      "text": "Design: thegent install CLI Command",
      "link": "/plans/2026-02-14-thegent-install-design.md"
    },
    {
      "text": "thegent install Implementation Plan",
      "link": "/plans/2026-02-14-thegent-install-implementation-plan.md"
    },
    {
      "text": "Research and Elicitation Plan \u2014 2026-02-15",
      "link": "/plans/2026-02-15-RESEARCH-AND-ELICITATION-PLAN.md"
    },
    {
      "text": "thegent sitback \u2014 Design & Implementation Plan",
      "link": "/plans/2026-02-15-thegent-sitback-design.md"
    },
    {
      "text": "Tray Application Design - Plugin-Based Architecture",
      "link": "/plans/2026-02-15-tray-application-design.md"
    },
    {
      "text": "AgentDeployer + LifecycleController Integration Review",
      "link": "/plans/2026-02-16-AGENT_DEPLOYER_REVIEW.md"
    },
    {
      "text": "Cycleloop + AgilePlus Integration Plan",
      "link": "/plans/2026-02-16-CYCLELOOP_AGILEPLUS_INTEGRATION.md"
    },
    {
      "text": "Full LiteLLM Feature Integration Plan",
      "link": "/plans/2026-02-16-litellm-full-features-plan.md"
    },
    {
      "text": "LiteLLM Integration Design",
      "link": "/plans/2026-02-16-litellm-integration-design.md"
    },
    {
      "text": "LiteLLM Router Integration Implementation Plan",
      "link": "/plans/2026-02-16-litellm-integration-plan.md"
    },
    {
      "text": "Supermemory.ai Integration Plan (WP-5001-SM)",
      "link": "/plans/2026-02-16-supermemory-integration-plan.md"
    },
    {
      "text": "Agent Sandboxing Implementation Plan",
      "link": "/plans/AGENT_SANDBOXING_IMPLEMENTATION_PLAN.md"
    },
    {
      "text": "Catalog \u2194 CLIProxyAPIPlus Fork Alignment",
      "link": "/plans/CATALOG_CLIPROXY_FORK_ALIGNMENT.md"
    },
    {
      "text": "CLIProxyAPI & Thegent Work Plan \u2013 Unified Phased WBS",
      "link": "/plans/CLIPROXY_API_AND_THGENT_UNIFIED_PLAN.md"
    },
    {
      "text": "Agent Orchestration Harness: Multi-Platform (Extreme-Depth Plan)",
      "link": "/plans/CODEX_DONUT_HARNESS_PLAN.md"
    },
    {
      "text": "Cross-Platform Multi-Tenant Desktop Automation Complete Plan",
      "link": "/plans/CROSS_PLATFORM_COMPLETE_PLAN.md"
    },
    {
      "text": "Cross-Platform Multi-Tenant Desktop Automation Implementation Plan",
      "link": "/plans/CROSS_PLATFORM_MULTI_TENANT_IMPLEMENTATION_PLAN.md"
    },
    {
      "text": "Cursor API Integration Research & Plan",
      "link": "/plans/CURSOR_API_INTEGRATION_RESEARCH.md"
    },
    {
      "text": "Debug Tags and Metrics (Transient Response Tags)",
      "link": "/plans/DEBUG_TAGS_AND_METRICS.md"
    },
    {
      "text": "Distributed Model Routing Plan",
      "link": "/plans/DISTRIBUTED_MODEL_ROUTING_PLAN.md"
    },
    {
      "text": "Documentation Expansion Process",
      "link": "/plans/DOCUMENTATION_EXPANSION_PROCESS.md"
    },
    {
      "text": "Documentation Expansion TODO",
      "link": "/plans/DOCUMENTATION_EXPANSION_TODO.md"
    },
    {
      "text": "Documentation Consolidation & Implementation WBS",
      "link": "/plans/DOC_CONSOLIDATION_AND_IMPLEMENTATION_WBS.md"
    },
    {
      "text": "Factory Droid Harness Integration Plan",
      "link": "/plans/FACTORY_DROID_HARNESS_INTEGRATION_PLAN.md"
    },
    {
      "text": "Full Shell \u2192 Rust Where Beneficial",
      "link": "/plans/FULL_SHELL_TO_RUST_WHERE_BENEFICIAL.md"
    },
    {
      "text": "Holistic + Harmonious Design & Full Integration Plan",
      "link": "/plans/HOLISTIC_HARMONIOUS_DESIGN_AND_INTEGRATION_PLAN.md"
    },
    {
      "text": "Hook Runtime Rust Migration Complete Guide",
      "link": "/plans/HOOK_RUNTIME_RUST_COMPLETE.md"
    },
    {
      "text": "Hook Runtime: Full Rust Migration Design (Deep & Wide)",
      "link": "/plans/HOOK_RUNTIME_RUST_DESIGN.md"
    },
    {
      "text": "Hybrid Mac/Windows Environment Implementation Plan",
      "link": "/plans/HYBRID_ENV_IMPLEMENTATION_PLAN.md"
    },
    {
      "text": "LiteLLM + CLIProxyAPIPlus + Bifrost Harmony",
      "link": "/plans/LITELLM_CLIPROXY_BIFROST_HARMONY.md"
    },
    {
      "text": "MCP Bundle: thegent + Browser Tools (Replace Manual Playwright)",
      "link": "/plans/MCP_BUNDLE_PLAYWRIGHT_REPLACEMENT.md"
    },
    {
      "text": "MCP Tool Optimization, Polish & Enhancement Plan",
      "link": "/plans/MCP_TOOL_OPTIMIZATION_PLAN.md"
    },
    {
      "text": "Multi-Platform Parity Master Plan & Matrix",
      "link": "/plans/MULTI_PLATFORM_PARITY_MASTER_PLAN.md"
    },
    {
      "text": "New Providers Auth Research & Plan",
      "link": "/plans/NEW_PROVIDERS_AUTH_RESEARCH.md"
    },
    {
      "text": "OpenRouter-Style Routing + CLIProxyAPIPlus Integration",
      "link": "/plans/OPENROUTER_STYLE_ROUTING_AND_CLIPROXY.md"
    },
    {
      "text": "Process & Tool Optimization Complete Plan",
      "link": "/plans/PROCESS_OPTIMIZATION_COMPLETE_PLAN.md"
    },
    {
      "text": "Process and Tool Optimization Plan",
      "link": "/plans/PROCESS_OPTIMIZATION_PLAN.md"
    },
    {
      "text": "Prompt History Collection & Audit System: Comprehensive Plan",
      "link": "/plans/PROMPT_HISTORY_COLLECTION_AND_AUDIT_SYSTEM.md"
    },
    {
      "text": "Prompt History Collection & Audit System Complete Guide",
      "link": "/plans/PROMPT_HISTORY_COLLECTION_COMPLETE.md"
    },
    {
      "text": "Remote Compute Implementation Detail",
      "link": "/plans/REMOTE_COMPUTE_IMPLEMENTATION_DETAIL.md"
    },
    {
      "text": "thegent Setup: Proposed Hooks, Plugins, Skills, MCP & Docs",
      "link": "/plans/SETUP_PROPOSED_ITEMS.md"
    },
    {
      "text": "Shell Environment Advanced Enhancement Plan",
      "link": "/plans/SHELL_ENVIRONMENT_ADVANCED_ENHANCEMENT_PLAN.md"
    },
    {
      "text": "Shell Environment Advanced Enhancement - Implementation Summary",
      "link": "/plans/SHELL_ENVIRONMENT_ADVANCED_IMPLEMENTATION_SUMMARY.md"
    },
    {
      "text": "Shell Environment Complete Plan",
      "link": "/plans/SHELL_ENVIRONMENT_COMPLETE_PLAN.md"
    },
    {
      "text": "Shell Environment Implementation Summary",
      "link": "/plans/SHELL_ENVIRONMENT_IMPLEMENTATION_SUMMARY.md"
    },
    {
      "text": "Shell Environment Optimization & Enhancement Plan",
      "link": "/plans/SHELL_ENVIRONMENT_OPTIMIZATION_PLAN.md"
    },
    {
      "text": "Sync/Update Command & Full System Audit Plan",
      "link": "/plans/SYNC_UPDATE_COMMAND_AND_SYSTEM_AUDIT_PLAN.md"
    },
    {
      "text": "Thegent FastMCP 3.0 Implementation Plan",
      "link": "/plans/THGENT_FASTMCP_IMPLEMENTATION_PLAN.md"
    },
    {
      "text": "Runtime Dispatch Consolidation & Fork Fix: Complete",
      "link": "/plans/ULTRA_SHIM_CONSOLIDATION_COMPLETE.md"
    },
    {
      "text": "Ultra-Shim Fork Failure Fix: Root Cause Analysis & Solution",
      "link": "/plans/ULTRA_SHIM_FORK_FAILURE_FIX.md"
    },
    {
      "text": "Unified Login Flow: Open URL + Prompt for Key",
      "link": "/plans/UNIFIED_LOGIN_FLOW.md"
    },
    {
      "text": "Unified System Application Plan",
      "link": "/plans/UNIFIED_SYSTEM_APPLICATION_PLAN.md"
    }
  ],
  "/changes/": [
    {
      "text": "Hexagonal Migration",
      "collapsed": false,
      "items": [
        {
          "text": "Hexagonal Architecture Migration -- thegent",
          "link": "/hexagonal-migration/proposal.md"
        }
      ]
    }
  ],
  "/checklists/": [
    {
      "text": "Hybrid Mac/Windows Environment Setup Checklist",
      "link": "/checklists/HYBRID_ENV_SETUP_CHECKLIST.md"
    }
  ],
  "/contracts/": [
    {
      "text": "Contract Authority",
      "link": "/contracts/CONTRACT_AUTHORITY.md"
    },
    {
      "text": "Fallback Control Plane",
      "link": "/contracts/FALLBACK_POLICY.md"
    },
    {
      "text": "Provider Adapter Contracts (G-RV-05)",
      "link": "/contracts/PROVIDER_ADAPTER_CONTRACTS.md"
    },
    {
      "text": "Contract Upgrade Playbook",
      "link": "/contracts/UPGRADE_PLAYBOOK.md"
    }
  ],
  "/scratchpad/": [
    {
      "text": "Session Scratch Board & Optimization Plan",
      "link": "/scratchpad/session_review.md"
    }
  ],
  "/architecture/": [
    {
      "text": "Agent Sandboxing Architecture: WASM/Containers/VMs (No Docker)",
      "link": "/architecture/AGENT_SANDBOXING_ARCHITECTURE.md"
    },
    {
      "text": "Python Frontmatter + Native Backmatter Architecture",
      "link": "/architecture/FRONTMATTER_BACKMATTER_ARCHITECTURE.md"
    },
    {
      "text": "Hybrid Mac/Windows Development Environment Architecture",
      "link": "/architecture/HYBRID_MAC_WIN_DEV_ENVIRONMENT.md"
    }
  ],
  "/guides/": [
    {
      "text": "Agent Debugging and Remediation Guide",
      "link": "/guides/AGENT_DEBUGGING_AND_REMEDIATION_GUIDE.md"
    },
    {
      "text": "Agent Instructions: thegent Deep-Dive",
      "link": "/guides/AGENT_INSTRUCTIONS_THEGENT.md"
    },
    {
      "text": "Automated Documentation Demos",
      "link": "/guides/AUTOMATED_DEMOS.md"
    },
    {
      "text": "BKM Implementation Guides",
      "link": "/guides/BKM_IMPLEMENTATION_GUIDES.md"
    },
    {
      "text": "Cross-Platform Desktop Automation \u2014 Complete Guide",
      "link": "/guides/CROSS_PLATFORM_COMPLETE.md"
    },
    {
      "text": "Cross-Platform Desktop Automation: Developer Cookbook",
      "link": "/guides/CROSS_PLATFORM_DEVELOPER_COOKBOOK.md"
    },
    {
      "text": "Cross-Platform Desktop Automation: Implementation Templates",
      "link": "/guides/CROSS_PLATFORM_IMPLEMENTATION_TEMPLATES.md"
    },
    {
      "text": "Cross-Platform Desktop Automation: Migration Guide",
      "link": "/guides/CROSS_PLATFORM_MIGRATION_GUIDE.md"
    },
    {
      "text": "Cross-Platform Desktop Automation: Quick Start Guide",
      "link": "/guides/CROSS_PLATFORM_QUICK_START.md"
    },
    {
      "text": "Cross-Platform Desktop Automation: Implementation Roadmap",
      "link": "/guides/CROSS_PLATFORM_ROADMAP.md"
    },
    {
      "text": "Doctor Command Fixes",
      "link": "/guides/DOCTOR_FIXES.md"
    },
    {
      "text": "Fix Shell Corruption Issue",
      "link": "/guides/FIX_SHELL_CORRUPTION.md"
    },
    {
      "text": "Fix Shell Fork Errors: Quick Guide",
      "link": "/guides/FIX_SHELL_FORK_ERRORS.md"
    },
    {
      "text": "Guides Index",
      "link": "/guides/GUIDES_INDEX.md"
    },
    {
      "text": "Hybrid Mac/Windows Environment Quick Start Guide",
      "link": "/guides/HYBRID_ENV_QUICK_START.md"
    },
    {
      "text": "Implementation Patterns Guide",
      "link": "/guides/IMPLEMENTATION_PATTERNS.md"
    },
    {
      "text": "Job Pool System - Usage Guide",
      "link": "/guides/JOB_POOL_USAGE.md"
    },
    {
      "text": "OAuth-Only Authentication Policy",
      "link": "/guides/OAUTH_ONLY_AUTHENTICATION.md"
    },
    {
      "text": "Operational Learning Assets (WP-12008)",
      "link": "/guides/OPERATIONAL_LEARNING.md"
    },
    {
      "text": "oxlint Integration Guide (Phase 4)",
      "link": "/guides/OXLINT_INTEGRATION_GUIDE.md"
    },
    {
      "text": "Thegent Phase 10 Summary and Migration Guide (WP-10010)",
      "link": "/guides/PHASE_10_GUIDE.md"
    },
    {
      "text": "Thegent Phase 11 Summary and Evidence Pack (WP-11010)",
      "link": "/guides/PHASE_11_GUIDE.md"
    },
    {
      "text": "Phase 4 Quick Start: ESLint \u2192 oxlint Migration",
      "link": "/guides/PHASE_4_QUICK_START.md"
    },
    {
      "text": "Thegent Phase 7-9 Summary and Training Guide (WP-9010)",
      "link": "/guides/PHASE_7_9_GUIDE.md"
    },
    {
      "text": "Prompts Tooling \u2014 Cursor / Codex / Claude Aggregate",
      "link": "/guides/PROMPTS_TOOLING.md"
    },
    {
      "text": "Provider Setup Guide",
      "link": "/guides/PROVIDER_SETUP_GUIDE.md"
    },
    {
      "text": "Quality Assurance Guide",
      "link": "/guides/QUALITY_ASSURANCE.md"
    },
    {
      "text": "Quick Fix: Shell Setup Issues",
      "link": "/guides/QUICK_FIX_SHELL_SETUP.md"
    },
    {
      "text": "Runtime Optimization Guide",
      "link": "/guides/RUNTIME_OPTIMIZATION.md"
    },
    {
      "text": "Shell Advanced Features Guide",
      "link": "/guides/SHELL_ADVANCED_FEATURES.md"
    },
    {
      "text": "Shell Corruption Fix - Complete Solution",
      "link": "/guides/SHELL_CORRUPTION_FIX_COMPLETE.md"
    },
    {
      "text": "Complete Shell Environment System",
      "link": "/guides/SHELL_ENVIRONMENT_COMPLETE.md"
    },
    {
      "text": "Shell Environment Management",
      "link": "/guides/SHELL_ENVIRONMENT_MANAGEMENT.md"
    },
    {
      "text": "Shell Optimization Guide",
      "link": "/guides/SHELL_OPTIMIZATION_GUIDE.md"
    },
    {
      "text": "Shell & Zsh Plugin Setup \u2014 Long-Term Fix",
      "link": "/guides/SHELL_ZSH_PLUGIN_SETUP.md"
    },
    {
      "text": "Sitback Plugin API",
      "link": "/guides/SITBACK_PLUGINS.md"
    },
    {
      "text": "Starship + direnv Setup Complete",
      "link": "/guides/STARSHIP_DIRENV_SETUP.md"
    },
    {
      "text": "\u{1F680} Hooks Optimization Initiative - START HERE",
      "link": "/guides/START_HERE.md"
    },
    {
      "text": "Task Routing Quick Reference Guide",
      "link": "/guides/TASK_ROUTING_QUICK_REF.md"
    },
    {
      "text": "thegent Testing Guide",
      "link": "/guides/TESTING.md"
    },
    {
      "text": "Troubleshooting Guide",
      "link": "/guides/TROUBLESHOOTING.md"
    },
    {
      "text": "VitePress Docsite Setup",
      "link": "/guides/VITEPPRESS_SETUP.md"
    },
    {
      "text": "Anti-Pattern Detection Guide",
      "link": "/guides/anti-patterns.md"
    },
    {
      "text": "Architecture Enforcement Guide",
      "link": "/guides/architecture-enforcement.md"
    },
    {
      "text": "Guides",
      "link": "/guides/index.md"
    }
  ],
  "/governance/": [
    {
      "text": "Cost Governance Design (G-GP-06)",
      "link": "/governance/COST_GOVERNANCE_DESIGN.md"
    },
    {
      "text": "HITL (Human-in-the-Loop) Design (G-GP-05)",
      "link": "/governance/HITL_DESIGN.md"
    },
    {
      "text": "NeMo Guardrails Design (G-GP-02)",
      "link": "/governance/NEMO_GUARDRAILS_DESIGN.md"
    },
    {
      "text": "OPA Integration Design (G-GP-01)",
      "link": "/governance/OPA_INTEGRATION_DESIGN.md"
    },
    {
      "text": "Retention Policy Design (G-GP-07)",
      "link": "/governance/RETENTION_POLICY_DESIGN.md"
    },
    {
      "text": "Sandboxing Design (G-GP-08)",
      "link": "/governance/SANDBOXING_DESIGN.md"
    }
  ],
  "/migration/": [
    {
      "text": "Advanced Performance Patterns & Best Practices",
      "link": "/migration/ADVANCED_PATTERNS.md"
    },
    {
      "text": "Complete Solution: Polished, Optimized, Production-Ready",
      "link": "/migration/COMPLETE_SOLUTION.md"
    },
    {
      "text": "Comprehensive Benchmarking Strategy",
      "link": "/migration/COMPREHENSIVE_BENCHMARKING.md"
    },
    {
      "text": "Comprehensive Performance Analysis & Migration Strategy",
      "link": "/migration/COMPREHENSIVE_PERFORMANCE_ANALYSIS.md"
    },
    {
      "text": "Design Principles",
      "link": "/migration/DESIGN_PRINCIPLES.md"
    },
    {
      "text": "Usage Examples",
      "link": "/migration/EXAMPLES.md"
    },
    {
      "text": "Fork Failure (EAGAIN) Analysis & Solutions",
      "link": "/migration/FORK_FAILURE_ANALYSIS.md"
    },
    {
      "text": "Comprehensive Implementation Roadmap",
      "link": "/migration/IMPLEMENTATION_ROADMAP.md"
    },
    {
      "text": "Production Readiness Checklist",
      "link": "/migration/PRODUCTION_READINESS.md"
    },
    {
      "text": "Quick Start Guide",
      "link": "/migration/QUICK_START.md"
    },
    {
      "text": "Shell to Rust/Go Migration Plan",
      "link": "/migration/RUST_GO_MIGRATION_PLAN.md"
    },
    {
      "text": "Performance Optimization Summary",
      "link": "/migration/SUMMARY.md"
    },
    {
      "text": "The Ultimate Guide: Comprehensive Performance Optimization & Migration",
      "link": "/migration/ULTIMATE_GUIDE.md"
    },
    {
      "text": "User Guide: thegent Performance Optimizations",
      "link": "/migration/USER_GUIDE.md"
    }
  ],
  "/demos/": [
    {
      "text": "Demo Scripts for VitePress Documentation",
      "link": "/demos/README.md"
    }
  ],
  "/reference/": [
    {
      "text": "Routing System: Project Complete Summary",
      "link": "/reference/00_ROUTING_PROJECT_COMPLETE.md"
    },
    {
      "text": "Agent Identity & Sovereignty Depth (WP-6004)",
      "link": "/reference/AGENT_IDENTITY_SOVEREIGNTY_DEPTH.md"
    },
    {
      "text": "Agent Communication Language (JSON-ACL) & Negotiation (WP-1006)",
      "link": "/reference/AGENT_NEGOTIATION_ACL_DEPTH.md"
    },
    {
      "text": "Agent OS Principals \u2014 Depth Document",
      "link": "/reference/AGENT_OS_PRINCIPALS_DEPTH.md"
    },
    {
      "text": "Benchmark Comparison: SWE-Bench vs Terminal Bench 2.0",
      "link": "/reference/BENCHMARK_COMPARISON_SWE_BENCH_VS_TERMINAL_BENCH_2_0.md"
    },
    {
      "text": "Global Claude Code Instructions",
      "link": "/reference/CLAUDE_CORE_GUIDELINES.md"
    },
    {
      "text": "CLAUDE Appendix: thegent-specific and domain workflow rules",
      "link": "/reference/CLAUDE_THEGENT_RUNTIME_APPENDIX.md"
    },
    {
      "text": "Complete Provider Routing Map (All 12+ Providers)",
      "link": "/reference/COMPLETE_PROVIDER_ROUTING_MAP.md"
    },
    {
      "text": "Constitutional Enforcement & Proof of Alignment (WP-3001)",
      "link": "/reference/CONSTITUTIONAL_ENFORCEMENT_DEPTH.md"
    },
    {
      "text": "Context Management & Semantic Compression Depth (WP-5001)",
      "link": "/reference/CONTEXT_MANAGEMENT_DEPTH.md"
    },
    {
      "text": "Cost Enforcement Policy: 2x Limit & Escalation Framework",
      "link": "/reference/COST_ENFORCEMENT_POLICY.md"
    },
    {
      "text": "Cross-Platform Desktop Automation: API Reference",
      "link": "/reference/CROSS_PLATFORM_API_REFERENCE.md"
    },
    {
      "text": "Cross-Platform Multi-Tenant Desktop Automation Quick Reference",
      "link": "/reference/CROSS_PLATFORM_MULTI_TENANT_QUICK_REFERENCE.md"
    },
    {
      "text": "Dominance Proof Reference",
      "link": "/reference/DOMINANCE_PROOF_REFERENCE.md"
    },
    {
      "text": "Economic Governance & Token ROI Modeling (WP-5003)",
      "link": "/reference/ECONOMIC_GOVERNANCE_DEPTH.md"
    },
    {
      "text": "Frontmatter/Backmatter Integration Points",
      "link": "/reference/FRONTMATTER_BACKMATTER_INTEGRATION_POINTS.md"
    },
    {
      "text": "FR Tracker: thegent",
      "link": "/reference/FR_TRACKER.md"
    },
    {
      "text": "Gardener Architecture",
      "link": "/reference/GARDENER_ARCHITECTURE.md"
    },
    {
      "text": "Human-Agent Collaboration (HAC) & HITL Patterns (WP-4001..4009)",
      "link": "/reference/HAC_AND_HITL_PATTERNS.md"
    },
    {
      "text": "Hook Optimization Strategy",
      "link": "/reference/HOOK_OPTIMIZATION_STRATEGY.md"
    },
    {
      "text": "Hybrid Mac/Windows Development Environment - Summary",
      "link": "/reference/HYBRID_ENV_SUMMARY.md"
    },
    {
      "text": "Indexing and Optimization Systems \u2014 Reference",
      "link": "/reference/INDEXING_AND_OPTIMIZATION_SYSTEMS.md"
    },
    {
      "text": "TaskRouter + Pareto Routing Integration Architecture",
      "link": "/reference/INTEGRATION_ARCHITECTURE.md"
    },
    {
      "text": "TaskRouter + Pareto Routing Integration \u2014 Document Index",
      "link": "/reference/INTEGRATION_INDEX.md"
    },
    {
      "text": "TaskRouter Integration Quick Start",
      "link": "/reference/INTEGRATION_QUICK_START.md"
    },
    {
      "text": "MAIF Artifact Specification & Provenance Depth (WP-3002)",
      "link": "/reference/MAIF_ARTIFACT_SPEC_DEPTH.md"
    },
    {
      "text": "MCP Tool Retry Policy",
      "link": "/reference/MCP_RETRY_POLICY.md"
    },
    {
      "text": "Corrected Model Ranking Using Pareto Frontier",
      "link": "/reference/MODEL_RANKING_CORRECTED.md"
    },
    {
      "text": "Model Routing Decision Tree",
      "link": "/reference/MODEL_ROUTING_DECISION_TREE.md"
    },
    {
      "text": "Model Routing & Cost Governance: Complete Index",
      "link": "/reference/MODEL_ROUTING_INDEX.md"
    },
    {
      "text": "Model Routing & Cost Governance: Quick Reference",
      "link": "/reference/MODEL_ROUTING_SUMMARY.md"
    },
    {
      "text": "Model Routing: Terminal Bench 2.0 Quick Reference",
      "link": "/reference/MODEL_ROUTING_TERMINAL_BENCH_2_0_QUICK_REF.md"
    },
    {
      "text": "Model Selection Documentation Index",
      "link": "/reference/MODEL_SELECTION_INDEX.md"
    },
    {
      "text": "Monitoring Alert Rules",
      "link": "/reference/MONITORING_ALERT_RULES.md"
    },
    {
      "text": "Monitoring Dashboard Specifications",
      "link": "/reference/MONITORING_DASHBOARD_SPEC.md"
    },
    {
      "text": "Monitoring Metrics Reference",
      "link": "/reference/MONITORING_METRICS_REFERENCE.md"
    },
    {
      "text": "Monitoring System Documentation",
      "link": "/reference/MONITORING_README.md"
    },
    {
      "text": "Monitoring Setup Guide",
      "link": "/reference/MONITORING_SETUP_GUIDE.md"
    },
    {
      "text": "Civilizational Multi-Swarm Hierarchy (WP-1006, WP-5004)",
      "link": "/reference/MULTI_SWARM_HIERARCHY_DEPTH.md"
    },
    {
      "text": "OpenTelemetry GenAI & Observability Depth (WP-Y6)",
      "link": "/reference/OTEL_GENAI_AND_HYSTERESIS_DEPTH.md"
    },
    {
      "text": "oxlint Rule Mapping Reference",
      "link": "/reference/OXLINT_RULE_MAPPING.md"
    },
    {
      "text": "Pareto Frontier Algorithm: Pseudocode & Implementation Guide",
      "link": "/reference/PARETO_ALGORITHM_PSEUDOCODE.md"
    },
    {
      "text": "Pareto Frontier: Executive Summary",
      "link": "/reference/PARETO_EXECUTIVE_SUMMARY.md"
    },
    {
      "text": "Pareto Frontier Analysis & Model Ranking Algorithm",
      "link": "/reference/PARETO_FRONTIER_ANALYSIS.md"
    },
    {
      "text": "Pareto Frontier Analysis: Complete Model Evaluation",
      "link": "/reference/PARETO_FRONTIER_COMPLETE_ANALYSIS.md"
    },
    {
      "text": "Pareto Frontier Matrix: Model Selection Guide",
      "link": "/reference/PARETO_FRONTIER_MATRIX.md"
    },
    {
      "text": "Pareto Frontier Quick Reference",
      "link": "/reference/PARETO_FRONTIER_QUICK_REFERENCE.md"
    },
    {
      "text": "Pareto Frontier Analysis: Complete Data Table",
      "link": "/reference/PARETO_FRONTIER_TABLE.md"
    },
    {
      "text": "Pareto Frontier Analysis: Terminal Bench 2.0 (Corrected)",
      "link": "/reference/PARETO_FRONTIER_TERMINAL_BENCH_2_0.md"
    },
    {
      "text": "Pareto Frontier Analysis: Complete Index",
      "link": "/reference/PARETO_INDEX.md"
    },
    {
      "text": "Multi-Objective Provider Routing & Pareto Fronts (WP-1004)",
      "link": "/reference/PARETO_ROUTING_DESIGN.md"
    },
    {
      "text": "Pareto Frontier Visualization & Diagrams",
      "link": "/reference/PARETO_VISUALIZATION.md"
    },
    {
      "text": "Phase 3.5 Quick Reference",
      "link": "/reference/PHASE_3_5_QUICK_REFERENCE.md"
    },
    {
      "text": "Phase 4 UX: Operator Cockpit & Rationale Depth (WP-4001)",
      "link": "/reference/PHASE_4_COCKPIT_UX_DEPTH.md"
    },
    {
      "text": "Phase 5 Scale: Redis & Distributed Robustness (WP-5004)",
      "link": "/reference/PHASE_5_SCALE_ROBUSTNESS_DEPTH.md"
    },
    {
      "text": "POSIX + pwsh Shell Strategy",
      "link": "/reference/POSIX_PWSH_SHELL_STRATEGY.md"
    },
    {
      "text": "Provider Limits and Auto-Fallback",
      "link": "/reference/PROVIDER_LIMITS_AND_FALLBACK.md"
    },
    {
      "text": "Provider Model Behavior Constraints",
      "link": "/reference/PROVIDER_MODEL_BEHAVIOR.md"
    },
    {
      "text": "Provider Model Reference",
      "link": "/reference/PROVIDER_MODEL_REFERENCE.md"
    },
    {
      "text": "Robustness, Breadth, and Depth \u2014 Phase Evolution",
      "link": "/reference/ROBUSTNESS_AND_FUTURE_DEPTH.md"
    },
    {
      "text": "Routing Decision Matrix: Task Category Logic",
      "link": "/reference/ROUTING_DECISION_MATRIX.md"
    },
    {
      "text": "Final Routing Recommendation (Terminal Bench 2.0)",
      "link": "/reference/ROUTING_FINAL_RECOMMENDATION.md"
    },
    {
      "text": "Task Routing Implementation Architecture",
      "link": "/reference/ROUTING_IMPLEMENTATION_ARCHITECTURE.md"
    },
    {
      "text": "Model Routing Quick Card (Pocket Reference)",
      "link": "/reference/ROUTING_QUICK_CARD.md"
    },
    {
      "text": "Routing System: Master Summary & Implementation Roadmap",
      "link": "/reference/ROUTING_SYSTEM_MASTER_SUMMARY.md"
    },
    {
      "text": "Rust-Based CLI Tooling",
      "link": "/reference/RUST_TOOLING.md"
    },
    {
      "text": "Agentic CI/CD & Self-Healing Loops (WP-2004)",
      "link": "/reference/SELF_HEALING_AGENTIC_CICD_DEPTH.md"
    },
    {
      "text": "Planning Simulation & Replay Sandbox Depth (WP-4007, WP-12004)",
      "link": "/reference/SIMULATION_AND_SANDBOX_DEPTH.md"
    },
    {
      "text": "MCP Tool SLO Targets (G-OP-08)",
      "link": "/reference/SLO_TARGETS.md"
    },
    {
      "text": "Speed & Quality Index Implementation Plan",
      "link": "/reference/SPEED_QUALITY_INDEX_IMPLEMENTATION_PLAN.md"
    },
    {
      "text": "Starship Prompt \u2014 Long-Term Fix for Scan Timeout",
      "link": "/reference/STARSHIP_SETUP.md"
    },
    {
      "text": "Swarm Memory & Multi-Agent Coordination (WP-1006)",
      "link": "/reference/SWARM_MEMORY_COORDINATION_DEPTH.md"
    },
    {
      "text": "Swarm Process Optimizations (Multi-Agent / Multi-Tenant / Multi-Project)",
      "link": "/reference/SWARM_PROCESS_OPTIMIZATIONS.md"
    },
    {
      "text": "Task Categorization & AI Agent Dispatch Routing Design",
      "link": "/reference/TASK_ROUTING_DESIGN.md"
    },
    {
      "text": "Terminal Bench 2.0: Corrected Pareto Frontier & Routing",
      "link": "/reference/TERMINAL_BENCH_2_0_CORRECTED_FRONTIER.md"
    },
    {
      "text": "Tooling & Global Optimizations Audit (In-Depth)",
      "link": "/reference/TOOLING_AND_GLOBAL_OPTIMIZATIONS_AUDIT.md"
    },
    {
      "text": "Tooling and Global Optimizations Audit",
      "link": "/reference/TOOLING_AND_OPTIMIZATION_AUDIT.md"
    },
    {
      "text": "Touchpoint Integration \u2014 Deep Dive",
      "link": "/reference/TOUCHPOINT_INTEGRATION_DEEP_DIVE.md"
    },
    {
      "text": "Touchpoint Integration Evaluation",
      "link": "/reference/TOUCHPOINT_INTEGRATION_EVALUATION.md"
    },
    {
      "text": "Unified Work Stream \u2014 Design",
      "link": "/reference/UNIFIED_WORK_STREAM_DESIGN.md"
    },
    {
      "text": "WBS Agent Progress \u2014 Claim & Coordination",
      "link": "/reference/WBS_AGENT_PROGRESS.md"
    },
    {
      "text": "Unified Work Stream \u2014 Canonical",
      "link": "/reference/WORK_STREAM.md"
    },
    {
      "text": "Zen (OpenCode) Integration Analysis",
      "link": "/reference/ZEN_INTEGRATION.md"
    },
    {
      "text": "Reference",
      "link": "/reference/index.md"
    }
  ],
  "/reports/": [
    {
      "text": "BKM Phase 1 Completion Report",
      "link": "/reports/BKM_PHASE_1_COMPLETION_REPORT.md"
    },
    {
      "text": "Critical Issue #2: Git Cache Invalidation Fix - Complete Report",
      "link": "/reports/CACHE_INVALIDATION_FIX_REPORT.md"
    },
    {
      "text": "Critical Issues Fixes - Completion Report",
      "link": "/reports/CRITICAL_FIXES_COMPLETION_REPORT.md"
    },
    {
      "text": "Critical Issue #2: Unsafe Git Cache Invalidation - Executive Summary",
      "link": "/reports/CRITICAL_ISSUE_2_SUMMARY.md"
    },
    {
      "text": "Phase 10-12 Closure and Final Handoff Note (WP-12010)",
      "link": "/reports/FINAL_CLOSURE_NOTE.md"
    },
    {
      "text": "Holistic + Harmonious Design & Integration \u2014 Implementation Complete \u2705",
      "link": "/reports/HOLISTIC_DESIGN_IMPLEMENTATION_COMPLETE.md"
    },
    {
      "text": "Holistic + Harmonious Design & Integration \u2014 Implementation Progress",
      "link": "/reports/HOLISTIC_DESIGN_IMPLEMENTATION_PROGRESS.md"
    },
    {
      "text": "Thegent Implementation Status Report",
      "link": "/reports/IMPLEMENTATION_STATUS.md"
    },
    {
      "text": "Thegent Implementation Summary",
      "link": "/reports/IMPLEMENTATION_SUMMARY.md"
    },
    {
      "text": "P7.1 Verification Report: Per-Project Quality Gate Checks",
      "link": "/reports/P7.1_VERIFICATION_REPORT.md"
    },
    {
      "text": "P7.2 Cross-Project Consistency Report",
      "link": "/reports/P7.2_CROSS_PROJECT_CONSISTENCY.md"
    },
    {
      "text": "Phase 10-12 Closure and Handoff Note (WP-12010)",
      "link": "/reports/PHASE_10_12_CLOSURE.md"
    },
    {
      "text": "Phase 13: Policy Federation Progress Report",
      "link": "/reports/PHASE_13_PROGRESS_REPORT.md"
    },
    {
      "text": "Phase 14: Autonomous Learning and Cost Sensing Progress Report",
      "link": "/reports/PHASE_14_PROGRESS_REPORT.md"
    },
    {
      "text": "Phase 15: Enterprise Lifecycle and Compliance Progress Report",
      "link": "/reports/PHASE_15_PROGRESS_REPORT.md"
    },
    {
      "text": "Phase 3.5 Optimization Summary",
      "link": "/reports/PHASE_3_5_SUMMARY.md"
    },
    {
      "text": "Phase 3.5 Optimization Validation Report",
      "link": "/reports/PHASE_3_5_VALIDATION.md"
    },
    {
      "text": "Phase 3: Job Pool Implementation - Completion Summary",
      "link": "/reports/PHASE_3_COMPLETION_SUMMARY.md"
    },
    {
      "text": "Phase 3 - Job Pool Implementation Report",
      "link": "/reports/PHASE_3_JOB_POOL_IMPLEMENTATION.md"
    },
    {
      "text": "Phase 4: Advanced Bash Optimizations Report",
      "link": "/reports/PHASE_4_ADVANCED_OPTIMIZATIONS.md"
    },
    {
      "text": "Phase 4 Implementation Summary: ESLint \u2192 oxlint Migration",
      "link": "/reports/PHASE_4_IMPLEMENTATION_SUMMARY.md"
    },
    {
      "text": "Phase 4: Advanced Bash Optimizations - Implementation Summary",
      "link": "/reports/PHASE_4_SUMMARY.md"
    },
    {
      "text": "\u{1F3C1} Project Completion Report: thegent",
      "link": "/reports/PROJECT_COMPLETION_REPORT.md"
    }
  ]
};

// docs/.vitepress/config.ts
import { createRequire } from "module";
var __vite_injected_original_import_meta_url = "file:///Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/docs/.vitepress/config.ts";
var require2 = createRequire(__vite_injected_original_import_meta_url);
var markdownItKatex = require2("markdown-it-katex");
var markdownItEmoji = require2("markdown-it-emoji").full;
var config = defineConfig({
  title: "thegent",
  description: "AI Agent Governance & MCP Server",
  appearance: true,
  lastUpdated: true,
  // Exclude problematic directories from the build
  srcExclude: [
    "docset/**",
    "plans/**",
    "research/**"
  ],
  // Disable dead link check (links are external or cross-project)
  ignoreDeadLinks: true,
  vite: {
    plugins: [
      OramaPlugin({
        // Orama search plugin configuration
        // Automatically indexes all markdown content
        // Supports full-text search with typo tolerance
        // OSS, self-hosted, no external services required
      }),
      imagetools({
        // Image optimization: WebP/AVIF conversion, lazy loading
        // Usage: ![Image](./image.jpg?format=webp&w=800)
        defaultDirectives: (url) => {
          if (url.searchParams.has("format")) {
            return new URLSearchParams({
              format: url.searchParams.get("format") || "webp"
            });
          }
          return new URLSearchParams();
        }
      })
    ],
    build: {
      rollupOptions: {
        output: {
          manualChunks: (id) => {
            if (id.includes("node_modules")) {
              if (id.includes("mermaid")) {
                return "mermaid";
              }
              if (id.includes("vue")) {
                return "vue";
              }
              if (id.includes("@orama")) {
                return "orama";
              }
              if (id.includes("markdown-it")) {
                return "markdown";
              }
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
      md.use(videoEmbedPlugin, {
        controls: true,
        width: "100%"
      });
      md.use(markdownItKatex, {
        throwOnError: false,
        errorColor: "#cc0000"
      });
      md.use(markdownItEmoji, {
        shortcuts: {},
        defs: {}
      });
    },
    // Enable line numbers for code blocks
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
        text: "Architecture",
        link: "/ARCHITECTURE_LAYERS.md",
        activeMatch: "/architecture/"
      },
      {
        text: "Guides",
        link: "/guides/",
        activeMatch: "/guides/"
      },
      {
        text: "Reference",
        link: "/reference/",
        activeMatch: "/reference/"
      }
    ],
    sidebar,
    socialLinks: [],
    search: {
      provider: "orama",
      options: {
        // Orama search configuration
        // Indexes all markdown content automatically
        // Supports full-text, vector, and hybrid search
      }
    },
    outline: "deep",
    editLink: {
      pattern: "https://github.com/kooshapari/temp-PRODVERCEL/485/kush/thegent/edit/main/docs/:path",
      text: "Edit this page on GitHub"
    }
  },
  build: {
    outDir: "../docs-dist",
    assetsDir: "assets"
  },
  // Mermaid configuration
  mermaid: {
    theme: "base",
    themeVariables: {
      primaryColor: "#42b883",
      background: "var(--vp-c-bg)",
      primaryTextColor: "var(--vp-c-text-1)",
      primaryBorderColor: "var(--vp-c-divider)",
      lineColor: "var(--vp-c-text-2)",
      secondaryColor: "var(--vp-c-brand-light)",
      tertiaryColor: "var(--vp-c-bg-soft)"
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
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsiZG9jcy8udml0ZXByZXNzL2NvbmZpZy50cyIsICJkb2NzLy52aXRlcHJlc3MvcGx1Z2lucy9jcm9zcy1wcm9qZWN0LWxpbmtzLnRzIiwgImRvY3MvLnZpdGVwcmVzcy9wbHVnaW5zL3ZpZGVvLWVtYmVkLnRzIiwgImRvY3MvLnZpdGVwcmVzcy9zaWRlYmFyLnRzIl0sCiAgInNvdXJjZXNDb250ZW50IjogWyJjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZGlybmFtZSA9IFwiL1VzZXJzL2tvb3NoYXBhcmkvdGVtcC1QUk9EVkVSQ0VMLzQ4NS9rdXNoL3RoZWdlbnQvZG9jcy8udml0ZXByZXNzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCIvVXNlcnMva29vc2hhcGFyaS90ZW1wLVBST0RWRVJDRUwvNDg1L2t1c2gvdGhlZ2VudC9kb2NzLy52aXRlcHJlc3MvY29uZmlnLnRzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ltcG9ydF9tZXRhX3VybCA9IFwiZmlsZTovLy9Vc2Vycy9rb29zaGFwYXJpL3RlbXAtUFJPRFZFUkNFTC80ODUva3VzaC90aGVnZW50L2RvY3MvLnZpdGVwcmVzcy9jb25maWcudHNcIjtpbXBvcnQgeyBkZWZpbmVDb25maWcgfSBmcm9tICd2aXRlcHJlc3MnXG5pbXBvcnQgeyB3aXRoTWVybWFpZCB9IGZyb20gJ3ZpdGVwcmVzcy1wbHVnaW4tbWVybWFpZCdcbmltcG9ydCB7IE9yYW1hUGx1Z2luIH0gZnJvbSAnQG9yYW1hL3BsdWdpbi12aXRlcHJlc3MnXG5pbXBvcnQgeyBpbWFnZXRvb2xzIH0gZnJvbSAndml0ZS1pbWFnZXRvb2xzJ1xuaW1wb3J0IHsgY3Jvc3NQcm9qZWN0TGlua3MgfSBmcm9tICcuL3BsdWdpbnMvY3Jvc3MtcHJvamVjdC1saW5rcydcbmltcG9ydCB7IGNvbnRlbnRUYWJzUGx1Z2luIH0gZnJvbSAnLi9wbHVnaW5zL2NvbnRlbnQtdGFicydcbmltcG9ydCB7IHZpZGVvRW1iZWRQbHVnaW4gfSBmcm9tICcuL3BsdWdpbnMvdmlkZW8tZW1iZWQnXG5pbXBvcnQgeyBzaWRlYmFyIH0gZnJvbSAnLi9zaWRlYmFyJ1xuaW1wb3J0IHsgY3JlYXRlUmVxdWlyZSB9IGZyb20gJ21vZHVsZSdcblxuY29uc3QgcmVxdWlyZSA9IGNyZWF0ZVJlcXVpcmUoaW1wb3J0Lm1ldGEudXJsKVxuY29uc3QgbWFya2Rvd25JdEthdGV4ID0gcmVxdWlyZSgnbWFya2Rvd24taXQta2F0ZXgnKVxuY29uc3QgbWFya2Rvd25JdEVtb2ppID0gcmVxdWlyZSgnbWFya2Rvd24taXQtZW1vamknKS5mdWxsXG5cbmNvbnN0IGNvbmZpZyA9IGRlZmluZUNvbmZpZyh7XG4gIHRpdGxlOiAndGhlZ2VudCcsXG4gIGRlc2NyaXB0aW9uOiAnQUkgQWdlbnQgR292ZXJuYW5jZSAmIE1DUCBTZXJ2ZXInLFxuICBhcHBlYXJhbmNlOiB0cnVlLFxuICBsYXN0VXBkYXRlZDogdHJ1ZSxcblxuICAvLyBFeGNsdWRlIHByb2JsZW1hdGljIGRpcmVjdG9yaWVzIGZyb20gdGhlIGJ1aWxkXG4gIHNyY0V4Y2x1ZGU6IFtcbiAgICAnZG9jc2V0LyoqJyxcbiAgICAncGxhbnMvKionLFxuICAgICdyZXNlYXJjaC8qKicsXG4gIF0sXG5cbiAgLy8gRGlzYWJsZSBkZWFkIGxpbmsgY2hlY2sgKGxpbmtzIGFyZSBleHRlcm5hbCBvciBjcm9zcy1wcm9qZWN0KVxuICBpZ25vcmVEZWFkTGlua3M6IHRydWUsXG5cbiAgdml0ZToge1xuICAgIHBsdWdpbnM6IFtcbiAgICAgIE9yYW1hUGx1Z2luKHtcbiAgICAgICAgLy8gT3JhbWEgc2VhcmNoIHBsdWdpbiBjb25maWd1cmF0aW9uXG4gICAgICAgIC8vIEF1dG9tYXRpY2FsbHkgaW5kZXhlcyBhbGwgbWFya2Rvd24gY29udGVudFxuICAgICAgICAvLyBTdXBwb3J0cyBmdWxsLXRleHQgc2VhcmNoIHdpdGggdHlwbyB0b2xlcmFuY2VcbiAgICAgICAgLy8gT1NTLCBzZWxmLWhvc3RlZCwgbm8gZXh0ZXJuYWwgc2VydmljZXMgcmVxdWlyZWRcbiAgICAgIH0pLFxuICAgICAgaW1hZ2V0b29scyh7XG4gICAgICAgIC8vIEltYWdlIG9wdGltaXphdGlvbjogV2ViUC9BVklGIGNvbnZlcnNpb24sIGxhenkgbG9hZGluZ1xuICAgICAgICAvLyBVc2FnZTogIVtJbWFnZV0oLi9pbWFnZS5qcGc/Zm9ybWF0PXdlYnAmdz04MDApXG4gICAgICAgIGRlZmF1bHREaXJlY3RpdmVzOiAodXJsKSA9PiB7XG4gICAgICAgICAgaWYgKHVybC5zZWFyY2hQYXJhbXMuaGFzKCdmb3JtYXQnKSkge1xuICAgICAgICAgICAgcmV0dXJuIG5ldyBVUkxTZWFyY2hQYXJhbXMoe1xuICAgICAgICAgICAgICBmb3JtYXQ6IHVybC5zZWFyY2hQYXJhbXMuZ2V0KCdmb3JtYXQnKSB8fCAnd2VicCcsXG4gICAgICAgICAgICB9KVxuICAgICAgICAgIH1cbiAgICAgICAgICByZXR1cm4gbmV3IFVSTFNlYXJjaFBhcmFtcygpXG4gICAgICAgIH1cbiAgICAgIH0pXG4gICAgXSxcbiAgICBidWlsZDoge1xuICAgICAgcm9sbHVwT3B0aW9uczoge1xuICAgICAgICBvdXRwdXQ6IHtcbiAgICAgICAgICBtYW51YWxDaHVua3M6IChpZCkgPT4ge1xuICAgICAgICAgICAgLy8gT3B0aW1pemUgY29kZSBzcGxpdHRpbmcgZm9yIGZhc3RlciBsb2Fkc1xuICAgICAgICAgICAgaWYgKGlkLmluY2x1ZGVzKCdub2RlX21vZHVsZXMnKSkge1xuICAgICAgICAgICAgICAvLyBTcGxpdCBsYXJnZSB2ZW5kb3IgY2h1bmtzXG4gICAgICAgICAgICAgIGlmIChpZC5pbmNsdWRlcygnbWVybWFpZCcpKSB7XG4gICAgICAgICAgICAgICAgcmV0dXJuICdtZXJtYWlkJ1xuICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgIGlmIChpZC5pbmNsdWRlcygndnVlJykpIHtcbiAgICAgICAgICAgICAgICByZXR1cm4gJ3Z1ZSdcbiAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICBpZiAoaWQuaW5jbHVkZXMoJ0BvcmFtYScpKSB7XG4gICAgICAgICAgICAgICAgcmV0dXJuICdvcmFtYSdcbiAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICBpZiAoaWQuaW5jbHVkZXMoJ21hcmtkb3duLWl0JykpIHtcbiAgICAgICAgICAgICAgICByZXR1cm4gJ21hcmtkb3duJ1xuICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgIHJldHVybiAndmVuZG9yJ1xuICAgICAgICAgICAgfVxuICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgICAgfVxuICAgIH1cbiAgfSxcblxuICBtYXJrZG93bjoge1xuICAgIGNvbmZpZzogKG1kKSA9PiB7XG4gICAgICBtZC51c2UoY3Jvc3NQcm9qZWN0TGlua3MpXG4gICAgICAvLyBtZC51c2UoY29udGVudFRhYnNQbHVnaW4pXG4gICAgICBtZC51c2UodmlkZW9FbWJlZFBsdWdpbiwge1xuICAgICAgICBjb250cm9sczogdHJ1ZSxcbiAgICAgICAgd2lkdGg6ICcxMDAlJyxcbiAgICAgIH0pXG5cbiAgICAgIC8vIE1hdGggc3VwcG9ydCAoS2FUZVgpXG4gICAgICBtZC51c2UobWFya2Rvd25JdEthdGV4LCB7XG4gICAgICAgIHRocm93T25FcnJvcjogZmFsc2UsXG4gICAgICAgIGVycm9yQ29sb3I6ICcjY2MwMDAwJ1xuICAgICAgfSlcblxuICAgICAgLy8gRW1vamkgc3VwcG9ydFxuICAgICAgbWQudXNlKG1hcmtkb3duSXRFbW9qaSwge1xuICAgICAgICBzaG9ydGN1dHM6IHt9LFxuICAgICAgICBkZWZzOiB7fVxuICAgICAgfSlcbiAgICB9LFxuICAgIC8vIEVuYWJsZSBsaW5lIG51bWJlcnMgZm9yIGNvZGUgYmxvY2tzXG4gICAgbGluZU51bWJlcnM6IHRydWUsXG4gICAgLy8gRW5hYmxlIGNvZGUgaGlnaGxpZ2h0aW5nXG4gICAgdGhlbWU6IHtcbiAgICAgIGxpZ2h0OiAnZ2l0aHViLWxpZ2h0JyxcbiAgICAgIGRhcms6ICdnaXRodWItZGFyaydcbiAgICB9XG4gIH0sXG5cbiAgdGhlbWVDb25maWc6IHtcbiAgICBuYXY6IFtcbiAgICAgIHsgdGV4dDogJ0hvbWUnLCBsaW5rOiAnLycgfSxcbiAgICAgIHsgXG4gICAgICAgIHRleHQ6ICdBcmNoaXRlY3R1cmUnLCBcbiAgICAgICAgbGluazogJy9BUkNISVRFQ1RVUkVfTEFZRVJTLm1kJyxcbiAgICAgICAgYWN0aXZlTWF0Y2g6ICcvYXJjaGl0ZWN0dXJlLydcbiAgICAgIH0sXG4gICAgICB7IFxuICAgICAgICB0ZXh0OiAnR3VpZGVzJywgXG4gICAgICAgIGxpbms6ICcvZ3VpZGVzLycsXG4gICAgICAgIGFjdGl2ZU1hdGNoOiAnL2d1aWRlcy8nXG4gICAgICB9LFxuICAgICAgeyBcbiAgICAgICAgdGV4dDogJ1JlZmVyZW5jZScsIFxuICAgICAgICBsaW5rOiAnL3JlZmVyZW5jZS8nLFxuICAgICAgICBhY3RpdmVNYXRjaDogJy9yZWZlcmVuY2UvJ1xuICAgICAgfSxcbiAgICBdLFxuXG4gICAgc2lkZWJhcjogc2lkZWJhcixcblxuICAgIHNvY2lhbExpbmtzOiBbXSxcbiAgICBzZWFyY2g6IHtcbiAgICAgIHByb3ZpZGVyOiAnb3JhbWEnLFxuICAgICAgb3B0aW9uczoge1xuICAgICAgICAvLyBPcmFtYSBzZWFyY2ggY29uZmlndXJhdGlvblxuICAgICAgICAvLyBJbmRleGVzIGFsbCBtYXJrZG93biBjb250ZW50IGF1dG9tYXRpY2FsbHlcbiAgICAgICAgLy8gU3VwcG9ydHMgZnVsbC10ZXh0LCB2ZWN0b3IsIGFuZCBoeWJyaWQgc2VhcmNoXG4gICAgICB9XG4gICAgfSxcbiAgICBvdXRsaW5lOiAnZGVlcCcsXG5cbiAgICBlZGl0TGluazoge1xuICAgICAgcGF0dGVybjogJ2h0dHBzOi8vZ2l0aHViLmNvbS9rb29zaGFwYXJpL3RlbXAtUFJPRFZFUkNFTC80ODUva3VzaC90aGVnZW50L2VkaXQvbWFpbi9kb2NzLzpwYXRoJyxcbiAgICAgIHRleHQ6ICdFZGl0IHRoaXMgcGFnZSBvbiBHaXRIdWInXG4gICAgfSxcbiAgfSxcblxuICBidWlsZDoge1xuICAgIG91dERpcjogJy4uL2RvY3MtZGlzdCcsXG4gICAgYXNzZXRzRGlyOiAnYXNzZXRzJyxcbiAgfSxcblxuICAvLyBNZXJtYWlkIGNvbmZpZ3VyYXRpb25cbiAgbWVybWFpZDoge1xuICAgIHRoZW1lOiAnYmFzZScsXG4gICAgdGhlbWVWYXJpYWJsZXM6IHtcbiAgICAgIHByaW1hcnlDb2xvcjogJyM0MmI4ODMnLFxuICAgICAgYmFja2dyb3VuZDogJ3ZhcigtLXZwLWMtYmcpJyxcbiAgICAgIHByaW1hcnlUZXh0Q29sb3I6ICd2YXIoLS12cC1jLXRleHQtMSknLFxuICAgICAgcHJpbWFyeUJvcmRlckNvbG9yOiAndmFyKC0tdnAtYy1kaXZpZGVyKScsXG4gICAgICBsaW5lQ29sb3I6ICd2YXIoLS12cC1jLXRleHQtMiknLFxuICAgICAgc2Vjb25kYXJ5Q29sb3I6ICd2YXIoLS12cC1jLWJyYW5kLWxpZ2h0KScsXG4gICAgICB0ZXJ0aWFyeUNvbG9yOiAndmFyKC0tdnAtYy1iZy1zb2Z0KScsXG4gICAgfSxcbiAgICBmbG93Y2hhcnQ6IHtcbiAgICAgIHVzZU1heFdpZHRoOiB0cnVlLFxuICAgICAgaHRtbExhYmVsczogdHJ1ZSxcbiAgICB9LFxuICAgIHNlcXVlbmNlOiB7XG4gICAgICB1c2VNYXhXaWR0aDogdHJ1ZSxcbiAgICB9LFxuICAgIGdhbnR0OiB7XG4gICAgICB1c2VNYXhXaWR0aDogdHJ1ZSxcbiAgICB9LFxuICB9LFxuXG59KVxuXG5leHBvcnQgZGVmYXVsdCB3aXRoTWVybWFpZChjb25maWcpXG4iLCAiY29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2Rpcm5hbWUgPSBcIi9Vc2Vycy9rb29zaGFwYXJpL3RlbXAtUFJPRFZFUkNFTC80ODUva3VzaC90aGVnZW50L2RvY3MvLnZpdGVwcmVzcy9wbHVnaW5zXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCIvVXNlcnMva29vc2hhcGFyaS90ZW1wLVBST0RWRVJDRUwvNDg1L2t1c2gvdGhlZ2VudC9kb2NzLy52aXRlcHJlc3MvcGx1Z2lucy9jcm9zcy1wcm9qZWN0LWxpbmtzLnRzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ltcG9ydF9tZXRhX3VybCA9IFwiZmlsZTovLy9Vc2Vycy9rb29zaGFwYXJpL3RlbXAtUFJPRFZFUkNFTC80ODUva3VzaC90aGVnZW50L2RvY3MvLnZpdGVwcmVzcy9wbHVnaW5zL2Nyb3NzLXByb2plY3QtbGlua3MudHNcIjtpbXBvcnQgdHlwZSBNYXJrZG93bkl0IGZyb20gJ21hcmtkb3duLWl0J1xuaW1wb3J0IHR5cGUgeyBSZW5kZXJSdWxlIH0gZnJvbSAndml0ZXByZXNzJ1xuXG4vLyBNYXAgcHJvamVjdCBuYW1lcyB0byB0aGVpciBkb2NzLWRpc3QgcGF0aHNcbmNvbnN0IFBST0pFQ1RfUEFUSFM6IFJlY29yZDxzdHJpbmcsIHN0cmluZz4gPSB7XG4gICd0aGVnZW50JzogJy9Vc2Vycy9rb29zaGFwYXJpL3RlbXAtUFJPRFZFUkNFTC80ODUva3VzaC90aGVnZW50L2RvY3MtZGlzdC9tYWluJyxcbiAgJ2pvYmh1bnRlcic6ICcvVXNlcnMva29vc2hhcGFyaS9EZXYvam9iLWh1bnRlci9kb2NzLWRpc3QnLFxuICAnaGVsaW9zU2hpZWxkJzogJy9Vc2Vycy9rb29zaGFwYXJpL3RlbXAtUFJPRFZFUkNFTC00ODUva3VzaC9oZWxpb3NTaGllbGQvZG9jcy1kaXN0JyxcbiAgJ3RyYWNlJzogJy9Vc2Vycy9rb29zaGFwYXJpL2t1c2gvdHJhY2UvZG9jcy1kaXN0Jyxcbn1cblxuZXhwb3J0IGZ1bmN0aW9uIGNyb3NzUHJvamVjdExpbmtzKG1kOiBNYXJrZG93bkl0KSB7XG4gIGNvbnN0IGRlZmF1bHRSZW5kZXI6IFJlbmRlclJ1bGUgPSBtZC5yZW5kZXJlci5ydWxlcy5saW5rX29wZW4gfHwgZnVuY3Rpb24odG9rZW5zLCBpZHgsIG9wdGlvbnMsIF9lbnYsIHNlbGYpIHtcbiAgICByZXR1cm4gc2VsZi5yZW5kZXJUb2tlbih0b2tlbnMsIGlkeCwgb3B0aW9ucylcbiAgfVxuXG4gIG1kLnJlbmRlcmVyLnJ1bGVzLmxpbmtfb3BlbiA9IGZ1bmN0aW9uKHRva2VucywgaWR4LCBvcHRpb25zLCBlbnYsIHNlbGYpIHtcbiAgICBjb25zdCBocmVmID0gdG9rZW5zW2lkeF0uYXR0ckdldCgnaHJlZicpXG5cbiAgICAvLyBDaGVjayBmb3IgfnByb2plY3Q6L3BhdGggcGF0dGVyblxuICAgIGlmIChocmVmICYmIGhyZWYuc3RhcnRzV2l0aCgnficpKSB7XG4gICAgICBjb25zdCBtYXRjaCA9IGhyZWYubWF0Y2goL15+KFteOl0rKTooLispJC8pXG4gICAgICBpZiAobWF0Y2gpIHtcbiAgICAgICAgY29uc3QgWywgcHJvamVjdCwgcGF0aF0gPSBtYXRjaFxuICAgICAgICBjb25zdCBiYXNlUGF0aCA9IFBST0pFQ1RfUEFUSFNbcHJvamVjdF1cblxuICAgICAgICBpZiAoYmFzZVBhdGgpIHtcbiAgICAgICAgICAvLyBDb252ZXJ0IG1hcmtkb3duIHBhdGggdG8gSFRNTCBwYXRoXG4gICAgICAgICAgY29uc3QgaHRtbFBhdGggPSBwYXRoXG4gICAgICAgICAgICAucmVwbGFjZSgvXFwubWQkLywgJy5odG1sJylcbiAgICAgICAgICAgIC5yZXBsYWNlKC9eXFwvKy8sICcnKVxuXG4gICAgICAgICAgdG9rZW5zW2lkeF0uYXR0clNldCgnaHJlZicsIGBmaWxlOi8vJHtiYXNlUGF0aH0vJHtodG1sUGF0aH1gKVxuICAgICAgICAgIHRva2Vuc1tpZHhdLmF0dHJTZXQoJ3RhcmdldCcsICdfYmxhbmsnKVxuICAgICAgICAgIHRva2Vuc1tpZHhdLmF0dHJTZXQoJ2NsYXNzJywgJ2Nyb3NzLXByb2plY3QtbGluaycpXG4gICAgICAgIH1cbiAgICAgIH1cbiAgICB9XG5cbiAgICByZXR1cm4gZGVmYXVsdFJlbmRlcih0b2tlbnMsIGlkeCwgb3B0aW9ucywgZW52LCBzZWxmKVxuICB9XG59XG4iLCAiY29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2Rpcm5hbWUgPSBcIi9Vc2Vycy9rb29zaGFwYXJpL3RlbXAtUFJPRFZFUkNFTC80ODUva3VzaC90aGVnZW50L2RvY3MvLnZpdGVwcmVzcy9wbHVnaW5zXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCIvVXNlcnMva29vc2hhcGFyaS90ZW1wLVBST0RWRVJDRUwvNDg1L2t1c2gvdGhlZ2VudC9kb2NzLy52aXRlcHJlc3MvcGx1Z2lucy92aWRlby1lbWJlZC50c1wiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9pbXBvcnRfbWV0YV91cmwgPSBcImZpbGU6Ly8vVXNlcnMva29vc2hhcGFyaS90ZW1wLVBST0RWRVJDRUwvNDg1L2t1c2gvdGhlZ2VudC9kb2NzLy52aXRlcHJlc3MvcGx1Z2lucy92aWRlby1lbWJlZC50c1wiOy8qKlxuICogVmlkZW8gZW1iZWQgcGx1Z2luIGZvciBWaXRlUHJlc3MgbWFya2Rvd24uXG4gKlxuICogQWxsb3dzIGVtYmVkZGluZyByZWNvcmRlZCBQbGF5d3JpZ2h0IHZpZGVvcyBpbiBkb2N1bWVudGF0aW9uIHVzaW5nOlxuICogICAhW0FsdCB0ZXh0XSgvcGF0aC90by92aWRlby53ZWJtKVxuICogICBvciBjdXN0b20gc3ludGF4OlxuICogICA8dmlkZW8gd2lkdGg9XCIxMDAlXCIgY29udHJvbHM+XG4gKiAgICAgPHNvdXJjZSBzcmM9XCIvcmVjb3JkaW5ncy9kZW1vLndlYm1cIiB0eXBlPVwidmlkZW8vd2VibVwiPlxuICogICA8L3ZpZGVvPlxuICpcbiAqIFN1cHBvcnRzIHdlYm0sIG1wNCwgYW5kIG90aGVyIEhUTUw1IHZpZGVvIGZvcm1hdHMuXG4gKi9cblxuaW1wb3J0IHR5cGUgeyBNYXJrZG93bkl0IH0gZnJvbSAnbWFya2Rvd24taXQnXG5cbmludGVyZmFjZSBWaWRlb0VtYmVkT3B0aW9ucyB7XG4gIHdpZHRoPzogc3RyaW5nXG4gIGhlaWdodD86IHN0cmluZ1xuICBjb250cm9scz86IGJvb2xlYW5cbiAgYXV0b3BsYXk/OiBib29sZWFuXG4gIGxvb3A/OiBib29sZWFuXG4gIG11dGVkPzogYm9vbGVhblxufVxuXG4vKipcbiAqIFBhcnNlIHZpZGVvIGVtYmVkIGRpcmVjdGl2ZSBzeW50YXguXG4gKiBFeGFtcGxlOiA6OjogdmlkZW8gL3BhdGgvdG8vdmlkZW8ud2VibSA6OjpcbiAqL1xuZnVuY3Rpb24gcGFyc2VWaWRlb0RpcmVjdGl2ZShcbiAgbWQ6IE1hcmtkb3duSXQsXG4gIF9vcHRpb25zOiBWaWRlb0VtYmVkT3B0aW9uc1xuKTogdm9pZCB7XG4gIGNvbnN0IHZpZGVvQmxvY2tSdWxlID0gKHN0YXRlOiBhbnksIHN0YXJ0TGluZTogbnVtYmVyLCBlbmRMaW5lOiBudW1iZXIpID0+IHtcbiAgICBjb25zdCBwb3MgPSBzdGF0ZS5iTWFya3Nbc3RhcnRMaW5lXSArIHN0YXRlLnRTaGlmdFtzdGFydExpbmVdXG4gICAgY29uc3QgbWF4aW11bSA9IHN0YXRlLmVNYXJrc1tzdGFydExpbmVdXG5cbiAgICAvLyBDaGVjayBmb3IgOjo6IHZpZGVvIHN5bnRheFxuICAgIGlmIChwb3MgKyAzID4gbWF4aW11bSkgcmV0dXJuIGZhbHNlXG4gICAgaWYgKHN0YXRlLnNyYy5zbGljZShwb3MsIHBvcyArIDMpICE9PSAnOjo6JykgcmV0dXJuIGZhbHNlXG5cbiAgICBjb25zdCBtYXJrZXJDb3VudCA9IDNcbiAgICBjb25zdCBtYXJrdXAgPSBzdGF0ZS5zcmMuc2xpY2UocG9zLCBwb3MgKyBtYXJrZXJDb3VudClcbiAgICBjb25zdCBwYXJhbXMgPSBzdGF0ZS5zcmMuc2xpY2UocG9zICsgbWFya2VyQ291bnQsIG1heGltdW0pLnRyaW0oKVxuXG4gICAgaWYgKCFwYXJhbXMuc3RhcnRzV2l0aCgndmlkZW8gJykpIHJldHVybiBmYWxzZVxuXG4gICAgY29uc3QgdmlkZW9TcmMgPSBwYXJhbXMuc2xpY2UoNikudHJpbSgpXG4gICAgaWYgKCF2aWRlb1NyYykgcmV0dXJuIGZhbHNlXG5cbiAgICBsZXQgbmV4dExpbmUgPSBzdGFydExpbmUgKyAxXG5cbiAgICAvLyBGaW5kIGNsb3NpbmcgbWFya2VyXG4gICAgd2hpbGUgKG5leHRMaW5lIDwgZW5kTGluZSkge1xuICAgICAgaWYgKFxuICAgICAgICBzdGF0ZS5iTWFya3NbbmV4dExpbmVdICsgc3RhdGUudFNoaWZ0W25leHRMaW5lXSArIDMgPD1cbiAgICAgICAgc3RhdGUuZU1hcmtzW25leHRMaW5lXVxuICAgICAgKSB7XG4gICAgICAgIGNvbnN0IGNsb3NlUG9zID1cbiAgICAgICAgICBzdGF0ZS5iTWFya3NbbmV4dExpbmVdICsgc3RhdGUudFNoaWZ0W25leHRMaW5lXVxuICAgICAgICBpZiAoXG4gICAgICAgICAgc3RhdGUuc3JjLnNsaWNlKGNsb3NlUG9zLCBjbG9zZVBvcyArIDMpID09PSAnOjo6J1xuICAgICAgICApIHtcbiAgICAgICAgICBicmVha1xuICAgICAgICB9XG4gICAgICB9XG4gICAgICBuZXh0TGluZSsrXG4gICAgfVxuXG4gICAgY29uc3Qgb2xkUGFyZW50ID0gc3RhdGUucGFyZW50VHlwZVxuICAgIHN0YXRlLnBhcmVudFR5cGUgPSAncGFyYWdyYXBoJ1xuXG4gICAgY29uc3QgdG9rZW4gPSBzdGF0ZS5wdXNoKCd2aWRlb19ibG9jaycsICdkaXYnLCAwKVxuICAgIHRva2VuLm1hcmt1cCA9IG1hcmt1cFxuICAgIHRva2VuLm1ldGEgPSB7IHNyYzogdmlkZW9TcmMgfVxuICAgIHRva2VuLm1hcCA9IFtzdGFydExpbmUsIG5leHRMaW5lICsgMV1cblxuICAgIHN0YXRlLnBhcmVudFR5cGUgPSBvbGRQYXJlbnRcbiAgICBzdGF0ZS5saW5lID0gbmV4dExpbmUgKyAxXG5cbiAgICByZXR1cm4gdHJ1ZVxuICB9XG5cbiAgbWQuYmxvY2sucnVsZXIuYmVmb3JlKFxuICAgICdmZW5jZScsXG4gICAgJ3ZpZGVvX2Jsb2NrJyxcbiAgICB2aWRlb0Jsb2NrUnVsZVxuICApXG5cbiAgbWQucmVuZGVyZXIucnVsZXMudmlkZW9fYmxvY2sgPSAodG9rZW5zLCBpZHgpID0+IHtcbiAgICBjb25zdCB0b2tlbiA9IHRva2Vuc1tpZHhdXG4gICAgY29uc3Qgc3JjID0gdG9rZW4ubWV0YT8uc3JjIHx8ICcnXG5cbiAgICByZXR1cm4gYDx2aWRlbyB3aWR0aD1cIjEwMCVcIiBjb250cm9scz5cbiAgPHNvdXJjZSBzcmM9XCIke3NyY31cIiB0eXBlPVwidmlkZW8vd2VibVwiPlxuICBZb3VyIGJyb3dzZXIgZG9lcyBub3Qgc3VwcG9ydCB0aGUgdmlkZW8gdGFnLlxuPC92aWRlbz5cXG5gXG4gIH1cbn1cblxuLyoqXG4gKiBFbmhhbmNlZCBpbWFnZSByZW5kZXJpbmcgdG8gc3VwcG9ydCB2aWRlbyBmaWxlcy5cbiAqIENvbnZlcnRzICFbdmlkZW9dKGZpbGUud2VibSkgdG8gPHZpZGVvPiB0YWdzLlxuICovXG5mdW5jdGlvbiBlbmhhbmNlSW1hZ2VSZW5kZXJpbmcoXG4gIG1kOiBNYXJrZG93bkl0LFxuICBvcHRpb25zOiBWaWRlb0VtYmVkT3B0aW9uc1xuKTogdm9pZCB7XG4gIGNvbnN0IG9yaWdpbmFsSW1hZ2VSdWxlID0gbWQucmVuZGVyZXIucnVsZXMuaW1hZ2VcblxuICBtZC5yZW5kZXJlci5ydWxlcy5pbWFnZSA9ICh0b2tlbnMsIGlkeCwgX29wdGlvbnMsIGVudiwgcmVuZGVyZXIpID0+IHtcbiAgICBjb25zdCB0b2tlbiA9IHRva2Vuc1tpZHhdXG4gICAgY29uc3Qgc3JjID0gdG9rZW4uYXR0ckdldCgnc3JjJykgfHwgJydcblxuICAgIC8vIENoZWNrIGlmIGl0J3MgYSB2aWRlbyBmaWxlXG4gICAgaWYgKHNyYy5tYXRjaCgvXFwuKHdlYm18bXA0fG9nZ3xtb3YpJC9pKSkge1xuICAgICAgY29uc3QgYWx0ID0gdG9rZW4uY29udGVudCB8fCAnVmlkZW8nXG4gICAgICBjb25zdCB3aWR0aCA9IG9wdGlvbnMud2lkdGggfHwgJzEwMCUnXG4gICAgICBjb25zdCBjb250cm9scyA9IG9wdGlvbnMuY29udHJvbHMgIT09IGZhbHNlID8gJ2NvbnRyb2xzJyA6ICcnXG4gICAgICBjb25zdCBhdXRvcGxheSA9IG9wdGlvbnMuYXV0b3BsYXkgPyAnYXV0b3BsYXknIDogJydcbiAgICAgIGNvbnN0IGxvb3AgPSBvcHRpb25zLmxvb3AgPyAnbG9vcCcgOiAnJ1xuICAgICAgY29uc3QgbXV0ZWQgPSBvcHRpb25zLm11dGVkID8gJ211dGVkJyA6ICcnXG5cbiAgICAgIGNvbnN0IGV4dCA9IHNyYy5zcGxpdCgnLicpLnBvcCgpPy50b0xvd2VyQ2FzZSgpXG4gICAgICBsZXQgdHlwZSA9ICd2aWRlby93ZWJtJ1xuICAgICAgaWYgKGV4dCA9PT0gJ21wNCcpIHR5cGUgPSAndmlkZW8vbXA0J1xuICAgICAgZWxzZSBpZiAoZXh0ID09PSAnb2dnJykgdHlwZSA9ICd2aWRlby9vZ2cnXG4gICAgICBlbHNlIGlmIChleHQgPT09ICdtb3YnKSB0eXBlID0gJ3ZpZGVvL3F1aWNrdGltZSdcblxuICAgICAgcmV0dXJuIGA8dmlkZW8gd2lkdGg9XCIke3dpZHRofVwiICR7Y29udHJvbHN9ICR7YXV0b3BsYXl9ICR7bG9vcH0gJHttdXRlZH0+XG4gIDxzb3VyY2Ugc3JjPVwiJHtzcmN9XCIgdHlwZT1cIiR7dHlwZX1cIj5cbiAgJHthbHR9XG48L3ZpZGVvPmBcbiAgICB9XG5cbiAgICAvLyBGYWxsIGJhY2sgdG8gZGVmYXVsdCBpbWFnZSByZW5kZXJpbmdcbiAgICByZXR1cm4gb3JpZ2luYWxJbWFnZVJ1bGU/Lih0b2tlbnMsIGlkeCwgX29wdGlvbnMsIGVudiwgcmVuZGVyZXIpIHx8ICcnXG4gIH1cbn1cblxuLyoqXG4gKiBWaXRlUHJlc3MgcGx1Z2luIGZvciB2aWRlbyBlbWJlZGRpbmcgaW4gbWFya2Rvd24uXG4gKlxuICogVXNhZ2UgaW4gbWFya2Rvd246XG4gKiAgICFbTXkgVmlkZW9dKC9yZWNvcmRpbmdzL2RlbW8ud2VibSlcbiAqICAgb3I6XG4gKiAgIDo6OiB2aWRlbyAvcmVjb3JkaW5ncy9kZW1vLndlYm0gOjo6XG4gKlxuICogQHBhcmFtIG1kIE1hcmtkb3duSXQgaW5zdGFuY2VcbiAqIEBwYXJhbSBvcHRpb25zIFZpZGVvIGVtYmVkIG9wdGlvbnNcbiAqL1xuZXhwb3J0IGZ1bmN0aW9uIHZpZGVvRW1iZWRQbHVnaW4oXG4gIG1kOiBNYXJrZG93bkl0LFxuICBvcHRpb25zOiBQYXJ0aWFsPFZpZGVvRW1iZWRPcHRpb25zPiA9IHt9XG4pOiB2b2lkIHtcbiAgY29uc3QgZGVmYXVsdE9wdGlvbnM6IFZpZGVvRW1iZWRPcHRpb25zID0ge1xuICAgIHdpZHRoOiAnMTAwJScsXG4gICAgaGVpZ2h0OiAnYXV0bycsXG4gICAgY29udHJvbHM6IHRydWUsXG4gICAgYXV0b3BsYXk6IGZhbHNlLFxuICAgIGxvb3A6IGZhbHNlLFxuICAgIG11dGVkOiBmYWxzZSxcbiAgICAuLi5vcHRpb25zLFxuICB9XG5cbiAgcGFyc2VWaWRlb0RpcmVjdGl2ZShtZCwgZGVmYXVsdE9wdGlvbnMpXG4gIGVuaGFuY2VJbWFnZVJlbmRlcmluZyhtZCwgZGVmYXVsdE9wdGlvbnMpXG59XG5cbmV4cG9ydCB0eXBlIHsgVmlkZW9FbWJlZE9wdGlvbnMgfVxuIiwgImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCIvVXNlcnMva29vc2hhcGFyaS90ZW1wLVBST0RWRVJDRUwvNDg1L2t1c2gvdGhlZ2VudC9kb2NzLy52aXRlcHJlc3NcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZmlsZW5hbWUgPSBcIi9Vc2Vycy9rb29zaGFwYXJpL3RlbXAtUFJPRFZFUkNFTC80ODUva3VzaC90aGVnZW50L2RvY3MvLnZpdGVwcmVzcy9zaWRlYmFyLnRzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ltcG9ydF9tZXRhX3VybCA9IFwiZmlsZTovLy9Vc2Vycy9rb29zaGFwYXJpL3RlbXAtUFJPRFZFUkNFTC80ODUva3VzaC90aGVnZW50L2RvY3MvLnZpdGVwcmVzcy9zaWRlYmFyLnRzXCI7ZXhwb3J0IGNvbnN0IHNpZGViYXIgPSB7XG4gIFwiL1wiOiBbXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQXJjaGl0ZWN0dXJlXCIsXG4gICAgICBcImNvbGxhcHNlZFwiOiBmYWxzZSxcbiAgICAgIFwiaXRlbXNcIjogW1xuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQWdlbnQgU2FuZGJveGluZyBBcmNoaXRlY3R1cmU6IFdBU00vQ29udGFpbmVycy9WTXMgKE5vIERvY2tlcilcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvYXJjaGl0ZWN0dXJlL0FHRU5UX1NBTkRCT1hJTkdfQVJDSElURUNUVVJFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlB5dGhvbiBGcm9udG1hdHRlciArIE5hdGl2ZSBCYWNrbWF0dGVyIEFyY2hpdGVjdHVyZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9hcmNoaXRlY3R1cmUvRlJPTlRNQVRURVJfQkFDS01BVFRFUl9BUkNISVRFQ1RVUkUubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiSHlicmlkIE1hYy9XaW5kb3dzIERldmVsb3BtZW50IEVudmlyb25tZW50IEFyY2hpdGVjdHVyZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9hcmNoaXRlY3R1cmUvSFlCUklEX01BQ19XSU5fREVWX0VOVklST05NRU5ULm1kXCJcbiAgICAgICAgfVxuICAgICAgXVxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQ2hhbmdlc1wiLFxuICAgICAgXCJjb2xsYXBzZWRcIjogZmFsc2UsXG4gICAgICBcIml0ZW1zXCI6IFtcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkhleGFnb25hbCBNaWdyYXRpb25cIixcbiAgICAgICAgICBcImNvbGxhcHNlZFwiOiBmYWxzZSxcbiAgICAgICAgICBcIml0ZW1zXCI6IFtcbiAgICAgICAgICAgIHtcbiAgICAgICAgICAgICAgXCJ0ZXh0XCI6IFwiSGV4YWdvbmFsIEFyY2hpdGVjdHVyZSBNaWdyYXRpb24gLS0gdGhlZ2VudFwiLFxuICAgICAgICAgICAgICBcImxpbmtcIjogXCIvaGV4YWdvbmFsLW1pZ3JhdGlvbi9wcm9wb3NhbC5tZFwiXG4gICAgICAgICAgICB9XG4gICAgICAgICAgXVxuICAgICAgICB9XG4gICAgICBdXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJDaGVja2xpc3RzXCIsXG4gICAgICBcImNvbGxhcHNlZFwiOiBmYWxzZSxcbiAgICAgIFwiaXRlbXNcIjogW1xuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiSHlicmlkIE1hYy9XaW5kb3dzIEVudmlyb25tZW50IFNldHVwIENoZWNrbGlzdFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9jaGVja2xpc3RzL0hZQlJJRF9FTlZfU0VUVVBfQ0hFQ0tMSVNULm1kXCJcbiAgICAgICAgfVxuICAgICAgXVxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQ2xvc3VyZVwiLFxuICAgICAgXCJjb2xsYXBzZWRcIjogZmFsc2UsXG4gICAgICBcIml0ZW1zXCI6IFtcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkRSIFJlaGVhcnNhbCBSZXBvcnRcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvY2xvc3VyZS9EUl9SRUhFQVJTQUxfUkVQT1JULm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkdvdmVybmFuY2UgJiBDb21wbGlhbmNlIEJ1bmRsZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9jbG9zdXJlL0dPVkVSTkFOQ0VfQ09NUExJQU5DRV9CVU5ETEUubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUGhhc2UgNiBSZWFkaW5lc3MgUmVwb3J0XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2Nsb3N1cmUvUEhBU0U2X1JFQURJTkVTU19SRVBPUlQubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUG9zdC1MYXVuY2ggMjgtRGF5IE9ic2VydmF0aW9uIFBsYW5cIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvY2xvc3VyZS9QT1NUX0xBVU5DSF8yOERBWV9PQlNFUlZBVElPTi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJSb2xsYmFjayBSZXNlcnZlIFBsYW5cIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvY2xvc3VyZS9ST0xMQkFDS19SRVNFUlZFX1BMQU4ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiU0xPIENlcnRpZmljYXRpb24gTWF0cml4XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2Nsb3N1cmUvU0xPX0NFUlRJRklDQVRJT05fTUFUUklYLm1kXCJcbiAgICAgICAgfVxuICAgICAgXVxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQ29udHJhY3RzXCIsXG4gICAgICBcImNvbGxhcHNlZFwiOiBmYWxzZSxcbiAgICAgIFwiaXRlbXNcIjogW1xuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQ29udHJhY3QgQXV0aG9yaXR5XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2NvbnRyYWN0cy9DT05UUkFDVF9BVVRIT1JJVFkubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiRmFsbGJhY2sgQ29udHJvbCBQbGFuZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9jb250cmFjdHMvRkFMTEJBQ0tfUE9MSUNZLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlByb3ZpZGVyIEFkYXB0ZXIgQ29udHJhY3RzIChHLVJWLTA1KVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9jb250cmFjdHMvUFJPVklERVJfQURBUFRFUl9DT05UUkFDVFMubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQ29udHJhY3QgVXBncmFkZSBQbGF5Ym9va1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9jb250cmFjdHMvVVBHUkFERV9QTEFZQk9PSy5tZFwiXG4gICAgICAgIH1cbiAgICAgIF1cbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkRlbW9zXCIsXG4gICAgICBcImNvbGxhcHNlZFwiOiBmYWxzZSxcbiAgICAgIFwiaXRlbXNcIjogW1xuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiRGVtbyBTY3JpcHRzIGZvciBWaXRlUHJlc3MgRG9jdW1lbnRhdGlvblwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kZW1vcy9SRUFETUUubWRcIlxuICAgICAgICB9XG4gICAgICBdXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJEb2NzZXRcIixcbiAgICAgIFwiY29sbGFwc2VkXCI6IGZhbHNlLFxuICAgICAgXCJpdGVtc1wiOiBbXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJEQUcgTm9kZS10by1TZXJ2aWNlIENvbnRyYWN0IENoZWNrbGlzdFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvREFHX05PREVfU0VSVklDRV9DT05UUkFDVF9DSEVDS0xJU1QubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiREFHIE5vZGUtdG8tU2VydmljZSBDb250cmFjdCBDaGVja2xpc3RcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZG9jc2V0L0RBR19OT0RFX1RPX1NFUlZJQ0VfQ09OVFJBQ1RfQ0hFQ0tMSVNULm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkUyRSBOZXh0IENodW5rIFBsYW4gXHUyMDE0IEZ1bGwtUGhhc2UgTWVnYSBDaHVua1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvRTJFX05FWFRfQ0hVTktfUExBTi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJFMkUgUmVtYWluaW5nIEZ1bGwtRGVwdGggUGxhblwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvRTJFX1JFTUFJTklOR19GVUxMX0RFUFRIX1BMQU4ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiRmFzdE1DUCAzLjAgSW50ZWdyYXRpb24gUmVmZXJlbmNlIGZvciBUaGVnZW50XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC9GQVNUTUNQX0lOVEVHUkFUSU9OLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgSW1wbGVtZW50YXRpb24gU3RhdHVzIFRyYWNrZXJcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZG9jc2V0L0lNUExFTUVOVEFUSU9OX1NUQVRVUy5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUaGVnZW50IE9wdGltaXphdGlvbiwgUG9saXNoLCBhbmQgUm9idXN0bmVzcyBBZGRlbmR1bVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvT1BUSU1JWkFUSU9OX1BPTElTSF9BRERFTkRVTS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUaGVnZW50IFBhdHRlcm4gQ2F0YWxvZ1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvUEFUVEVSTlMubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQ29tcHJlaGVuc2l2ZSBUZXN0IFBsYW4gTWF0cml4XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC9QUkRfVEVTVF9QTEFOX01BVFJJWC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJSZW1haW5pbmcgR2FwcyBcdTIwMTQgRnVsbCBEZXB0aCBBbmFseXNpc1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvUkVNQUlOSU5HX0dBUFNfREVFUF9ESVZFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlJlbWFpbmluZyBHYXBzIFx1MjAxNCBGdWxsIERlcHRoIEFuYWx5c2lzXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC9SRU1BSU5JTkdfR0FQU19GVUxMX0RFUFRILm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUmlza3MgYW5kIEFudGktUGF0dGVybnMgQ2F0YWxvZ1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvUklTS1NfQU5EX0FOVElQQVRURVJOUy5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJXQlMtdG8tSXNzdWUgSW1wb3J0IE1hdHJpeFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvV0JTX1RPX0lTU1VFX0lNUE9SVF9NQVRSSVgubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBDTEkgU2luZ2xlIFNvdXJjZSBvZiBUcnV0aCBBdWRpdFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1jbGktc2luZ2xlLXNvdXJjZS1vZi10cnV0aC1hdWRpdC0yMDI2LTAyLTE0Lm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgQ3Jvc3MtQW5hbHlzaXMgTWF0cml4IChEZWVwKVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1jcm9zcy1hbmFseXNpcy1tYXRyaXgtMjAyNi0wMi0xNC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUaGVnZW50IEZpbmFsIERBRyBTcGVjaWZpY2F0aW9uXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LWRhZy1maW5hbC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUaGVnZW50IERBRyBFeHRlbnNpb24gXHUyMDE0IFBoYXNlcyAxMCB0byAxMlwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1kYWctcGhhc2UxMC0xMi1leHRlbnNpb24ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwidGhlZ2VudCBEQUcgRXh0ZW5zaW9uIFx1MjAxNCBQaGFzZXMgNywgOCwgOVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1kYWctcGhhc2U3LTktZXh0ZW5zaW9uLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgR2FwcyBhbmQgRGlzY292ZXJ5IFJlcG9ydFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1nYXBzLWFuZC1kaXNjb3ZlcnktMjAyNi0wMi0xNC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUaGVnZW50IEltcGxlbWVudGF0aW9uIExvZ1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1pbXBsZW1lbnRhdGlvbi1sb2ctMjAyNi0wMi0xNC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUaGVnZW50IEt1c2ggRG9jcyBEZWVwIERpdmUgKFplbiArIEFkamFjZW50IFByb2plY3RzKVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1rdXNoLWRvY3MtZGVlcC1kaXZlLTIwMjYtMDItMTQubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBNZWdhIFJlc2VhcmNoIFN5bnRoZXNpc1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1tZWdhLXJlc2VhcmNoLXN5bnRoZXNpcy0yMDI2LTAyLTE0Lm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgT3JjaGVzdHJhdGlvbiBPcHRpbWl6YXRpb24gJiBFeHBhbnNpb24gUFJEIChMaXZpbmcgRG9jdW1lbnQpXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LW9yY2hlc3RyYXRpb24tb3B0aW1pemF0aW9uLXByZC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUaGVnZW50IFBhdHRlcm4gRW5oYW5jZW1lbnQgU3ludGhlc2lzXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBhdHRlcm5zLWVuaGFuY2VtZW50LXN5bnRoZXNpcy5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDEwXHUyMDEzMTIgQnVuZGxlIEIgU3ByaW50IFBsYXlib29rXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMTAtMTItYnVuZGxlLWItc3ByaW50LXBsYXlib29rLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgMTBcdTIwMTMxMiBCdW5kbGUgU2lnbm9mZiBhbmQgSGFuZG9mZiBQYWNrYWdlc1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTEwLTEyLWJ1bmRsZS1zaWdub2ZmLWFuZC1oYW5kb2ZmLXBhY2thZ2VzLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgMTBcdTIwMTMxMiBDbG9zdXJlIFJlYWRpbmVzcyBQYWNrIFRlbXBsYXRlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMTAtMTItY2xvc3VyZS1yZWFkaW5lc3MtcGFjay10ZW1wbGF0ZS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDEwXHUyMDEzMTIgQ29tcGFjdCBFeGVjdXRpb24gRGFzaGJvYXJkXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMTAtMTItY29tcGFjdC1leGVjdXRpb24tZGFzaGJvYXJkLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgMTBcdTIwMTMxMiBEcmlmdCBSZWNvbmNpbGlhdGlvbiBQbGF5Ym9va1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTEwLTEyLWRyaWZ0LXJlY29uY2lsaWF0aW9uLXBsYXlib29rLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgMTBcdTIwMTMxMiBFeGVjdXRpb24gQnVuZGxlcyBQbGF5Ym9va1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTEwLTEyLWV4ZWN1dGlvbi1idW5kbGVzLXBsYXlib29rLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgMTBcdTIwMTMxMiBFeGVjdXRpb24gU3ludGhlc2lzIFBsYXlib29rXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMTAtMTItZXhlY3V0aW9uLXN5bnRoZXNpcy1wbGF5Ym9vay5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDEwXHUyMDEzMTIgRXhlY3V0aW9uIFdvcmtib2FyZCAoQ2h1bmsgNClcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtcGhhc2UxMC0xMi1leGVjdXRpb24td29ya2JvYXJkLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgMTBcdTIwMTMxMiBIYXJkLVN0b3AsIFJvbGxiYWNrLCBhbmQgU3RhYmlsaXR5IE1hdHJpeFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTEwLTEyLWhhcmQtc3RvcC1hbmQtcm9sbGJhY2stbWF0cml4Lm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgMTBcdTIwMTMxMiBJbXBsZW1lbnRhdGlvbiBDaHVuayBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMTAtMTItaW1wbGVtZW50YXRpb24tY2h1bmstcGxhbi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDEwXHUyMDEzMTIgSW1wbGVtZW50YXRpb24gSXNzdWUgUXVldWVcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtcGhhc2UxMC0xMi1pbXBsZW1lbnRhdGlvbi1pc3N1ZS1xdWV1ZS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDEwXHUyMDEzMTIgSW1wbGVtZW50YXRpb24gVGlja2V0IFRlbXBsYXRlcyAoQ2h1bmsgMylcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtcGhhc2UxMC0xMi1pbXBsZW1lbnRhdGlvbi10aWNrZXQtdGVtcGxhdGVzLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgMTBcdTIwMTMxMiBJc3N1ZSBCb2FyZCBBdXRvbWF0aW9uIFBsYXlib29rXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMTAtMTItaXNzdWUtYm9hcmQtYXV0b21hdGlvbi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDEwXHUyMDEzMTIgSXNzdWUgQm9hcmQgSW1wb3J0IE5vdGVzXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMTAtMTItaXNzdWUtYm9hcmQtaW1wb3J0LW5vdGVzLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgMTBcdTIwMTMxMiBMYXVuY2ggU2NoZWR1bGUgKERheS1ieS1EYXkgRXhlY3V0aW9uIFBsYW4pXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMTAtMTItbGF1bmNoLXNjaGVkdWxlLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgMTBcdTIwMTMxMiBNYXN0ZXIgVHJhY2VhYmlsaXR5IExlZGdlclwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTEwLTEyLW1hc3Rlci10cmFjZWFiaWxpdHktbGVkZ2VyLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgXHUyMDE0IFBoYXNlIDEwXHUyMDEzMTIgUFJEIChPcHRpbWl6YXRpb24tRGVwdGggYW5kIFByb2R1Y3RpemF0aW9uIFdhdmUpXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMTAtMTItb3B0aW1hbC1kZXNpZ24tcHJkLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgMTBcdTIwMTMxMiBPcmNoZXN0cmF0b3IgVG9vbGluZyBTdGFja1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTEwLTEyLW9yY2hlc3RyYXRvci10b29saW5nLXN0YWNrLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgMTBcdTIwMTMxMiBQb2xpY3ktYXMtQ29kZSBhbmQgQXV0b21hdGlvbiBDb250cmFjdFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTEwLTEyLXBvbGljeS1hcy1jb2RlLWFuZC1hdXRvbWF0aW9uLWNvbnRyYWN0Lm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgMTBcdTIwMTMxMiBQUkRcdTIxOTRXQlMgRmluYWxpemF0aW9uIENyb3NzLU1hcFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTEwLTEyLXByZC13YnMtY3Jvc3NtYXAtZmluYWxpemF0aW9uLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgMTBcdTIwMTMxMiBQUkQtV0JTLURBRy1UaWNrZXQgVmFsaWRhdGlvbiBGcmFtZXdvcmtcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtcGhhc2UxMC0xMi1wcmQtd2JzLWRhZy10aWNrZXQtdmFsaWRhdGlvbi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDEwXHUyMDEzMTIgUmVsZWFzZSBSZWFkaW5lc3MgYW5kIERlbHRhIFBhY2tcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtcGhhc2UxMC0xMi1yZWxlYXNlLXJlYWRpbmVzcy1hbmQtZGVsdGEtcGFjay5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDEwXHUyMDEzMTIgVGVzdCBhbmQgUmVhZGluZXNzIFBhY2tcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtcGhhc2UxMC0xMi10ZXN0LXJlYWRpbmVzcy1wYWNrLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgMTEgU3ByaW50IFBsYXlib29rIChCdW5kbGVzIEMgYW5kIEQpXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMTEtY29udHJvbC1hbmQtYWRhcHRhdGlvbi1zcHJpbnQtcGxheWJvb2subWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBQaGFzZSAxMiBTcHJpbnQgUGxheWJvb2sgKEJ1bmRsZXMgRSBhbmQgRilcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtcGhhc2UxMi1leHBsYWluYWJpbGl0eS1hbmQtY2xvc3VyZS1zcHJpbnQtcGxheWJvb2subWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBQaGFzZSAxMysgRXh0ZW5zaW9uIEJvdW5kYXJ5IFByb3Bvc2FsXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMTMtcGx1cy1leHRlbnNpb24tcHJvcG9zYWwubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBQaGFzZSAzXHUyMDEzNiBDbG9zdXJlIEFjY2VwdGFuY2UgQ29udHJhY3QgU2NoZW1hXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMy02LWNsb3N1cmUtYWNjZXB0YW5jZS1jb250cmFjdC1zY2hlbWEubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBQaGFzZSAzXHUyMDEzNiBDbG9zdXJlIEFjY2VwdGFuY2UgUGFjayBUZW1wbGF0ZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTMtNi1jbG9zdXJlLWFjY2VwdGFuY2UtcGFjay10ZW1wbGF0ZS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDNcdTIwMTM2IENsb3N1cmUgVmFsaWRhdG9yIEF1dG9tYXRpb24gUGFja2FnZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTMtNi1jbG9zdXJlLXZhbGlkYXRvci1hdXRvbWF0aW9uLXBhY2thZ2UubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBQaGFzZSAzXHUyMDEzNiBDbG9zdXJlIFZhbGlkYXRpb24gRXZlbnQgYW5kIFdhaXZlciBDb250cmFjdCB2MVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTMtNi1jbG9zdXJlLXZhbGlkYXRvci1ldmVudC1hbmQtd2FpdmVyLWNvbnRyYWN0LXYxLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgM1x1MjAxMzYgQ2xvc3VyZSBWYWxpZGF0b3IgRmF1bHQgSW5qZWN0aW9uIGFuZCBDaGFvcyBUZXN0c1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTMtNi1jbG9zdXJlLXZhbGlkYXRvci1mYXVsdC1pbmplY3Rpb24tYW5kLWNoYW9zLXRlc3RzLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgM1x1MjAxMzYgQ2xvc3VyZSBWYWxpZGF0b3IgSW1wbGVtZW50YXRpb24gQmx1ZXByaW50XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMy02LWNsb3N1cmUtdmFsaWRhdG9yLWltcGxlbWVudGF0aW9uLWJsdWVwcmludC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDNcdTIwMTM2IENsb3N1cmUgVmFsaWRhdG9yIFB5dGhvbiBJbXBsZW1lbnRhdGlvbiBCbHVlcHJpbnRcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtcGhhc2UzLTYtY2xvc3VyZS12YWxpZGF0b3ItcHl0aG9uLWltcGxlbWVudGF0aW9uLWJsdWVwcmludC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDMtNiBDbG9zdXJlIFZhbGlkYXRvciBSdW50aW1lIENMSSBhbmQgQWRhcHRlciBQbGF5Ym9va1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTMtNi1jbG9zdXJlLXZhbGlkYXRvci1ydW50aW1lLWNsaS1hbmQtYWRhcHRlci1wbGF5Ym9vay5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDNcdTIwMTM2IENyb3NzLVdhdmUgQnJpZGdlIGFuZCBDb250aW51aXR5IFBsYW5cIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtcGhhc2UzLTYtY3Jvc3N3YXZlLWJyaWRnZS1hbmQtY29udGludWl0eS1wbGFuLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgXHUyMDE0IFBoYXNlIDNcdTIwMTM2IEZ1bGwtRGVwdGggRXhlY3V0aW9uIENodW5rXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMy02LWZ1bGwtZGVwdGgtZXhlY3V0aW9uLXByZC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDdcdTIwMTM5IE5leHQtV2F2ZSBQUkQgKFBvc3QtQ2xvc3VyZSBPcHRpbWl6YXRpb24pXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlNy05LW5leHQtd2F2ZS1wcmQubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBQaGFzZSA3XHUyMDEzOSBUZXN0IGFuZCBSZWFkaW5lc3MgUGFja1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTctOS10ZXN0LXJlYWRpbmVzcy1wYWNrLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgT3JjaGVzdHJhdGlvbiBGaW5hbCBQbGFuIEluZGV4XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBsYW4tZmluYWwtaW5kZXgubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBQcm9kdWN0aW9uIE9yY2hlc3RyYXRpb24gUFJEIChGaW5hbClcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtcHJkLWZpbmFsLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUmVzZWFyY2ggVmFsaWRhdGlvbiBBZGRlbmR1bSAoWmVuICsgVGFzayBUb29scylcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtcmVzZWFyY2gtdmFsaWRhdGlvbi0yMDI2LTAyLTE0Lm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcInRoZWdlbnQgVGhpcmQtUGFydHkgQnVuZGxlIE1hbmlmZXN0XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXRoaXJkLXBhcnR5LWJ1bmRsZS1tYW5pZmVzdC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUaGVnZW50IEZpbmFsIFdCUyAoQ29tcHJlaGVuc2l2ZSlcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtd2JzLWZpbmFsLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgV0JTIFx1MjAxNCBQaGFzZSAxMCB0byBQaGFzZSAxMiAoT3B0aW1pemF0aW9uLURlcHRoIGFuZCBQcm9kdWN0aXphdGlvbilcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtd2JzLXBoYXNlMTAtMTIubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBXQlMgXHUyMDE0IFBoYXNlIDcgdG8gUGhhc2UgOSAoTmV4dC1XYXZlIEV4ZWN1dGlvbilcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtd2JzLXBoYXNlNy05Lm1kXCJcbiAgICAgICAgfVxuICAgICAgXVxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiRW50ZXJwcmlzZVwiLFxuICAgICAgXCJjb2xsYXBzZWRcIjogZmFsc2UsXG4gICAgICBcIml0ZW1zXCI6IFtcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkRlY29tbWlzc2lvbmluZyBhbmQgU3Vuc2V0IFBsYW5cIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZW50ZXJwcmlzZS9ERUNPTU1JU1NJT05JTkdfUExBTi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJQcm9ncmFtIE9wZXJhdGluZyBNb2RlbCBhbmQgT3duZXJzaGlwIE1hcFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9lbnRlcnByaXNlL09QRVJBVElOR19NT0RFTC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJTZWN1cml0eSBhbmQgQ29tcGxpYW5jZSBTaWdub2ZmIFBhY2thZ2VcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZW50ZXJwcmlzZS9TRUNVUklUWV9DT01QTElBTkNFX1NJR05PRkYubWRcIlxuICAgICAgICB9XG4gICAgICBdXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJHb3Zlcm5hbmNlXCIsXG4gICAgICBcImNvbGxhcHNlZFwiOiBmYWxzZSxcbiAgICAgIFwiaXRlbXNcIjogW1xuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQ29zdCBHb3Zlcm5hbmNlIERlc2lnbiAoRy1HUC0wNilcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZ292ZXJuYW5jZS9DT1NUX0dPVkVSTkFOQ0VfREVTSUdOLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkhJVEwgKEh1bWFuLWluLXRoZS1Mb29wKSBEZXNpZ24gKEctR1AtMDUpXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2dvdmVybmFuY2UvSElUTF9ERVNJR04ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiTmVNbyBHdWFyZHJhaWxzIERlc2lnbiAoRy1HUC0wMilcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZ292ZXJuYW5jZS9ORU1PX0dVQVJEUkFJTFNfREVTSUdOLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIk9QQSBJbnRlZ3JhdGlvbiBEZXNpZ24gKEctR1AtMDEpXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2dvdmVybmFuY2UvT1BBX0lOVEVHUkFUSU9OX0RFU0lHTi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJSZXRlbnRpb24gUG9saWN5IERlc2lnbiAoRy1HUC0wNylcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZ292ZXJuYW5jZS9SRVRFTlRJT05fUE9MSUNZX0RFU0lHTi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJTYW5kYm94aW5nIERlc2lnbiAoRy1HUC0wOClcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZ292ZXJuYW5jZS9TQU5EQk9YSU5HX0RFU0lHTi5tZFwiXG4gICAgICAgIH1cbiAgICAgIF1cbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkd1aWRlc1wiLFxuICAgICAgXCJjb2xsYXBzZWRcIjogZmFsc2UsXG4gICAgICBcIml0ZW1zXCI6IFtcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkFnZW50IERlYnVnZ2luZyBhbmQgUmVtZWRpYXRpb24gR3VpZGVcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL0FHRU5UX0RFQlVHR0lOR19BTkRfUkVNRURJQVRJT05fR1VJREUubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQWdlbnQgSW5zdHJ1Y3Rpb25zOiB0aGVnZW50IERlZXAtRGl2ZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvQUdFTlRfSU5TVFJVQ1RJT05TX1RIRUdFTlQubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQXV0b21hdGVkIERvY3VtZW50YXRpb24gRGVtb3NcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL0FVVE9NQVRFRF9ERU1PUy5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJCS00gSW1wbGVtZW50YXRpb24gR3VpZGVzXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9CS01fSU1QTEVNRU5UQVRJT05fR1VJREVTLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkNyb3NzLVBsYXRmb3JtIERlc2t0b3AgQXV0b21hdGlvbiBcdTIwMTQgQ29tcGxldGUgR3VpZGVcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL0NST1NTX1BMQVRGT1JNX0NPTVBMRVRFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkNyb3NzLVBsYXRmb3JtIERlc2t0b3AgQXV0b21hdGlvbjogRGV2ZWxvcGVyIENvb2tib29rXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9DUk9TU19QTEFURk9STV9ERVZFTE9QRVJfQ09PS0JPT0subWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQ3Jvc3MtUGxhdGZvcm0gRGVza3RvcCBBdXRvbWF0aW9uOiBJbXBsZW1lbnRhdGlvbiBUZW1wbGF0ZXNcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL0NST1NTX1BMQVRGT1JNX0lNUExFTUVOVEFUSU9OX1RFTVBMQVRFUy5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJDcm9zcy1QbGF0Zm9ybSBEZXNrdG9wIEF1dG9tYXRpb246IE1pZ3JhdGlvbiBHdWlkZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvQ1JPU1NfUExBVEZPUk1fTUlHUkFUSU9OX0dVSURFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkNyb3NzLVBsYXRmb3JtIERlc2t0b3AgQXV0b21hdGlvbjogUXVpY2sgU3RhcnQgR3VpZGVcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL0NST1NTX1BMQVRGT1JNX1FVSUNLX1NUQVJULm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkNyb3NzLVBsYXRmb3JtIERlc2t0b3AgQXV0b21hdGlvbjogSW1wbGVtZW50YXRpb24gUm9hZG1hcFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvQ1JPU1NfUExBVEZPUk1fUk9BRE1BUC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJEb2N0b3IgQ29tbWFuZCBGaXhlc1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvRE9DVE9SX0ZJWEVTLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkZpeCBTaGVsbCBDb3JydXB0aW9uIElzc3VlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9GSVhfU0hFTExfQ09SUlVQVElPTi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJGaXggU2hlbGwgRm9yayBFcnJvcnM6IFF1aWNrIEd1aWRlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9GSVhfU0hFTExfRk9SS19FUlJPUlMubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiR3VpZGVzIEluZGV4XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9HVUlERVNfSU5ERVgubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiSHlicmlkIE1hYy9XaW5kb3dzIEVudmlyb25tZW50IFF1aWNrIFN0YXJ0IEd1aWRlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9IWUJSSURfRU5WX1FVSUNLX1NUQVJULm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkltcGxlbWVudGF0aW9uIFBhdHRlcm5zIEd1aWRlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9JTVBMRU1FTlRBVElPTl9QQVRURVJOUy5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJKb2IgUG9vbCBTeXN0ZW0gLSBVc2FnZSBHdWlkZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvSk9CX1BPT0xfVVNBR0UubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiT0F1dGgtT25seSBBdXRoZW50aWNhdGlvbiBQb2xpY3lcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL09BVVRIX09OTFlfQVVUSEVOVElDQVRJT04ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiT3BlcmF0aW9uYWwgTGVhcm5pbmcgQXNzZXRzIChXUC0xMjAwOClcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL09QRVJBVElPTkFMX0xFQVJOSU5HLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIm94bGludCBJbnRlZ3JhdGlvbiBHdWlkZSAoUGhhc2UgNClcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL09YTElOVF9JTlRFR1JBVElPTl9HVUlERS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDEwIFN1bW1hcnkgYW5kIE1pZ3JhdGlvbiBHdWlkZSAoV1AtMTAwMTApXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9QSEFTRV8xMF9HVUlERS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDExIFN1bW1hcnkgYW5kIEV2aWRlbmNlIFBhY2sgKFdQLTExMDEwKVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvUEhBU0VfMTFfR1VJREUubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUGhhc2UgNCBRdWljayBTdGFydDogRVNMaW50IFx1MjE5MiBveGxpbnQgTWlncmF0aW9uXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9QSEFTRV80X1FVSUNLX1NUQVJULm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgNy05IFN1bW1hcnkgYW5kIFRyYWluaW5nIEd1aWRlIChXUC05MDEwKVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvUEhBU0VfN185X0dVSURFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlByb21wdHMgVG9vbGluZyBcdTIwMTQgQ3Vyc29yIC8gQ29kZXggLyBDbGF1ZGUgQWdncmVnYXRlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9QUk9NUFRTX1RPT0xJTkcubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUHJvdmlkZXIgU2V0dXAgR3VpZGVcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL1BST1ZJREVSX1NFVFVQX0dVSURFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlF1YWxpdHkgQXNzdXJhbmNlIEd1aWRlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9RVUFMSVRZX0FTU1VSQU5DRS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJRdWljayBGaXg6IFNoZWxsIFNldHVwIElzc3Vlc1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvUVVJQ0tfRklYX1NIRUxMX1NFVFVQLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlJ1bnRpbWUgT3B0aW1pemF0aW9uIEd1aWRlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9SVU5USU1FX09QVElNSVpBVElPTi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJTaGVsbCBBZHZhbmNlZCBGZWF0dXJlcyBHdWlkZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvU0hFTExfQURWQU5DRURfRkVBVFVSRVMubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiU2hlbGwgQ29ycnVwdGlvbiBGaXggLSBDb21wbGV0ZSBTb2x1dGlvblwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvU0hFTExfQ09SUlVQVElPTl9GSVhfQ09NUExFVEUubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQ29tcGxldGUgU2hlbGwgRW52aXJvbm1lbnQgU3lzdGVtXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9TSEVMTF9FTlZJUk9OTUVOVF9DT01QTEVURS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJTaGVsbCBFbnZpcm9ubWVudCBNYW5hZ2VtZW50XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9TSEVMTF9FTlZJUk9OTUVOVF9NQU5BR0VNRU5ULm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlNoZWxsIE9wdGltaXphdGlvbiBHdWlkZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvU0hFTExfT1BUSU1JWkFUSU9OX0dVSURFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlNoZWxsICYgWnNoIFBsdWdpbiBTZXR1cCBcdTIwMTQgTG9uZy1UZXJtIEZpeFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvU0hFTExfWlNIX1BMVUdJTl9TRVRVUC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJTaXRiYWNrIFBsdWdpbiBBUElcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL1NJVEJBQ0tfUExVR0lOUy5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJTdGFyc2hpcCArIGRpcmVudiBTZXR1cCBDb21wbGV0ZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvU1RBUlNISVBfRElSRU5WX1NFVFVQLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlx1RDgzRFx1REU4MCBIb29rcyBPcHRpbWl6YXRpb24gSW5pdGlhdGl2ZSAtIFNUQVJUIEhFUkVcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL1NUQVJUX0hFUkUubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVGFzayBSb3V0aW5nIFF1aWNrIFJlZmVyZW5jZSBHdWlkZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvVEFTS19ST1VUSU5HX1FVSUNLX1JFRi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJ0aGVnZW50IFRlc3RpbmcgR3VpZGVcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL1RFU1RJTkcubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVHJvdWJsZXNob290aW5nIEd1aWRlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9UUk9VQkxFU0hPT1RJTkcubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVml0ZVByZXNzIERvY3NpdGUgU2V0dXBcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL1ZJVEVQUFJFU1NfU0VUVVAubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQW50aS1QYXR0ZXJuIERldGVjdGlvbiBHdWlkZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvYW50aS1wYXR0ZXJucy5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJBcmNoaXRlY3R1cmUgRW5mb3JjZW1lbnQgR3VpZGVcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL2FyY2hpdGVjdHVyZS1lbmZvcmNlbWVudC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJHdWlkZXNcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL2luZGV4Lm1kXCJcbiAgICAgICAgfVxuICAgICAgXVxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiTWlncmF0aW9uXCIsXG4gICAgICBcImNvbGxhcHNlZFwiOiBmYWxzZSxcbiAgICAgIFwiaXRlbXNcIjogW1xuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQWR2YW5jZWQgUGVyZm9ybWFuY2UgUGF0dGVybnMgJiBCZXN0IFByYWN0aWNlc1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9taWdyYXRpb24vQURWQU5DRURfUEFUVEVSTlMubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQ29tcGxldGUgU29sdXRpb246IFBvbGlzaGVkLCBPcHRpbWl6ZWQsIFByb2R1Y3Rpb24tUmVhZHlcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvbWlncmF0aW9uL0NPTVBMRVRFX1NPTFVUSU9OLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkNvbXByZWhlbnNpdmUgQmVuY2htYXJraW5nIFN0cmF0ZWd5XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL21pZ3JhdGlvbi9DT01QUkVIRU5TSVZFX0JFTkNITUFSS0lORy5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJDb21wcmVoZW5zaXZlIFBlcmZvcm1hbmNlIEFuYWx5c2lzICYgTWlncmF0aW9uIFN0cmF0ZWd5XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL21pZ3JhdGlvbi9DT01QUkVIRU5TSVZFX1BFUkZPUk1BTkNFX0FOQUxZU0lTLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkRlc2lnbiBQcmluY2lwbGVzXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL21pZ3JhdGlvbi9ERVNJR05fUFJJTkNJUExFUy5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJVc2FnZSBFeGFtcGxlc1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9taWdyYXRpb24vRVhBTVBMRVMubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiRm9yayBGYWlsdXJlIChFQUdBSU4pIEFuYWx5c2lzICYgU29sdXRpb25zXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL21pZ3JhdGlvbi9GT1JLX0ZBSUxVUkVfQU5BTFlTSVMubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQ29tcHJlaGVuc2l2ZSBJbXBsZW1lbnRhdGlvbiBSb2FkbWFwXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL21pZ3JhdGlvbi9JTVBMRU1FTlRBVElPTl9ST0FETUFQLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlByb2R1Y3Rpb24gUmVhZGluZXNzIENoZWNrbGlzdFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9taWdyYXRpb24vUFJPRFVDVElPTl9SRUFESU5FU1MubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUXVpY2sgU3RhcnQgR3VpZGVcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvbWlncmF0aW9uL1FVSUNLX1NUQVJULm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlNoZWxsIHRvIFJ1c3QvR28gTWlncmF0aW9uIFBsYW5cIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvbWlncmF0aW9uL1JVU1RfR09fTUlHUkFUSU9OX1BMQU4ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUGVyZm9ybWFuY2UgT3B0aW1pemF0aW9uIFN1bW1hcnlcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvbWlncmF0aW9uL1NVTU1BUlkubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVGhlIFVsdGltYXRlIEd1aWRlOiBDb21wcmVoZW5zaXZlIFBlcmZvcm1hbmNlIE9wdGltaXphdGlvbiAmIE1pZ3JhdGlvblwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9taWdyYXRpb24vVUxUSU1BVEVfR1VJREUubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVXNlciBHdWlkZTogdGhlZ2VudCBQZXJmb3JtYW5jZSBPcHRpbWl6YXRpb25zXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL21pZ3JhdGlvbi9VU0VSX0dVSURFLm1kXCJcbiAgICAgICAgfVxuICAgICAgXVxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUGxhbnNcIixcbiAgICAgIFwiY29sbGFwc2VkXCI6IGZhbHNlLFxuICAgICAgXCJpdGVtc1wiOiBbXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUaGVnZW50IFVuaWZpZWQgUGxhbiBcdTIwMTQgTWFzdGVyIEluZGV4XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zLzAwLU1BU1RFUi1JTkRFWC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCIwMSBcdTIwMTQgUHJvamVjdCBTdGF0ZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9wbGFucy8wMS1QUk9KRUNULVNUQVRFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIjAyIFx1MjAxNCBVbmlmaWVkIFdvcmsgQnJlYWtkb3duIFN0cnVjdHVyZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9wbGFucy8wMi1VTklGSUVELVdCUy5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCIwMyBcdTIwMTQgVW5pZmllZCBEQUcgU3BlY2lmaWNhdGlvbnNcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcGxhbnMvMDMtVU5JRklFRC1EQUcubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiMDQgXHUyMDE0IFVuaWZpZWQgUmVxdWlyZW1lbnRzXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zLzA0LVJFUVVJUkVNRU5UUy5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCIwNSBcdTIwMTQgQXJjaGl0ZWN0dXJlICYgUGF0dGVybnNcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcGxhbnMvMDUtQVJDSElURUNUVVJFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIjA2IFx1MjAxNCBJbXBsZW1lbnRhdGlvbiBHdWlkZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9wbGFucy8wNi1JTVBMRU1FTlRBVElPTi1HVUlERS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCIwNyBcdTIwMTQgVGVzdCBTdHJhdGVneVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9wbGFucy8wNy1URVNULVNUUkFURUdZLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIjA4IFx1MjAxNCBPcHRpbWl6YXRpb24sIFBvbGlzaCwgRW5oYW5jZW1lbnQgJiBSb2J1c3RuZXNzIENhdGFsb2dcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcGxhbnMvMDgtT1BUSU1JWkFUSU9OLUNBVEFMT0cubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiMDkgXHUyMDE0IFJpc2sgUmVnaXN0cnkgJiBBbnRpLVBhdHRlcm5zXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zLzA5LVJJU0stUkVHSVNUUlkubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiMTAgXHUyMDE0IFN1YmFnZW50IERpc3BhdGNoIFBsYW5cIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcGxhbnMvMTAtU1VCQUdFTlQtRElTUEFUQ0gubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiMTIgXHUyMDE0IEN5Y2xlbG9vcCBMb29wcyAmIENoZWNrZXIgQWdlbnQgRGVzaWduXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zLzEyLUxJRkVDWUNMRS1MT09QLURFU0lHTi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJEZXNpZ246IHRoZWdlbnQgaW5zdGFsbCBDTEkgQ29tbWFuZFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9wbGFucy8yMDI2LTAyLTE0LXRoZWdlbnQtaW5zdGFsbC1kZXNpZ24ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwidGhlZ2VudCBpbnN0YWxsIEltcGxlbWVudGF0aW9uIFBsYW5cIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcGxhbnMvMjAyNi0wMi0xNC10aGVnZW50LWluc3RhbGwtaW1wbGVtZW50YXRpb24tcGxhbi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJSZXNlYXJjaCBhbmQgRWxpY2l0YXRpb24gUGxhbiBcdTIwMTQgMjAyNi0wMi0xNVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9wbGFucy8yMDI2LTAyLTE1LVJFU0VBUkNILUFORC1FTElDSVRBVElPTi1QTEFOLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcInRoZWdlbnQgc2l0YmFjayBcdTIwMTQgRGVzaWduICYgSW1wbGVtZW50YXRpb24gUGxhblwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9wbGFucy8yMDI2LTAyLTE1LXRoZWdlbnQtc2l0YmFjay1kZXNpZ24ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVHJheSBBcHBsaWNhdGlvbiBEZXNpZ24gLSBQbHVnaW4tQmFzZWQgQXJjaGl0ZWN0dXJlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zLzIwMjYtMDItMTUtdHJheS1hcHBsaWNhdGlvbi1kZXNpZ24ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQWdlbnREZXBsb3llciArIExpZmVjeWNsZUNvbnRyb2xsZXIgSW50ZWdyYXRpb24gUmV2aWV3XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zLzIwMjYtMDItMTYtQUdFTlRfREVQTE9ZRVJfUkVWSUVXLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkN5Y2xlbG9vcCArIEFnaWxlUGx1cyBJbnRlZ3JhdGlvbiBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zLzIwMjYtMDItMTYtQ1lDTEVMT09QX0FHSUxFUExVU19JTlRFR1JBVElPTi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJGdWxsIExpdGVMTE0gRmVhdHVyZSBJbnRlZ3JhdGlvbiBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zLzIwMjYtMDItMTYtbGl0ZWxsbS1mdWxsLWZlYXR1cmVzLXBsYW4ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiTGl0ZUxMTSBJbnRlZ3JhdGlvbiBEZXNpZ25cIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcGxhbnMvMjAyNi0wMi0xNi1saXRlbGxtLWludGVncmF0aW9uLWRlc2lnbi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJMaXRlTExNIFJvdXRlciBJbnRlZ3JhdGlvbiBJbXBsZW1lbnRhdGlvbiBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zLzIwMjYtMDItMTYtbGl0ZWxsbS1pbnRlZ3JhdGlvbi1wbGFuLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlN1cGVybWVtb3J5LmFpIEludGVncmF0aW9uIFBsYW4gKFdQLTUwMDEtU00pXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zLzIwMjYtMDItMTYtc3VwZXJtZW1vcnktaW50ZWdyYXRpb24tcGxhbi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJBZ2VudCBTYW5kYm94aW5nIEltcGxlbWVudGF0aW9uIFBsYW5cIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcGxhbnMvQUdFTlRfU0FOREJPWElOR19JTVBMRU1FTlRBVElPTl9QTEFOLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkNhdGFsb2cgXHUyMTk0IENMSVByb3h5QVBJUGx1cyBGb3JrIEFsaWdubWVudFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9wbGFucy9DQVRBTE9HX0NMSVBST1hZX0ZPUktfQUxJR05NRU5ULm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkNMSVByb3h5QVBJICYgVGhlZ2VudCBXb3JrIFBsYW4gXHUyMDEzIFVuaWZpZWQgUGhhc2VkIFdCU1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9wbGFucy9DTElQUk9YWV9BUElfQU5EX1RIR0VOVF9VTklGSUVEX1BMQU4ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQWdlbnQgT3JjaGVzdHJhdGlvbiBIYXJuZXNzOiBNdWx0aS1QbGF0Zm9ybSAoRXh0cmVtZS1EZXB0aCBQbGFuKVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9wbGFucy9DT0RFWF9ET05VVF9IQVJORVNTX1BMQU4ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQ3Jvc3MtUGxhdGZvcm0gTXVsdGktVGVuYW50IERlc2t0b3AgQXV0b21hdGlvbiBDb21wbGV0ZSBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL0NST1NTX1BMQVRGT1JNX0NPTVBMRVRFX1BMQU4ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQ3Jvc3MtUGxhdGZvcm0gTXVsdGktVGVuYW50IERlc2t0b3AgQXV0b21hdGlvbiBJbXBsZW1lbnRhdGlvbiBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL0NST1NTX1BMQVRGT1JNX01VTFRJX1RFTkFOVF9JTVBMRU1FTlRBVElPTl9QTEFOLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkN1cnNvciBBUEkgSW50ZWdyYXRpb24gUmVzZWFyY2ggJiBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL0NVUlNPUl9BUElfSU5URUdSQVRJT05fUkVTRUFSQ0gubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiRGVidWcgVGFncyBhbmQgTWV0cmljcyAoVHJhbnNpZW50IFJlc3BvbnNlIFRhZ3MpXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL0RFQlVHX1RBR1NfQU5EX01FVFJJQ1MubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiRGlzdHJpYnV0ZWQgTW9kZWwgUm91dGluZyBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL0RJU1RSSUJVVEVEX01PREVMX1JPVVRJTkdfUExBTi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJEb2N1bWVudGF0aW9uIEV4cGFuc2lvbiBQcm9jZXNzXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL0RPQ1VNRU5UQVRJT05fRVhQQU5TSU9OX1BST0NFU1MubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiRG9jdW1lbnRhdGlvbiBFeHBhbnNpb24gVE9ET1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9wbGFucy9ET0NVTUVOVEFUSU9OX0VYUEFOU0lPTl9UT0RPLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkRvY3VtZW50YXRpb24gQ29uc29saWRhdGlvbiAmIEltcGxlbWVudGF0aW9uIFdCU1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9wbGFucy9ET0NfQ09OU09MSURBVElPTl9BTkRfSU1QTEVNRU5UQVRJT05fV0JTLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkZhY3RvcnkgRHJvaWQgSGFybmVzcyBJbnRlZ3JhdGlvbiBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL0ZBQ1RPUllfRFJPSURfSEFSTkVTU19JTlRFR1JBVElPTl9QTEFOLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkZ1bGwgU2hlbGwgXHUyMTkyIFJ1c3QgV2hlcmUgQmVuZWZpY2lhbFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9wbGFucy9GVUxMX1NIRUxMX1RPX1JVU1RfV0hFUkVfQkVORUZJQ0lBTC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJIb2xpc3RpYyArIEhhcm1vbmlvdXMgRGVzaWduICYgRnVsbCBJbnRlZ3JhdGlvbiBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL0hPTElTVElDX0hBUk1PTklPVVNfREVTSUdOX0FORF9JTlRFR1JBVElPTl9QTEFOLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkhvb2sgUnVudGltZSBSdXN0IE1pZ3JhdGlvbiBDb21wbGV0ZSBHdWlkZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9wbGFucy9IT09LX1JVTlRJTUVfUlVTVF9DT01QTEVURS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJIb29rIFJ1bnRpbWU6IEZ1bGwgUnVzdCBNaWdyYXRpb24gRGVzaWduIChEZWVwICYgV2lkZSlcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcGxhbnMvSE9PS19SVU5USU1FX1JVU1RfREVTSUdOLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkh5YnJpZCBNYWMvV2luZG93cyBFbnZpcm9ubWVudCBJbXBsZW1lbnRhdGlvbiBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL0hZQlJJRF9FTlZfSU1QTEVNRU5UQVRJT05fUExBTi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJMaXRlTExNICsgQ0xJUHJveHlBUElQbHVzICsgQmlmcm9zdCBIYXJtb255XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL0xJVEVMTE1fQ0xJUFJPWFlfQklGUk9TVF9IQVJNT05ZLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIk1DUCBCdW5kbGU6IHRoZWdlbnQgKyBCcm93c2VyIFRvb2xzIChSZXBsYWNlIE1hbnVhbCBQbGF5d3JpZ2h0KVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9wbGFucy9NQ1BfQlVORExFX1BMQVlXUklHSFRfUkVQTEFDRU1FTlQubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiTUNQIFRvb2wgT3B0aW1pemF0aW9uLCBQb2xpc2ggJiBFbmhhbmNlbWVudCBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL01DUF9UT09MX09QVElNSVpBVElPTl9QTEFOLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIk11bHRpLVBsYXRmb3JtIFBhcml0eSBNYXN0ZXIgUGxhbiAmIE1hdHJpeFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9wbGFucy9NVUxUSV9QTEFURk9STV9QQVJJVFlfTUFTVEVSX1BMQU4ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiTmV3IFByb3ZpZGVycyBBdXRoIFJlc2VhcmNoICYgUGxhblwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9wbGFucy9ORVdfUFJPVklERVJTX0FVVEhfUkVTRUFSQ0gubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiT3BlblJvdXRlci1TdHlsZSBSb3V0aW5nICsgQ0xJUHJveHlBUElQbHVzIEludGVncmF0aW9uXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL09QRU5ST1VURVJfU1RZTEVfUk9VVElOR19BTkRfQ0xJUFJPWFkubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUHJvY2VzcyAmIFRvb2wgT3B0aW1pemF0aW9uIENvbXBsZXRlIFBsYW5cIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcGxhbnMvUFJPQ0VTU19PUFRJTUlaQVRJT05fQ09NUExFVEVfUExBTi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJQcm9jZXNzIGFuZCBUb29sIE9wdGltaXphdGlvbiBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL1BST0NFU1NfT1BUSU1JWkFUSU9OX1BMQU4ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUHJvbXB0IEhpc3RvcnkgQ29sbGVjdGlvbiAmIEF1ZGl0IFN5c3RlbTogQ29tcHJlaGVuc2l2ZSBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL1BST01QVF9ISVNUT1JZX0NPTExFQ1RJT05fQU5EX0FVRElUX1NZU1RFTS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJQcm9tcHQgSGlzdG9yeSBDb2xsZWN0aW9uICYgQXVkaXQgU3lzdGVtIENvbXBsZXRlIEd1aWRlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL1BST01QVF9ISVNUT1JZX0NPTExFQ1RJT05fQ09NUExFVEUubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUmVtb3RlIENvbXB1dGUgSW1wbGVtZW50YXRpb24gRGV0YWlsXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL1JFTU9URV9DT01QVVRFX0lNUExFTUVOVEFUSU9OX0RFVEFJTC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJ0aGVnZW50IFNldHVwOiBQcm9wb3NlZCBIb29rcywgUGx1Z2lucywgU2tpbGxzLCBNQ1AgJiBEb2NzXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL1NFVFVQX1BST1BPU0VEX0lURU1TLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlNoZWxsIEVudmlyb25tZW50IEFkdmFuY2VkIEVuaGFuY2VtZW50IFBsYW5cIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcGxhbnMvU0hFTExfRU5WSVJPTk1FTlRfQURWQU5DRURfRU5IQU5DRU1FTlRfUExBTi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJTaGVsbCBFbnZpcm9ubWVudCBBZHZhbmNlZCBFbmhhbmNlbWVudCAtIEltcGxlbWVudGF0aW9uIFN1bW1hcnlcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcGxhbnMvU0hFTExfRU5WSVJPTk1FTlRfQURWQU5DRURfSU1QTEVNRU5UQVRJT05fU1VNTUFSWS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJTaGVsbCBFbnZpcm9ubWVudCBDb21wbGV0ZSBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL1NIRUxMX0VOVklST05NRU5UX0NPTVBMRVRFX1BMQU4ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiU2hlbGwgRW52aXJvbm1lbnQgSW1wbGVtZW50YXRpb24gU3VtbWFyeVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9wbGFucy9TSEVMTF9FTlZJUk9OTUVOVF9JTVBMRU1FTlRBVElPTl9TVU1NQVJZLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlNoZWxsIEVudmlyb25tZW50IE9wdGltaXphdGlvbiAmIEVuaGFuY2VtZW50IFBsYW5cIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcGxhbnMvU0hFTExfRU5WSVJPTk1FTlRfT1BUSU1JWkFUSU9OX1BMQU4ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiU3luYy9VcGRhdGUgQ29tbWFuZCAmIEZ1bGwgU3lzdGVtIEF1ZGl0IFBsYW5cIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcGxhbnMvU1lOQ19VUERBVEVfQ09NTUFORF9BTkRfU1lTVEVNX0FVRElUX1BMQU4ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBGYXN0TUNQIDMuMCBJbXBsZW1lbnRhdGlvbiBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL1RIR0VOVF9GQVNUTUNQX0lNUExFTUVOVEFUSU9OX1BMQU4ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUnVudGltZSBEaXNwYXRjaCBDb25zb2xpZGF0aW9uICYgRm9yayBGaXg6IENvbXBsZXRlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL1VMVFJBX1NISU1fQ09OU09MSURBVElPTl9DT01QTEVURS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJVbHRyYS1TaGltIEZvcmsgRmFpbHVyZSBGaXg6IFJvb3QgQ2F1c2UgQW5hbHlzaXMgJiBTb2x1dGlvblwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9wbGFucy9VTFRSQV9TSElNX0ZPUktfRkFJTFVSRV9GSVgubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVW5pZmllZCBMb2dpbiBGbG93OiBPcGVuIFVSTCArIFByb21wdCBmb3IgS2V5XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL1VOSUZJRURfTE9HSU5fRkxPVy5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJVbmlmaWVkIFN5c3RlbSBBcHBsaWNhdGlvbiBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL1VOSUZJRURfU1lTVEVNX0FQUExJQ0FUSU9OX1BMQU4ubWRcIlxuICAgICAgICB9XG4gICAgICBdXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJSZWZlcmVuY2VcIixcbiAgICAgIFwiY29sbGFwc2VkXCI6IGZhbHNlLFxuICAgICAgXCJpdGVtc1wiOiBbXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJSb3V0aW5nIFN5c3RlbTogUHJvamVjdCBDb21wbGV0ZSBTdW1tYXJ5XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS8wMF9ST1VUSU5HX1BST0pFQ1RfQ09NUExFVEUubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQWdlbnQgSWRlbnRpdHkgJiBTb3ZlcmVpZ250eSBEZXB0aCAoV1AtNjAwNClcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL0FHRU5UX0lERU5USVRZX1NPVkVSRUlHTlRZX0RFUFRILm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkFnZW50IENvbW11bmljYXRpb24gTGFuZ3VhZ2UgKEpTT04tQUNMKSAmIE5lZ290aWF0aW9uIChXUC0xMDA2KVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvQUdFTlRfTkVHT1RJQVRJT05fQUNMX0RFUFRILm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkFnZW50IE9TIFByaW5jaXBhbHMgXHUyMDE0IERlcHRoIERvY3VtZW50XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9BR0VOVF9PU19QUklOQ0lQQUxTX0RFUFRILm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkJlbmNobWFyayBDb21wYXJpc29uOiBTV0UtQmVuY2ggdnMgVGVybWluYWwgQmVuY2ggMi4wXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9CRU5DSE1BUktfQ09NUEFSSVNPTl9TV0VfQkVOQ0hfVlNfVEVSTUlOQUxfQkVOQ0hfMl8wLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkdsb2JhbCBDbGF1ZGUgQ29kZSBJbnN0cnVjdGlvbnNcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL0NMQVVERV9DT1JFX0dVSURFTElORVMubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQ0xBVURFIEFwcGVuZGl4OiB0aGVnZW50LXNwZWNpZmljIGFuZCBkb21haW4gd29ya2Zsb3cgcnVsZXNcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL0NMQVVERV9USEVHRU5UX1JVTlRJTUVfQVBQRU5ESVgubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQ29tcGxldGUgUHJvdmlkZXIgUm91dGluZyBNYXAgKEFsbCAxMisgUHJvdmlkZXJzKVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvQ09NUExFVEVfUFJPVklERVJfUk9VVElOR19NQVAubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQ29uc3RpdHV0aW9uYWwgRW5mb3JjZW1lbnQgJiBQcm9vZiBvZiBBbGlnbm1lbnQgKFdQLTMwMDEpXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9DT05TVElUVVRJT05BTF9FTkZPUkNFTUVOVF9ERVBUSC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJDb250ZXh0IE1hbmFnZW1lbnQgJiBTZW1hbnRpYyBDb21wcmVzc2lvbiBEZXB0aCAoV1AtNTAwMSlcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL0NPTlRFWFRfTUFOQUdFTUVOVF9ERVBUSC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJDb3N0IEVuZm9yY2VtZW50IFBvbGljeTogMnggTGltaXQgJiBFc2NhbGF0aW9uIEZyYW1ld29ya1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvQ09TVF9FTkZPUkNFTUVOVF9QT0xJQ1kubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQ3Jvc3MtUGxhdGZvcm0gRGVza3RvcCBBdXRvbWF0aW9uOiBBUEkgUmVmZXJlbmNlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9DUk9TU19QTEFURk9STV9BUElfUkVGRVJFTkNFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkNyb3NzLVBsYXRmb3JtIE11bHRpLVRlbmFudCBEZXNrdG9wIEF1dG9tYXRpb24gUXVpY2sgUmVmZXJlbmNlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9DUk9TU19QTEFURk9STV9NVUxUSV9URU5BTlRfUVVJQ0tfUkVGRVJFTkNFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkRvbWluYW5jZSBQcm9vZiBSZWZlcmVuY2VcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL0RPTUlOQU5DRV9QUk9PRl9SRUZFUkVOQ0UubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiRWNvbm9taWMgR292ZXJuYW5jZSAmIFRva2VuIFJPSSBNb2RlbGluZyAoV1AtNTAwMylcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL0VDT05PTUlDX0dPVkVSTkFOQ0VfREVQVEgubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiRnJvbnRtYXR0ZXIvQmFja21hdHRlciBJbnRlZ3JhdGlvbiBQb2ludHNcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL0ZST05UTUFUVEVSX0JBQ0tNQVRURVJfSU5URUdSQVRJT05fUE9JTlRTLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkZSIFRyYWNrZXI6IHRoZWdlbnRcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL0ZSX1RSQUNLRVIubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiR2FyZGVuZXIgQXJjaGl0ZWN0dXJlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9HQVJERU5FUl9BUkNISVRFQ1RVUkUubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiSHVtYW4tQWdlbnQgQ29sbGFib3JhdGlvbiAoSEFDKSAmIEhJVEwgUGF0dGVybnMgKFdQLTQwMDEuLjQwMDkpXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9IQUNfQU5EX0hJVExfUEFUVEVSTlMubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiSG9vayBPcHRpbWl6YXRpb24gU3RyYXRlZ3lcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL0hPT0tfT1BUSU1JWkFUSU9OX1NUUkFURUdZLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkh5YnJpZCBNYWMvV2luZG93cyBEZXZlbG9wbWVudCBFbnZpcm9ubWVudCAtIFN1bW1hcnlcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL0hZQlJJRF9FTlZfU1VNTUFSWS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJJbmRleGluZyBhbmQgT3B0aW1pemF0aW9uIFN5c3RlbXMgXHUyMDE0IFJlZmVyZW5jZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvSU5ERVhJTkdfQU5EX09QVElNSVpBVElPTl9TWVNURU1TLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRhc2tSb3V0ZXIgKyBQYXJldG8gUm91dGluZyBJbnRlZ3JhdGlvbiBBcmNoaXRlY3R1cmVcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL0lOVEVHUkFUSU9OX0FSQ0hJVEVDVFVSRS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUYXNrUm91dGVyICsgUGFyZXRvIFJvdXRpbmcgSW50ZWdyYXRpb24gXHUyMDE0IERvY3VtZW50IEluZGV4XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9JTlRFR1JBVElPTl9JTkRFWC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUYXNrUm91dGVyIEludGVncmF0aW9uIFF1aWNrIFN0YXJ0XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9JTlRFR1JBVElPTl9RVUlDS19TVEFSVC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJNQUlGIEFydGlmYWN0IFNwZWNpZmljYXRpb24gJiBQcm92ZW5hbmNlIERlcHRoIChXUC0zMDAyKVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvTUFJRl9BUlRJRkFDVF9TUEVDX0RFUFRILm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIk1DUCBUb29sIFJldHJ5IFBvbGljeVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvTUNQX1JFVFJZX1BPTElDWS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJDb3JyZWN0ZWQgTW9kZWwgUmFua2luZyBVc2luZyBQYXJldG8gRnJvbnRpZXJcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL01PREVMX1JBTktJTkdfQ09SUkVDVEVELm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIk1vZGVsIFJvdXRpbmcgRGVjaXNpb24gVHJlZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvTU9ERUxfUk9VVElOR19ERUNJU0lPTl9UUkVFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIk1vZGVsIFJvdXRpbmcgJiBDb3N0IEdvdmVybmFuY2U6IENvbXBsZXRlIEluZGV4XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9NT0RFTF9ST1VUSU5HX0lOREVYLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIk1vZGVsIFJvdXRpbmcgJiBDb3N0IEdvdmVybmFuY2U6IFF1aWNrIFJlZmVyZW5jZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvTU9ERUxfUk9VVElOR19TVU1NQVJZLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIk1vZGVsIFJvdXRpbmc6IFRlcm1pbmFsIEJlbmNoIDIuMCBRdWljayBSZWZlcmVuY2VcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL01PREVMX1JPVVRJTkdfVEVSTUlOQUxfQkVOQ0hfMl8wX1FVSUNLX1JFRi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJNb2RlbCBTZWxlY3Rpb24gRG9jdW1lbnRhdGlvbiBJbmRleFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvTU9ERUxfU0VMRUNUSU9OX0lOREVYLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIk1vbml0b3JpbmcgQWxlcnQgUnVsZXNcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL01PTklUT1JJTkdfQUxFUlRfUlVMRVMubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiTW9uaXRvcmluZyBEYXNoYm9hcmQgU3BlY2lmaWNhdGlvbnNcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL01PTklUT1JJTkdfREFTSEJPQVJEX1NQRUMubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiTW9uaXRvcmluZyBNZXRyaWNzIFJlZmVyZW5jZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvTU9OSVRPUklOR19NRVRSSUNTX1JFRkVSRU5DRS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJNb25pdG9yaW5nIFN5c3RlbSBEb2N1bWVudGF0aW9uXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9NT05JVE9SSU5HX1JFQURNRS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJNb25pdG9yaW5nIFNldHVwIEd1aWRlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9NT05JVE9SSU5HX1NFVFVQX0dVSURFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkNpdmlsaXphdGlvbmFsIE11bHRpLVN3YXJtIEhpZXJhcmNoeSAoV1AtMTAwNiwgV1AtNTAwNClcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL01VTFRJX1NXQVJNX0hJRVJBUkNIWV9ERVBUSC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJPcGVuVGVsZW1ldHJ5IEdlbkFJICYgT2JzZXJ2YWJpbGl0eSBEZXB0aCAoV1AtWTYpXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9PVEVMX0dFTkFJX0FORF9IWVNURVJFU0lTX0RFUFRILm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIm94bGludCBSdWxlIE1hcHBpbmcgUmVmZXJlbmNlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9PWExJTlRfUlVMRV9NQVBQSU5HLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlBhcmV0byBGcm9udGllciBBbGdvcml0aG06IFBzZXVkb2NvZGUgJiBJbXBsZW1lbnRhdGlvbiBHdWlkZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvUEFSRVRPX0FMR09SSVRITV9QU0VVRE9DT0RFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlBhcmV0byBGcm9udGllcjogRXhlY3V0aXZlIFN1bW1hcnlcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL1BBUkVUT19FWEVDVVRJVkVfU1VNTUFSWS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJQYXJldG8gRnJvbnRpZXIgQW5hbHlzaXMgJiBNb2RlbCBSYW5raW5nIEFsZ29yaXRobVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvUEFSRVRPX0ZST05USUVSX0FOQUxZU0lTLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlBhcmV0byBGcm9udGllciBBbmFseXNpczogQ29tcGxldGUgTW9kZWwgRXZhbHVhdGlvblwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvUEFSRVRPX0ZST05USUVSX0NPTVBMRVRFX0FOQUxZU0lTLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlBhcmV0byBGcm9udGllciBNYXRyaXg6IE1vZGVsIFNlbGVjdGlvbiBHdWlkZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvUEFSRVRPX0ZST05USUVSX01BVFJJWC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJQYXJldG8gRnJvbnRpZXIgUXVpY2sgUmVmZXJlbmNlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9QQVJFVE9fRlJPTlRJRVJfUVVJQ0tfUkVGRVJFTkNFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlBhcmV0byBGcm9udGllciBBbmFseXNpczogQ29tcGxldGUgRGF0YSBUYWJsZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvUEFSRVRPX0ZST05USUVSX1RBQkxFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlBhcmV0byBGcm9udGllciBBbmFseXNpczogVGVybWluYWwgQmVuY2ggMi4wIChDb3JyZWN0ZWQpXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9QQVJFVE9fRlJPTlRJRVJfVEVSTUlOQUxfQkVOQ0hfMl8wLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlBhcmV0byBGcm9udGllciBBbmFseXNpczogQ29tcGxldGUgSW5kZXhcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL1BBUkVUT19JTkRFWC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJNdWx0aS1PYmplY3RpdmUgUHJvdmlkZXIgUm91dGluZyAmIFBhcmV0byBGcm9udHMgKFdQLTEwMDQpXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9QQVJFVE9fUk9VVElOR19ERVNJR04ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUGFyZXRvIEZyb250aWVyIFZpc3VhbGl6YXRpb24gJiBEaWFncmFtc1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvUEFSRVRPX1ZJU1VBTElaQVRJT04ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUGhhc2UgMy41IFF1aWNrIFJlZmVyZW5jZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvUEhBU0VfM181X1FVSUNLX1JFRkVSRU5DRS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJQaGFzZSA0IFVYOiBPcGVyYXRvciBDb2NrcGl0ICYgUmF0aW9uYWxlIERlcHRoIChXUC00MDAxKVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvUEhBU0VfNF9DT0NLUElUX1VYX0RFUFRILm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlBoYXNlIDUgU2NhbGU6IFJlZGlzICYgRGlzdHJpYnV0ZWQgUm9idXN0bmVzcyAoV1AtNTAwNClcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL1BIQVNFXzVfU0NBTEVfUk9CVVNUTkVTU19ERVBUSC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJQT1NJWCArIHB3c2ggU2hlbGwgU3RyYXRlZ3lcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL1BPU0lYX1BXU0hfU0hFTExfU1RSQVRFR1kubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUHJvdmlkZXIgTGltaXRzIGFuZCBBdXRvLUZhbGxiYWNrXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9QUk9WSURFUl9MSU1JVFNfQU5EX0ZBTExCQUNLLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlByb3ZpZGVyIE1vZGVsIEJlaGF2aW9yIENvbnN0cmFpbnRzXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9QUk9WSURFUl9NT0RFTF9CRUhBVklPUi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJQcm92aWRlciBNb2RlbCBSZWZlcmVuY2VcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL1BST1ZJREVSX01PREVMX1JFRkVSRU5DRS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJSb2J1c3RuZXNzLCBCcmVhZHRoLCBhbmQgRGVwdGggXHUyMDE0IFBoYXNlIEV2b2x1dGlvblwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvUk9CVVNUTkVTU19BTkRfRlVUVVJFX0RFUFRILm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlJvdXRpbmcgRGVjaXNpb24gTWF0cml4OiBUYXNrIENhdGVnb3J5IExvZ2ljXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9ST1VUSU5HX0RFQ0lTSU9OX01BVFJJWC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJGaW5hbCBSb3V0aW5nIFJlY29tbWVuZGF0aW9uIChUZXJtaW5hbCBCZW5jaCAyLjApXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9ST1VUSU5HX0ZJTkFMX1JFQ09NTUVOREFUSU9OLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRhc2sgUm91dGluZyBJbXBsZW1lbnRhdGlvbiBBcmNoaXRlY3R1cmVcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL1JPVVRJTkdfSU1QTEVNRU5UQVRJT05fQVJDSElURUNUVVJFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIk1vZGVsIFJvdXRpbmcgUXVpY2sgQ2FyZCAoUG9ja2V0IFJlZmVyZW5jZSlcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL1JPVVRJTkdfUVVJQ0tfQ0FSRC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJSb3V0aW5nIFN5c3RlbTogTWFzdGVyIFN1bW1hcnkgJiBJbXBsZW1lbnRhdGlvbiBSb2FkbWFwXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9ST1VUSU5HX1NZU1RFTV9NQVNURVJfU1VNTUFSWS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJSdXN0LUJhc2VkIENMSSBUb29saW5nXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9SVVNUX1RPT0xJTkcubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQWdlbnRpYyBDSS9DRCAmIFNlbGYtSGVhbGluZyBMb29wcyAoV1AtMjAwNClcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL1NFTEZfSEVBTElOR19BR0VOVElDX0NJQ0RfREVQVEgubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUGxhbm5pbmcgU2ltdWxhdGlvbiAmIFJlcGxheSBTYW5kYm94IERlcHRoIChXUC00MDA3LCBXUC0xMjAwNClcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL1NJTVVMQVRJT05fQU5EX1NBTkRCT1hfREVQVEgubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiTUNQIFRvb2wgU0xPIFRhcmdldHMgKEctT1AtMDgpXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9TTE9fVEFSR0VUUy5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJTcGVlZCAmIFF1YWxpdHkgSW5kZXggSW1wbGVtZW50YXRpb24gUGxhblwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvU1BFRURfUVVBTElUWV9JTkRFWF9JTVBMRU1FTlRBVElPTl9QTEFOLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlN0YXJzaGlwIFByb21wdCBcdTIwMTQgTG9uZy1UZXJtIEZpeCBmb3IgU2NhbiBUaW1lb3V0XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9TVEFSU0hJUF9TRVRVUC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJTd2FybSBNZW1vcnkgJiBNdWx0aS1BZ2VudCBDb29yZGluYXRpb24gKFdQLTEwMDYpXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9TV0FSTV9NRU1PUllfQ09PUkRJTkFUSU9OX0RFUFRILm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlN3YXJtIFByb2Nlc3MgT3B0aW1pemF0aW9ucyAoTXVsdGktQWdlbnQgLyBNdWx0aS1UZW5hbnQgLyBNdWx0aS1Qcm9qZWN0KVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvU1dBUk1fUFJPQ0VTU19PUFRJTUlaQVRJT05TLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRhc2sgQ2F0ZWdvcml6YXRpb24gJiBBSSBBZ2VudCBEaXNwYXRjaCBSb3V0aW5nIERlc2lnblwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvVEFTS19ST1VUSU5HX0RFU0lHTi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUZXJtaW5hbCBCZW5jaCAyLjA6IENvcnJlY3RlZCBQYXJldG8gRnJvbnRpZXIgJiBSb3V0aW5nXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9URVJNSU5BTF9CRU5DSF8yXzBfQ09SUkVDVEVEX0ZST05USUVSLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRvb2xpbmcgJiBHbG9iYWwgT3B0aW1pemF0aW9ucyBBdWRpdCAoSW4tRGVwdGgpXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9UT09MSU5HX0FORF9HTE9CQUxfT1BUSU1JWkFUSU9OU19BVURJVC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUb29saW5nIGFuZCBHbG9iYWwgT3B0aW1pemF0aW9ucyBBdWRpdFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvVE9PTElOR19BTkRfT1BUSU1JWkFUSU9OX0FVRElULm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRvdWNocG9pbnQgSW50ZWdyYXRpb24gXHUyMDE0IERlZXAgRGl2ZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvVE9VQ0hQT0lOVF9JTlRFR1JBVElPTl9ERUVQX0RJVkUubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVG91Y2hwb2ludCBJbnRlZ3JhdGlvbiBFdmFsdWF0aW9uXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9UT1VDSFBPSU5UX0lOVEVHUkFUSU9OX0VWQUxVQVRJT04ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVW5pZmllZCBXb3JrIFN0cmVhbSBcdTIwMTQgRGVzaWduXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9VTklGSUVEX1dPUktfU1RSRUFNX0RFU0lHTi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJXQlMgQWdlbnQgUHJvZ3Jlc3MgXHUyMDE0IENsYWltICYgQ29vcmRpbmF0aW9uXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9XQlNfQUdFTlRfUFJPR1JFU1MubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVW5pZmllZCBXb3JrIFN0cmVhbSBcdTIwMTQgQ2Fub25pY2FsXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9XT1JLX1NUUkVBTS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJaZW4gKE9wZW5Db2RlKSBJbnRlZ3JhdGlvbiBBbmFseXNpc1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvWkVOX0lOVEVHUkFUSU9OLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlJlZmVyZW5jZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvaW5kZXgubWRcIlxuICAgICAgICB9XG4gICAgICBdXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJSZXBvcnRzXCIsXG4gICAgICBcImNvbGxhcHNlZFwiOiBmYWxzZSxcbiAgICAgIFwiaXRlbXNcIjogW1xuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQktNIFBoYXNlIDEgQ29tcGxldGlvbiBSZXBvcnRcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVwb3J0cy9CS01fUEhBU0VfMV9DT01QTEVUSU9OX1JFUE9SVC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJDcml0aWNhbCBJc3N1ZSAjMjogR2l0IENhY2hlIEludmFsaWRhdGlvbiBGaXggLSBDb21wbGV0ZSBSZXBvcnRcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVwb3J0cy9DQUNIRV9JTlZBTElEQVRJT05fRklYX1JFUE9SVC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJDcml0aWNhbCBJc3N1ZXMgRml4ZXMgLSBDb21wbGV0aW9uIFJlcG9ydFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXBvcnRzL0NSSVRJQ0FMX0ZJWEVTX0NPTVBMRVRJT05fUkVQT1JULm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkNyaXRpY2FsIElzc3VlICMyOiBVbnNhZmUgR2l0IENhY2hlIEludmFsaWRhdGlvbiAtIEV4ZWN1dGl2ZSBTdW1tYXJ5XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlcG9ydHMvQ1JJVElDQUxfSVNTVUVfMl9TVU1NQVJZLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlBoYXNlIDEwLTEyIENsb3N1cmUgYW5kIEZpbmFsIEhhbmRvZmYgTm90ZSAoV1AtMTIwMTApXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlcG9ydHMvRklOQUxfQ0xPU1VSRV9OT1RFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkhvbGlzdGljICsgSGFybW9uaW91cyBEZXNpZ24gJiBJbnRlZ3JhdGlvbiBcdTIwMTQgSW1wbGVtZW50YXRpb24gQ29tcGxldGUgXHUyNzA1XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlcG9ydHMvSE9MSVNUSUNfREVTSUdOX0lNUExFTUVOVEFUSU9OX0NPTVBMRVRFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkhvbGlzdGljICsgSGFybW9uaW91cyBEZXNpZ24gJiBJbnRlZ3JhdGlvbiBcdTIwMTQgSW1wbGVtZW50YXRpb24gUHJvZ3Jlc3NcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVwb3J0cy9IT0xJU1RJQ19ERVNJR05fSU1QTEVNRU5UQVRJT05fUFJPR1JFU1MubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBJbXBsZW1lbnRhdGlvbiBTdGF0dXMgUmVwb3J0XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlcG9ydHMvSU1QTEVNRU5UQVRJT05fU1RBVFVTLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgSW1wbGVtZW50YXRpb24gU3VtbWFyeVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXBvcnRzL0lNUExFTUVOVEFUSU9OX1NVTU1BUlkubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUDcuMSBWZXJpZmljYXRpb24gUmVwb3J0OiBQZXItUHJvamVjdCBRdWFsaXR5IEdhdGUgQ2hlY2tzXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlcG9ydHMvUDcuMV9WRVJJRklDQVRJT05fUkVQT1JULm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlA3LjIgQ3Jvc3MtUHJvamVjdCBDb25zaXN0ZW5jeSBSZXBvcnRcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVwb3J0cy9QNy4yX0NST1NTX1BST0pFQ1RfQ09OU0lTVEVOQ1kubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUGhhc2UgMTAtMTIgQ2xvc3VyZSBhbmQgSGFuZG9mZiBOb3RlIChXUC0xMjAxMClcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVwb3J0cy9QSEFTRV8xMF8xMl9DTE9TVVJFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlBoYXNlIDEzOiBQb2xpY3kgRmVkZXJhdGlvbiBQcm9ncmVzcyBSZXBvcnRcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVwb3J0cy9QSEFTRV8xM19QUk9HUkVTU19SRVBPUlQubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUGhhc2UgMTQ6IEF1dG9ub21vdXMgTGVhcm5pbmcgYW5kIENvc3QgU2Vuc2luZyBQcm9ncmVzcyBSZXBvcnRcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVwb3J0cy9QSEFTRV8xNF9QUk9HUkVTU19SRVBPUlQubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUGhhc2UgMTU6IEVudGVycHJpc2UgTGlmZWN5Y2xlIGFuZCBDb21wbGlhbmNlIFByb2dyZXNzIFJlcG9ydFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXBvcnRzL1BIQVNFXzE1X1BST0dSRVNTX1JFUE9SVC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJQaGFzZSAzLjUgT3B0aW1pemF0aW9uIFN1bW1hcnlcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVwb3J0cy9QSEFTRV8zXzVfU1VNTUFSWS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJQaGFzZSAzLjUgT3B0aW1pemF0aW9uIFZhbGlkYXRpb24gUmVwb3J0XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlcG9ydHMvUEhBU0VfM181X1ZBTElEQVRJT04ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUGhhc2UgMzogSm9iIFBvb2wgSW1wbGVtZW50YXRpb24gLSBDb21wbGV0aW9uIFN1bW1hcnlcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVwb3J0cy9QSEFTRV8zX0NPTVBMRVRJT05fU1VNTUFSWS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJQaGFzZSAzIC0gSm9iIFBvb2wgSW1wbGVtZW50YXRpb24gUmVwb3J0XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlcG9ydHMvUEhBU0VfM19KT0JfUE9PTF9JTVBMRU1FTlRBVElPTi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJQaGFzZSA0OiBBZHZhbmNlZCBCYXNoIE9wdGltaXphdGlvbnMgUmVwb3J0XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlcG9ydHMvUEhBU0VfNF9BRFZBTkNFRF9PUFRJTUlaQVRJT05TLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlBoYXNlIDQgSW1wbGVtZW50YXRpb24gU3VtbWFyeTogRVNMaW50IFx1MjE5MiBveGxpbnQgTWlncmF0aW9uXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3JlcG9ydHMvUEhBU0VfNF9JTVBMRU1FTlRBVElPTl9TVU1NQVJZLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlBoYXNlIDQ6IEFkdmFuY2VkIEJhc2ggT3B0aW1pemF0aW9ucyAtIEltcGxlbWVudGF0aW9uIFN1bW1hcnlcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVwb3J0cy9QSEFTRV80X1NVTU1BUlkubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiXHVEODNDXHVERkMxIFByb2plY3QgQ29tcGxldGlvbiBSZXBvcnQ6IHRoZWdlbnRcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVwb3J0cy9QUk9KRUNUX0NPTVBMRVRJT05fUkVQT1JULm1kXCJcbiAgICAgICAgfVxuICAgICAgXVxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUmVzZWFyY2hcIixcbiAgICAgIFwiY29sbGFwc2VkXCI6IGZhbHNlLFxuICAgICAgXCJpdGVtc1wiOiBbXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJJZGVhIFNlZWRzXCIsXG4gICAgICAgICAgXCJjb2xsYXBzZWRcIjogZmFsc2UsXG4gICAgICAgICAgXCJpdGVtc1wiOiBbXG4gICAgICAgICAgICB7XG4gICAgICAgICAgICAgIFwidGV4dFwiOiBcIklkZWEgU2VlZCBFeHBhbnNpb24gXHUyMDE0IENvbXBsZXRlXCIsXG4gICAgICAgICAgICAgIFwibGlua1wiOiBcIi9pZGVhLXNlZWRzL0lERUFfU0VFRF9FWFBBTlNJT05fQ09NUExFVEUubWRcIlxuICAgICAgICAgICAgfSxcbiAgICAgICAgICAgIHtcbiAgICAgICAgICAgICAgXCJ0ZXh0XCI6IFwiSWRlYSBzZWVkOiAkaWRlYSBwcm9tcHQgaGFydmVzdGluZyAoQ3Vyc29yL0NvZGV4L0NsYXVkZSlcIixcbiAgICAgICAgICAgICAgXCJsaW5rXCI6IFwiL2lkZWEtc2VlZHMvc2VlZF9jdXJzb3JfMjAyNjAyMTZUMTAzMDE3Wl84N2M5OGIyZS05Yzg3LTQ1OWMtOTE5ZS0xNDMwYzQ2YzViNWJfMTk5Lm1kXCJcbiAgICAgICAgICAgIH0sXG4gICAgICAgICAgICB7XG4gICAgICAgICAgICAgIFwidGV4dFwiOiBcIklkZWEgc2VlZDogJGlkZWEgcHJvbXB0IGhhcnZlc3RpbmcgKEN1cnNvci9Db2RleC9DbGF1ZGUpXCIsXG4gICAgICAgICAgICAgIFwibGlua1wiOiBcIi9pZGVhLXNlZWRzL3NlZWRfY3Vyc29yXzIwMjYwMjE2VDEwMzAxN1pfODdjOThiMmUtOWM4Ny00NTljLTkxOWUtMTQzMGM0NmM1YjViXzIwMS5tZFwiXG4gICAgICAgICAgICB9LFxuICAgICAgICAgICAge1xuICAgICAgICAgICAgICBcInRleHRcIjogXCJJZGVhIHNlZWQ6ICRpZGVhIHByb21wdCBoYXJ2ZXN0aW5nIChDdXJzb3IvQ29kZXgvQ2xhdWRlKVwiLFxuICAgICAgICAgICAgICBcImxpbmtcIjogXCIvaWRlYS1zZWVkcy9zZWVkX2N1cnNvcl8yMDI2MDIxNlQxMDMyMzdaXzg3Yzk4YjJlLTljODctNDU5Yy05MTllLTE0MzBjNDZjNWI1Yl8xOTkubWRcIlxuICAgICAgICAgICAgfSxcbiAgICAgICAgICAgIHtcbiAgICAgICAgICAgICAgXCJ0ZXh0XCI6IFwiSWRlYSBzZWVkOiAkaWRlYSBwcm9tcHQgaGFydmVzdGluZyAoQ3Vyc29yL0NvZGV4L0NsYXVkZSlcIixcbiAgICAgICAgICAgICAgXCJsaW5rXCI6IFwiL2lkZWEtc2VlZHMvc2VlZF9jdXJzb3JfMjAyNjAyMTZUMTAzMjM3Wl84N2M5OGIyZS05Yzg3LTQ1OWMtOTE5ZS0xNDMwYzQ2YzViNWJfMjAxLm1kXCJcbiAgICAgICAgICAgIH1cbiAgICAgICAgICBdXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJBRFItMDEzOiBNdWx0aS1PcmcgUG9saWN5IEZlZGVyYXRpb25cIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvQURSLTAxMy1QT0xJQ1ktRkVERVJBVElPTi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJBRFItMDE0OiBBdXRvbm9tb3VzIExlYXJuaW5nIGFuZCBDb3N0IFNlbnNpbmdcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvQURSLTAxNC1BVVRPTk9NT1VTLUxFQVJOSU5HLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkFEUi0wMTU6IEVudGVycHJpc2UgTGlmZWN5Y2xlIGFuZCBDb21wbGlhbmNlIEFQSVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9BRFItMDE1LUVOVEVSUFJJU0UtQ09NUExJQU5DRS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJBZHZhbmNlZCBTdG9yYWdlLCBXb3JrZmxvdyAmIEFJIFN5c3RlbXM6IERlZXAgQ29tcGFyaXNvbiAmIE9wdGltaXphdGlvbiBTdHJhdGVnaWVzXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0FEVkFOQ0VEX1NUT1JBR0VfV09SS0ZMT1dfQUlfU1lTVEVNU19ERUVQX0NPTVBBUklTT04ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQWR2YW5jZWQgU3RyYXRlZ2llcyAmIFJlc2lsaWVuY2UgXHUyMDE0IEZ1bGwtRGVwdGggUmVzZWFyY2ggJiBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0FEVkFOQ0VEX1NUUkFURUdJRVNfQU5EX1JFU0lMSUVOQ0VfUkVTRUFSQ0gubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQWdlbnQgQWNjZXNzIGFuZCBPcHRpbWl6YXRpb24gXHUyMDE0IEF1ZGl0IGFuZCBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0FHRU5UX0FDQ0VTU19BTkRfT1BUSU1JWkFUSU9OX0FVRElUX1BMQU4ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQWdlbnQgRmlsZSBTZWFyY2ggXHUyMDE0IFVuaWZpZWQgVG9vbCBSZXNlYXJjaFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9BR0VOVF9GSUxFX1NFQVJDSF9VTklGSUVEX1RPT0xfUkVTRUFSQ0gubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQWdlbnQgUGxhdGZvcm1zIENvbXBsZXRlIFJlc2VhcmNoICYgSW50ZWdyYXRpb24gR3VpZGVcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvQUdFTlRfUExBVEZPUk1TX0NPTVBMRVRFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkFnZW50IFBsYXRmb3Jtczoga2lsbywgcm9vLCBPcGVuQ29kZSwgWmVuICsgQ0xJUHJveHlBUEkgXHUyMDE0IFJlc2VhcmNoXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0FHRU5UX1BMQVRGT1JNU19LSUxPX1JPT19PUGVuY29kZV9DTElQUk9YWV9SRVNFQVJDSC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJBZ2VudCBQcm9jZXNzIEFyY2hpdGVjdHVyZSBcdTIwMTQgUmVzZWFyY2ggTm90ZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9BR0VOVF9QUk9DRVNTX0FSQ0hJVEVDVFVSRV9SRVNFQVJDSC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJBUEksIENMSSwgYW5kIERldk9wcyBEb2N1bWVudGF0aW9uIFRvb2xzIFJlc2VhcmNoIFJlcG9ydFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9BUElfQ0xJX0RFVk9QU19UT09MSU5HLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkNhY2hpbmcsIEluZGV4aW5nICYgUHJlLXdhcm1pbmcgQ29tcGxldGUgUHJhY3RpY2FsIEd1aWRlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0NBQ0hJTkdfQ09NUExFVEUubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQ2FjaGluZywgSW5kZXhpbmcgJiBQcmUtd2FybWluZzogRGVlcCBSZXNlYXJjaCAmIFN0cmF0ZWdpZXNcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvQ0FDSElOR19JTkRFWElOR19QUkVXQVJNSU5HX0RFRVBfUkVTRUFSQ0gubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQ0kvQ0QgYW5kIERldmVsb3BlciBFeHBlcmllbmNlIFRvb2xpbmcgUmVzZWFyY2ggUmVwb3J0ICgyMDI1LTIwMjYpXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0NJX0NEX0RFVlhfVE9PTElORy5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJNdWx0aS1BZ2VudCBGZWF0dXJlIFBhcml0eSBBdWRpdFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9DTEFVREVfQ09ERV9GRUFUVVJFX1BBUklUWV9BVURJVC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJDbGF1ZGUgQ29kZTogUXVldWUgUGVuZGluZyAmIEJsb2NraW5nIE1lc3NhZ2VzIChSZXNlYXJjaCAmIFBsYW4pXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0NMQVVERV9DT0RFX1FVRVVFX1BFTkRJTkdfQkxPQ0tJTkcubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQ2xhdWRlIENvZGUgUGxhbiAmIERlbGVnYXRlIE1vZGVzIFx1MjAxNCBEZWVwIFJlc2VhcmNoIGZvciB0aGVnZW50IFRvb2xpbmdcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvQ0xBVURFX1BMQU5fREVMRUdBVEVfTU9ERVNfUkVTRUFSQ0gubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQ2xpZW50LVNpZGUgU29mdHdhcmUgUGFja2FnZSBEZXNpZ24gJiBEZXBsb3ltZW50IFJlc2VhcmNoXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0NMSUVOVF9TSURFX1BBQ0tBR0VfREVTSUdOX1JFU0VBUkNILm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkNvZGV4IEhvb2tzLCBOb3RpZmljYXRpb25zICYgRXh0ZW5zaW9uIE9wdGlvbnNcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvQ09ERVhfSE9PS1NfQU5EX0VYVEVOU0lPTl9PUFRJT05TLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkNvZGV4ICsgQ0xJUHJveHlBUElQbHVzOiBSZXNlYXJjaCBhbmQgUGxhblwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9DT0RFWF9NSU5JTUFYX0NMSVBST1hZX1JFU0VBUkNIX0FORF9QTEFOLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkNvbXByZWhlbnNpdmUgTm9uLUNhbm9uaWNhbCBBdWRpdCBhbmQgQ29uc29saWRhdGlvbiBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0NPTVBSRUhFTlNJVkVfTk9OX0NBTk9OSUNBTF9BVURJVC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJDb252ZXJzYXRpb24gRHVtcCBcdTIwMTQgMjAyNi0wMi0xNlwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9DT05WRVJTQVRJT05fRFVNUF8yMDI2LTAyLTE2Lm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkNvbnZlcnNhdGlvbiBEdW1wIENvbXBsZXRlIFx1MjAxNCAyMDI2LTAyLTE2IFN0cnVjdHVyZWQgJiBFeHBhbmRlZFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9DT05WRVJTQVRJT05fRFVNUF8yMDI2LTAyLTE2X0NPTVBMRVRFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkNvbnZlcnNhdGlvbiBEdW1wIDIwMjYtMDItMTYgXHUyMDE0IENvbXBsZXRlIEV4cGFuc2lvblwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9DT05WRVJTQVRJT05fRFVNUF8yMDI2LTAyLTE2X0VYUEFOREVELm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkNvc3QtQmFzZWQgUm91dGluZyBcdTIwMTQgRGVmZXJyZWQgU2NvcGVcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvQ09TVF9ST1VUSU5HX0RFRkVSUkVELm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkNvc3QgUm91dGluZyBEZWZlcnJlZCBcdTIwMTQgRm9ybWFsIERlY2lzaW9uIFJlY29yZFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9DT1NUX1JPVVRJTkdfREVGRVJSRURfRVhQQU5ERUQubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQ3Jvc3MtUGxhdGZvcm0gTXVsdGktVGVuYW50IERlc2t0b3AgQXV0b21hdGlvbjogQWR2YW5jZWQgUGF0dGVybnNcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvQ1JPU1NfUExBVEZPUk1fQURWQU5DRURfUEFUVEVSTlMubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQ3Jvc3MtUGxhdGZvcm0gRXh0ZW5zaW9uczogV2lkZXIsIERlZXBlciwgUG9saXNoICYgT3B0aW1pemF0aW9uXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0NST1NTX1BMQVRGT1JNX0VYVEVOU0lPTlNfV0lERVJfREVFUEVSX09QVElNSVpBVElPTi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJDcm9zcy1QbGF0Zm9ybSBHYXBzIGFuZCBFeHRlbnNpb25zIFx1MjAxNCBSZXNlYXJjaCAmIFBsYW5cIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvQ1JPU1NfUExBVEZPUk1fR0FQU19BTkRfRVhURU5TSU9OU19SRVNFQVJDSC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJDcm9zcy1QbGF0Zm9ybSBEZXNrdG9wIEF1dG9tYXRpb246IEludGVncmF0aW9uIEd1aWRlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0NST1NTX1BMQVRGT1JNX0lOVEVHUkFUSU9OX0dVSURFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkNyb3NzLVBsYXRmb3JtIE11bHRpLVRlbmFudCBEZXNrdG9wIEF1dG9tYXRpb24gUmVzZWFyY2ggJiBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0NST1NTX1BMQVRGT1JNX01VTFRJX1RFTkFOVF9ERVNLVE9QX0FVVE9NQVRJT05fUkVTRUFSQ0gubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQ3Jvc3MtUGxhdGZvcm0gRGVza3RvcCBBdXRvbWF0aW9uOiBQZXJmb3JtYW5jZSBCZW5jaG1hcmtzICYgU0xBc1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9DUk9TU19QTEFURk9STV9QRVJGT1JNQU5DRV9CRU5DSE1BUktTLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkNyb3NzLVBsYXRmb3JtIFJlc2VhcmNoIENvbXBsZXRlIFx1MjAxNCBDb21wcmVoZW5zaXZlIENvbnNvbGlkYXRlZCBHdWlkZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9DUk9TU19QTEFURk9STV9SRVNFQVJDSF9DT01QTEVURS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJDcm9zcy1QbGF0Zm9ybSBEZXNrdG9wIEF1dG9tYXRpb246IFJlc2VhcmNoIENvbXBsZXRpb24gU3VtbWFyeVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9DUk9TU19QTEFURk9STV9SRVNFQVJDSF9DT01QTEVUSU9OX1NVTU1BUlkubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiQ3Jvc3MtUGxhdGZvcm0gUmVzZWFyY2ggXHUyMDE0IENvbnNvbGlkYXRlZCBDb21wcmVoZW5zaXZlIEd1aWRlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0NST1NTX1BMQVRGT1JNX1JFU0VBUkNIX0NPTlNPTElEQVRFRC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJDcm9zcy1QbGF0Zm9ybSBEZXNrdG9wIEF1dG9tYXRpb246IFJlc2VhcmNoIEluZGV4XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0NST1NTX1BMQVRGT1JNX1JFU0VBUkNIX0lOREVYLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkNyb3NzLVBsYXRmb3JtIE11bHRpLVRlbmFudCBEZXNrdG9wIEF1dG9tYXRpb246IFJlc2VhcmNoIFN1bW1hcnlcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvQ1JPU1NfUExBVEZPUk1fUkVTRUFSQ0hfU1VNTUFSWS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJDcm9zcy1QbGF0Zm9ybSBEZXNrdG9wIEF1dG9tYXRpb246IFNlY3VyaXR5IERlZXAgRGl2ZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9DUk9TU19QTEFURk9STV9TRUNVUklUWV9ERUVQX0RJVkUubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiRG9jdG9yIENvbW1hbmQ6IE9BdXRoLU9ubHkgQXV0aGVudGljYXRpb24gVXBkYXRlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0RPQ1RPUl9PQVVUSF9PTkxZX1VQREFURS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJFU0xpbnQgXHUyMTkyIG94bGludCBNaWdyYXRpb24gQXVkaXQgKFBoYXNlIDQpXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0VTTElOVF9BVURJVC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJFeHBhbnNpb24gQ29tcGxldGUgXHUyMDE0IEZpbmFsIFJlcG9ydFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9FWFBBTlNJT05fQ09NUExFVEVfRklOQUwubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiRXhwYW5zaW9uIFBoYXNlIFx1MjAxNCBDb21wbGV0ZSBTdW1tYXJ5XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0VYUEFOU0lPTl9QSEFTRV9DT01QTEVURS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJGYXN0TUNQIENvbXBsZXRlIFx1MjAxNCBDb21wcmVoZW5zaXZlIEltcGxlbWVudGF0aW9uIEd1aWRlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0ZBU1RNQ1BfQ09NUExFVEUubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiRmFzdE1DUCBFbGljaXRhdGlvbiAmIENvbnRleHQgQVBJIFN1bW1hcnlcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvRkFTVE1DUF9FTElDSVRBVElPTl9DT05URVhULm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkZhc3RNQ1AgRmVhdHVyZXMgJiBNQ1AgVHJhbnNwb3J0IFNwZWMgR2Fwc1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9GQVNUTUNQX0ZFQVRVUkVTX0FORF9UUkFOU1BPUlRfR0FQUy5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJGYXN0TUNQIEltcGxlbWVudGF0aW9uIEd1aWRlIGZvciB0aGVnZW50XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0ZBU1RNQ1BfSU1QTEVNRU5UQVRJT05fR1VJREUubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiRmFzdE1DUCBNaWRkbGV3YXJlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0ZBU1RNQ1BfTUlERExFV0FSRS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJGYXN0TUNQIFByb2dyZXNzICYgVGFza3MgQVBJIFN1bW1hcnlcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvRkFTVE1DUF9QUk9HUkVTU19UQVNLUy5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJGYXN0TUNQIFNhbXBsaW5nICYgVGVsZW1ldHJ5XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0ZBU1RNQ1BfU0FNUExJTkdfVEVMRU1FVFJZLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkZhc3RNQ1AgU3BlYyBEZWVwIERpdmVcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvRkFTVE1DUF9TUEVDX0RFRVBfRElWRS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJGYXN0TUNQIFN0b3JhZ2UgQmFja2VuZHMgJiBFdmVudFN0b3JlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0ZBU1RNQ1BfU1RPUkFHRV9FVkVOVFNUT1JFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkZhc3RNQ1AgVHJhbnNmb3JtcyAmIERlcGxveW1lbnQgU3VtbWFyeVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9GQVNUTUNQX1RSQU5TRk9STVNfREVQTE9ZTUVOVC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJGaW5hbCBFeHBhbnNpb24gUmVwb3J0IFx1MjAxNCBDb21wbGV0ZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9GSU5BTF9FWFBBTlNJT05fUkVQT1JULm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkdpdCBTaGltIFN0YXJzaGlwIE9wdGltaXphdGlvbiBcdTIwMTQgRml4IGZvciA4KyBNaW51dGUgUHJvbXB0IERlbGF5c1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9HSVRfU0hJTV9TVEFSU0hJUF9PUFRJTUlaQVRJT04ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiR2l0IFRvb2xpbmcgQXVkaXQgYW5kIE1vZGVybml6YXRpb24gUGxhblwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9HSVRfVE9PTElOR19BVURJVF9BTkRfUExBTi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJHb3Zlcm5hbmNlLCBQb2xpY3kgRW5mb3JjZW1lbnQsIGFuZCBBdWRpdCBUcmFpbCBSZXNlYXJjaFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9HT1ZFUk5BTkNFX1BPTElDWV9BVURJVF9SRVNFQVJDSC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJHb3Zlcm5hbmNlIFdQIEdhcHMgXHUyMDE0IEltcGxlbWVudGF0aW9uIE5vdGVzXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0dPVkVSTkFOQ0VfV1BfR0FQUy5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJHb3Zlcm5hbmNlIFdQIEdhcHMgXHUyMDE0IEV4cGFuZGVkICYgQkFDS0xPRyBJdGVtc1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9HT1ZFUk5BTkNFX1dQX0dBUFNfRVhQQU5ERUQubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiSG9vayBSdXN0IE1pZ3JhdGlvbiBDb21wbGV0ZSBcdTIwMTQgQ29tcHJlaGVuc2l2ZSBNaWdyYXRpb24gU3RyYXRlZ3kgJiBUaW1lbGluZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9IT09LX1JVU1RfTUlHUkFUSU9OX0NPTVBMRVRFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkhvb2sgUnVudGltZSBSdXN0IE1pZ3JhdGlvbjogUmVzZWFyY2ggU3ludGhlc2lzXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0hPT0tfUlVTVF9NSUdSQVRJT05fUkVTRUFSQ0hfU1lOVEhFU0lTLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkhvb2sgUnVudGltZSBSdXN0IE1pZ3JhdGlvbiBcdTIwMTQgQ29tcGxldGUgRXhwYW5zaW9uXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0hPT0tfUlVTVF9NSUdSQVRJT05fUkVTRUFSQ0hfU1lOVEhFU0lTX0VYUEFOREVELm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIklkZWEgU2VlZHMgJiBTZXNzaW9uIFN0b3JhZ2VcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvSURFQV9TRUVEU19TRVNTSU9OX1NUT1JBR0UubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiSWRlYSBTZWVkIFJldmlldyBDb21wbGV0ZSBcdTIwMTQgQ29uc29saWRhdGlvbiAmIFJhdGlvbmFsZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9JREVBX1NFRURfUkVWSUVXX0NPTVBMRVRFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkluZGV4IFNwcmF3bCBTdGF0dXMgVXBkYXRlIFx1MjAxNCBDb21wbGV0ZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9JTkRFWF9TUFJBV0xfU1RBVFVTX1VQREFURS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJJbi1EZXB0aCBUb29saW5nIGFuZCBHbG9iYWwgT3B0aW1pemF0aW9ucyBBdWRpdCAoMjAyNi0wMi0xNSlcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvSU5fREVQVEhfVE9PTElOR19BVURJVF8yMDI2Lm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkxpYnJhcnktRmlyc3QgQXVkaXQgYW5kIFBsYW5cIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvTElCUkFSWV9GSVJTVF9BVURJVF9BTkRfUExBTi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJMaWJyYXJ5IFJlcGxhY2VtZW50IEF1ZGl0IFx1MjAxNCBEZWVwICYgV2lkZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9MSUJSQVJZX1JFUExBQ0VNRU5UX0FVRElUX0RFRVAubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiTGlicmFyeSBSZXBsYWNlbWVudCBDb21wbGV0ZSBcdTIwMTQgQ29tcHJlaGVuc2l2ZSBBdWRpdCAmIE1pZ3JhdGlvbiBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0xJQlJBUllfUkVQTEFDRU1FTlRfQ09NUExFVEUubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiTGlicmFyeSBSZXBsYWNlbWVudCBcdTIwMTQgQ29uc29saWRhdGVkIE1pZ3JhdGlvbiBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0xJQlJBUllfUkVQTEFDRU1FTlRfQ09OU09MSURBVEVELm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIkxpYnJhcnkgUmVwbGFjZW1lbnQgXHUyMDE0IFBoYXNlIERlc2lnbiBXb3JrIEJyZWFrZG93bnMgKERXQnMpXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0xJQlJBUllfUkVQTEFDRU1FTlRfUEhBU0VfRFdCUy5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJNYXN0ZXIgRXhwYW5zaW9uIFRPRE8gXHUyMDE0IENvbXBsZXRlIERvY3VtZW50YXRpb24gU3ByYXdsXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL01BU1RFUl9FWFBBTlNJT05fVE9ETy5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJNQ1AgRnVsbCBQYXJpdHkgJiBGYXN0TUNQIFRyYW5zcG9ydCBTcGVjIEF1ZGl0XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL01DUF9GVUxMX1BBUklUWV9BTkRfRkFTVE1DUF9BVURJVC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJNQ1AgYW5kIENsaWVudCBGZWF0dXJlcyBmb3IgU2Vzc2lvbiBOb3RpZmljYXRpb25zXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL01DUF9OT1RJRklDQVRJT05fT1BUSU9OUy5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJNRCBEb2N1bWVudGF0aW9uIE5vcm1hbGl6YXRpb24gR3VpZGVcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvTURfTk9STUFMSVpBVElPTl9HVUlERS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJNZW1vcnkgT3B0aW1pemF0aW9uIFx1MjAxNCBMb25nLVRlcm0gUGxhblwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9NRU1PUllfT1BUSU1JWkFUSU9OX0xPTkdfVEVSTV9QTEFOLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIk11bHRpLVBsYXRmb3JtIEFnZW50IERlZXAgRGl2ZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9NVUxUSV9QTEFURk9STV9ERUVQX0RJVkUubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiT3BlbkNsYXcgLyBBZ2VudCBaZXJvIGFzIE1haW4gQWdlbnQgXHUyMDE0IFJlc2VhcmNoXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL09QRU5DTEFXX0FHRU5UWkVST19BU19NQUlOX0FHRU5UX1JFU0VBUkNILm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIk9wZW5DbGF3LCBDbGF3SHViLCBBZ2VudCBaZXJvIFx1MjAxNCBVc2UgQ2FzZXMgZm9yIHRoZWdlbnRcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvT1BFTkNMQVdfQ0xBV0hVQl9BR0VOVFpFUk9fVVNFX0NBU0VTLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlByaW9yaXR5IDEgKFAxKSBFeHBhbnNpb24gXHUyMDE0IENvbXBsZXRlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1AxX0VYUEFOU0lPTl9DT01QTEVURS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJQcmlvcml0eSAxIChQMSkgUGhhc2UgXHUyMDE0IENvbXBsZXRlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1AxX1BIQVNFX0NPTVBMRVRFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlAzIFBvbGlzaCBDb21wbGV0ZSBcdTIwMTQgRnVsbCBSZXNlYXJjaCBEb2NzXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1AzX1BPTElTSF9DT01QTEVURS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJQNCBOb3JtYWxpemF0aW9uIFx1MjAxNCBDb21wbGV0ZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9QNF9OT1JNQUxJWkFUSU9OX0NPTVBMRVRFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlA0IE5vcm1hbGl6YXRpb24gXHUyMDE0IEZpbmFsIFN0YXR1c1wiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9QNF9OT1JNQUxJWkFUSU9OX0ZJTkFMLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlA0IE5vcm1hbGl6YXRpb24gUHJvZ3Jlc3MgXHUyMDE0IEFsbCBNRCBEb2NzXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1A0X05PUk1BTElaQVRJT05fUFJPR1JFU1MubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUDQgTm9ybWFsaXphdGlvbiBTdW1tYXJ5IFx1MjAxNCBDb21wbGV0ZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9QNF9OT1JNQUxJWkFUSU9OX1NVTU1BUlkubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUDQgTm9ybWFsaXphdGlvbiBVcGRhdGUgXHUyMDE0IFByb2dyZXNzIFJlcG9ydFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9QNF9OT1JNQUxJWkFUSU9OX1VQREFURS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJQYWNrYWdlIERlc2lnbiBSZXNlYXJjaCBTdW1tYXJ5XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1BBQ0tBR0VfREVTSUdOX1JFU0VBUkNIX1NVTU1BUlkubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUGhhc2UgRG9jdW1lbnRzIFx1MjAxNCBDb21wbGV0ZSBFeHBhbnNpb25cIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvUEhBU0VfRE9DVU1FTlRTX0VYUEFOREVELm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlBsYW4gVXNhZ2UgYW5kIEJ1ZGdldCBSZXNlYXJjaFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9QTEFOX1VTQUdFX0FORF9CVURHRVRfUkVTRUFSQ0gubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUHJvYWN0aXZlIEdvdmVybmFuY2UgRXZvbHV0aW9uIFBsYW5cIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvUFJPQUNUSVZFX0dPVkVSTkFOQ0VfRVZPTFVUSU9OX1BMQU4ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUHJvZHVjdGlvbiBQYWNrYWdpbmcsIFBvbGlzaCAmIE9wdGltaXphdGlvbiBBdWRpdCArIFBsYW5cIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvUFJPRFVDVElPTl9QQUNLQUdJTkdfUE9MSVNIX09QVElNSVpBVElPTl9BVURJVF9BTkRfUExBTi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJQeXRob24gRnJvbnRtYXR0ZXIgKyBOYXRpdmUgQmFja21hdHRlcjogUmVzZWFyY2ggQXVkaXQgJiBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1BZVEhPTl9GUk9OVE1BVFRFUl9OQVRJVkVfQkFDS01BVFRFUl9BVURJVF9QTEFOLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlF3ZW4zLjUgUGx1cyAwMi0xNSBvbiBPcGVuUm91dGVyIFx1MjAxNCBQYXJldG8gUmVzZWFyY2hcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvUVdFTjMuNV9QTFVTX09QRU5ST1VURVJfUEFSRVRPX1JFU0VBUkNILm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlJlbW92ZSBEaXJlY3RvcnkgRGVwZW5kZW5jaWVzIFx1MjAxNCBQcm9kdWN0aW9uIEluc3RhbGxhdGlvbiBPcHRpbWl6YXRpb25cIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvUkVNT1ZFX0RJUkVDVE9SWV9ERVBFTkRFTkNJRVNfQVVESVRfQU5EX1BMQU4ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUmVzZWFyY2gsIFNlZWQgJiBGcmFnbWVudCBJbnZlbnRvcnkgXHUyMDE0IFNwcmF3bCBUb2RvICYgVW5pZmllZCBXb3JrIFN0cmVhbVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9SRVNFQVJDSF9TRUVEX0ZSQUdNRU5UX0lOVkVOVE9SWV9BTkRfU1BSQVdMX1RPRE8ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiXFxcIlNlZSBBbHNvXFxcIiBTZWN0aW9uIFRlbXBsYXRlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1NFRV9BTFNPX1RFTVBMQVRFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlNlc3Npb24gUmVzZWFyY2ggQ29tcGxldGUgXHUyMDE0IENvbXByZWhlbnNpdmUgRGVlcC1EaXZlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1NFU1NJT05fUkVTRUFSQ0hfQ09NUExFVEUubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiU2Vzc2lvbiBSZXNlYXJjaCBGcmFnbWVudHMgXHUyMDE0IDIwMjYtMDItMTVcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvU0VTU0lPTl9SRVNFQVJDSF9GUkFHTUVOVFMubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiU2Vzc2lvbiBSZXNlYXJjaCBGcmFnbWVudHMgXHUyMDE0IENvbXBsZXRlIEV4cGFuc2lvblwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9TRVNTSU9OX1JFU0VBUkNIX0ZSQUdNRU5UU19FWFBBTkRFRC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJTaGVsbCBDb25maWd1cmF0aW9uIEF1ZGl0IGFuZCBDb25zb2xpZGF0aW9uIFBsYW5cIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvU0hFTExfQ09ORklHX0FVRElUX0FORF9DT05TT0xJREFUSU9OX1BMQU4ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiU2hlbGwgRXJyb3IgRml4ZXMgXHUyMDE0IHpzaCBCYWQgU3Vic3RpdHV0aW9uXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1NIRUxMX0VSUk9SX0ZJWEVTLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlNtYXJ0ICYgUm9idXN0IFByb2Nlc3MgU3RyYXRlZ2llcyBcdTIwMTQgUmVzZWFyY2ggJiBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1NNQVJUX1JPQlVTVF9TVFJBVEVHSUVTX1JFU0VBUkNILm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlN3YXJtIE1hbmFnZW1lbnQgQ29tcGxldGUgUmVzZWFyY2ggJiBJbXBsZW1lbnRhdGlvbiBHdWlkZVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9TV0FSTV9DT01QTEVURS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJTd2FybSBPcHRpbWl6YXRpb24sIE1hbmFnZW1lbnQgJiBTY2hlZHVsaW5nIFx1MjAxNCBEZWVwIFJlc2VhcmNoXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1NXQVJNX09QVElNSVpBVElPTl9TQ0hFRFVMSU5HX0RFRVBfUkVTRUFSQ0gubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiU3dhcm0gUHJvY2VzcyBBdXRvbWF0aW9uIFx1MjAxNCBEZWVwIFJlc2VhcmNoICYgUGxhblwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9TV0FSTV9QUk9DRVNTX0FVVE9NQVRJT05fREVFUF9SRVNFQVJDSC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJTd2FybSAmIFJlc291cmNlIE9wdGltaXphdGlvbiBcdTIwMTQgUmVzZWFyY2ggSW5kZXhcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvU1dBUk1fUkVTRUFSQ0hfSU5ERVgubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiU3lzdGVtIFJlc291cmNlcyBDb21wbGV0ZSBQcmFjdGljYWwgR3VpZGVcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvU1lTVEVNX1JFU09VUkNFU19DT01QTEVURS5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJTeXN0ZW0gUmVzb3VyY2VzIChGRCwgQ1BVLCBUaHJlYWRzLCBQb3J0cykgXHUyMDE0IEZ1bGwtRGVwdGggUmVzZWFyY2ggJiBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1NZU1RFTV9SRVNPVVJDRVNfRkRfQ1BVX0RFRVBfUkVTRUFSQ0gubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBUZWFtbWF0ZXM6IFJlc2VhcmNoIGFuZCBJbXBsZW1lbnRhdGlvbiBQbGFuICgyMDI2LTAyLTE1KVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9URUFNTUFURVNfUkVTRUFSQ0hfQU5EX1BMQU4ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVGVuYWNpdHkgdnMgQ3VzdG9tIFJldHJ5IFx1MjAxNCBBdWRpdCAmIFBsYW5cIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvVEVOQUNJVFlfUkVUUllfQVVESVRfUExBTi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJUaGVnZW50IENvbW1hbmQgTW9kZWwgT3B0aW9ucyBhbmQgQWdlbnQgRmVhdHVyZXMgUmVzZWFyY2hcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvVEhHRU5UX0NPTU1BTkRfTU9ERUxfT1BUSU9OU19BTkRfQUdFTlRfRkVBVFVSRVNfUkVTRUFSQ0gubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVFVJIENvbXBvc2l0b3IgQ29tcGFyaXNvbiBSZXNlYXJjaFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9UVUlfQ09NUE9TSVRPUl9DT01QQVJJU09OLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlVuaWZpZWQgV29yayBTdHJlYW0gSW50ZWdyYXRpb24gXHUyMDE0IENvbXBsZXRlXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1VOSUZJRURfV09SS19TVFJFQU1fSU5URUdSQVRJT04ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVXNlciBRdWV1ZSArIFRVSTogRWRpdGFibGUgUHJvbXB0cyBXaGlsZSBBZ2VudCBSdW5zXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1VTRVJfUVVFVUVfVFVJX0FORF9BR0VOVF9QT0xMLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlZpdGVQcmVzcyBFbmhhbmNlbWVudHMgUmVzZWFyY2ggUmVwb3J0ICgyMDI1LTIwMjYpXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1ZJVEVQUkVTU19FTkhBTkNFTUVOVFMubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVml0ZVByZXNzIFBoYXNlIDEgSW1wbGVtZW50YXRpb24gXHUyMDE0IFx1MjcwNSBDT01QTEVURVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9WSVRFUFJFU1NfUEhBU0UxX0NPTVBMRVRFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlZpdGVQcmVzcyBQaGFzZSAxIEltcGxlbWVudGF0aW9uIFx1MjAxNCBTdGF0dXNcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvVklURVBSRVNTX1BIQVNFMV9JTVBMRU1FTlRBVElPTi5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJWaXRlUHJlc3MgUGhhc2UgMiBJbXBsZW1lbnRhdGlvbiBcdTIwMTQgU3RhdHVzXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1ZJVEVQUkVTU19QSEFTRTJfSU1QTEVNRU5UQVRJT04ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVml0ZVByZXNzIFBoYXNlIDMgSW1wbGVtZW50YXRpb24gXHUyMDE0IFx1MjcwNSBDT01QTEVURVwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9WSVRFUFJFU1NfUEhBU0UzX0NPTVBMRVRFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlZpdGVQcmVzcyBSaWNoIERvY3VtZW50YXRpb24gQXVkaXQgJiBJbXBsZW1lbnRhdGlvbiBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1ZJVEVQUkVTU19SSUNIX0RPQ1VNRU5UQVRJT05fQVVESVQubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiVml0ZVByZXNzIFJpY2ggRG9jdW1lbnRhdGlvbiBcdTIwMTQgSW1wbGVtZW50YXRpb24gUGxhblwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9WSVRFUFJFU1NfUklDSF9ET0NVTUVOVEFUSU9OX0lNUExFTUVOVEFUSU9OX1BMQU4ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUGhhc2UgMTM6IENvbXBsaWFuY2UgUHJvZmlsZSBNYXBwaW5nXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL3BoYXNlMTMtY29tcGxpYW5jZS1wcm9maWxlLW1hcHBpbmcubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUGhhc2UgMTM6IENvc3QgU2Vuc2l0aXZpdHkgRXhwZXJpbWVudCBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL3BoYXNlMTMtY29zdC1zZW5zaXRpdml0eS1leHBlcmltZW50LXBsYW4ubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUGhhc2UgMTM6IFBvbGljeSBGZWRlcmF0aW9uIFN1cmZhY2UgTWFwXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL3BoYXNlMTMtcG9saWN5LWZlZGVyYXRpb24tc3VyZmFjZS1tYXAubWRcIlxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiUGhhc2UgMTM6IFRlbmFudCBCb3VuZGFyeSBUZXN0IE1hdHJpeFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9waGFzZTEzLXRlbmFudC1ib3VuZGFyeS10ZXN0LW1hdHJpeC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJQaGFzZSAxNDogQXV0b25vbW91cyBMZWFybmluZyBhbmQgQ29zdCBTZW5zaW5nIFN1cmZhY2UgTWFwXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL3BoYXNlMTQtYXV0b25vbW91cy1sZWFybmluZy1zdXJmYWNlLW1hcC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJQaGFzZSAxNDogQ29zdCBTZW5zaW5nIGFuZCBMZWFybmluZyBUZXN0IE1hdHJpeFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9waGFzZTE0LWNvc3Qtc2Vuc2luZy10ZXN0LW1hdHJpeC5tZFwiXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBcInRleHRcIjogXCJQaGFzZSAxNTogRW50ZXJwcmlzZSBDb21wbGlhbmNlIFRlc3QgTWF0cml4XCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL3BoYXNlMTUtZW50ZXJwcmlzZS1jb21wbGlhbmNlLXRlc3QtbWF0cml4Lm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlBoYXNlIDE1OiBFbnRlcnByaXNlIExpZmVjeWNsZSBhbmQgQ29tcGxpYW5jZSBTdXJmYWNlIE1hcFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9waGFzZTE1LWVudGVycHJpc2UtbGlmZWN5Y2xlLXN1cmZhY2UtbWFwLm1kXCJcbiAgICAgICAgfVxuICAgICAgXVxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiU2NyYXRjaHBhZFwiLFxuICAgICAgXCJjb2xsYXBzZWRcIjogZmFsc2UsXG4gICAgICBcIml0ZW1zXCI6IFtcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIlNlc3Npb24gU2NyYXRjaCBCb2FyZCAmIE9wdGltaXphdGlvbiBQbGFuXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL3NjcmF0Y2hwYWQvc2Vzc2lvbl9yZXZpZXcubWRcIlxuICAgICAgICB9XG4gICAgICBdXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJDcm9zcy1Qcm9qZWN0IEFnZW50IEluc3RydWN0aW9uc1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3MvQUdFTlRfSU5TVFJVQ1RJT05TLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkFyY2hpdGVjdHVyZSBMYXllcnMgKEctS0QtMDUpXCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jcy9BUkNISVRFQ1RVUkVfTEFZRVJTLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkNyb3NzLVBsYXRmb3JtIERlc2t0b3AgQXV0b21hdGlvbjogTWFzdGVyIERvY3VtZW50IEluZGV4XCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jcy9DUk9TU19QTEFURk9STV9NQVNURVJfSU5ERVgubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiRGlzY292ZXJ5IFN1cmZhY2UgKEctRFMpXCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jcy9ESVNDT1ZFUlkubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiRG9jdW1lbnQgUXVldWUgSW50ZWdyYXRpb24gR3VpZGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzL0RPQ1VNRU5UX1FVRVVFX0lOVEVHUkFUSU9OLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkZhc3RNQ1AgRGVwbG95bWVudCBHdWlkZSAoRy1GTS0wMSBQaGFzZSA1KVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3MvRkFTVE1DUF9ERVBMT1lNRU5UX0dVSURFLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkZhc3RNQ1AgR3JhY2VmdWwgU2h1dGRvd24gKEctT1AtMTApXCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jcy9GQVNUTUNQX0dSQUNFRlVMX1NIVVRET1dOLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkZhc3RNQ1AgSWNvbnMgYW5kIFVYIEhpbnRzIChHLUZNLTA0KVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3MvRkFTVE1DUF9JQ09OU19VWF9ISU5UUy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJGYXN0TUNQIE9wdGltaXphdGlvbiAmIFBvbGlzaCBBdWRpdCAoRy1PUC0wNFx1MjAxM0ctT1AtMTApXCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jcy9GQVNUTUNQX09QVElNSVpBVElPTl9BVURJVC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJGYXN0TUNQIFBoYXNlIENoZWNrbGlzdCBWZXJpZmljYXRpb24gKEctRk0tMDYpXCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jcy9GQVNUTUNQX1BIQVNFX0NIRUNLTElTVF9WRVJJRklDQVRJT04ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiRmFzdE1DUCBUZXN0aW5nIFN0cmF0ZWd5IChHLUZNLTA1KVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3MvRkFTVE1DUF9URVNUSU5HX1NUUkFURUdZLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgR2FwIEFuYWx5c2lzICYgUmVtZWRpYXRpb24gUGxhblwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3MvR0FQX0FOQUxZU0lTX0FORF9SRU1FRElBVElPTi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJHb3Zlcm5hbmNlIFdQIEltcGxlbWVudGF0aW9uIFZlcmlmaWNhdGlvbiAoRy1HUC0wMVx1MjAxMzA5KVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3MvR09WRVJOQU5DRV9XUF9WRVJJRklDQVRJT04ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiTXVsdGktQWdlbnQgT3JjaGVzdHJhdGlvbiBNb2RlIENhdGFsb2dcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzL01VTFRJX0FHRU5UX01PREVfQ0FUQUxPRy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJUaGVnZW50IE9yY2hlc3RyYXRpb24gT3B0aW1pemF0aW9uIFByb2dyYW0gKHYxLjApXCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jcy9PUkNIRVNUUkFUSU9OLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlBsYW5uaW5nIFNpbXVsYXRpb24gRGVzaWduIChHLUNBLTA0KVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3MvUExBTk5JTkdfU0lNVUxBVElPTl9ERVNJR04ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUG9zdC1MYXVuY2ggT2JzZXJ2YXRpb24gUGxheWJvb2tcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzL1BPU1RfTEFVTkNIX09CU0VSVkFUSU9OX1BMQVlCT09LLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgT3JjaGVzdHJhdGlvbiBSdW5ib29rICh2MS4wKVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3MvUlVOQk9PSy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJTZXR1cCBSZXN0b3JlIFx1MjAxNCBMb25nLXRlcm0gRml4ZXMgQXBwbGllZFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3MvU0VUVVAtUkVTVE9SRS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJTdGF0ZS1Bd2FyZSBPcmNoZXN0cmF0aW9uIERlc2lnblwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3MvU1RBVEVfQVdBUkVfT1JDSEVTVFJBVElPTl9ERVNJR04ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBGYXN0TUNQIFZlcmlmaWNhdGlvbiBSdW5ib29rXCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jcy9WRVJJRklDQVRJT05fUlVOQk9PSy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJDcm9zcy1Qcm9qZWN0IExpbmtzIFRlc3RcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzL2Nyb3NzLWxpbmtzLXRlc3QubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiSW5kZXhcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzL2luZGV4Lm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRlc3QgQ2FsbG91dHNcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzL3Rlc3QtY2FsbG91dHMubWRcIlxuICAgIH1cbiAgXSxcbiAgXCIvcmVzZWFyY2gvXCI6IFtcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJJZGVhIFNlZWRzXCIsXG4gICAgICBcImNvbGxhcHNlZFwiOiBmYWxzZSxcbiAgICAgIFwiaXRlbXNcIjogW1xuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiSWRlYSBTZWVkIEV4cGFuc2lvbiBcdTIwMTQgQ29tcGxldGVcIixcbiAgICAgICAgICBcImxpbmtcIjogXCIvaWRlYS1zZWVkcy9JREVBX1NFRURfRVhQQU5TSU9OX0NPTVBMRVRFLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIklkZWEgc2VlZDogJGlkZWEgcHJvbXB0IGhhcnZlc3RpbmcgKEN1cnNvci9Db2RleC9DbGF1ZGUpXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2lkZWEtc2VlZHMvc2VlZF9jdXJzb3JfMjAyNjAyMTZUMTAzMDE3Wl84N2M5OGIyZS05Yzg3LTQ1OWMtOTE5ZS0xNDMwYzQ2YzViNWJfMTk5Lm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIklkZWEgc2VlZDogJGlkZWEgcHJvbXB0IGhhcnZlc3RpbmcgKEN1cnNvci9Db2RleC9DbGF1ZGUpXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2lkZWEtc2VlZHMvc2VlZF9jdXJzb3JfMjAyNjAyMTZUMTAzMDE3Wl84N2M5OGIyZS05Yzg3LTQ1OWMtOTE5ZS0xNDMwYzQ2YzViNWJfMjAxLm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIklkZWEgc2VlZDogJGlkZWEgcHJvbXB0IGhhcnZlc3RpbmcgKEN1cnNvci9Db2RleC9DbGF1ZGUpXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2lkZWEtc2VlZHMvc2VlZF9jdXJzb3JfMjAyNjAyMTZUMTAzMjM3Wl84N2M5OGIyZS05Yzg3LTQ1OWMtOTE5ZS0xNDMwYzQ2YzViNWJfMTk5Lm1kXCJcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIFwidGV4dFwiOiBcIklkZWEgc2VlZDogJGlkZWEgcHJvbXB0IGhhcnZlc3RpbmcgKEN1cnNvci9Db2RleC9DbGF1ZGUpXCIsXG4gICAgICAgICAgXCJsaW5rXCI6IFwiL2lkZWEtc2VlZHMvc2VlZF9jdXJzb3JfMjAyNjAyMTZUMTAzMjM3Wl84N2M5OGIyZS05Yzg3LTQ1OWMtOTE5ZS0xNDMwYzQ2YzViNWJfMjAxLm1kXCJcbiAgICAgICAgfVxuICAgICAgXVxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQURSLTAxMzogTXVsdGktT3JnIFBvbGljeSBGZWRlcmF0aW9uXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvQURSLTAxMy1QT0xJQ1ktRkVERVJBVElPTi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJBRFItMDE0OiBBdXRvbm9tb3VzIExlYXJuaW5nIGFuZCBDb3N0IFNlbnNpbmdcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9BRFItMDE0LUFVVE9OT01PVVMtTEVBUk5JTkcubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQURSLTAxNTogRW50ZXJwcmlzZSBMaWZlY3ljbGUgYW5kIENvbXBsaWFuY2UgQVBJXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvQURSLTAxNS1FTlRFUlBSSVNFLUNPTVBMSUFOQ0UubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQWR2YW5jZWQgU3RvcmFnZSwgV29ya2Zsb3cgJiBBSSBTeXN0ZW1zOiBEZWVwIENvbXBhcmlzb24gJiBPcHRpbWl6YXRpb24gU3RyYXRlZ2llc1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0FEVkFOQ0VEX1NUT1JBR0VfV09SS0ZMT1dfQUlfU1lTVEVNU19ERUVQX0NPTVBBUklTT04ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQWR2YW5jZWQgU3RyYXRlZ2llcyAmIFJlc2lsaWVuY2UgXHUyMDE0IEZ1bGwtRGVwdGggUmVzZWFyY2ggJiBQbGFuXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvQURWQU5DRURfU1RSQVRFR0lFU19BTkRfUkVTSUxJRU5DRV9SRVNFQVJDSC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJBZ2VudCBBY2Nlc3MgYW5kIE9wdGltaXphdGlvbiBcdTIwMTQgQXVkaXQgYW5kIFBsYW5cIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9BR0VOVF9BQ0NFU1NfQU5EX09QVElNSVpBVElPTl9BVURJVF9QTEFOLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkFnZW50IEZpbGUgU2VhcmNoIFx1MjAxNCBVbmlmaWVkIFRvb2wgUmVzZWFyY2hcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9BR0VOVF9GSUxFX1NFQVJDSF9VTklGSUVEX1RPT0xfUkVTRUFSQ0gubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQWdlbnQgUGxhdGZvcm1zIENvbXBsZXRlIFJlc2VhcmNoICYgSW50ZWdyYXRpb24gR3VpZGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9BR0VOVF9QTEFURk9STVNfQ09NUExFVEUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQWdlbnQgUGxhdGZvcm1zOiBraWxvLCByb28sIE9wZW5Db2RlLCBaZW4gKyBDTElQcm94eUFQSSBcdTIwMTQgUmVzZWFyY2hcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9BR0VOVF9QTEFURk9STVNfS0lMT19ST09fT1BlbmNvZGVfQ0xJUFJPWFlfUkVTRUFSQ0gubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQWdlbnQgUHJvY2VzcyBBcmNoaXRlY3R1cmUgXHUyMDE0IFJlc2VhcmNoIE5vdGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9BR0VOVF9QUk9DRVNTX0FSQ0hJVEVDVFVSRV9SRVNFQVJDSC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJBUEksIENMSSwgYW5kIERldk9wcyBEb2N1bWVudGF0aW9uIFRvb2xzIFJlc2VhcmNoIFJlcG9ydFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0FQSV9DTElfREVWT1BTX1RPT0xJTkcubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQ2FjaGluZywgSW5kZXhpbmcgJiBQcmUtd2FybWluZyBDb21wbGV0ZSBQcmFjdGljYWwgR3VpZGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9DQUNISU5HX0NPTVBMRVRFLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkNhY2hpbmcsIEluZGV4aW5nICYgUHJlLXdhcm1pbmc6IERlZXAgUmVzZWFyY2ggJiBTdHJhdGVnaWVzXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvQ0FDSElOR19JTkRFWElOR19QUkVXQVJNSU5HX0RFRVBfUkVTRUFSQ0gubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQ0kvQ0QgYW5kIERldmVsb3BlciBFeHBlcmllbmNlIFRvb2xpbmcgUmVzZWFyY2ggUmVwb3J0ICgyMDI1LTIwMjYpXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvQ0lfQ0RfREVWWF9UT09MSU5HLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIk11bHRpLUFnZW50IEZlYXR1cmUgUGFyaXR5IEF1ZGl0XCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvQ0xBVURFX0NPREVfRkVBVFVSRV9QQVJJVFlfQVVESVQubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQ2xhdWRlIENvZGU6IFF1ZXVlIFBlbmRpbmcgJiBCbG9ja2luZyBNZXNzYWdlcyAoUmVzZWFyY2ggJiBQbGFuKVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0NMQVVERV9DT0RFX1FVRVVFX1BFTkRJTkdfQkxPQ0tJTkcubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQ2xhdWRlIENvZGUgUGxhbiAmIERlbGVnYXRlIE1vZGVzIFx1MjAxNCBEZWVwIFJlc2VhcmNoIGZvciB0aGVnZW50IFRvb2xpbmdcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9DTEFVREVfUExBTl9ERUxFR0FURV9NT0RFU19SRVNFQVJDSC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJDbGllbnQtU2lkZSBTb2Z0d2FyZSBQYWNrYWdlIERlc2lnbiAmIERlcGxveW1lbnQgUmVzZWFyY2hcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9DTElFTlRfU0lERV9QQUNLQUdFX0RFU0lHTl9SRVNFQVJDSC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJDb2RleCBIb29rcywgTm90aWZpY2F0aW9ucyAmIEV4dGVuc2lvbiBPcHRpb25zXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvQ09ERVhfSE9PS1NfQU5EX0VYVEVOU0lPTl9PUFRJT05TLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkNvZGV4ICsgQ0xJUHJveHlBUElQbHVzOiBSZXNlYXJjaCBhbmQgUGxhblwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0NPREVYX01JTklNQVhfQ0xJUFJPWFlfUkVTRUFSQ0hfQU5EX1BMQU4ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQ29tcHJlaGVuc2l2ZSBOb24tQ2Fub25pY2FsIEF1ZGl0IGFuZCBDb25zb2xpZGF0aW9uIFBsYW5cIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9DT01QUkVIRU5TSVZFX05PTl9DQU5PTklDQUxfQVVESVQubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQ29udmVyc2F0aW9uIER1bXAgXHUyMDE0IDIwMjYtMDItMTZcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9DT05WRVJTQVRJT05fRFVNUF8yMDI2LTAyLTE2Lm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkNvbnZlcnNhdGlvbiBEdW1wIENvbXBsZXRlIFx1MjAxNCAyMDI2LTAyLTE2IFN0cnVjdHVyZWQgJiBFeHBhbmRlZFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0NPTlZFUlNBVElPTl9EVU1QXzIwMjYtMDItMTZfQ09NUExFVEUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQ29udmVyc2F0aW9uIER1bXAgMjAyNi0wMi0xNiBcdTIwMTQgQ29tcGxldGUgRXhwYW5zaW9uXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvQ09OVkVSU0FUSU9OX0RVTVBfMjAyNi0wMi0xNl9FWFBBTkRFRC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJDb3N0LUJhc2VkIFJvdXRpbmcgXHUyMDE0IERlZmVycmVkIFNjb3BlXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvQ09TVF9ST1VUSU5HX0RFRkVSUkVELm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkNvc3QgUm91dGluZyBEZWZlcnJlZCBcdTIwMTQgRm9ybWFsIERlY2lzaW9uIFJlY29yZFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0NPU1RfUk9VVElOR19ERUZFUlJFRF9FWFBBTkRFRC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJDcm9zcy1QbGF0Zm9ybSBNdWx0aS1UZW5hbnQgRGVza3RvcCBBdXRvbWF0aW9uOiBBZHZhbmNlZCBQYXR0ZXJuc1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0NST1NTX1BMQVRGT1JNX0FEVkFOQ0VEX1BBVFRFUk5TLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkNyb3NzLVBsYXRmb3JtIEV4dGVuc2lvbnM6IFdpZGVyLCBEZWVwZXIsIFBvbGlzaCAmIE9wdGltaXphdGlvblwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0NST1NTX1BMQVRGT1JNX0VYVEVOU0lPTlNfV0lERVJfREVFUEVSX09QVElNSVpBVElPTi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJDcm9zcy1QbGF0Zm9ybSBHYXBzIGFuZCBFeHRlbnNpb25zIFx1MjAxNCBSZXNlYXJjaCAmIFBsYW5cIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9DUk9TU19QTEFURk9STV9HQVBTX0FORF9FWFRFTlNJT05TX1JFU0VBUkNILm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkNyb3NzLVBsYXRmb3JtIERlc2t0b3AgQXV0b21hdGlvbjogSW50ZWdyYXRpb24gR3VpZGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9DUk9TU19QTEFURk9STV9JTlRFR1JBVElPTl9HVUlERS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJDcm9zcy1QbGF0Zm9ybSBNdWx0aS1UZW5hbnQgRGVza3RvcCBBdXRvbWF0aW9uIFJlc2VhcmNoICYgUGxhblwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0NST1NTX1BMQVRGT1JNX01VTFRJX1RFTkFOVF9ERVNLVE9QX0FVVE9NQVRJT05fUkVTRUFSQ0gubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQ3Jvc3MtUGxhdGZvcm0gRGVza3RvcCBBdXRvbWF0aW9uOiBQZXJmb3JtYW5jZSBCZW5jaG1hcmtzICYgU0xBc1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0NST1NTX1BMQVRGT1JNX1BFUkZPUk1BTkNFX0JFTkNITUFSS1MubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQ3Jvc3MtUGxhdGZvcm0gUmVzZWFyY2ggQ29tcGxldGUgXHUyMDE0IENvbXByZWhlbnNpdmUgQ29uc29saWRhdGVkIEd1aWRlXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvQ1JPU1NfUExBVEZPUk1fUkVTRUFSQ0hfQ09NUExFVEUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQ3Jvc3MtUGxhdGZvcm0gRGVza3RvcCBBdXRvbWF0aW9uOiBSZXNlYXJjaCBDb21wbGV0aW9uIFN1bW1hcnlcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9DUk9TU19QTEFURk9STV9SRVNFQVJDSF9DT01QTEVUSU9OX1NVTU1BUlkubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQ3Jvc3MtUGxhdGZvcm0gUmVzZWFyY2ggXHUyMDE0IENvbnNvbGlkYXRlZCBDb21wcmVoZW5zaXZlIEd1aWRlXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvQ1JPU1NfUExBVEZPUk1fUkVTRUFSQ0hfQ09OU09MSURBVEVELm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkNyb3NzLVBsYXRmb3JtIERlc2t0b3AgQXV0b21hdGlvbjogUmVzZWFyY2ggSW5kZXhcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9DUk9TU19QTEFURk9STV9SRVNFQVJDSF9JTkRFWC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJDcm9zcy1QbGF0Zm9ybSBNdWx0aS1UZW5hbnQgRGVza3RvcCBBdXRvbWF0aW9uOiBSZXNlYXJjaCBTdW1tYXJ5XCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvQ1JPU1NfUExBVEZPUk1fUkVTRUFSQ0hfU1VNTUFSWS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJDcm9zcy1QbGF0Zm9ybSBEZXNrdG9wIEF1dG9tYXRpb246IFNlY3VyaXR5IERlZXAgRGl2ZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0NST1NTX1BMQVRGT1JNX1NFQ1VSSVRZX0RFRVBfRElWRS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJEb2N0b3IgQ29tbWFuZDogT0F1dGgtT25seSBBdXRoZW50aWNhdGlvbiBVcGRhdGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9ET0NUT1JfT0FVVEhfT05MWV9VUERBVEUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiRVNMaW50IFx1MjE5MiBveGxpbnQgTWlncmF0aW9uIEF1ZGl0IChQaGFzZSA0KVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0VTTElOVF9BVURJVC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJFeHBhbnNpb24gQ29tcGxldGUgXHUyMDE0IEZpbmFsIFJlcG9ydFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0VYUEFOU0lPTl9DT01QTEVURV9GSU5BTC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJFeHBhbnNpb24gUGhhc2UgXHUyMDE0IENvbXBsZXRlIFN1bW1hcnlcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9FWFBBTlNJT05fUEhBU0VfQ09NUExFVEUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiRmFzdE1DUCBDb21wbGV0ZSBcdTIwMTQgQ29tcHJlaGVuc2l2ZSBJbXBsZW1lbnRhdGlvbiBHdWlkZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0ZBU1RNQ1BfQ09NUExFVEUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiRmFzdE1DUCBFbGljaXRhdGlvbiAmIENvbnRleHQgQVBJIFN1bW1hcnlcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9GQVNUTUNQX0VMSUNJVEFUSU9OX0NPTlRFWFQubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiRmFzdE1DUCBGZWF0dXJlcyAmIE1DUCBUcmFuc3BvcnQgU3BlYyBHYXBzXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvRkFTVE1DUF9GRUFUVVJFU19BTkRfVFJBTlNQT1JUX0dBUFMubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiRmFzdE1DUCBJbXBsZW1lbnRhdGlvbiBHdWlkZSBmb3IgdGhlZ2VudFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0ZBU1RNQ1BfSU1QTEVNRU5UQVRJT05fR1VJREUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiRmFzdE1DUCBNaWRkbGV3YXJlXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvRkFTVE1DUF9NSURETEVXQVJFLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkZhc3RNQ1AgUHJvZ3Jlc3MgJiBUYXNrcyBBUEkgU3VtbWFyeVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0ZBU1RNQ1BfUFJPR1JFU1NfVEFTS1MubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiRmFzdE1DUCBTYW1wbGluZyAmIFRlbGVtZXRyeVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0ZBU1RNQ1BfU0FNUExJTkdfVEVMRU1FVFJZLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkZhc3RNQ1AgU3BlYyBEZWVwIERpdmVcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9GQVNUTUNQX1NQRUNfREVFUF9ESVZFLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkZhc3RNQ1AgU3RvcmFnZSBCYWNrZW5kcyAmIEV2ZW50U3RvcmVcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9GQVNUTUNQX1NUT1JBR0VfRVZFTlRTVE9SRS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJGYXN0TUNQIFRyYW5zZm9ybXMgJiBEZXBsb3ltZW50IFN1bW1hcnlcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9GQVNUTUNQX1RSQU5TRk9STVNfREVQTE9ZTUVOVC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJGaW5hbCBFeHBhbnNpb24gUmVwb3J0IFx1MjAxNCBDb21wbGV0ZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0ZJTkFMX0VYUEFOU0lPTl9SRVBPUlQubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiR2l0IFNoaW0gU3RhcnNoaXAgT3B0aW1pemF0aW9uIFx1MjAxNCBGaXggZm9yIDgrIE1pbnV0ZSBQcm9tcHQgRGVsYXlzXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvR0lUX1NISU1fU1RBUlNISVBfT1BUSU1JWkFUSU9OLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkdpdCBUb29saW5nIEF1ZGl0IGFuZCBNb2Rlcm5pemF0aW9uIFBsYW5cIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9HSVRfVE9PTElOR19BVURJVF9BTkRfUExBTi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJHb3Zlcm5hbmNlLCBQb2xpY3kgRW5mb3JjZW1lbnQsIGFuZCBBdWRpdCBUcmFpbCBSZXNlYXJjaFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0dPVkVSTkFOQ0VfUE9MSUNZX0FVRElUX1JFU0VBUkNILm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkdvdmVybmFuY2UgV1AgR2FwcyBcdTIwMTQgSW1wbGVtZW50YXRpb24gTm90ZXNcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9HT1ZFUk5BTkNFX1dQX0dBUFMubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiR292ZXJuYW5jZSBXUCBHYXBzIFx1MjAxNCBFeHBhbmRlZCAmIEJBQ0tMT0cgSXRlbXNcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9HT1ZFUk5BTkNFX1dQX0dBUFNfRVhQQU5ERUQubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiSG9vayBSdXN0IE1pZ3JhdGlvbiBDb21wbGV0ZSBcdTIwMTQgQ29tcHJlaGVuc2l2ZSBNaWdyYXRpb24gU3RyYXRlZ3kgJiBUaW1lbGluZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0hPT0tfUlVTVF9NSUdSQVRJT05fQ09NUExFVEUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiSG9vayBSdW50aW1lIFJ1c3QgTWlncmF0aW9uOiBSZXNlYXJjaCBTeW50aGVzaXNcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9IT09LX1JVU1RfTUlHUkFUSU9OX1JFU0VBUkNIX1NZTlRIRVNJUy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJIb29rIFJ1bnRpbWUgUnVzdCBNaWdyYXRpb24gXHUyMDE0IENvbXBsZXRlIEV4cGFuc2lvblwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0hPT0tfUlVTVF9NSUdSQVRJT05fUkVTRUFSQ0hfU1lOVEhFU0lTX0VYUEFOREVELm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIklkZWEgU2VlZHMgJiBTZXNzaW9uIFN0b3JhZ2VcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9JREVBX1NFRURTX1NFU1NJT05fU1RPUkFHRS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJJZGVhIFNlZWQgUmV2aWV3IENvbXBsZXRlIFx1MjAxNCBDb25zb2xpZGF0aW9uICYgUmF0aW9uYWxlXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvSURFQV9TRUVEX1JFVklFV19DT01QTEVURS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJJbmRleCBTcHJhd2wgU3RhdHVzIFVwZGF0ZSBcdTIwMTQgQ29tcGxldGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9JTkRFWF9TUFJBV0xfU1RBVFVTX1VQREFURS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJJbi1EZXB0aCBUb29saW5nIGFuZCBHbG9iYWwgT3B0aW1pemF0aW9ucyBBdWRpdCAoMjAyNi0wMi0xNSlcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9JTl9ERVBUSF9UT09MSU5HX0FVRElUXzIwMjYubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiTGlicmFyeS1GaXJzdCBBdWRpdCBhbmQgUGxhblwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0xJQlJBUllfRklSU1RfQVVESVRfQU5EX1BMQU4ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiTGlicmFyeSBSZXBsYWNlbWVudCBBdWRpdCBcdTIwMTQgRGVlcCAmIFdpZGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9MSUJSQVJZX1JFUExBQ0VNRU5UX0FVRElUX0RFRVAubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiTGlicmFyeSBSZXBsYWNlbWVudCBDb21wbGV0ZSBcdTIwMTQgQ29tcHJlaGVuc2l2ZSBBdWRpdCAmIE1pZ3JhdGlvbiBQbGFuXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvTElCUkFSWV9SRVBMQUNFTUVOVF9DT01QTEVURS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJMaWJyYXJ5IFJlcGxhY2VtZW50IFx1MjAxNCBDb25zb2xpZGF0ZWQgTWlncmF0aW9uIFBsYW5cIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9MSUJSQVJZX1JFUExBQ0VNRU5UX0NPTlNPTElEQVRFRC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJMaWJyYXJ5IFJlcGxhY2VtZW50IFx1MjAxNCBQaGFzZSBEZXNpZ24gV29yayBCcmVha2Rvd25zIChEV0JzKVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL0xJQlJBUllfUkVQTEFDRU1FTlRfUEhBU0VfRFdCUy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJNYXN0ZXIgRXhwYW5zaW9uIFRPRE8gXHUyMDE0IENvbXBsZXRlIERvY3VtZW50YXRpb24gU3ByYXdsXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvTUFTVEVSX0VYUEFOU0lPTl9UT0RPLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIk1DUCBGdWxsIFBhcml0eSAmIEZhc3RNQ1AgVHJhbnNwb3J0IFNwZWMgQXVkaXRcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9NQ1BfRlVMTF9QQVJJVFlfQU5EX0ZBU1RNQ1BfQVVESVQubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiTUNQIGFuZCBDbGllbnQgRmVhdHVyZXMgZm9yIFNlc3Npb24gTm90aWZpY2F0aW9uc1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL01DUF9OT1RJRklDQVRJT05fT1BUSU9OUy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJNRCBEb2N1bWVudGF0aW9uIE5vcm1hbGl6YXRpb24gR3VpZGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9NRF9OT1JNQUxJWkFUSU9OX0dVSURFLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIk1lbW9yeSBPcHRpbWl6YXRpb24gXHUyMDE0IExvbmctVGVybSBQbGFuXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvTUVNT1JZX09QVElNSVpBVElPTl9MT05HX1RFUk1fUExBTi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJNdWx0aS1QbGF0Zm9ybSBBZ2VudCBEZWVwIERpdmVcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9NVUxUSV9QTEFURk9STV9ERUVQX0RJVkUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiT3BlbkNsYXcgLyBBZ2VudCBaZXJvIGFzIE1haW4gQWdlbnQgXHUyMDE0IFJlc2VhcmNoXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvT1BFTkNMQVdfQUdFTlRaRVJPX0FTX01BSU5fQUdFTlRfUkVTRUFSQ0gubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiT3BlbkNsYXcsIENsYXdIdWIsIEFnZW50IFplcm8gXHUyMDE0IFVzZSBDYXNlcyBmb3IgdGhlZ2VudFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL09QRU5DTEFXX0NMQVdIVUJfQUdFTlRaRVJPX1VTRV9DQVNFUy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJQcmlvcml0eSAxIChQMSkgRXhwYW5zaW9uIFx1MjAxNCBDb21wbGV0ZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1AxX0VYUEFOU0lPTl9DT01QTEVURS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJQcmlvcml0eSAxIChQMSkgUGhhc2UgXHUyMDE0IENvbXBsZXRlXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvUDFfUEhBU0VfQ09NUExFVEUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUDMgUG9saXNoIENvbXBsZXRlIFx1MjAxNCBGdWxsIFJlc2VhcmNoIERvY3NcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9QM19QT0xJU0hfQ09NUExFVEUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUDQgTm9ybWFsaXphdGlvbiBcdTIwMTQgQ29tcGxldGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9QNF9OT1JNQUxJWkFUSU9OX0NPTVBMRVRFLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlA0IE5vcm1hbGl6YXRpb24gXHUyMDE0IEZpbmFsIFN0YXR1c1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1A0X05PUk1BTElaQVRJT05fRklOQUwubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUDQgTm9ybWFsaXphdGlvbiBQcm9ncmVzcyBcdTIwMTQgQWxsIE1EIERvY3NcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9QNF9OT1JNQUxJWkFUSU9OX1BST0dSRVNTLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlA0IE5vcm1hbGl6YXRpb24gU3VtbWFyeSBcdTIwMTQgQ29tcGxldGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9QNF9OT1JNQUxJWkFUSU9OX1NVTU1BUlkubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUDQgTm9ybWFsaXphdGlvbiBVcGRhdGUgXHUyMDE0IFByb2dyZXNzIFJlcG9ydFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1A0X05PUk1BTElaQVRJT05fVVBEQVRFLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlBhY2thZ2UgRGVzaWduIFJlc2VhcmNoIFN1bW1hcnlcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9QQUNLQUdFX0RFU0lHTl9SRVNFQVJDSF9TVU1NQVJZLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlBoYXNlIERvY3VtZW50cyBcdTIwMTQgQ29tcGxldGUgRXhwYW5zaW9uXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvUEhBU0VfRE9DVU1FTlRTX0VYUEFOREVELm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlBsYW4gVXNhZ2UgYW5kIEJ1ZGdldCBSZXNlYXJjaFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1BMQU5fVVNBR0VfQU5EX0JVREdFVF9SRVNFQVJDSC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJQcm9hY3RpdmUgR292ZXJuYW5jZSBFdm9sdXRpb24gUGxhblwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1BST0FDVElWRV9HT1ZFUk5BTkNFX0VWT0xVVElPTl9QTEFOLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlByb2R1Y3Rpb24gUGFja2FnaW5nLCBQb2xpc2ggJiBPcHRpbWl6YXRpb24gQXVkaXQgKyBQbGFuXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvUFJPRFVDVElPTl9QQUNLQUdJTkdfUE9MSVNIX09QVElNSVpBVElPTl9BVURJVF9BTkRfUExBTi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJQeXRob24gRnJvbnRtYXR0ZXIgKyBOYXRpdmUgQmFja21hdHRlcjogUmVzZWFyY2ggQXVkaXQgJiBQbGFuXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvUFlUSE9OX0ZST05UTUFUVEVSX05BVElWRV9CQUNLTUFUVEVSX0FVRElUX1BMQU4ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUXdlbjMuNSBQbHVzIDAyLTE1IG9uIE9wZW5Sb3V0ZXIgXHUyMDE0IFBhcmV0byBSZXNlYXJjaFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1FXRU4zLjVfUExVU19PUEVOUk9VVEVSX1BBUkVUT19SRVNFQVJDSC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJSZW1vdmUgRGlyZWN0b3J5IERlcGVuZGVuY2llcyBcdTIwMTQgUHJvZHVjdGlvbiBJbnN0YWxsYXRpb24gT3B0aW1pemF0aW9uXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvUkVNT1ZFX0RJUkVDVE9SWV9ERVBFTkRFTkNJRVNfQVVESVRfQU5EX1BMQU4ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUmVzZWFyY2gsIFNlZWQgJiBGcmFnbWVudCBJbnZlbnRvcnkgXHUyMDE0IFNwcmF3bCBUb2RvICYgVW5pZmllZCBXb3JrIFN0cmVhbVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1JFU0VBUkNIX1NFRURfRlJBR01FTlRfSU5WRU5UT1JZX0FORF9TUFJBV0xfVE9ETy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJcXFwiU2VlIEFsc29cXFwiIFNlY3Rpb24gVGVtcGxhdGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9TRUVfQUxTT19URU1QTEFURS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJTZXNzaW9uIFJlc2VhcmNoIENvbXBsZXRlIFx1MjAxNCBDb21wcmVoZW5zaXZlIERlZXAtRGl2ZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1NFU1NJT05fUkVTRUFSQ0hfQ09NUExFVEUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiU2Vzc2lvbiBSZXNlYXJjaCBGcmFnbWVudHMgXHUyMDE0IDIwMjYtMDItMTVcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9TRVNTSU9OX1JFU0VBUkNIX0ZSQUdNRU5UUy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJTZXNzaW9uIFJlc2VhcmNoIEZyYWdtZW50cyBcdTIwMTQgQ29tcGxldGUgRXhwYW5zaW9uXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvU0VTU0lPTl9SRVNFQVJDSF9GUkFHTUVOVFNfRVhQQU5ERUQubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiU2hlbGwgQ29uZmlndXJhdGlvbiBBdWRpdCBhbmQgQ29uc29saWRhdGlvbiBQbGFuXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvU0hFTExfQ09ORklHX0FVRElUX0FORF9DT05TT0xJREFUSU9OX1BMQU4ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiU2hlbGwgRXJyb3IgRml4ZXMgXHUyMDE0IHpzaCBCYWQgU3Vic3RpdHV0aW9uXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvU0hFTExfRVJST1JfRklYRVMubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiU21hcnQgJiBSb2J1c3QgUHJvY2VzcyBTdHJhdGVnaWVzIFx1MjAxNCBSZXNlYXJjaCAmIFBsYW5cIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9TTUFSVF9ST0JVU1RfU1RSQVRFR0lFU19SRVNFQVJDSC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJTd2FybSBNYW5hZ2VtZW50IENvbXBsZXRlIFJlc2VhcmNoICYgSW1wbGVtZW50YXRpb24gR3VpZGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9TV0FSTV9DT01QTEVURS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJTd2FybSBPcHRpbWl6YXRpb24sIE1hbmFnZW1lbnQgJiBTY2hlZHVsaW5nIFx1MjAxNCBEZWVwIFJlc2VhcmNoXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvU1dBUk1fT1BUSU1JWkFUSU9OX1NDSEVEVUxJTkdfREVFUF9SRVNFQVJDSC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJTd2FybSBQcm9jZXNzIEF1dG9tYXRpb24gXHUyMDE0IERlZXAgUmVzZWFyY2ggJiBQbGFuXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvU1dBUk1fUFJPQ0VTU19BVVRPTUFUSU9OX0RFRVBfUkVTRUFSQ0gubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiU3dhcm0gJiBSZXNvdXJjZSBPcHRpbWl6YXRpb24gXHUyMDE0IFJlc2VhcmNoIEluZGV4XCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvU1dBUk1fUkVTRUFSQ0hfSU5ERVgubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiU3lzdGVtIFJlc291cmNlcyBDb21wbGV0ZSBQcmFjdGljYWwgR3VpZGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9TWVNURU1fUkVTT1VSQ0VTX0NPTVBMRVRFLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlN5c3RlbSBSZXNvdXJjZXMgKEZELCBDUFUsIFRocmVhZHMsIFBvcnRzKSBcdTIwMTQgRnVsbC1EZXB0aCBSZXNlYXJjaCAmIFBsYW5cIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9TWVNURU1fUkVTT1VSQ0VTX0ZEX0NQVV9ERUVQX1JFU0VBUkNILm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgVGVhbW1hdGVzOiBSZXNlYXJjaCBhbmQgSW1wbGVtZW50YXRpb24gUGxhbiAoMjAyNi0wMi0xNSlcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9URUFNTUFURVNfUkVTRUFSQ0hfQU5EX1BMQU4ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGVuYWNpdHkgdnMgQ3VzdG9tIFJldHJ5IFx1MjAxNCBBdWRpdCAmIFBsYW5cIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9URU5BQ0lUWV9SRVRSWV9BVURJVF9QTEFOLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgQ29tbWFuZCBNb2RlbCBPcHRpb25zIGFuZCBBZ2VudCBGZWF0dXJlcyBSZXNlYXJjaFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1RIR0VOVF9DT01NQU5EX01PREVMX09QVElPTlNfQU5EX0FHRU5UX0ZFQVRVUkVTX1JFU0VBUkNILm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRVSSBDb21wb3NpdG9yIENvbXBhcmlzb24gUmVzZWFyY2hcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9UVUlfQ09NUE9TSVRPUl9DT01QQVJJU09OLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlVuaWZpZWQgV29yayBTdHJlYW0gSW50ZWdyYXRpb24gXHUyMDE0IENvbXBsZXRlXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvVU5JRklFRF9XT1JLX1NUUkVBTV9JTlRFR1JBVElPTi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJVc2VyIFF1ZXVlICsgVFVJOiBFZGl0YWJsZSBQcm9tcHRzIFdoaWxlIEFnZW50IFJ1bnNcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9VU0VSX1FVRVVFX1RVSV9BTkRfQUdFTlRfUE9MTC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJWaXRlUHJlc3MgRW5oYW5jZW1lbnRzIFJlc2VhcmNoIFJlcG9ydCAoMjAyNS0yMDI2KVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1ZJVEVQUkVTU19FTkhBTkNFTUVOVFMubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVml0ZVByZXNzIFBoYXNlIDEgSW1wbGVtZW50YXRpb24gXHUyMDE0IFx1MjcwNSBDT01QTEVURVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1ZJVEVQUkVTU19QSEFTRTFfQ09NUExFVEUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVml0ZVByZXNzIFBoYXNlIDEgSW1wbGVtZW50YXRpb24gXHUyMDE0IFN0YXR1c1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1ZJVEVQUkVTU19QSEFTRTFfSU1QTEVNRU5UQVRJT04ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVml0ZVByZXNzIFBoYXNlIDIgSW1wbGVtZW50YXRpb24gXHUyMDE0IFN0YXR1c1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1ZJVEVQUkVTU19QSEFTRTJfSU1QTEVNRU5UQVRJT04ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVml0ZVByZXNzIFBoYXNlIDMgSW1wbGVtZW50YXRpb24gXHUyMDE0IFx1MjcwNSBDT01QTEVURVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL1ZJVEVQUkVTU19QSEFTRTNfQ09NUExFVEUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVml0ZVByZXNzIFJpY2ggRG9jdW1lbnRhdGlvbiBBdWRpdCAmIEltcGxlbWVudGF0aW9uIFBsYW5cIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9WSVRFUFJFU1NfUklDSF9ET0NVTUVOVEFUSU9OX0FVRElULm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlZpdGVQcmVzcyBSaWNoIERvY3VtZW50YXRpb24gXHUyMDE0IEltcGxlbWVudGF0aW9uIFBsYW5cIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9WSVRFUFJFU1NfUklDSF9ET0NVTUVOVEFUSU9OX0lNUExFTUVOVEFUSU9OX1BMQU4ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUGhhc2UgMTM6IENvbXBsaWFuY2UgUHJvZmlsZSBNYXBwaW5nXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvcGhhc2UxMy1jb21wbGlhbmNlLXByb2ZpbGUtbWFwcGluZy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJQaGFzZSAxMzogQ29zdCBTZW5zaXRpdml0eSBFeHBlcmltZW50IFBsYW5cIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9waGFzZTEzLWNvc3Qtc2Vuc2l0aXZpdHktZXhwZXJpbWVudC1wbGFuLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlBoYXNlIDEzOiBQb2xpY3kgRmVkZXJhdGlvbiBTdXJmYWNlIE1hcFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL3BoYXNlMTMtcG9saWN5LWZlZGVyYXRpb24tc3VyZmFjZS1tYXAubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUGhhc2UgMTM6IFRlbmFudCBCb3VuZGFyeSBUZXN0IE1hdHJpeFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3Jlc2VhcmNoL3BoYXNlMTMtdGVuYW50LWJvdW5kYXJ5LXRlc3QtbWF0cml4Lm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlBoYXNlIDE0OiBBdXRvbm9tb3VzIExlYXJuaW5nIGFuZCBDb3N0IFNlbnNpbmcgU3VyZmFjZSBNYXBcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9waGFzZTE0LWF1dG9ub21vdXMtbGVhcm5pbmctc3VyZmFjZS1tYXAubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUGhhc2UgMTQ6IENvc3QgU2Vuc2luZyBhbmQgTGVhcm5pbmcgVGVzdCBNYXRyaXhcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXNlYXJjaC9waGFzZTE0LWNvc3Qtc2Vuc2luZy10ZXN0LW1hdHJpeC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJQaGFzZSAxNTogRW50ZXJwcmlzZSBDb21wbGlhbmNlIFRlc3QgTWF0cml4XCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvcGhhc2UxNS1lbnRlcnByaXNlLWNvbXBsaWFuY2UtdGVzdC1tYXRyaXgubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUGhhc2UgMTU6IEVudGVycHJpc2UgTGlmZWN5Y2xlIGFuZCBDb21wbGlhbmNlIFN1cmZhY2UgTWFwXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVzZWFyY2gvcGhhc2UxNS1lbnRlcnByaXNlLWxpZmVjeWNsZS1zdXJmYWNlLW1hcC5tZFwiXG4gICAgfVxuICBdLFxuICBcIi9jbG9zdXJlL1wiOiBbXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiRFIgUmVoZWFyc2FsIFJlcG9ydFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2Nsb3N1cmUvRFJfUkVIRUFSU0FMX1JFUE9SVC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJHb3Zlcm5hbmNlICYgQ29tcGxpYW5jZSBCdW5kbGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9jbG9zdXJlL0dPVkVSTkFOQ0VfQ09NUExJQU5DRV9CVU5ETEUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUGhhc2UgNiBSZWFkaW5lc3MgUmVwb3J0XCIsXG4gICAgICBcImxpbmtcIjogXCIvY2xvc3VyZS9QSEFTRTZfUkVBRElORVNTX1JFUE9SVC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJQb3N0LUxhdW5jaCAyOC1EYXkgT2JzZXJ2YXRpb24gUGxhblwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2Nsb3N1cmUvUE9TVF9MQVVOQ0hfMjhEQVlfT0JTRVJWQVRJT04ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUm9sbGJhY2sgUmVzZXJ2ZSBQbGFuXCIsXG4gICAgICBcImxpbmtcIjogXCIvY2xvc3VyZS9ST0xMQkFDS19SRVNFUlZFX1BMQU4ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiU0xPIENlcnRpZmljYXRpb24gTWF0cml4XCIsXG4gICAgICBcImxpbmtcIjogXCIvY2xvc3VyZS9TTE9fQ0VSVElGSUNBVElPTl9NQVRSSVgubWRcIlxuICAgIH1cbiAgXSxcbiAgXCIvZG9jc2V0L1wiOiBbXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiREFHIE5vZGUtdG8tU2VydmljZSBDb250cmFjdCBDaGVja2xpc3RcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvREFHX05PREVfU0VSVklDRV9DT05UUkFDVF9DSEVDS0xJU1QubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiREFHIE5vZGUtdG8tU2VydmljZSBDb250cmFjdCBDaGVja2xpc3RcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvREFHX05PREVfVE9fU0VSVklDRV9DT05UUkFDVF9DSEVDS0xJU1QubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiRTJFIE5leHQgQ2h1bmsgUGxhbiBcdTIwMTQgRnVsbC1QaGFzZSBNZWdhIENodW5rXCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jc2V0L0UyRV9ORVhUX0NIVU5LX1BMQU4ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiRTJFIFJlbWFpbmluZyBGdWxsLURlcHRoIFBsYW5cIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvRTJFX1JFTUFJTklOR19GVUxMX0RFUFRIX1BMQU4ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiRmFzdE1DUCAzLjAgSW50ZWdyYXRpb24gUmVmZXJlbmNlIGZvciBUaGVnZW50XCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jc2V0L0ZBU1RNQ1BfSU5URUdSQVRJT04ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBJbXBsZW1lbnRhdGlvbiBTdGF0dXMgVHJhY2tlclwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC9JTVBMRU1FTlRBVElPTl9TVEFUVVMubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBPcHRpbWl6YXRpb24sIFBvbGlzaCwgYW5kIFJvYnVzdG5lc3MgQWRkZW5kdW1cIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvT1BUSU1JWkFUSU9OX1BPTElTSF9BRERFTkRVTS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJUaGVnZW50IFBhdHRlcm4gQ2F0YWxvZ1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC9QQVRURVJOUy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJDb21wcmVoZW5zaXZlIFRlc3QgUGxhbiBNYXRyaXhcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvUFJEX1RFU1RfUExBTl9NQVRSSVgubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUmVtYWluaW5nIEdhcHMgXHUyMDE0IEZ1bGwgRGVwdGggQW5hbHlzaXNcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvUkVNQUlOSU5HX0dBUFNfREVFUF9ESVZFLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlJlbWFpbmluZyBHYXBzIFx1MjAxNCBGdWxsIERlcHRoIEFuYWx5c2lzXCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jc2V0L1JFTUFJTklOR19HQVBTX0ZVTExfREVQVEgubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBSaXNrcyBhbmQgQW50aS1QYXR0ZXJucyBDYXRhbG9nXCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jc2V0L1JJU0tTX0FORF9BTlRJUEFUVEVSTlMubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiV0JTLXRvLUlzc3VlIEltcG9ydCBNYXRyaXhcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvV0JTX1RPX0lTU1VFX0lNUE9SVF9NQVRSSVgubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBDTEkgU2luZ2xlIFNvdXJjZSBvZiBUcnV0aCBBdWRpdFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LWNsaS1zaW5nbGUtc291cmNlLW9mLXRydXRoLWF1ZGl0LTIwMjYtMDItMTQubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBDcm9zcy1BbmFseXNpcyBNYXRyaXggKERlZXApXCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtY3Jvc3MtYW5hbHlzaXMtbWF0cml4LTIwMjYtMDItMTQubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBGaW5hbCBEQUcgU3BlY2lmaWNhdGlvblwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LWRhZy1maW5hbC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJUaGVnZW50IERBRyBFeHRlbnNpb24gXHUyMDE0IFBoYXNlcyAxMCB0byAxMlwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LWRhZy1waGFzZTEwLTEyLWV4dGVuc2lvbi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJ0aGVnZW50IERBRyBFeHRlbnNpb24gXHUyMDE0IFBoYXNlcyA3LCA4LCA5XCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtZGFnLXBoYXNlNy05LWV4dGVuc2lvbi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJUaGVnZW50IEdhcHMgYW5kIERpc2NvdmVyeSBSZXBvcnRcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1nYXBzLWFuZC1kaXNjb3ZlcnktMjAyNi0wMi0xNC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJUaGVnZW50IEltcGxlbWVudGF0aW9uIExvZ1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LWltcGxlbWVudGF0aW9uLWxvZy0yMDI2LTAyLTE0Lm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgS3VzaCBEb2NzIERlZXAgRGl2ZSAoWmVuICsgQWRqYWNlbnQgUHJvamVjdHMpXCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQta3VzaC1kb2NzLWRlZXAtZGl2ZS0yMDI2LTAyLTE0Lm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgTWVnYSBSZXNlYXJjaCBTeW50aGVzaXNcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1tZWdhLXJlc2VhcmNoLXN5bnRoZXNpcy0yMDI2LTAyLTE0Lm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgT3JjaGVzdHJhdGlvbiBPcHRpbWl6YXRpb24gJiBFeHBhbnNpb24gUFJEIChMaXZpbmcgRG9jdW1lbnQpXCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtb3JjaGVzdHJhdGlvbi1vcHRpbWl6YXRpb24tcHJkLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGF0dGVybiBFbmhhbmNlbWVudCBTeW50aGVzaXNcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1wYXR0ZXJucy1lbmhhbmNlbWVudC1zeW50aGVzaXMubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBQaGFzZSAxMFx1MjAxMzEyIEJ1bmRsZSBCIFNwcmludCBQbGF5Ym9va1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMTAtMTItYnVuZGxlLWItc3ByaW50LXBsYXlib29rLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgMTBcdTIwMTMxMiBCdW5kbGUgU2lnbm9mZiBhbmQgSGFuZG9mZiBQYWNrYWdlc1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMTAtMTItYnVuZGxlLXNpZ25vZmYtYW5kLWhhbmRvZmYtcGFja2FnZXMubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBQaGFzZSAxMFx1MjAxMzEyIENsb3N1cmUgUmVhZGluZXNzIFBhY2sgVGVtcGxhdGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTEwLTEyLWNsb3N1cmUtcmVhZGluZXNzLXBhY2stdGVtcGxhdGUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBQaGFzZSAxMFx1MjAxMzEyIENvbXBhY3QgRXhlY3V0aW9uIERhc2hib2FyZFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMTAtMTItY29tcGFjdC1leGVjdXRpb24tZGFzaGJvYXJkLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgMTBcdTIwMTMxMiBEcmlmdCBSZWNvbmNpbGlhdGlvbiBQbGF5Ym9va1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMTAtMTItZHJpZnQtcmVjb25jaWxpYXRpb24tcGxheWJvb2subWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBQaGFzZSAxMFx1MjAxMzEyIEV4ZWN1dGlvbiBCdW5kbGVzIFBsYXlib29rXCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtcGhhc2UxMC0xMi1leGVjdXRpb24tYnVuZGxlcy1wbGF5Ym9vay5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDEwXHUyMDEzMTIgRXhlY3V0aW9uIFN5bnRoZXNpcyBQbGF5Ym9va1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMTAtMTItZXhlY3V0aW9uLXN5bnRoZXNpcy1wbGF5Ym9vay5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDEwXHUyMDEzMTIgRXhlY3V0aW9uIFdvcmtib2FyZCAoQ2h1bmsgNClcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTEwLTEyLWV4ZWN1dGlvbi13b3JrYm9hcmQubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBQaGFzZSAxMFx1MjAxMzEyIEhhcmQtU3RvcCwgUm9sbGJhY2ssIGFuZCBTdGFiaWxpdHkgTWF0cml4XCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtcGhhc2UxMC0xMi1oYXJkLXN0b3AtYW5kLXJvbGxiYWNrLW1hdHJpeC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDEwXHUyMDEzMTIgSW1wbGVtZW50YXRpb24gQ2h1bmsgUGxhblwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMTAtMTItaW1wbGVtZW50YXRpb24tY2h1bmstcGxhbi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDEwXHUyMDEzMTIgSW1wbGVtZW50YXRpb24gSXNzdWUgUXVldWVcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTEwLTEyLWltcGxlbWVudGF0aW9uLWlzc3VlLXF1ZXVlLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgMTBcdTIwMTMxMiBJbXBsZW1lbnRhdGlvbiBUaWNrZXQgVGVtcGxhdGVzIChDaHVuayAzKVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMTAtMTItaW1wbGVtZW50YXRpb24tdGlja2V0LXRlbXBsYXRlcy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDEwXHUyMDEzMTIgSXNzdWUgQm9hcmQgQXV0b21hdGlvbiBQbGF5Ym9va1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMTAtMTItaXNzdWUtYm9hcmQtYXV0b21hdGlvbi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDEwXHUyMDEzMTIgSXNzdWUgQm9hcmQgSW1wb3J0IE5vdGVzXCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtcGhhc2UxMC0xMi1pc3N1ZS1ib2FyZC1pbXBvcnQtbm90ZXMubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBQaGFzZSAxMFx1MjAxMzEyIExhdW5jaCBTY2hlZHVsZSAoRGF5LWJ5LURheSBFeGVjdXRpb24gUGxhbilcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTEwLTEyLWxhdW5jaC1zY2hlZHVsZS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDEwXHUyMDEzMTIgTWFzdGVyIFRyYWNlYWJpbGl0eSBMZWRnZXJcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTEwLTEyLW1hc3Rlci10cmFjZWFiaWxpdHktbGVkZ2VyLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgXHUyMDE0IFBoYXNlIDEwXHUyMDEzMTIgUFJEIChPcHRpbWl6YXRpb24tRGVwdGggYW5kIFByb2R1Y3RpemF0aW9uIFdhdmUpXCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtcGhhc2UxMC0xMi1vcHRpbWFsLWRlc2lnbi1wcmQubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBQaGFzZSAxMFx1MjAxMzEyIE9yY2hlc3RyYXRvciBUb29saW5nIFN0YWNrXCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtcGhhc2UxMC0xMi1vcmNoZXN0cmF0b3ItdG9vbGluZy1zdGFjay5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDEwXHUyMDEzMTIgUG9saWN5LWFzLUNvZGUgYW5kIEF1dG9tYXRpb24gQ29udHJhY3RcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTEwLTEyLXBvbGljeS1hcy1jb2RlLWFuZC1hdXRvbWF0aW9uLWNvbnRyYWN0Lm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgMTBcdTIwMTMxMiBQUkRcdTIxOTRXQlMgRmluYWxpemF0aW9uIENyb3NzLU1hcFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMTAtMTItcHJkLXdicy1jcm9zc21hcC1maW5hbGl6YXRpb24ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBQaGFzZSAxMFx1MjAxMzEyIFBSRC1XQlMtREFHLVRpY2tldCBWYWxpZGF0aW9uIEZyYW1ld29ya1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMTAtMTItcHJkLXdicy1kYWctdGlja2V0LXZhbGlkYXRpb24ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBQaGFzZSAxMFx1MjAxMzEyIFJlbGVhc2UgUmVhZGluZXNzIGFuZCBEZWx0YSBQYWNrXCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtcGhhc2UxMC0xMi1yZWxlYXNlLXJlYWRpbmVzcy1hbmQtZGVsdGEtcGFjay5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDEwXHUyMDEzMTIgVGVzdCBhbmQgUmVhZGluZXNzIFBhY2tcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTEwLTEyLXRlc3QtcmVhZGluZXNzLXBhY2subWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBQaGFzZSAxMSBTcHJpbnQgUGxheWJvb2sgKEJ1bmRsZXMgQyBhbmQgRClcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTExLWNvbnRyb2wtYW5kLWFkYXB0YXRpb24tc3ByaW50LXBsYXlib29rLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgMTIgU3ByaW50IFBsYXlib29rIChCdW5kbGVzIEUgYW5kIEYpXCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtcGhhc2UxMi1leHBsYWluYWJpbGl0eS1hbmQtY2xvc3VyZS1zcHJpbnQtcGxheWJvb2subWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBQaGFzZSAxMysgRXh0ZW5zaW9uIEJvdW5kYXJ5IFByb3Bvc2FsXCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtcGhhc2UxMy1wbHVzLWV4dGVuc2lvbi1wcm9wb3NhbC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDNcdTIwMTM2IENsb3N1cmUgQWNjZXB0YW5jZSBDb250cmFjdCBTY2hlbWFcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTMtNi1jbG9zdXJlLWFjY2VwdGFuY2UtY29udHJhY3Qtc2NoZW1hLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgM1x1MjAxMzYgQ2xvc3VyZSBBY2NlcHRhbmNlIFBhY2sgVGVtcGxhdGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTMtNi1jbG9zdXJlLWFjY2VwdGFuY2UtcGFjay10ZW1wbGF0ZS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDNcdTIwMTM2IENsb3N1cmUgVmFsaWRhdG9yIEF1dG9tYXRpb24gUGFja2FnZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMy02LWNsb3N1cmUtdmFsaWRhdG9yLWF1dG9tYXRpb24tcGFja2FnZS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDNcdTIwMTM2IENsb3N1cmUgVmFsaWRhdGlvbiBFdmVudCBhbmQgV2FpdmVyIENvbnRyYWN0IHYxXCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtcGhhc2UzLTYtY2xvc3VyZS12YWxpZGF0b3ItZXZlbnQtYW5kLXdhaXZlci1jb250cmFjdC12MS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDNcdTIwMTM2IENsb3N1cmUgVmFsaWRhdG9yIEZhdWx0IEluamVjdGlvbiBhbmQgQ2hhb3MgVGVzdHNcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTMtNi1jbG9zdXJlLXZhbGlkYXRvci1mYXVsdC1pbmplY3Rpb24tYW5kLWNoYW9zLXRlc3RzLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgM1x1MjAxMzYgQ2xvc3VyZSBWYWxpZGF0b3IgSW1wbGVtZW50YXRpb24gQmx1ZXByaW50XCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtcGhhc2UzLTYtY2xvc3VyZS12YWxpZGF0b3ItaW1wbGVtZW50YXRpb24tYmx1ZXByaW50Lm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgM1x1MjAxMzYgQ2xvc3VyZSBWYWxpZGF0b3IgUHl0aG9uIEltcGxlbWVudGF0aW9uIEJsdWVwcmludFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlMy02LWNsb3N1cmUtdmFsaWRhdG9yLXB5dGhvbi1pbXBsZW1lbnRhdGlvbi1ibHVlcHJpbnQubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBQaGFzZSAzLTYgQ2xvc3VyZSBWYWxpZGF0b3IgUnVudGltZSBDTEkgYW5kIEFkYXB0ZXIgUGxheWJvb2tcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTMtNi1jbG9zdXJlLXZhbGlkYXRvci1ydW50aW1lLWNsaS1hbmQtYWRhcHRlci1wbGF5Ym9vay5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJUaGVnZW50IFBoYXNlIDNcdTIwMTM2IENyb3NzLVdhdmUgQnJpZGdlIGFuZCBDb250aW51aXR5IFBsYW5cIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTMtNi1jcm9zc3dhdmUtYnJpZGdlLWFuZC1jb250aW51aXR5LXBsYW4ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBcdTIwMTQgUGhhc2UgM1x1MjAxMzYgRnVsbC1EZXB0aCBFeGVjdXRpb24gQ2h1bmtcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1waGFzZTMtNi1mdWxsLWRlcHRoLWV4ZWN1dGlvbi1wcmQubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBQaGFzZSA3XHUyMDEzOSBOZXh0LVdhdmUgUFJEIChQb3N0LUNsb3N1cmUgT3B0aW1pemF0aW9uKVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlNy05LW5leHQtd2F2ZS1wcmQubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBQaGFzZSA3XHUyMDEzOSBUZXN0IGFuZCBSZWFkaW5lc3MgUGFja1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXBoYXNlNy05LXRlc3QtcmVhZGluZXNzLXBhY2subWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBPcmNoZXN0cmF0aW9uIEZpbmFsIFBsYW4gSW5kZXhcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1wbGFuLWZpbmFsLWluZGV4Lm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUHJvZHVjdGlvbiBPcmNoZXN0cmF0aW9uIFBSRCAoRmluYWwpXCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtcHJkLWZpbmFsLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUmVzZWFyY2ggVmFsaWRhdGlvbiBBZGRlbmR1bSAoWmVuICsgVGFzayBUb29scylcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC1yZXNlYXJjaC12YWxpZGF0aW9uLTIwMjYtMDItMTQubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwidGhlZ2VudCBUaGlyZC1QYXJ0eSBCdW5kbGUgTWFuaWZlc3RcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC10aGlyZC1wYXJ0eS1idW5kbGUtbWFuaWZlc3QubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBGaW5hbCBXQlMgKENvbXByZWhlbnNpdmUpXCIsXG4gICAgICBcImxpbmtcIjogXCIvZG9jc2V0L3RoZWdlbnQtd2JzLWZpbmFsLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgV0JTIFx1MjAxNCBQaGFzZSAxMCB0byBQaGFzZSAxMiAoT3B0aW1pemF0aW9uLURlcHRoIGFuZCBQcm9kdWN0aXphdGlvbilcIixcbiAgICAgIFwibGlua1wiOiBcIi9kb2NzZXQvdGhlZ2VudC13YnMtcGhhc2UxMC0xMi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJUaGVnZW50IFdCUyBcdTIwMTQgUGhhc2UgNyB0byBQaGFzZSA5IChOZXh0LVdhdmUgRXhlY3V0aW9uKVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RvY3NldC90aGVnZW50LXdicy1waGFzZTctOS5tZFwiXG4gICAgfVxuICBdLFxuICBcIi9lbnRlcnByaXNlL1wiOiBbXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiRGVjb21taXNzaW9uaW5nIGFuZCBTdW5zZXQgUGxhblwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2VudGVycHJpc2UvREVDT01NSVNTSU9OSU5HX1BMQU4ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUHJvZ3JhbSBPcGVyYXRpbmcgTW9kZWwgYW5kIE93bmVyc2hpcCBNYXBcIixcbiAgICAgIFwibGlua1wiOiBcIi9lbnRlcnByaXNlL09QRVJBVElOR19NT0RFTC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJTZWN1cml0eSBhbmQgQ29tcGxpYW5jZSBTaWdub2ZmIFBhY2thZ2VcIixcbiAgICAgIFwibGlua1wiOiBcIi9lbnRlcnByaXNlL1NFQ1VSSVRZX0NPTVBMSUFOQ0VfU0lHTk9GRi5tZFwiXG4gICAgfVxuICBdLFxuICBcIi9wbGFucy9cIjogW1xuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgVW5pZmllZCBQbGFuIFx1MjAxNCBNYXN0ZXIgSW5kZXhcIixcbiAgICAgIFwibGlua1wiOiBcIi9wbGFucy8wMC1NQVNURVItSU5ERVgubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiMDEgXHUyMDE0IFByb2plY3QgU3RhdGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9wbGFucy8wMS1QUk9KRUNULVNUQVRFLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIjAyIFx1MjAxNCBVbmlmaWVkIFdvcmsgQnJlYWtkb3duIFN0cnVjdHVyZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zLzAyLVVOSUZJRUQtV0JTLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIjAzIFx1MjAxNCBVbmlmaWVkIERBRyBTcGVjaWZpY2F0aW9uc1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zLzAzLVVOSUZJRUQtREFHLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIjA0IFx1MjAxNCBVbmlmaWVkIFJlcXVpcmVtZW50c1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zLzA0LVJFUVVJUkVNRU5UUy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCIwNSBcdTIwMTQgQXJjaGl0ZWN0dXJlICYgUGF0dGVybnNcIixcbiAgICAgIFwibGlua1wiOiBcIi9wbGFucy8wNS1BUkNISVRFQ1RVUkUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiMDYgXHUyMDE0IEltcGxlbWVudGF0aW9uIEd1aWRlXCIsXG4gICAgICBcImxpbmtcIjogXCIvcGxhbnMvMDYtSU1QTEVNRU5UQVRJT04tR1VJREUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiMDcgXHUyMDE0IFRlc3QgU3RyYXRlZ3lcIixcbiAgICAgIFwibGlua1wiOiBcIi9wbGFucy8wNy1URVNULVNUUkFURUdZLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIjA4IFx1MjAxNCBPcHRpbWl6YXRpb24sIFBvbGlzaCwgRW5oYW5jZW1lbnQgJiBSb2J1c3RuZXNzIENhdGFsb2dcIixcbiAgICAgIFwibGlua1wiOiBcIi9wbGFucy8wOC1PUFRJTUlaQVRJT04tQ0FUQUxPRy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCIwOSBcdTIwMTQgUmlzayBSZWdpc3RyeSAmIEFudGktUGF0dGVybnNcIixcbiAgICAgIFwibGlua1wiOiBcIi9wbGFucy8wOS1SSVNLLVJFR0lTVFJZLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIjEwIFx1MjAxNCBTdWJhZ2VudCBEaXNwYXRjaCBQbGFuXCIsXG4gICAgICBcImxpbmtcIjogXCIvcGxhbnMvMTAtU1VCQUdFTlQtRElTUEFUQ0gubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiMTIgXHUyMDE0IEN5Y2xlbG9vcCBMb29wcyAmIENoZWNrZXIgQWdlbnQgRGVzaWduXCIsXG4gICAgICBcImxpbmtcIjogXCIvcGxhbnMvMTItTElGRUNZQ0xFLUxPT1AtREVTSUdOLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkRlc2lnbjogdGhlZ2VudCBpbnN0YWxsIENMSSBDb21tYW5kXCIsXG4gICAgICBcImxpbmtcIjogXCIvcGxhbnMvMjAyNi0wMi0xNC10aGVnZW50LWluc3RhbGwtZGVzaWduLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcInRoZWdlbnQgaW5zdGFsbCBJbXBsZW1lbnRhdGlvbiBQbGFuXCIsXG4gICAgICBcImxpbmtcIjogXCIvcGxhbnMvMjAyNi0wMi0xNC10aGVnZW50LWluc3RhbGwtaW1wbGVtZW50YXRpb24tcGxhbi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJSZXNlYXJjaCBhbmQgRWxpY2l0YXRpb24gUGxhbiBcdTIwMTQgMjAyNi0wMi0xNVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zLzIwMjYtMDItMTUtUkVTRUFSQ0gtQU5ELUVMSUNJVEFUSU9OLVBMQU4ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwidGhlZ2VudCBzaXRiYWNrIFx1MjAxNCBEZXNpZ24gJiBJbXBsZW1lbnRhdGlvbiBQbGFuXCIsXG4gICAgICBcImxpbmtcIjogXCIvcGxhbnMvMjAyNi0wMi0xNS10aGVnZW50LXNpdGJhY2stZGVzaWduLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRyYXkgQXBwbGljYXRpb24gRGVzaWduIC0gUGx1Z2luLUJhc2VkIEFyY2hpdGVjdHVyZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zLzIwMjYtMDItMTUtdHJheS1hcHBsaWNhdGlvbi1kZXNpZ24ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQWdlbnREZXBsb3llciArIExpZmVjeWNsZUNvbnRyb2xsZXIgSW50ZWdyYXRpb24gUmV2aWV3XCIsXG4gICAgICBcImxpbmtcIjogXCIvcGxhbnMvMjAyNi0wMi0xNi1BR0VOVF9ERVBMT1lFUl9SRVZJRVcubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQ3ljbGVsb29wICsgQWdpbGVQbHVzIEludGVncmF0aW9uIFBsYW5cIixcbiAgICAgIFwibGlua1wiOiBcIi9wbGFucy8yMDI2LTAyLTE2LUNZQ0xFTE9PUF9BR0lMRVBMVVNfSU5URUdSQVRJT04ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiRnVsbCBMaXRlTExNIEZlYXR1cmUgSW50ZWdyYXRpb24gUGxhblwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zLzIwMjYtMDItMTYtbGl0ZWxsbS1mdWxsLWZlYXR1cmVzLXBsYW4ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiTGl0ZUxMTSBJbnRlZ3JhdGlvbiBEZXNpZ25cIixcbiAgICAgIFwibGlua1wiOiBcIi9wbGFucy8yMDI2LTAyLTE2LWxpdGVsbG0taW50ZWdyYXRpb24tZGVzaWduLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkxpdGVMTE0gUm91dGVyIEludGVncmF0aW9uIEltcGxlbWVudGF0aW9uIFBsYW5cIixcbiAgICAgIFwibGlua1wiOiBcIi9wbGFucy8yMDI2LTAyLTE2LWxpdGVsbG0taW50ZWdyYXRpb24tcGxhbi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJTdXBlcm1lbW9yeS5haSBJbnRlZ3JhdGlvbiBQbGFuIChXUC01MDAxLVNNKVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zLzIwMjYtMDItMTYtc3VwZXJtZW1vcnktaW50ZWdyYXRpb24tcGxhbi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJBZ2VudCBTYW5kYm94aW5nIEltcGxlbWVudGF0aW9uIFBsYW5cIixcbiAgICAgIFwibGlua1wiOiBcIi9wbGFucy9BR0VOVF9TQU5EQk9YSU5HX0lNUExFTUVOVEFUSU9OX1BMQU4ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQ2F0YWxvZyBcdTIxOTQgQ0xJUHJveHlBUElQbHVzIEZvcmsgQWxpZ25tZW50XCIsXG4gICAgICBcImxpbmtcIjogXCIvcGxhbnMvQ0FUQUxPR19DTElQUk9YWV9GT1JLX0FMSUdOTUVOVC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJDTElQcm94eUFQSSAmIFRoZWdlbnQgV29yayBQbGFuIFx1MjAxMyBVbmlmaWVkIFBoYXNlZCBXQlNcIixcbiAgICAgIFwibGlua1wiOiBcIi9wbGFucy9DTElQUk9YWV9BUElfQU5EX1RIR0VOVF9VTklGSUVEX1BMQU4ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQWdlbnQgT3JjaGVzdHJhdGlvbiBIYXJuZXNzOiBNdWx0aS1QbGF0Zm9ybSAoRXh0cmVtZS1EZXB0aCBQbGFuKVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL0NPREVYX0RPTlVUX0hBUk5FU1NfUExBTi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJDcm9zcy1QbGF0Zm9ybSBNdWx0aS1UZW5hbnQgRGVza3RvcCBBdXRvbWF0aW9uIENvbXBsZXRlIFBsYW5cIixcbiAgICAgIFwibGlua1wiOiBcIi9wbGFucy9DUk9TU19QTEFURk9STV9DT01QTEVURV9QTEFOLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkNyb3NzLVBsYXRmb3JtIE11bHRpLVRlbmFudCBEZXNrdG9wIEF1dG9tYXRpb24gSW1wbGVtZW50YXRpb24gUGxhblwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL0NST1NTX1BMQVRGT1JNX01VTFRJX1RFTkFOVF9JTVBMRU1FTlRBVElPTl9QTEFOLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkN1cnNvciBBUEkgSW50ZWdyYXRpb24gUmVzZWFyY2ggJiBQbGFuXCIsXG4gICAgICBcImxpbmtcIjogXCIvcGxhbnMvQ1VSU09SX0FQSV9JTlRFR1JBVElPTl9SRVNFQVJDSC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJEZWJ1ZyBUYWdzIGFuZCBNZXRyaWNzIChUcmFuc2llbnQgUmVzcG9uc2UgVGFncylcIixcbiAgICAgIFwibGlua1wiOiBcIi9wbGFucy9ERUJVR19UQUdTX0FORF9NRVRSSUNTLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkRpc3RyaWJ1dGVkIE1vZGVsIFJvdXRpbmcgUGxhblwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL0RJU1RSSUJVVEVEX01PREVMX1JPVVRJTkdfUExBTi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJEb2N1bWVudGF0aW9uIEV4cGFuc2lvbiBQcm9jZXNzXCIsXG4gICAgICBcImxpbmtcIjogXCIvcGxhbnMvRE9DVU1FTlRBVElPTl9FWFBBTlNJT05fUFJPQ0VTUy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJEb2N1bWVudGF0aW9uIEV4cGFuc2lvbiBUT0RPXCIsXG4gICAgICBcImxpbmtcIjogXCIvcGxhbnMvRE9DVU1FTlRBVElPTl9FWFBBTlNJT05fVE9ETy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJEb2N1bWVudGF0aW9uIENvbnNvbGlkYXRpb24gJiBJbXBsZW1lbnRhdGlvbiBXQlNcIixcbiAgICAgIFwibGlua1wiOiBcIi9wbGFucy9ET0NfQ09OU09MSURBVElPTl9BTkRfSU1QTEVNRU5UQVRJT05fV0JTLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkZhY3RvcnkgRHJvaWQgSGFybmVzcyBJbnRlZ3JhdGlvbiBQbGFuXCIsXG4gICAgICBcImxpbmtcIjogXCIvcGxhbnMvRkFDVE9SWV9EUk9JRF9IQVJORVNTX0lOVEVHUkFUSU9OX1BMQU4ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiRnVsbCBTaGVsbCBcdTIxOTIgUnVzdCBXaGVyZSBCZW5lZmljaWFsXCIsXG4gICAgICBcImxpbmtcIjogXCIvcGxhbnMvRlVMTF9TSEVMTF9UT19SVVNUX1dIRVJFX0JFTkVGSUNJQUwubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiSG9saXN0aWMgKyBIYXJtb25pb3VzIERlc2lnbiAmIEZ1bGwgSW50ZWdyYXRpb24gUGxhblwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL0hPTElTVElDX0hBUk1PTklPVVNfREVTSUdOX0FORF9JTlRFR1JBVElPTl9QTEFOLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkhvb2sgUnVudGltZSBSdXN0IE1pZ3JhdGlvbiBDb21wbGV0ZSBHdWlkZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL0hPT0tfUlVOVElNRV9SVVNUX0NPTVBMRVRFLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkhvb2sgUnVudGltZTogRnVsbCBSdXN0IE1pZ3JhdGlvbiBEZXNpZ24gKERlZXAgJiBXaWRlKVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL0hPT0tfUlVOVElNRV9SVVNUX0RFU0lHTi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJIeWJyaWQgTWFjL1dpbmRvd3MgRW52aXJvbm1lbnQgSW1wbGVtZW50YXRpb24gUGxhblwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL0hZQlJJRF9FTlZfSU1QTEVNRU5UQVRJT05fUExBTi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJMaXRlTExNICsgQ0xJUHJveHlBUElQbHVzICsgQmlmcm9zdCBIYXJtb255XCIsXG4gICAgICBcImxpbmtcIjogXCIvcGxhbnMvTElURUxMTV9DTElQUk9YWV9CSUZST1NUX0hBUk1PTlkubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiTUNQIEJ1bmRsZTogdGhlZ2VudCArIEJyb3dzZXIgVG9vbHMgKFJlcGxhY2UgTWFudWFsIFBsYXl3cmlnaHQpXCIsXG4gICAgICBcImxpbmtcIjogXCIvcGxhbnMvTUNQX0JVTkRMRV9QTEFZV1JJR0hUX1JFUExBQ0VNRU5ULm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIk1DUCBUb29sIE9wdGltaXphdGlvbiwgUG9saXNoICYgRW5oYW5jZW1lbnQgUGxhblwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL01DUF9UT09MX09QVElNSVpBVElPTl9QTEFOLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIk11bHRpLVBsYXRmb3JtIFBhcml0eSBNYXN0ZXIgUGxhbiAmIE1hdHJpeFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL01VTFRJX1BMQVRGT1JNX1BBUklUWV9NQVNURVJfUExBTi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJOZXcgUHJvdmlkZXJzIEF1dGggUmVzZWFyY2ggJiBQbGFuXCIsXG4gICAgICBcImxpbmtcIjogXCIvcGxhbnMvTkVXX1BST1ZJREVSU19BVVRIX1JFU0VBUkNILm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIk9wZW5Sb3V0ZXItU3R5bGUgUm91dGluZyArIENMSVByb3h5QVBJUGx1cyBJbnRlZ3JhdGlvblwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL09QRU5ST1VURVJfU1RZTEVfUk9VVElOR19BTkRfQ0xJUFJPWFkubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUHJvY2VzcyAmIFRvb2wgT3B0aW1pemF0aW9uIENvbXBsZXRlIFBsYW5cIixcbiAgICAgIFwibGlua1wiOiBcIi9wbGFucy9QUk9DRVNTX09QVElNSVpBVElPTl9DT01QTEVURV9QTEFOLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlByb2Nlc3MgYW5kIFRvb2wgT3B0aW1pemF0aW9uIFBsYW5cIixcbiAgICAgIFwibGlua1wiOiBcIi9wbGFucy9QUk9DRVNTX09QVElNSVpBVElPTl9QTEFOLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlByb21wdCBIaXN0b3J5IENvbGxlY3Rpb24gJiBBdWRpdCBTeXN0ZW06IENvbXByZWhlbnNpdmUgUGxhblwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL1BST01QVF9ISVNUT1JZX0NPTExFQ1RJT05fQU5EX0FVRElUX1NZU1RFTS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJQcm9tcHQgSGlzdG9yeSBDb2xsZWN0aW9uICYgQXVkaXQgU3lzdGVtIENvbXBsZXRlIEd1aWRlXCIsXG4gICAgICBcImxpbmtcIjogXCIvcGxhbnMvUFJPTVBUX0hJU1RPUllfQ09MTEVDVElPTl9DT01QTEVURS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJSZW1vdGUgQ29tcHV0ZSBJbXBsZW1lbnRhdGlvbiBEZXRhaWxcIixcbiAgICAgIFwibGlua1wiOiBcIi9wbGFucy9SRU1PVEVfQ09NUFVURV9JTVBMRU1FTlRBVElPTl9ERVRBSUwubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwidGhlZ2VudCBTZXR1cDogUHJvcG9zZWQgSG9va3MsIFBsdWdpbnMsIFNraWxscywgTUNQICYgRG9jc1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL1NFVFVQX1BST1BPU0VEX0lURU1TLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlNoZWxsIEVudmlyb25tZW50IEFkdmFuY2VkIEVuaGFuY2VtZW50IFBsYW5cIixcbiAgICAgIFwibGlua1wiOiBcIi9wbGFucy9TSEVMTF9FTlZJUk9OTUVOVF9BRFZBTkNFRF9FTkhBTkNFTUVOVF9QTEFOLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlNoZWxsIEVudmlyb25tZW50IEFkdmFuY2VkIEVuaGFuY2VtZW50IC0gSW1wbGVtZW50YXRpb24gU3VtbWFyeVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL1NIRUxMX0VOVklST05NRU5UX0FEVkFOQ0VEX0lNUExFTUVOVEFUSU9OX1NVTU1BUlkubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiU2hlbGwgRW52aXJvbm1lbnQgQ29tcGxldGUgUGxhblwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL1NIRUxMX0VOVklST05NRU5UX0NPTVBMRVRFX1BMQU4ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiU2hlbGwgRW52aXJvbm1lbnQgSW1wbGVtZW50YXRpb24gU3VtbWFyeVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL1NIRUxMX0VOVklST05NRU5UX0lNUExFTUVOVEFUSU9OX1NVTU1BUlkubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiU2hlbGwgRW52aXJvbm1lbnQgT3B0aW1pemF0aW9uICYgRW5oYW5jZW1lbnQgUGxhblwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3BsYW5zL1NIRUxMX0VOVklST05NRU5UX09QVElNSVpBVElPTl9QTEFOLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlN5bmMvVXBkYXRlIENvbW1hbmQgJiBGdWxsIFN5c3RlbSBBdWRpdCBQbGFuXCIsXG4gICAgICBcImxpbmtcIjogXCIvcGxhbnMvU1lOQ19VUERBVEVfQ09NTUFORF9BTkRfU1lTVEVNX0FVRElUX1BMQU4ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBGYXN0TUNQIDMuMCBJbXBsZW1lbnRhdGlvbiBQbGFuXCIsXG4gICAgICBcImxpbmtcIjogXCIvcGxhbnMvVEhHRU5UX0ZBU1RNQ1BfSU1QTEVNRU5UQVRJT05fUExBTi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJSdW50aW1lIERpc3BhdGNoIENvbnNvbGlkYXRpb24gJiBGb3JrIEZpeDogQ29tcGxldGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9wbGFucy9VTFRSQV9TSElNX0NPTlNPTElEQVRJT05fQ09NUExFVEUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVWx0cmEtU2hpbSBGb3JrIEZhaWx1cmUgRml4OiBSb290IENhdXNlIEFuYWx5c2lzICYgU29sdXRpb25cIixcbiAgICAgIFwibGlua1wiOiBcIi9wbGFucy9VTFRSQV9TSElNX0ZPUktfRkFJTFVSRV9GSVgubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVW5pZmllZCBMb2dpbiBGbG93OiBPcGVuIFVSTCArIFByb21wdCBmb3IgS2V5XCIsXG4gICAgICBcImxpbmtcIjogXCIvcGxhbnMvVU5JRklFRF9MT0dJTl9GTE9XLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlVuaWZpZWQgU3lzdGVtIEFwcGxpY2F0aW9uIFBsYW5cIixcbiAgICAgIFwibGlua1wiOiBcIi9wbGFucy9VTklGSUVEX1NZU1RFTV9BUFBMSUNBVElPTl9QTEFOLm1kXCJcbiAgICB9XG4gIF0sXG4gIFwiL2NoYW5nZXMvXCI6IFtcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJIZXhhZ29uYWwgTWlncmF0aW9uXCIsXG4gICAgICBcImNvbGxhcHNlZFwiOiBmYWxzZSxcbiAgICAgIFwiaXRlbXNcIjogW1xuICAgICAgICB7XG4gICAgICAgICAgXCJ0ZXh0XCI6IFwiSGV4YWdvbmFsIEFyY2hpdGVjdHVyZSBNaWdyYXRpb24gLS0gdGhlZ2VudFwiLFxuICAgICAgICAgIFwibGlua1wiOiBcIi9oZXhhZ29uYWwtbWlncmF0aW9uL3Byb3Bvc2FsLm1kXCJcbiAgICAgICAgfVxuICAgICAgXVxuICAgIH1cbiAgXSxcbiAgXCIvY2hlY2tsaXN0cy9cIjogW1xuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkh5YnJpZCBNYWMvV2luZG93cyBFbnZpcm9ubWVudCBTZXR1cCBDaGVja2xpc3RcIixcbiAgICAgIFwibGlua1wiOiBcIi9jaGVja2xpc3RzL0hZQlJJRF9FTlZfU0VUVVBfQ0hFQ0tMSVNULm1kXCJcbiAgICB9XG4gIF0sXG4gIFwiL2NvbnRyYWN0cy9cIjogW1xuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkNvbnRyYWN0IEF1dGhvcml0eVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2NvbnRyYWN0cy9DT05UUkFDVF9BVVRIT1JJVFkubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiRmFsbGJhY2sgQ29udHJvbCBQbGFuZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2NvbnRyYWN0cy9GQUxMQkFDS19QT0xJQ1kubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUHJvdmlkZXIgQWRhcHRlciBDb250cmFjdHMgKEctUlYtMDUpXCIsXG4gICAgICBcImxpbmtcIjogXCIvY29udHJhY3RzL1BST1ZJREVSX0FEQVBURVJfQ09OVFJBQ1RTLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkNvbnRyYWN0IFVwZ3JhZGUgUGxheWJvb2tcIixcbiAgICAgIFwibGlua1wiOiBcIi9jb250cmFjdHMvVVBHUkFERV9QTEFZQk9PSy5tZFwiXG4gICAgfVxuICBdLFxuICBcIi9zY3JhdGNocGFkL1wiOiBbXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiU2Vzc2lvbiBTY3JhdGNoIEJvYXJkICYgT3B0aW1pemF0aW9uIFBsYW5cIixcbiAgICAgIFwibGlua1wiOiBcIi9zY3JhdGNocGFkL3Nlc3Npb25fcmV2aWV3Lm1kXCJcbiAgICB9XG4gIF0sXG4gIFwiL2FyY2hpdGVjdHVyZS9cIjogW1xuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkFnZW50IFNhbmRib3hpbmcgQXJjaGl0ZWN0dXJlOiBXQVNNL0NvbnRhaW5lcnMvVk1zIChObyBEb2NrZXIpXCIsXG4gICAgICBcImxpbmtcIjogXCIvYXJjaGl0ZWN0dXJlL0FHRU5UX1NBTkRCT1hJTkdfQVJDSElURUNUVVJFLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlB5dGhvbiBGcm9udG1hdHRlciArIE5hdGl2ZSBCYWNrbWF0dGVyIEFyY2hpdGVjdHVyZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2FyY2hpdGVjdHVyZS9GUk9OVE1BVFRFUl9CQUNLTUFUVEVSX0FSQ0hJVEVDVFVSRS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJIeWJyaWQgTWFjL1dpbmRvd3MgRGV2ZWxvcG1lbnQgRW52aXJvbm1lbnQgQXJjaGl0ZWN0dXJlXCIsXG4gICAgICBcImxpbmtcIjogXCIvYXJjaGl0ZWN0dXJlL0hZQlJJRF9NQUNfV0lOX0RFVl9FTlZJUk9OTUVOVC5tZFwiXG4gICAgfVxuICBdLFxuICBcIi9ndWlkZXMvXCI6IFtcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJBZ2VudCBEZWJ1Z2dpbmcgYW5kIFJlbWVkaWF0aW9uIEd1aWRlXCIsXG4gICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL0FHRU5UX0RFQlVHR0lOR19BTkRfUkVNRURJQVRJT05fR1VJREUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQWdlbnQgSW5zdHJ1Y3Rpb25zOiB0aGVnZW50IERlZXAtRGl2ZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9BR0VOVF9JTlNUUlVDVElPTlNfVEhFR0VOVC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJBdXRvbWF0ZWQgRG9jdW1lbnRhdGlvbiBEZW1vc1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9BVVRPTUFURURfREVNT1MubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQktNIEltcGxlbWVudGF0aW9uIEd1aWRlc1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9CS01fSU1QTEVNRU5UQVRJT05fR1VJREVTLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkNyb3NzLVBsYXRmb3JtIERlc2t0b3AgQXV0b21hdGlvbiBcdTIwMTQgQ29tcGxldGUgR3VpZGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvQ1JPU1NfUExBVEZPUk1fQ09NUExFVEUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQ3Jvc3MtUGxhdGZvcm0gRGVza3RvcCBBdXRvbWF0aW9uOiBEZXZlbG9wZXIgQ29va2Jvb2tcIixcbiAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvQ1JPU1NfUExBVEZPUk1fREVWRUxPUEVSX0NPT0tCT09LLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkNyb3NzLVBsYXRmb3JtIERlc2t0b3AgQXV0b21hdGlvbjogSW1wbGVtZW50YXRpb24gVGVtcGxhdGVzXCIsXG4gICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL0NST1NTX1BMQVRGT1JNX0lNUExFTUVOVEFUSU9OX1RFTVBMQVRFUy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJDcm9zcy1QbGF0Zm9ybSBEZXNrdG9wIEF1dG9tYXRpb246IE1pZ3JhdGlvbiBHdWlkZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9DUk9TU19QTEFURk9STV9NSUdSQVRJT05fR1VJREUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQ3Jvc3MtUGxhdGZvcm0gRGVza3RvcCBBdXRvbWF0aW9uOiBRdWljayBTdGFydCBHdWlkZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9DUk9TU19QTEFURk9STV9RVUlDS19TVEFSVC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJDcm9zcy1QbGF0Zm9ybSBEZXNrdG9wIEF1dG9tYXRpb246IEltcGxlbWVudGF0aW9uIFJvYWRtYXBcIixcbiAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvQ1JPU1NfUExBVEZPUk1fUk9BRE1BUC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJEb2N0b3IgQ29tbWFuZCBGaXhlc1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9ET0NUT1JfRklYRVMubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiRml4IFNoZWxsIENvcnJ1cHRpb24gSXNzdWVcIixcbiAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvRklYX1NIRUxMX0NPUlJVUFRJT04ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiRml4IFNoZWxsIEZvcmsgRXJyb3JzOiBRdWljayBHdWlkZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9GSVhfU0hFTExfRk9SS19FUlJPUlMubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiR3VpZGVzIEluZGV4XCIsXG4gICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL0dVSURFU19JTkRFWC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJIeWJyaWQgTWFjL1dpbmRvd3MgRW52aXJvbm1lbnQgUXVpY2sgU3RhcnQgR3VpZGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvSFlCUklEX0VOVl9RVUlDS19TVEFSVC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJJbXBsZW1lbnRhdGlvbiBQYXR0ZXJucyBHdWlkZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9JTVBMRU1FTlRBVElPTl9QQVRURVJOUy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJKb2IgUG9vbCBTeXN0ZW0gLSBVc2FnZSBHdWlkZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9KT0JfUE9PTF9VU0FHRS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJPQXV0aC1Pbmx5IEF1dGhlbnRpY2F0aW9uIFBvbGljeVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9PQVVUSF9PTkxZX0FVVEhFTlRJQ0FUSU9OLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIk9wZXJhdGlvbmFsIExlYXJuaW5nIEFzc2V0cyAoV1AtMTIwMDgpXCIsXG4gICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL09QRVJBVElPTkFMX0xFQVJOSU5HLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIm94bGludCBJbnRlZ3JhdGlvbiBHdWlkZSAoUGhhc2UgNClcIixcbiAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvT1hMSU5UX0lOVEVHUkFUSU9OX0dVSURFLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRoZWdlbnQgUGhhc2UgMTAgU3VtbWFyeSBhbmQgTWlncmF0aW9uIEd1aWRlIChXUC0xMDAxMClcIixcbiAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvUEhBU0VfMTBfR1VJREUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBQaGFzZSAxMSBTdW1tYXJ5IGFuZCBFdmlkZW5jZSBQYWNrIChXUC0xMTAxMClcIixcbiAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvUEhBU0VfMTFfR1VJREUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUGhhc2UgNCBRdWljayBTdGFydDogRVNMaW50IFx1MjE5MiBveGxpbnQgTWlncmF0aW9uXCIsXG4gICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL1BIQVNFXzRfUVVJQ0tfU1RBUlQubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBQaGFzZSA3LTkgU3VtbWFyeSBhbmQgVHJhaW5pbmcgR3VpZGUgKFdQLTkwMTApXCIsXG4gICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL1BIQVNFXzdfOV9HVUlERS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJQcm9tcHRzIFRvb2xpbmcgXHUyMDE0IEN1cnNvciAvIENvZGV4IC8gQ2xhdWRlIEFnZ3JlZ2F0ZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9QUk9NUFRTX1RPT0xJTkcubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUHJvdmlkZXIgU2V0dXAgR3VpZGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvUFJPVklERVJfU0VUVVBfR1VJREUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUXVhbGl0eSBBc3N1cmFuY2UgR3VpZGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvUVVBTElUWV9BU1NVUkFOQ0UubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUXVpY2sgRml4OiBTaGVsbCBTZXR1cCBJc3N1ZXNcIixcbiAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvUVVJQ0tfRklYX1NIRUxMX1NFVFVQLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlJ1bnRpbWUgT3B0aW1pemF0aW9uIEd1aWRlXCIsXG4gICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL1JVTlRJTUVfT1BUSU1JWkFUSU9OLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlNoZWxsIEFkdmFuY2VkIEZlYXR1cmVzIEd1aWRlXCIsXG4gICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL1NIRUxMX0FEVkFOQ0VEX0ZFQVRVUkVTLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlNoZWxsIENvcnJ1cHRpb24gRml4IC0gQ29tcGxldGUgU29sdXRpb25cIixcbiAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvU0hFTExfQ09SUlVQVElPTl9GSVhfQ09NUExFVEUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQ29tcGxldGUgU2hlbGwgRW52aXJvbm1lbnQgU3lzdGVtXCIsXG4gICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL1NIRUxMX0VOVklST05NRU5UX0NPTVBMRVRFLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlNoZWxsIEVudmlyb25tZW50IE1hbmFnZW1lbnRcIixcbiAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvU0hFTExfRU5WSVJPTk1FTlRfTUFOQUdFTUVOVC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJTaGVsbCBPcHRpbWl6YXRpb24gR3VpZGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvU0hFTExfT1BUSU1JWkFUSU9OX0dVSURFLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlNoZWxsICYgWnNoIFBsdWdpbiBTZXR1cCBcdTIwMTQgTG9uZy1UZXJtIEZpeFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9TSEVMTF9aU0hfUExVR0lOX1NFVFVQLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlNpdGJhY2sgUGx1Z2luIEFQSVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9TSVRCQUNLX1BMVUdJTlMubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiU3RhcnNoaXAgKyBkaXJlbnYgU2V0dXAgQ29tcGxldGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvU1RBUlNISVBfRElSRU5WX1NFVFVQLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlx1RDgzRFx1REU4MCBIb29rcyBPcHRpbWl6YXRpb24gSW5pdGlhdGl2ZSAtIFNUQVJUIEhFUkVcIixcbiAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvU1RBUlRfSEVSRS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJUYXNrIFJvdXRpbmcgUXVpY2sgUmVmZXJlbmNlIEd1aWRlXCIsXG4gICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL1RBU0tfUk9VVElOR19RVUlDS19SRUYubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwidGhlZ2VudCBUZXN0aW5nIEd1aWRlXCIsXG4gICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL1RFU1RJTkcubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVHJvdWJsZXNob290aW5nIEd1aWRlXCIsXG4gICAgICBcImxpbmtcIjogXCIvZ3VpZGVzL1RST1VCTEVTSE9PVElORy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJWaXRlUHJlc3MgRG9jc2l0ZSBTZXR1cFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9WSVRFUFBSRVNTX1NFVFVQLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkFudGktUGF0dGVybiBEZXRlY3Rpb24gR3VpZGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvYW50aS1wYXR0ZXJucy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJBcmNoaXRlY3R1cmUgRW5mb3JjZW1lbnQgR3VpZGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9ndWlkZXMvYXJjaGl0ZWN0dXJlLWVuZm9yY2VtZW50Lm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkd1aWRlc1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL2d1aWRlcy9pbmRleC5tZFwiXG4gICAgfVxuICBdLFxuICBcIi9nb3Zlcm5hbmNlL1wiOiBbXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQ29zdCBHb3Zlcm5hbmNlIERlc2lnbiAoRy1HUC0wNilcIixcbiAgICAgIFwibGlua1wiOiBcIi9nb3Zlcm5hbmNlL0NPU1RfR09WRVJOQU5DRV9ERVNJR04ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiSElUTCAoSHVtYW4taW4tdGhlLUxvb3ApIERlc2lnbiAoRy1HUC0wNSlcIixcbiAgICAgIFwibGlua1wiOiBcIi9nb3Zlcm5hbmNlL0hJVExfREVTSUdOLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIk5lTW8gR3VhcmRyYWlscyBEZXNpZ24gKEctR1AtMDIpXCIsXG4gICAgICBcImxpbmtcIjogXCIvZ292ZXJuYW5jZS9ORU1PX0dVQVJEUkFJTFNfREVTSUdOLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIk9QQSBJbnRlZ3JhdGlvbiBEZXNpZ24gKEctR1AtMDEpXCIsXG4gICAgICBcImxpbmtcIjogXCIvZ292ZXJuYW5jZS9PUEFfSU5URUdSQVRJT05fREVTSUdOLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlJldGVudGlvbiBQb2xpY3kgRGVzaWduIChHLUdQLTA3KVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2dvdmVybmFuY2UvUkVURU5USU9OX1BPTElDWV9ERVNJR04ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiU2FuZGJveGluZyBEZXNpZ24gKEctR1AtMDgpXCIsXG4gICAgICBcImxpbmtcIjogXCIvZ292ZXJuYW5jZS9TQU5EQk9YSU5HX0RFU0lHTi5tZFwiXG4gICAgfVxuICBdLFxuICBcIi9taWdyYXRpb24vXCI6IFtcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJBZHZhbmNlZCBQZXJmb3JtYW5jZSBQYXR0ZXJucyAmIEJlc3QgUHJhY3RpY2VzXCIsXG4gICAgICBcImxpbmtcIjogXCIvbWlncmF0aW9uL0FEVkFOQ0VEX1BBVFRFUk5TLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkNvbXBsZXRlIFNvbHV0aW9uOiBQb2xpc2hlZCwgT3B0aW1pemVkLCBQcm9kdWN0aW9uLVJlYWR5XCIsXG4gICAgICBcImxpbmtcIjogXCIvbWlncmF0aW9uL0NPTVBMRVRFX1NPTFVUSU9OLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkNvbXByZWhlbnNpdmUgQmVuY2htYXJraW5nIFN0cmF0ZWd5XCIsXG4gICAgICBcImxpbmtcIjogXCIvbWlncmF0aW9uL0NPTVBSRUhFTlNJVkVfQkVOQ0hNQVJLSU5HLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkNvbXByZWhlbnNpdmUgUGVyZm9ybWFuY2UgQW5hbHlzaXMgJiBNaWdyYXRpb24gU3RyYXRlZ3lcIixcbiAgICAgIFwibGlua1wiOiBcIi9taWdyYXRpb24vQ09NUFJFSEVOU0lWRV9QRVJGT1JNQU5DRV9BTkFMWVNJUy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJEZXNpZ24gUHJpbmNpcGxlc1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL21pZ3JhdGlvbi9ERVNJR05fUFJJTkNJUExFUy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJVc2FnZSBFeGFtcGxlc1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL21pZ3JhdGlvbi9FWEFNUExFUy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJGb3JrIEZhaWx1cmUgKEVBR0FJTikgQW5hbHlzaXMgJiBTb2x1dGlvbnNcIixcbiAgICAgIFwibGlua1wiOiBcIi9taWdyYXRpb24vRk9SS19GQUlMVVJFX0FOQUxZU0lTLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkNvbXByZWhlbnNpdmUgSW1wbGVtZW50YXRpb24gUm9hZG1hcFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL21pZ3JhdGlvbi9JTVBMRU1FTlRBVElPTl9ST0FETUFQLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlByb2R1Y3Rpb24gUmVhZGluZXNzIENoZWNrbGlzdFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL21pZ3JhdGlvbi9QUk9EVUNUSU9OX1JFQURJTkVTUy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJRdWljayBTdGFydCBHdWlkZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL21pZ3JhdGlvbi9RVUlDS19TVEFSVC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJTaGVsbCB0byBSdXN0L0dvIE1pZ3JhdGlvbiBQbGFuXCIsXG4gICAgICBcImxpbmtcIjogXCIvbWlncmF0aW9uL1JVU1RfR09fTUlHUkFUSU9OX1BMQU4ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUGVyZm9ybWFuY2UgT3B0aW1pemF0aW9uIFN1bW1hcnlcIixcbiAgICAgIFwibGlua1wiOiBcIi9taWdyYXRpb24vU1VNTUFSWS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJUaGUgVWx0aW1hdGUgR3VpZGU6IENvbXByZWhlbnNpdmUgUGVyZm9ybWFuY2UgT3B0aW1pemF0aW9uICYgTWlncmF0aW9uXCIsXG4gICAgICBcImxpbmtcIjogXCIvbWlncmF0aW9uL1VMVElNQVRFX0dVSURFLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlVzZXIgR3VpZGU6IHRoZWdlbnQgUGVyZm9ybWFuY2UgT3B0aW1pemF0aW9uc1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL21pZ3JhdGlvbi9VU0VSX0dVSURFLm1kXCJcbiAgICB9XG4gIF0sXG4gIFwiL2RlbW9zL1wiOiBbXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiRGVtbyBTY3JpcHRzIGZvciBWaXRlUHJlc3MgRG9jdW1lbnRhdGlvblwiLFxuICAgICAgXCJsaW5rXCI6IFwiL2RlbW9zL1JFQURNRS5tZFwiXG4gICAgfVxuICBdLFxuICBcIi9yZWZlcmVuY2UvXCI6IFtcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJSb3V0aW5nIFN5c3RlbTogUHJvamVjdCBDb21wbGV0ZSBTdW1tYXJ5XCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlLzAwX1JPVVRJTkdfUFJPSkVDVF9DT01QTEVURS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJBZ2VudCBJZGVudGl0eSAmIFNvdmVyZWlnbnR5IERlcHRoIChXUC02MDA0KVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9BR0VOVF9JREVOVElUWV9TT1ZFUkVJR05UWV9ERVBUSC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJBZ2VudCBDb21tdW5pY2F0aW9uIExhbmd1YWdlIChKU09OLUFDTCkgJiBOZWdvdGlhdGlvbiAoV1AtMTAwNilcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvQUdFTlRfTkVHT1RJQVRJT05fQUNMX0RFUFRILm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkFnZW50IE9TIFByaW5jaXBhbHMgXHUyMDE0IERlcHRoIERvY3VtZW50XCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL0FHRU5UX09TX1BSSU5DSVBBTFNfREVQVEgubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQmVuY2htYXJrIENvbXBhcmlzb246IFNXRS1CZW5jaCB2cyBUZXJtaW5hbCBCZW5jaCAyLjBcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvQkVOQ0hNQVJLX0NPTVBBUklTT05fU1dFX0JFTkNIX1ZTX1RFUk1JTkFMX0JFTkNIXzJfMC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJHbG9iYWwgQ2xhdWRlIENvZGUgSW5zdHJ1Y3Rpb25zXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL0NMQVVERV9DT1JFX0dVSURFTElORVMubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQ0xBVURFIEFwcGVuZGl4OiB0aGVnZW50LXNwZWNpZmljIGFuZCBkb21haW4gd29ya2Zsb3cgcnVsZXNcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvQ0xBVURFX1RIRUdFTlRfUlVOVElNRV9BUFBFTkRJWC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJDb21wbGV0ZSBQcm92aWRlciBSb3V0aW5nIE1hcCAoQWxsIDEyKyBQcm92aWRlcnMpXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL0NPTVBMRVRFX1BST1ZJREVSX1JPVVRJTkdfTUFQLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkNvbnN0aXR1dGlvbmFsIEVuZm9yY2VtZW50ICYgUHJvb2Ygb2YgQWxpZ25tZW50IChXUC0zMDAxKVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9DT05TVElUVVRJT05BTF9FTkZPUkNFTUVOVF9ERVBUSC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJDb250ZXh0IE1hbmFnZW1lbnQgJiBTZW1hbnRpYyBDb21wcmVzc2lvbiBEZXB0aCAoV1AtNTAwMSlcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvQ09OVEVYVF9NQU5BR0VNRU5UX0RFUFRILm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkNvc3QgRW5mb3JjZW1lbnQgUG9saWN5OiAyeCBMaW1pdCAmIEVzY2FsYXRpb24gRnJhbWV3b3JrXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL0NPU1RfRU5GT1JDRU1FTlRfUE9MSUNZLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkNyb3NzLVBsYXRmb3JtIERlc2t0b3AgQXV0b21hdGlvbjogQVBJIFJlZmVyZW5jZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9DUk9TU19QTEFURk9STV9BUElfUkVGRVJFTkNFLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkNyb3NzLVBsYXRmb3JtIE11bHRpLVRlbmFudCBEZXNrdG9wIEF1dG9tYXRpb24gUXVpY2sgUmVmZXJlbmNlXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL0NST1NTX1BMQVRGT1JNX01VTFRJX1RFTkFOVF9RVUlDS19SRUZFUkVOQ0UubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiRG9taW5hbmNlIFByb29mIFJlZmVyZW5jZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9ET01JTkFOQ0VfUFJPT0ZfUkVGRVJFTkNFLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkVjb25vbWljIEdvdmVybmFuY2UgJiBUb2tlbiBST0kgTW9kZWxpbmcgKFdQLTUwMDMpXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL0VDT05PTUlDX0dPVkVSTkFOQ0VfREVQVEgubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiRnJvbnRtYXR0ZXIvQmFja21hdHRlciBJbnRlZ3JhdGlvbiBQb2ludHNcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvRlJPTlRNQVRURVJfQkFDS01BVFRFUl9JTlRFR1JBVElPTl9QT0lOVFMubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiRlIgVHJhY2tlcjogdGhlZ2VudFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9GUl9UUkFDS0VSLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkdhcmRlbmVyIEFyY2hpdGVjdHVyZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9HQVJERU5FUl9BUkNISVRFQ1RVUkUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiSHVtYW4tQWdlbnQgQ29sbGFib3JhdGlvbiAoSEFDKSAmIEhJVEwgUGF0dGVybnMgKFdQLTQwMDEuLjQwMDkpXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL0hBQ19BTkRfSElUTF9QQVRURVJOUy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJIb29rIE9wdGltaXphdGlvbiBTdHJhdGVneVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9IT09LX09QVElNSVpBVElPTl9TVFJBVEVHWS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJIeWJyaWQgTWFjL1dpbmRvd3MgRGV2ZWxvcG1lbnQgRW52aXJvbm1lbnQgLSBTdW1tYXJ5XCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL0hZQlJJRF9FTlZfU1VNTUFSWS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJJbmRleGluZyBhbmQgT3B0aW1pemF0aW9uIFN5c3RlbXMgXHUyMDE0IFJlZmVyZW5jZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9JTkRFWElOR19BTkRfT1BUSU1JWkFUSU9OX1NZU1RFTVMubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGFza1JvdXRlciArIFBhcmV0byBSb3V0aW5nIEludGVncmF0aW9uIEFyY2hpdGVjdHVyZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9JTlRFR1JBVElPTl9BUkNISVRFQ1RVUkUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGFza1JvdXRlciArIFBhcmV0byBSb3V0aW5nIEludGVncmF0aW9uIFx1MjAxNCBEb2N1bWVudCBJbmRleFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9JTlRFR1JBVElPTl9JTkRFWC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJUYXNrUm91dGVyIEludGVncmF0aW9uIFF1aWNrIFN0YXJ0XCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL0lOVEVHUkFUSU9OX1FVSUNLX1NUQVJULm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIk1BSUYgQXJ0aWZhY3QgU3BlY2lmaWNhdGlvbiAmIFByb3ZlbmFuY2UgRGVwdGggKFdQLTMwMDIpXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL01BSUZfQVJUSUZBQ1RfU1BFQ19ERVBUSC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJNQ1AgVG9vbCBSZXRyeSBQb2xpY3lcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvTUNQX1JFVFJZX1BPTElDWS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJDb3JyZWN0ZWQgTW9kZWwgUmFua2luZyBVc2luZyBQYXJldG8gRnJvbnRpZXJcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvTU9ERUxfUkFOS0lOR19DT1JSRUNURUQubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiTW9kZWwgUm91dGluZyBEZWNpc2lvbiBUcmVlXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL01PREVMX1JPVVRJTkdfREVDSVNJT05fVFJFRS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJNb2RlbCBSb3V0aW5nICYgQ29zdCBHb3Zlcm5hbmNlOiBDb21wbGV0ZSBJbmRleFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9NT0RFTF9ST1VUSU5HX0lOREVYLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIk1vZGVsIFJvdXRpbmcgJiBDb3N0IEdvdmVybmFuY2U6IFF1aWNrIFJlZmVyZW5jZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9NT0RFTF9ST1VUSU5HX1NVTU1BUlkubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiTW9kZWwgUm91dGluZzogVGVybWluYWwgQmVuY2ggMi4wIFF1aWNrIFJlZmVyZW5jZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9NT0RFTF9ST1VUSU5HX1RFUk1JTkFMX0JFTkNIXzJfMF9RVUlDS19SRUYubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiTW9kZWwgU2VsZWN0aW9uIERvY3VtZW50YXRpb24gSW5kZXhcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvTU9ERUxfU0VMRUNUSU9OX0lOREVYLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIk1vbml0b3JpbmcgQWxlcnQgUnVsZXNcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvTU9OSVRPUklOR19BTEVSVF9SVUxFUy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJNb25pdG9yaW5nIERhc2hib2FyZCBTcGVjaWZpY2F0aW9uc1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9NT05JVE9SSU5HX0RBU0hCT0FSRF9TUEVDLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIk1vbml0b3JpbmcgTWV0cmljcyBSZWZlcmVuY2VcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvTU9OSVRPUklOR19NRVRSSUNTX1JFRkVSRU5DRS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJNb25pdG9yaW5nIFN5c3RlbSBEb2N1bWVudGF0aW9uXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL01PTklUT1JJTkdfUkVBRE1FLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIk1vbml0b3JpbmcgU2V0dXAgR3VpZGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvTU9OSVRPUklOR19TRVRVUF9HVUlERS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJDaXZpbGl6YXRpb25hbCBNdWx0aS1Td2FybSBIaWVyYXJjaHkgKFdQLTEwMDYsIFdQLTUwMDQpXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL01VTFRJX1NXQVJNX0hJRVJBUkNIWV9ERVBUSC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJPcGVuVGVsZW1ldHJ5IEdlbkFJICYgT2JzZXJ2YWJpbGl0eSBEZXB0aCAoV1AtWTYpXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL09URUxfR0VOQUlfQU5EX0hZU1RFUkVTSVNfREVQVEgubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwib3hsaW50IFJ1bGUgTWFwcGluZyBSZWZlcmVuY2VcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvT1hMSU5UX1JVTEVfTUFQUElORy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJQYXJldG8gRnJvbnRpZXIgQWxnb3JpdGhtOiBQc2V1ZG9jb2RlICYgSW1wbGVtZW50YXRpb24gR3VpZGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvUEFSRVRPX0FMR09SSVRITV9QU0VVRE9DT0RFLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlBhcmV0byBGcm9udGllcjogRXhlY3V0aXZlIFN1bW1hcnlcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvUEFSRVRPX0VYRUNVVElWRV9TVU1NQVJZLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlBhcmV0byBGcm9udGllciBBbmFseXNpcyAmIE1vZGVsIFJhbmtpbmcgQWxnb3JpdGhtXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL1BBUkVUT19GUk9OVElFUl9BTkFMWVNJUy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJQYXJldG8gRnJvbnRpZXIgQW5hbHlzaXM6IENvbXBsZXRlIE1vZGVsIEV2YWx1YXRpb25cIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvUEFSRVRPX0ZST05USUVSX0NPTVBMRVRFX0FOQUxZU0lTLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlBhcmV0byBGcm9udGllciBNYXRyaXg6IE1vZGVsIFNlbGVjdGlvbiBHdWlkZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9QQVJFVE9fRlJPTlRJRVJfTUFUUklYLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlBhcmV0byBGcm9udGllciBRdWljayBSZWZlcmVuY2VcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvUEFSRVRPX0ZST05USUVSX1FVSUNLX1JFRkVSRU5DRS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJQYXJldG8gRnJvbnRpZXIgQW5hbHlzaXM6IENvbXBsZXRlIERhdGEgVGFibGVcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvUEFSRVRPX0ZST05USUVSX1RBQkxFLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlBhcmV0byBGcm9udGllciBBbmFseXNpczogVGVybWluYWwgQmVuY2ggMi4wIChDb3JyZWN0ZWQpXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL1BBUkVUT19GUk9OVElFUl9URVJNSU5BTF9CRU5DSF8yXzAubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUGFyZXRvIEZyb250aWVyIEFuYWx5c2lzOiBDb21wbGV0ZSBJbmRleFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9QQVJFVE9fSU5ERVgubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiTXVsdGktT2JqZWN0aXZlIFByb3ZpZGVyIFJvdXRpbmcgJiBQYXJldG8gRnJvbnRzIChXUC0xMDA0KVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9QQVJFVE9fUk9VVElOR19ERVNJR04ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUGFyZXRvIEZyb250aWVyIFZpc3VhbGl6YXRpb24gJiBEaWFncmFtc1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9QQVJFVE9fVklTVUFMSVpBVElPTi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJQaGFzZSAzLjUgUXVpY2sgUmVmZXJlbmNlXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL1BIQVNFXzNfNV9RVUlDS19SRUZFUkVOQ0UubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUGhhc2UgNCBVWDogT3BlcmF0b3IgQ29ja3BpdCAmIFJhdGlvbmFsZSBEZXB0aCAoV1AtNDAwMSlcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvUEhBU0VfNF9DT0NLUElUX1VYX0RFUFRILm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlBoYXNlIDUgU2NhbGU6IFJlZGlzICYgRGlzdHJpYnV0ZWQgUm9idXN0bmVzcyAoV1AtNTAwNClcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvUEhBU0VfNV9TQ0FMRV9ST0JVU1RORVNTX0RFUFRILm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlBPU0lYICsgcHdzaCBTaGVsbCBTdHJhdGVneVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9QT1NJWF9QV1NIX1NIRUxMX1NUUkFURUdZLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlByb3ZpZGVyIExpbWl0cyBhbmQgQXV0by1GYWxsYmFja1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9QUk9WSURFUl9MSU1JVFNfQU5EX0ZBTExCQUNLLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlByb3ZpZGVyIE1vZGVsIEJlaGF2aW9yIENvbnN0cmFpbnRzXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL1BST1ZJREVSX01PREVMX0JFSEFWSU9SLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlByb3ZpZGVyIE1vZGVsIFJlZmVyZW5jZVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9QUk9WSURFUl9NT0RFTF9SRUZFUkVOQ0UubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUm9idXN0bmVzcywgQnJlYWR0aCwgYW5kIERlcHRoIFx1MjAxNCBQaGFzZSBFdm9sdXRpb25cIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvUk9CVVNUTkVTU19BTkRfRlVUVVJFX0RFUFRILm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlJvdXRpbmcgRGVjaXNpb24gTWF0cml4OiBUYXNrIENhdGVnb3J5IExvZ2ljXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL1JPVVRJTkdfREVDSVNJT05fTUFUUklYLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkZpbmFsIFJvdXRpbmcgUmVjb21tZW5kYXRpb24gKFRlcm1pbmFsIEJlbmNoIDIuMClcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvUk9VVElOR19GSU5BTF9SRUNPTU1FTkRBVElPTi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJUYXNrIFJvdXRpbmcgSW1wbGVtZW50YXRpb24gQXJjaGl0ZWN0dXJlXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL1JPVVRJTkdfSU1QTEVNRU5UQVRJT05fQVJDSElURUNUVVJFLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIk1vZGVsIFJvdXRpbmcgUXVpY2sgQ2FyZCAoUG9ja2V0IFJlZmVyZW5jZSlcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvUk9VVElOR19RVUlDS19DQVJELm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlJvdXRpbmcgU3lzdGVtOiBNYXN0ZXIgU3VtbWFyeSAmIEltcGxlbWVudGF0aW9uIFJvYWRtYXBcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvUk9VVElOR19TWVNURU1fTUFTVEVSX1NVTU1BUlkubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUnVzdC1CYXNlZCBDTEkgVG9vbGluZ1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9SVVNUX1RPT0xJTkcubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiQWdlbnRpYyBDSS9DRCAmIFNlbGYtSGVhbGluZyBMb29wcyAoV1AtMjAwNClcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvU0VMRl9IRUFMSU5HX0FHRU5USUNfQ0lDRF9ERVBUSC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJQbGFubmluZyBTaW11bGF0aW9uICYgUmVwbGF5IFNhbmRib3ggRGVwdGggKFdQLTQwMDcsIFdQLTEyMDA0KVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9TSU1VTEFUSU9OX0FORF9TQU5EQk9YX0RFUFRILm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIk1DUCBUb29sIFNMTyBUYXJnZXRzIChHLU9QLTA4KVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9TTE9fVEFSR0VUUy5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJTcGVlZCAmIFF1YWxpdHkgSW5kZXggSW1wbGVtZW50YXRpb24gUGxhblwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9TUEVFRF9RVUFMSVRZX0lOREVYX0lNUExFTUVOVEFUSU9OX1BMQU4ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiU3RhcnNoaXAgUHJvbXB0IFx1MjAxNCBMb25nLVRlcm0gRml4IGZvciBTY2FuIFRpbWVvdXRcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvU1RBUlNISVBfU0VUVVAubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiU3dhcm0gTWVtb3J5ICYgTXVsdGktQWdlbnQgQ29vcmRpbmF0aW9uIChXUC0xMDA2KVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9TV0FSTV9NRU1PUllfQ09PUkRJTkFUSU9OX0RFUFRILm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlN3YXJtIFByb2Nlc3MgT3B0aW1pemF0aW9ucyAoTXVsdGktQWdlbnQgLyBNdWx0aS1UZW5hbnQgLyBNdWx0aS1Qcm9qZWN0KVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9TV0FSTV9QUk9DRVNTX09QVElNSVpBVElPTlMubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGFzayBDYXRlZ29yaXphdGlvbiAmIEFJIEFnZW50IERpc3BhdGNoIFJvdXRpbmcgRGVzaWduXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL1RBU0tfUk9VVElOR19ERVNJR04ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGVybWluYWwgQmVuY2ggMi4wOiBDb3JyZWN0ZWQgUGFyZXRvIEZyb250aWVyICYgUm91dGluZ1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9URVJNSU5BTF9CRU5DSF8yXzBfQ09SUkVDVEVEX0ZST05USUVSLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRvb2xpbmcgJiBHbG9iYWwgT3B0aW1pemF0aW9ucyBBdWRpdCAoSW4tRGVwdGgpXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL1RPT0xJTkdfQU5EX0dMT0JBTF9PUFRJTUlaQVRJT05TX0FVRElULm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlRvb2xpbmcgYW5kIEdsb2JhbCBPcHRpbWl6YXRpb25zIEF1ZGl0XCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL1RPT0xJTkdfQU5EX09QVElNSVpBVElPTl9BVURJVC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJUb3VjaHBvaW50IEludGVncmF0aW9uIFx1MjAxNCBEZWVwIERpdmVcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvVE9VQ0hQT0lOVF9JTlRFR1JBVElPTl9ERUVQX0RJVkUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVG91Y2hwb2ludCBJbnRlZ3JhdGlvbiBFdmFsdWF0aW9uXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL1RPVUNIUE9JTlRfSU5URUdSQVRJT05fRVZBTFVBVElPTi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJVbmlmaWVkIFdvcmsgU3RyZWFtIFx1MjAxNCBEZXNpZ25cIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvVU5JRklFRF9XT1JLX1NUUkVBTV9ERVNJR04ubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiV0JTIEFnZW50IFByb2dyZXNzIFx1MjAxNCBDbGFpbSAmIENvb3JkaW5hdGlvblwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlZmVyZW5jZS9XQlNfQUdFTlRfUFJPR1JFU1MubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVW5pZmllZCBXb3JrIFN0cmVhbSBcdTIwMTQgQ2Fub25pY2FsXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL1dPUktfU1RSRUFNLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlplbiAoT3BlbkNvZGUpIEludGVncmF0aW9uIEFuYWx5c2lzXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVmZXJlbmNlL1pFTl9JTlRFR1JBVElPTi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJSZWZlcmVuY2VcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZWZlcmVuY2UvaW5kZXgubWRcIlxuICAgIH1cbiAgXSxcbiAgXCIvcmVwb3J0cy9cIjogW1xuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkJLTSBQaGFzZSAxIENvbXBsZXRpb24gUmVwb3J0XCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVwb3J0cy9CS01fUEhBU0VfMV9DT01QTEVUSU9OX1JFUE9SVC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJDcml0aWNhbCBJc3N1ZSAjMjogR2l0IENhY2hlIEludmFsaWRhdGlvbiBGaXggLSBDb21wbGV0ZSBSZXBvcnRcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXBvcnRzL0NBQ0hFX0lOVkFMSURBVElPTl9GSVhfUkVQT1JULm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIkNyaXRpY2FsIElzc3VlcyBGaXhlcyAtIENvbXBsZXRpb24gUmVwb3J0XCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVwb3J0cy9DUklUSUNBTF9GSVhFU19DT01QTEVUSU9OX1JFUE9SVC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJDcml0aWNhbCBJc3N1ZSAjMjogVW5zYWZlIEdpdCBDYWNoZSBJbnZhbGlkYXRpb24gLSBFeGVjdXRpdmUgU3VtbWFyeVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlcG9ydHMvQ1JJVElDQUxfSVNTVUVfMl9TVU1NQVJZLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlBoYXNlIDEwLTEyIENsb3N1cmUgYW5kIEZpbmFsIEhhbmRvZmYgTm90ZSAoV1AtMTIwMTApXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVwb3J0cy9GSU5BTF9DTE9TVVJFX05PVEUubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiSG9saXN0aWMgKyBIYXJtb25pb3VzIERlc2lnbiAmIEludGVncmF0aW9uIFx1MjAxNCBJbXBsZW1lbnRhdGlvbiBDb21wbGV0ZSBcdTI3MDVcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXBvcnRzL0hPTElTVElDX0RFU0lHTl9JTVBMRU1FTlRBVElPTl9DT01QTEVURS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJIb2xpc3RpYyArIEhhcm1vbmlvdXMgRGVzaWduICYgSW50ZWdyYXRpb24gXHUyMDE0IEltcGxlbWVudGF0aW9uIFByb2dyZXNzXCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVwb3J0cy9IT0xJU1RJQ19ERVNJR05fSU1QTEVNRU5UQVRJT05fUFJPR1JFU1MubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBJbXBsZW1lbnRhdGlvbiBTdGF0dXMgUmVwb3J0XCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVwb3J0cy9JTVBMRU1FTlRBVElPTl9TVEFUVVMubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiVGhlZ2VudCBJbXBsZW1lbnRhdGlvbiBTdW1tYXJ5XCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVwb3J0cy9JTVBMRU1FTlRBVElPTl9TVU1NQVJZLm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlA3LjEgVmVyaWZpY2F0aW9uIFJlcG9ydDogUGVyLVByb2plY3QgUXVhbGl0eSBHYXRlIENoZWNrc1wiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlcG9ydHMvUDcuMV9WRVJJRklDQVRJT05fUkVQT1JULm1kXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwidGV4dFwiOiBcIlA3LjIgQ3Jvc3MtUHJvamVjdCBDb25zaXN0ZW5jeSBSZXBvcnRcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXBvcnRzL1A3LjJfQ1JPU1NfUFJPSkVDVF9DT05TSVNURU5DWS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJQaGFzZSAxMC0xMiBDbG9zdXJlIGFuZCBIYW5kb2ZmIE5vdGUgKFdQLTEyMDEwKVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlcG9ydHMvUEhBU0VfMTBfMTJfQ0xPU1VSRS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJQaGFzZSAxMzogUG9saWN5IEZlZGVyYXRpb24gUHJvZ3Jlc3MgUmVwb3J0XCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVwb3J0cy9QSEFTRV8xM19QUk9HUkVTU19SRVBPUlQubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUGhhc2UgMTQ6IEF1dG9ub21vdXMgTGVhcm5pbmcgYW5kIENvc3QgU2Vuc2luZyBQcm9ncmVzcyBSZXBvcnRcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXBvcnRzL1BIQVNFXzE0X1BST0dSRVNTX1JFUE9SVC5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJQaGFzZSAxNTogRW50ZXJwcmlzZSBMaWZlY3ljbGUgYW5kIENvbXBsaWFuY2UgUHJvZ3Jlc3MgUmVwb3J0XCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVwb3J0cy9QSEFTRV8xNV9QUk9HUkVTU19SRVBPUlQubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUGhhc2UgMy41IE9wdGltaXphdGlvbiBTdW1tYXJ5XCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVwb3J0cy9QSEFTRV8zXzVfU1VNTUFSWS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJQaGFzZSAzLjUgT3B0aW1pemF0aW9uIFZhbGlkYXRpb24gUmVwb3J0XCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVwb3J0cy9QSEFTRV8zXzVfVkFMSURBVElPTi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJQaGFzZSAzOiBKb2IgUG9vbCBJbXBsZW1lbnRhdGlvbiAtIENvbXBsZXRpb24gU3VtbWFyeVwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlcG9ydHMvUEhBU0VfM19DT01QTEVUSU9OX1NVTU1BUlkubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUGhhc2UgMyAtIEpvYiBQb29sIEltcGxlbWVudGF0aW9uIFJlcG9ydFwiLFxuICAgICAgXCJsaW5rXCI6IFwiL3JlcG9ydHMvUEhBU0VfM19KT0JfUE9PTF9JTVBMRU1FTlRBVElPTi5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJQaGFzZSA0OiBBZHZhbmNlZCBCYXNoIE9wdGltaXphdGlvbnMgUmVwb3J0XCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVwb3J0cy9QSEFTRV80X0FEVkFOQ0VEX09QVElNSVpBVElPTlMubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiUGhhc2UgNCBJbXBsZW1lbnRhdGlvbiBTdW1tYXJ5OiBFU0xpbnQgXHUyMTkyIG94bGludCBNaWdyYXRpb25cIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXBvcnRzL1BIQVNFXzRfSU1QTEVNRU5UQVRJT05fU1VNTUFSWS5tZFwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcInRleHRcIjogXCJQaGFzZSA0OiBBZHZhbmNlZCBCYXNoIE9wdGltaXphdGlvbnMgLSBJbXBsZW1lbnRhdGlvbiBTdW1tYXJ5XCIsXG4gICAgICBcImxpbmtcIjogXCIvcmVwb3J0cy9QSEFTRV80X1NVTU1BUlkubWRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0ZXh0XCI6IFwiXHVEODNDXHVERkMxIFByb2plY3QgQ29tcGxldGlvbiBSZXBvcnQ6IHRoZWdlbnRcIixcbiAgICAgIFwibGlua1wiOiBcIi9yZXBvcnRzL1BST0pFQ1RfQ09NUExFVElPTl9SRVBPUlQubWRcIlxuICAgIH1cbiAgXVxufVxuIl0sCiAgIm1hcHBpbmdzIjogIjtBQUE4VyxTQUFTLG9CQUFvQjtBQUMzWSxTQUFTLG1CQUFtQjtBQUM1QixTQUFTLG1CQUFtQjtBQUM1QixTQUFTLGtCQUFrQjs7O0FDQzNCLElBQU0sZ0JBQXdDO0FBQUEsRUFDNUMsV0FBVztBQUFBLEVBQ1gsYUFBYTtBQUFBLEVBQ2IsZ0JBQWdCO0FBQUEsRUFDaEIsU0FBUztBQUNYO0FBRU8sU0FBUyxrQkFBa0IsSUFBZ0I7QUFDaEQsUUFBTSxnQkFBNEIsR0FBRyxTQUFTLE1BQU0sYUFBYSxTQUFTLFFBQVEsS0FBSyxTQUFTLE1BQU0sTUFBTTtBQUMxRyxXQUFPLEtBQUssWUFBWSxRQUFRLEtBQUssT0FBTztBQUFBLEVBQzlDO0FBRUEsS0FBRyxTQUFTLE1BQU0sWUFBWSxTQUFTLFFBQVEsS0FBSyxTQUFTLEtBQUssTUFBTTtBQUN0RSxVQUFNLE9BQU8sT0FBTyxHQUFHLEVBQUUsUUFBUSxNQUFNO0FBR3ZDLFFBQUksUUFBUSxLQUFLLFdBQVcsR0FBRyxHQUFHO0FBQ2hDLFlBQU0sUUFBUSxLQUFLLE1BQU0saUJBQWlCO0FBQzFDLFVBQUksT0FBTztBQUNULGNBQU0sQ0FBQyxFQUFFLFNBQVMsSUFBSSxJQUFJO0FBQzFCLGNBQU0sV0FBVyxjQUFjLE9BQU87QUFFdEMsWUFBSSxVQUFVO0FBRVosZ0JBQU0sV0FBVyxLQUNkLFFBQVEsU0FBUyxPQUFPLEVBQ3hCLFFBQVEsUUFBUSxFQUFFO0FBRXJCLGlCQUFPLEdBQUcsRUFBRSxRQUFRLFFBQVEsVUFBVSxRQUFRLElBQUksUUFBUSxFQUFFO0FBQzVELGlCQUFPLEdBQUcsRUFBRSxRQUFRLFVBQVUsUUFBUTtBQUN0QyxpQkFBTyxHQUFHLEVBQUUsUUFBUSxTQUFTLG9CQUFvQjtBQUFBLFFBQ25EO0FBQUEsTUFDRjtBQUFBLElBQ0Y7QUFFQSxXQUFPLGNBQWMsUUFBUSxLQUFLLFNBQVMsS0FBSyxJQUFJO0FBQUEsRUFDdEQ7QUFDRjs7O0FDYkEsU0FBUyxvQkFDUCxJQUNBLFVBQ007QUFDTixRQUFNLGlCQUFpQixDQUFDLE9BQVksV0FBbUIsWUFBb0I7QUFDekUsVUFBTSxNQUFNLE1BQU0sT0FBTyxTQUFTLElBQUksTUFBTSxPQUFPLFNBQVM7QUFDNUQsVUFBTSxVQUFVLE1BQU0sT0FBTyxTQUFTO0FBR3RDLFFBQUksTUFBTSxJQUFJLFFBQVMsUUFBTztBQUM5QixRQUFJLE1BQU0sSUFBSSxNQUFNLEtBQUssTUFBTSxDQUFDLE1BQU0sTUFBTyxRQUFPO0FBRXBELFVBQU0sY0FBYztBQUNwQixVQUFNLFNBQVMsTUFBTSxJQUFJLE1BQU0sS0FBSyxNQUFNLFdBQVc7QUFDckQsVUFBTSxTQUFTLE1BQU0sSUFBSSxNQUFNLE1BQU0sYUFBYSxPQUFPLEVBQUUsS0FBSztBQUVoRSxRQUFJLENBQUMsT0FBTyxXQUFXLFFBQVEsRUFBRyxRQUFPO0FBRXpDLFVBQU0sV0FBVyxPQUFPLE1BQU0sQ0FBQyxFQUFFLEtBQUs7QUFDdEMsUUFBSSxDQUFDLFNBQVUsUUFBTztBQUV0QixRQUFJLFdBQVcsWUFBWTtBQUczQixXQUFPLFdBQVcsU0FBUztBQUN6QixVQUNFLE1BQU0sT0FBTyxRQUFRLElBQUksTUFBTSxPQUFPLFFBQVEsSUFBSSxLQUNsRCxNQUFNLE9BQU8sUUFBUSxHQUNyQjtBQUNBLGNBQU0sV0FDSixNQUFNLE9BQU8sUUFBUSxJQUFJLE1BQU0sT0FBTyxRQUFRO0FBQ2hELFlBQ0UsTUFBTSxJQUFJLE1BQU0sVUFBVSxXQUFXLENBQUMsTUFBTSxPQUM1QztBQUNBO0FBQUEsUUFDRjtBQUFBLE1BQ0Y7QUFDQTtBQUFBLElBQ0Y7QUFFQSxVQUFNLFlBQVksTUFBTTtBQUN4QixVQUFNLGFBQWE7QUFFbkIsVUFBTSxRQUFRLE1BQU0sS0FBSyxlQUFlLE9BQU8sQ0FBQztBQUNoRCxVQUFNLFNBQVM7QUFDZixVQUFNLE9BQU8sRUFBRSxLQUFLLFNBQVM7QUFDN0IsVUFBTSxNQUFNLENBQUMsV0FBVyxXQUFXLENBQUM7QUFFcEMsVUFBTSxhQUFhO0FBQ25CLFVBQU0sT0FBTyxXQUFXO0FBRXhCLFdBQU87QUFBQSxFQUNUO0FBRUEsS0FBRyxNQUFNLE1BQU07QUFBQSxJQUNiO0FBQUEsSUFDQTtBQUFBLElBQ0E7QUFBQSxFQUNGO0FBRUEsS0FBRyxTQUFTLE1BQU0sY0FBYyxDQUFDLFFBQVEsUUFBUTtBQUMvQyxVQUFNLFFBQVEsT0FBTyxHQUFHO0FBQ3hCLFVBQU0sTUFBTSxNQUFNLE1BQU0sT0FBTztBQUUvQixXQUFPO0FBQUEsaUJBQ00sR0FBRztBQUFBO0FBQUE7QUFBQTtBQUFBLEVBR2xCO0FBQ0Y7QUFNQSxTQUFTLHNCQUNQLElBQ0EsU0FDTTtBQUNOLFFBQU0sb0JBQW9CLEdBQUcsU0FBUyxNQUFNO0FBRTVDLEtBQUcsU0FBUyxNQUFNLFFBQVEsQ0FBQyxRQUFRLEtBQUssVUFBVSxLQUFLLGFBQWE7QUFDbEUsVUFBTSxRQUFRLE9BQU8sR0FBRztBQUN4QixVQUFNLE1BQU0sTUFBTSxRQUFRLEtBQUssS0FBSztBQUdwQyxRQUFJLElBQUksTUFBTSx3QkFBd0IsR0FBRztBQUN2QyxZQUFNLE1BQU0sTUFBTSxXQUFXO0FBQzdCLFlBQU0sUUFBUSxRQUFRLFNBQVM7QUFDL0IsWUFBTSxXQUFXLFFBQVEsYUFBYSxRQUFRLGFBQWE7QUFDM0QsWUFBTSxXQUFXLFFBQVEsV0FBVyxhQUFhO0FBQ2pELFlBQU0sT0FBTyxRQUFRLE9BQU8sU0FBUztBQUNyQyxZQUFNLFFBQVEsUUFBUSxRQUFRLFVBQVU7QUFFeEMsWUFBTSxNQUFNLElBQUksTUFBTSxHQUFHLEVBQUUsSUFBSSxHQUFHLFlBQVk7QUFDOUMsVUFBSSxPQUFPO0FBQ1gsVUFBSSxRQUFRLE1BQU8sUUFBTztBQUFBLGVBQ2pCLFFBQVEsTUFBTyxRQUFPO0FBQUEsZUFDdEIsUUFBUSxNQUFPLFFBQU87QUFFL0IsYUFBTyxpQkFBaUIsS0FBSyxLQUFLLFFBQVEsSUFBSSxRQUFRLElBQUksSUFBSSxJQUFJLEtBQUs7QUFBQSxpQkFDNUQsR0FBRyxXQUFXLElBQUk7QUFBQSxJQUMvQixHQUFHO0FBQUE7QUFBQSxJQUVIO0FBR0EsV0FBTyxvQkFBb0IsUUFBUSxLQUFLLFVBQVUsS0FBSyxRQUFRLEtBQUs7QUFBQSxFQUN0RTtBQUNGO0FBYU8sU0FBUyxpQkFDZCxJQUNBLFVBQXNDLENBQUMsR0FDakM7QUFDTixRQUFNLGlCQUFvQztBQUFBLElBQ3hDLE9BQU87QUFBQSxJQUNQLFFBQVE7QUFBQSxJQUNSLFVBQVU7QUFBQSxJQUNWLFVBQVU7QUFBQSxJQUNWLE1BQU07QUFBQSxJQUNOLE9BQU87QUFBQSxJQUNQLEdBQUc7QUFBQSxFQUNMO0FBRUEsc0JBQW9CLElBQUksY0FBYztBQUN0Qyx3QkFBc0IsSUFBSSxjQUFjO0FBQzFDOzs7QUN0S3VYLElBQU0sVUFBVTtBQUFBLEVBQ3JZLEtBQUs7QUFBQSxJQUNIO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixhQUFhO0FBQUEsTUFDYixTQUFTO0FBQUEsUUFDUDtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsTUFDRjtBQUFBLElBQ0Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixhQUFhO0FBQUEsTUFDYixTQUFTO0FBQUEsUUFDUDtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsYUFBYTtBQUFBLFVBQ2IsU0FBUztBQUFBLFlBQ1A7QUFBQSxjQUNFLFFBQVE7QUFBQSxjQUNSLFFBQVE7QUFBQSxZQUNWO0FBQUEsVUFDRjtBQUFBLFFBQ0Y7QUFBQSxNQUNGO0FBQUEsSUFDRjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLGFBQWE7QUFBQSxNQUNiLFNBQVM7QUFBQSxRQUNQO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLE1BQ0Y7QUFBQSxJQUNGO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsYUFBYTtBQUFBLE1BQ2IsU0FBUztBQUFBLFFBQ1A7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLE1BQ0Y7QUFBQSxJQUNGO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsYUFBYTtBQUFBLE1BQ2IsU0FBUztBQUFBLFFBQ1A7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsTUFDRjtBQUFBLElBQ0Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixhQUFhO0FBQUEsTUFDYixTQUFTO0FBQUEsUUFDUDtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxNQUNGO0FBQUEsSUFDRjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLGFBQWE7QUFBQSxNQUNiLFNBQVM7QUFBQSxRQUNQO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxNQUNGO0FBQUEsSUFDRjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLGFBQWE7QUFBQSxNQUNiLFNBQVM7QUFBQSxRQUNQO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxNQUNGO0FBQUEsSUFDRjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLGFBQWE7QUFBQSxNQUNiLFNBQVM7QUFBQSxRQUNQO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxNQUNGO0FBQUEsSUFDRjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLGFBQWE7QUFBQSxNQUNiLFNBQVM7QUFBQSxRQUNQO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxNQUNGO0FBQUEsSUFDRjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLGFBQWE7QUFBQSxNQUNiLFNBQVM7QUFBQSxRQUNQO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsTUFDRjtBQUFBLElBQ0Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixhQUFhO0FBQUEsTUFDYixTQUFTO0FBQUEsUUFDUDtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxNQUNGO0FBQUEsSUFDRjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLGFBQWE7QUFBQSxNQUNiLFNBQVM7QUFBQSxRQUNQO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxNQUNGO0FBQUEsSUFDRjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLGFBQWE7QUFBQSxNQUNiLFNBQVM7QUFBQSxRQUNQO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsTUFDRjtBQUFBLElBQ0Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixhQUFhO0FBQUEsTUFDYixTQUFTO0FBQUEsUUFDUDtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsYUFBYTtBQUFBLFVBQ2IsU0FBUztBQUFBLFlBQ1A7QUFBQSxjQUNFLFFBQVE7QUFBQSxjQUNSLFFBQVE7QUFBQSxZQUNWO0FBQUEsWUFDQTtBQUFBLGNBQ0UsUUFBUTtBQUFBLGNBQ1IsUUFBUTtBQUFBLFlBQ1Y7QUFBQSxZQUNBO0FBQUEsY0FDRSxRQUFRO0FBQUEsY0FDUixRQUFRO0FBQUEsWUFDVjtBQUFBLFlBQ0E7QUFBQSxjQUNFLFFBQVE7QUFBQSxjQUNSLFFBQVE7QUFBQSxZQUNWO0FBQUEsWUFDQTtBQUFBLGNBQ0UsUUFBUTtBQUFBLGNBQ1IsUUFBUTtBQUFBLFlBQ1Y7QUFBQSxVQUNGO0FBQUEsUUFDRjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLE1BQ0Y7QUFBQSxJQUNGO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsYUFBYTtBQUFBLE1BQ2IsU0FBUztBQUFBLFFBQ1A7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsTUFDRjtBQUFBLElBQ0Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxFQUNGO0FBQUEsRUFDQSxjQUFjO0FBQUEsSUFDWjtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsYUFBYTtBQUFBLE1BQ2IsU0FBUztBQUFBLFFBQ1A7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxRQUNBO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLFFBQ0E7QUFBQSxVQUNFLFFBQVE7QUFBQSxVQUNSLFFBQVE7QUFBQSxRQUNWO0FBQUEsUUFDQTtBQUFBLFVBQ0UsUUFBUTtBQUFBLFVBQ1IsUUFBUTtBQUFBLFFBQ1Y7QUFBQSxNQUNGO0FBQUEsSUFDRjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLEVBQ0Y7QUFBQSxFQUNBLGFBQWE7QUFBQSxJQUNYO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxFQUNGO0FBQUEsRUFDQSxZQUFZO0FBQUEsSUFDVjtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsRUFDRjtBQUFBLEVBQ0EsZ0JBQWdCO0FBQUEsSUFDZDtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsRUFDRjtBQUFBLEVBQ0EsV0FBVztBQUFBLElBQ1Q7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsRUFDRjtBQUFBLEVBQ0EsYUFBYTtBQUFBLElBQ1g7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLGFBQWE7QUFBQSxNQUNiLFNBQVM7QUFBQSxRQUNQO0FBQUEsVUFDRSxRQUFRO0FBQUEsVUFDUixRQUFRO0FBQUEsUUFDVjtBQUFBLE1BQ0Y7QUFBQSxJQUNGO0FBQUEsRUFDRjtBQUFBLEVBQ0EsZ0JBQWdCO0FBQUEsSUFDZDtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxFQUNGO0FBQUEsRUFDQSxlQUFlO0FBQUEsSUFDYjtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxFQUNGO0FBQUEsRUFDQSxnQkFBZ0I7QUFBQSxJQUNkO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLEVBQ0Y7QUFBQSxFQUNBLGtCQUFrQjtBQUFBLElBQ2hCO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxFQUNGO0FBQUEsRUFDQSxZQUFZO0FBQUEsSUFDVjtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsRUFDRjtBQUFBLEVBQ0EsZ0JBQWdCO0FBQUEsSUFDZDtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsRUFDRjtBQUFBLEVBQ0EsZUFBZTtBQUFBLElBQ2I7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxFQUNGO0FBQUEsRUFDQSxXQUFXO0FBQUEsSUFDVDtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxFQUNGO0FBQUEsRUFDQSxlQUFlO0FBQUEsSUFDYjtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsRUFDRjtBQUFBLEVBQ0EsYUFBYTtBQUFBLElBQ1g7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxRQUFRO0FBQUEsTUFDUixRQUFRO0FBQUEsSUFDVjtBQUFBLElBQ0E7QUFBQSxNQUNFLFFBQVE7QUFBQSxNQUNSLFFBQVE7QUFBQSxJQUNWO0FBQUEsSUFDQTtBQUFBLE1BQ0UsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLElBQ1Y7QUFBQSxFQUNGO0FBQ0Y7OztBSDMwSEEsU0FBUyxxQkFBcUI7QUFSeU0sSUFBTSwyQ0FBMkM7QUFVeFIsSUFBTUEsV0FBVSxjQUFjLHdDQUFlO0FBQzdDLElBQU0sa0JBQWtCQSxTQUFRLG1CQUFtQjtBQUNuRCxJQUFNLGtCQUFrQkEsU0FBUSxtQkFBbUIsRUFBRTtBQUVyRCxJQUFNLFNBQVMsYUFBYTtBQUFBLEVBQzFCLE9BQU87QUFBQSxFQUNQLGFBQWE7QUFBQSxFQUNiLFlBQVk7QUFBQSxFQUNaLGFBQWE7QUFBQTtBQUFBLEVBR2IsWUFBWTtBQUFBLElBQ1Y7QUFBQSxJQUNBO0FBQUEsSUFDQTtBQUFBLEVBQ0Y7QUFBQTtBQUFBLEVBR0EsaUJBQWlCO0FBQUEsRUFFakIsTUFBTTtBQUFBLElBQ0osU0FBUztBQUFBLE1BQ1AsWUFBWTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUEsTUFLWixDQUFDO0FBQUEsTUFDRCxXQUFXO0FBQUE7QUFBQTtBQUFBLFFBR1QsbUJBQW1CLENBQUMsUUFBUTtBQUMxQixjQUFJLElBQUksYUFBYSxJQUFJLFFBQVEsR0FBRztBQUNsQyxtQkFBTyxJQUFJLGdCQUFnQjtBQUFBLGNBQ3pCLFFBQVEsSUFBSSxhQUFhLElBQUksUUFBUSxLQUFLO0FBQUEsWUFDNUMsQ0FBQztBQUFBLFVBQ0g7QUFDQSxpQkFBTyxJQUFJLGdCQUFnQjtBQUFBLFFBQzdCO0FBQUEsTUFDRixDQUFDO0FBQUEsSUFDSDtBQUFBLElBQ0EsT0FBTztBQUFBLE1BQ0wsZUFBZTtBQUFBLFFBQ2IsUUFBUTtBQUFBLFVBQ04sY0FBYyxDQUFDLE9BQU87QUFFcEIsZ0JBQUksR0FBRyxTQUFTLGNBQWMsR0FBRztBQUUvQixrQkFBSSxHQUFHLFNBQVMsU0FBUyxHQUFHO0FBQzFCLHVCQUFPO0FBQUEsY0FDVDtBQUNBLGtCQUFJLEdBQUcsU0FBUyxLQUFLLEdBQUc7QUFDdEIsdUJBQU87QUFBQSxjQUNUO0FBQ0Esa0JBQUksR0FBRyxTQUFTLFFBQVEsR0FBRztBQUN6Qix1QkFBTztBQUFBLGNBQ1Q7QUFDQSxrQkFBSSxHQUFHLFNBQVMsYUFBYSxHQUFHO0FBQzlCLHVCQUFPO0FBQUEsY0FDVDtBQUNBLHFCQUFPO0FBQUEsWUFDVDtBQUFBLFVBQ0Y7QUFBQSxRQUNGO0FBQUEsTUFDRjtBQUFBLElBQ0Y7QUFBQSxFQUNGO0FBQUEsRUFFQSxVQUFVO0FBQUEsSUFDUixRQUFRLENBQUMsT0FBTztBQUNkLFNBQUcsSUFBSSxpQkFBaUI7QUFFeEIsU0FBRyxJQUFJLGtCQUFrQjtBQUFBLFFBQ3ZCLFVBQVU7QUFBQSxRQUNWLE9BQU87QUFBQSxNQUNULENBQUM7QUFHRCxTQUFHLElBQUksaUJBQWlCO0FBQUEsUUFDdEIsY0FBYztBQUFBLFFBQ2QsWUFBWTtBQUFBLE1BQ2QsQ0FBQztBQUdELFNBQUcsSUFBSSxpQkFBaUI7QUFBQSxRQUN0QixXQUFXLENBQUM7QUFBQSxRQUNaLE1BQU0sQ0FBQztBQUFBLE1BQ1QsQ0FBQztBQUFBLElBQ0g7QUFBQTtBQUFBLElBRUEsYUFBYTtBQUFBO0FBQUEsSUFFYixPQUFPO0FBQUEsTUFDTCxPQUFPO0FBQUEsTUFDUCxNQUFNO0FBQUEsSUFDUjtBQUFBLEVBQ0Y7QUFBQSxFQUVBLGFBQWE7QUFBQSxJQUNYLEtBQUs7QUFBQSxNQUNILEVBQUUsTUFBTSxRQUFRLE1BQU0sSUFBSTtBQUFBLE1BQzFCO0FBQUEsUUFDRSxNQUFNO0FBQUEsUUFDTixNQUFNO0FBQUEsUUFDTixhQUFhO0FBQUEsTUFDZjtBQUFBLE1BQ0E7QUFBQSxRQUNFLE1BQU07QUFBQSxRQUNOLE1BQU07QUFBQSxRQUNOLGFBQWE7QUFBQSxNQUNmO0FBQUEsTUFDQTtBQUFBLFFBQ0UsTUFBTTtBQUFBLFFBQ04sTUFBTTtBQUFBLFFBQ04sYUFBYTtBQUFBLE1BQ2Y7QUFBQSxJQUNGO0FBQUEsSUFFQTtBQUFBLElBRUEsYUFBYSxDQUFDO0FBQUEsSUFDZCxRQUFRO0FBQUEsTUFDTixVQUFVO0FBQUEsTUFDVixTQUFTO0FBQUE7QUFBQTtBQUFBO0FBQUEsTUFJVDtBQUFBLElBQ0Y7QUFBQSxJQUNBLFNBQVM7QUFBQSxJQUVULFVBQVU7QUFBQSxNQUNSLFNBQVM7QUFBQSxNQUNULE1BQU07QUFBQSxJQUNSO0FBQUEsRUFDRjtBQUFBLEVBRUEsT0FBTztBQUFBLElBQ0wsUUFBUTtBQUFBLElBQ1IsV0FBVztBQUFBLEVBQ2I7QUFBQTtBQUFBLEVBR0EsU0FBUztBQUFBLElBQ1AsT0FBTztBQUFBLElBQ1AsZ0JBQWdCO0FBQUEsTUFDZCxjQUFjO0FBQUEsTUFDZCxZQUFZO0FBQUEsTUFDWixrQkFBa0I7QUFBQSxNQUNsQixvQkFBb0I7QUFBQSxNQUNwQixXQUFXO0FBQUEsTUFDWCxnQkFBZ0I7QUFBQSxNQUNoQixlQUFlO0FBQUEsSUFDakI7QUFBQSxJQUNBLFdBQVc7QUFBQSxNQUNULGFBQWE7QUFBQSxNQUNiLFlBQVk7QUFBQSxJQUNkO0FBQUEsSUFDQSxVQUFVO0FBQUEsTUFDUixhQUFhO0FBQUEsSUFDZjtBQUFBLElBQ0EsT0FBTztBQUFBLE1BQ0wsYUFBYTtBQUFBLElBQ2Y7QUFBQSxFQUNGO0FBRUYsQ0FBQztBQUVELElBQU8saUJBQVEsWUFBWSxNQUFNOyIsCiAgIm5hbWVzIjogWyJyZXF1aXJlIl0KfQo=
