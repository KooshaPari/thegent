// Canonical sidebar - aligned with FastMCP/uv/Svelte patterns
// Based on research: Get Started → Tutorials → How-to → Reference → Explanation → Operations → Governance

export const sidebar = {
  '/': [
    {
      text: 'Getting Started',
      collapsed: false,
      items: [
        { text: 'Home', link: '/' },
        { text: 'Start Here', link: '/start-here.md' },
      ]
    },
    {
      text: 'Tutorials',
      collapsed: false,
      items: [
        { text: 'Tutorials Overview', link: '/tutorials/' },
        { text: 'Quick Start', link: '/tutorials/01-quick-start.md' },
        { text: 'Configuration', link: '/tutorials/02-configuration.md' },
      ]
    },
    {
      text: 'How-to Guides',
      collapsed: false,
      items: [
        { text: 'How-to Overview', link: '/how-to/' },
        { text: 'Installation', link: '/guides/INSTALLATION.md' },
        { text: 'Provider Setup', link: '/guides/PROVIDER_SETUP_GUIDE.md' },
        { text: 'Testing', link: '/guides/TESTING.md' },
        { text: 'Troubleshooting', link: '/guides/TROUBLESHOOTING.md' },
      ]
    },
    {
      text: 'Reference',
      collapsed: false,
      items: [
        { text: 'Reference Index', link: '/reference/' },
        { text: 'Configuration', link: '/reference/configuration.md' },
        { text: 'Routing', link: '/reference/routing.md' },
        { text: 'CLAUDE Core Guidelines', link: '/reference/CLAUDE_CORE_GUIDELINES.md' },
        { text: 'MCP Retry Policy', link: '/reference/MCP_RETRY_POLICY.md' },
      ]
    },
    {
      text: 'Explanation',
      collapsed: false,
      items: [
        { text: 'Explanation Overview', link: '/explanation/' },
        { text: 'Agent Sandboxing', link: '/architecture/AGENT_SANDBOXING_ARCHITECTURE.md' },
        { text: 'Cost Governance', link: '/governance/COST_GOVERNANCE_DESIGN.md' },
        { text: 'OPA Integration', link: '/governance/OPA_INTEGRATION_DESIGN.md' },
      ]
    },
    {
      text: 'Operations',
      collapsed: false,
      items: [
        { text: 'Operations Overview', link: '/operations/' },
        { text: 'Runbooks', link: '/operations/runbooks.md' },
        { text: 'Troubleshooting', link: '/operations/troubleshooting.md' },
      ]
    },
    {
      text: 'Governance',
      collapsed: false,
      items: [
        { text: 'Governance Overview', link: '/governance/' },
        { text: 'TDD/BDD/SDD', link: '/governance/TDD_BDD_SDD_GOVERNANCE.md' },
        { text: 'Test Strategy', link: '/governance/AGENT_ONLY_TEST_STRATEGY.md' },
        { text: 'Terminology', link: '/governance/TERMINOLOGY_LAYERS.md' },
        { text: 'Context Docs', link: '/governance/CONTEXT_DOCS_PROCESS.md' },
      ]
    },
    {
      text: 'Guides',
      collapsed: true,
      items: [
        { text: 'Guides Index', link: '/guides/' },
        { text: 'Docs Governance', link: '/guides/VITEPRESS_DOCS_GOVERNANCE.md' },
        { text: 'VitePress Setup', link: '/guides/VITEPPRESS_SETUP.md' },
        { text: 'VitePress Usage', link: '/guides/VITEPRESS_USAGE_GUIDE.md' },
        { text: 'Quick Reference', link: '/guides/QUICK_REFERENCE.md' },
        { text: 'Shell Environment', link: '/guides/SHELL_ENVIRONMENT_COMPLETE.md' },
        { text: 'Cross-Platform', link: '/guides/CROSS_PLATFORM_COMPLETE.md' },
      ]
    },
    {
      text: 'API',
      collapsed: false,
      items: [
        { text: 'API Overview', link: '/api/' },
        { text: 'API README', link: '/api/README.md' },
      ]
    },
    {
      text: 'Architecture',
      collapsed: true,
      items: [
        { text: 'Module Dependencies', link: '/architecture/diagrams/module-dependencies.md' },
        { text: 'Package Structure', link: '/architecture/diagrams/package-structure.md' },
      ]
    },
    {
      text: 'Contracts',
      collapsed: true,
      items: [
        { text: 'Contract Authority', link: '/contracts/CONTRACT_AUTHORITY.md' },
        { text: 'Fallback Policy', link: '/contracts/FALLBACK_POLICY.md' },
        { text: 'Provider Adapter Contracts', link: '/contracts/PROVIDER_ADAPTER_CONTRACTS.md' },
      ]
    },
    {
      text: 'Enterprise',
      collapsed: true,
      items: [
        { text: 'Operating Model', link: '/enterprise/OPERATING_MODEL.md' },
        { text: 'Security Compliance', link: '/enterprise/SECURITY_COMPLIANCE_SIGNOFF.md' },
        { text: 'Decommissioning Plan', link: '/enterprise/DECOMMISSIONING_PLAN.md' },
      ]
    },
    {
      text: 'Examples',
      collapsed: true,
      items: [
        { text: 'Examples Overview', link: '/examples/README.md' },
        { text: 'Code Playground', link: '/examples/code-playground-example.md' },
        { text: 'Mermaid Diagrams', link: '/examples/mermaid-example.md' },
        { text: 'Tooltips', link: '/examples/tooltip-example.md' },
      ]
    },
  ]
}
