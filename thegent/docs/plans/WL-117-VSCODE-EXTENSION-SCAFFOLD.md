# WL-117 VS Code Extension Scaffold

**Status:** COMPLETED (extension built; see `extensions/vscode/`)
**Unblock condition:** WL-104 COMPLETED (2026-02-20)
**B90-W2-E5 Note:** WL-104 is confirmed COMPLETED as of 2026-02-20. WL-117 extension is also COMPLETED. This document records the scaffold specification for reference and any follow-on iteration.

## Extension Identity

- Name: `thegent-vscode`
- Display name: `thegent`
- Package directory: `extensions/vscode/`
- VS Code engine requirement: `^1.95.0`
- Node requirement: `>=18.0.0`

## Required Extension Capabilities

| Capability | Status | Implementation |
|-----------|--------|----------------|
| Language server (stdio JSON-RPC) | Done | `src/agentServerClient.ts` |
| Command palette commands | Done | `src/extension.ts` (6 commands) |
| Status bar (context budget) | Done | `src/contextBudgetStatusBar.ts` |
| Session tree view | Done | `src/sessionListProvider.ts` |
| Inline approval (diff + grant/reject) | Done | `src/approvalWebviewPanel.ts` |

## Dependencies

```json
{
  "engines": { "vscode": "^1.95.0", "node": ">=18.0.0" },
  "devDependencies": {
    "@types/vscode": "^1.95.0",
    "typescript": "^5.4.0"
  }
}
```

## Scaffold Steps (yo code Pattern)

These are the steps that would have been followed to scaffold from scratch using `yo code`:

```bash
# 1. Install VS Code extension generator
npm install -g yo generator-code

# 2. Scaffold extension skeleton
yo code
# Select: New Extension (TypeScript)
# Name: thegent-vscode
# Identifier: thegent-vscode
# Description: VS Code extension for thegent MCP client
# Initialize git repo: No (already in thegent repo)
# Bundle with webpack/esbuild: No (use tsc directly)
# Package manager: npm

# 3. Move scaffold output to extensions/vscode/
mv thegent-vscode extensions/vscode

# 4. Add vscode engine and types
cd extensions/vscode && npm install --save-dev @types/vscode
```

## Directory Structure

```
extensions/vscode/
  package.json             Extension manifest (commands, views, configuration)
  tsconfig.json            TypeScript config (strict mode)
  tsconfig.test.json       TypeScript config for tests
  .eslintrc.json           ESLint config
  src/
    extension.ts           Activation/deactivation + command registration
    agentServerClient.ts   stdio JSON-RPC 2.0 client over child_process
    sessionListProvider.ts TreeDataProvider for session list
    contextBudgetStatusBar.ts Status bar showing context budget
    approvalWebviewPanel.ts Webview: diff viewer + Approve/Reject buttons
    types.ts               Strict wire-format TypeScript types
    __tests__/
      agentServerClient.test.ts   (16 tests)
      sessionListProvider.test.ts (8 tests)
      contextBudgetStatusBar.test.ts (6 tests)
      run-tests.js
  test/
    protocolClient.test.js  Protocol contract test (1 test)
  docs/
    protocol-contract.md   Wire format specification
  out/                     Compiled JavaScript output
```

## Wire Protocol (WL-104 Dependency)

The extension connects to `thegent agent-server` over stdio using Codex App Server v2 compatible wire format:

**Methods:**
- `session/start`, `session/resume`, `session/list`, `session/read`
- `turn/submit`, `turn/cancel`
- `config/read`

**Notifications:**
- `turn/started`, `turn/completed`
- `item/agentMessage/delta`, `item/toolCall/started`, `item/toolCall/completed`
- `approval/requested`

## Validation Commands

```bash
# Compile TypeScript
cd extensions/vscode && npm run compile

# Type check (zero errors)
cd extensions/vscode && npm run typecheck

# Run tests (31 tests)
cd extensions/vscode && npm test

# Lint
cd extensions/vscode && npm run lint

# Package as .vsix (requires vsce)
npm install -g @vscode/vsce
cd extensions/vscode && vsce package
```

## Follow-on Work (Post-Scaffold)

- [ ] Add skill tree view using skill list API
- [ ] Package as `.vsix` and add to CI artifact upload
- [ ] Add integration tests against live `thegent agent-server` process
- [ ] Add `thegent.cancelTurn` command with streaming cancellation
- [ ] Publish to VS Code Marketplace (WL-117 acceptance target)

_Scaffold plan — WL-117 B90-W2-E5_
