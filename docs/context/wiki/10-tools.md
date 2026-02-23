# Tools

> Generated from Ante documentation webarchive

Skip to main content

[Ante home page![light logo](https://mintcdn.com/antigmalabs/cvR1z2_cg6Q1RLzi/assets/ante.png?fit=max&auto=format&n=cvR1z2_cg6Q1RLzi&q=85&s=827303a37dd6c12ec797767e55c94972)![dark logo](https://mintcdn.com/antigmalabs/cvR1z2_cg6Q1RLzi/assets/ante.png?fit=max&auto=format&n=cvR1z2_cg6Q1RLzi&q=85&s=827303a37dd6c12ec797767e55c94972)](/)

Search...

⌘K

##### Getting Started

  * [Overview](/start/overview)
  * [Quickstart](/start/quickstart)
  * [Eval & Benchmark](/start/eval)

##### Concepts

  * [Core Concepts & Protocol](/concepts/core-concepts)
  * [Architecture](/concepts/architecture)

##### Agent Org

  * [Agent Organization (Experimental)](/agent-org)

##### Offline Mode

  * [Offline Mode (Experimental)](/offline)

##### Usage

  * [Interactive TUI](/usage/tui)
  * [Headless Mode](/usage/headless)

##### Extensibility

  * [Skills](/extend/skills)
  * [Sub-Agents](/extend/subagents)

##### Configuration

  * [Model & Provider Catalog](/configuration/catalog)
  * [Preferences](/configuration/preference)
  * [Adding a 3rd Party Provider](/configuration/third-party-provider)

##### Memory

  * [Memory](/memory)

##### Reference

  * [Tools](/tools)

  * [Website](https://antigma.ai)
  * [Discord](https://discord.gg/pqhj3DNGz2)
  * [GitHub](https://github.com/AntigmaLabs/ante-preview)
  *   * Log Out
  * 

[Ante home page![light logo](https://mintcdn.com/antigmalabs/cvR1z2_cg6Q1RLzi/assets/ante.png?fit=max&auto=format&n=cvR1z2_cg6Q1RLzi&q=85&s=827303a37dd6c12ec797767e55c94972)![dark logo](https://mintcdn.com/antigmalabs/cvR1z2_cg6Q1RLzi/assets/ante.png?fit=max&auto=format&n=cvR1z2_cg6Q1RLzi&q=85&s=827303a37dd6c12ec797767e55c94972)](/)

Search...

⌘KAsk AI

  * [Website](https://antigma.ai)
  * [Discord](https://discord.gg/pqhj3DNGz2)
  * [GitHub](https://github.com/AntigmaLabs/ante-preview)
  * Log Out

Search...

Navigation

Reference

Tools

[Ante Preview](/start/overview)

[Ante Preview](/start/overview)

Reference

# Tools

Reference for all built-in tools available to the agent

Tools are the capabilities available to the agent during a session. Each tool has a name, description, input schema, and an approval requirement.

## 

​

File I/O

### 

​

Read

Read file contents. Supports text files, images (PNG, JPG), PDFs, and Jupyter notebooks.

  * **Approval required** : No
  * **Key inputs** : `file_path` (absolute path), optional `offset` and `limit` for large files

### 

​

Write

Create or overwrite a file.

  * **Approval required** : Yes
  * **Key inputs** : `file_path`, `content`

### 

​

Edit

Perform exact string replacements in files. Finds `old_string` and replaces it with `new_string`.

  * **Approval required** : Yes
  * **Key inputs** : `file_path`, `old_string`, `new_string`, optional `replace_all`

### 

​

Glob

Find files matching a glob pattern (e.g., `**/*.rs`, `src/**/*.ts`).

  * **Approval required** : No
  * **Key inputs** : `pattern`, optional `path` (search directory)

### 

​

Grep

Search file contents with regex patterns. Built on ripgrep.

  * **Approval required** : No
  * **Key inputs** : `pattern` (regex), optional `path`, `glob` filter, `type` filter, `output_mode`

## 

​

Shell

### 

​

Bash

Execute shell commands with optional timeout (default 2 minutes, max 10 minutes).

  * **Approval required** : Yes
  * **Key inputs** : `command`, optional `description`, `timeout`

### 

​

BashOutput

Read output from a running or completed background shell.

  * **Approval required** : No
  * **Key inputs** : `id` (shell identifier)

### 

​

KillShell

Terminate a background shell process.

  * **Approval required** : No
  * **Key inputs** : `id` (shell identifier)

## 

​

Builtin

### 

​

Task

Spawn a sub-agent to handle complex, multi-step tasks autonomously.

  * **Approval required** : No
  * **Key inputs** : `prompt`, `subagent_type`

### 

​

TodoWrite

Manage a task list for tracking progress on multi-step work.

  * **Approval required** : No
  * **Key inputs** : `todos` (list of items with id, content, status)

### 

​

WebFetch

Fetch content from a URL and process it.

  * **Approval required** : No
  * **Key inputs** : `url`, `prompt` (what to extract)

### 

​

WebSearch

Search the web and return results.

  * **Approval required** : No
  * **Key inputs** : `query`

## 

​

Tool filtering

Control which tools are available in a session:

Copy

Ask AI
    
    
    # Only allow these tools
    ante --allowed-tools Read Glob Grep "analyze the code"
    
    # Remove these tools
    ante --disallowed-tools Bash Write "read-only analysis"
    

Supports ToolMatcher syntax for fine-grained control:

Copy

Ask AI
    
    
    # Allow Bash but only for specific patterns
    ante --allowed-tools "Read" "Bash(cargo test)" "Bash(cargo clippy)"
    

[PreviousMemoryPersistent auto-memory that carries context across conversations](/memory)

[Powered by](https://www.mintlify.com?utm_campaign=poweredBy&utm_medium=referral&utm_source=antigmalabs)

On this page

  * File I/O
  * Read
  * Write
  * Edit
  * Glob
  * Grep
  * Shell
  * Bash
  * BashOutput
  * KillShell
  * Builtin
  * Task
  * TodoWrite
  * WebFetch
  * WebSearch
  * Tool filtering

Assistant

Responses are generated using AI and may contain mistakes.

Tools - Ante

