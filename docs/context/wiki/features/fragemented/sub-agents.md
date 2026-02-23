# Sub-Agents

**Navigation:** home > [Features](../features/)

##### Getting Started Overview
- Quickstart
- Eval & Benchmark
##### Concepts Core Concepts & Protocol
- Architecture
##### Agent Org Agent Organization (Experimental)
##### Offline Mode Offline Mode (Experimental)
##### Usage Interactive TUI
- Headless Mode
##### Extensibility Skills
- Sub-Agents
##### Configuration Model & Provider Catalog
- Preferences
- Adding a 3rd Party Provider
##### Memory Memory
##### Reference Tools
- Website
- Discord
- GitHub
- Log Out
Ante home page Search... ⌘K Ask AI Search... Navigation Extensibility Sub-Agents Ante Preview Ante Preview Extensibility # Sub-Agents Delegate complex tasks to specialized sub-agents
Sub-agents are specialized agents that the main agent can spawn to handle complex, multi-step tasks. Each sub-agent runs with its own prompt, tool set, and optional model override. ## ​ Built-in sub-agents Ante ships with two built-in sub-agents: ​ General A general-purpose agent for researching complex questions, searching for code, and executing multi-step tasks. The main agent delegates to this when it needs to perform a search it isn’t confident about completing in a few tries. ​ Explorer A fast agent specialized for codebase exploration. It can quickly find files by patterns, search code for keywords, and answer structural questions about the codebase. ​ Creating custom sub-agents Create a markdown file in ~/.ante/agents/
with YAML frontmatter: Copy Ask AI --- name : "security-reviewer" description : "Reviews code for security vulnerabilities and OWASP top 10 issues" color : "red" --- You are a security-focused code reviewer. Analyze the provided code for: - Injection vulnerabilities (SQL, command, XSS) - Authentication and authorization flaws - Sensitive data exposure - Security misconfiguration - Known vulnerable dependencies Provide findings with severity ratings and remediation steps. ### ​ Frontmatter fields Field Required Description name
Yes Unique identifier for the agent description Yes What this agent does (shown to the main agent for delegation decisions) model No Override the LLM model for this agent tools No Restrict which tools this agent can use color No Display color in the TUI ## ​ How sub-agents work When the main agent encounters a task that matches a sub-agent’s description, it uses the Task
tool to spawn the sub-agent: - The main agent evaluates available sub-agents and their descriptions
- It delegates the task via the Task
tool with a detailed prompt - The sub-agent runs independently with its own context
- The result is returned to the main agent, which incorporates it into the conversation
Copy Ask AI ┌────────────┐     Task      ┌──────────────┐ │ Main Agent │ ────────────▶ │  Sub-Agent   │ │            │ ◀──────────── │  (Explorer)  │ │            │    Result     └──────────────┘ │            │ │            │     Task      ┌──────────────┐ │            │ ────────────▶ │  Sub-Agent   │ │            │ ◀──────────── │  (General)   │ └────────────┘    Result     └──────────────┘ ## ​ Discovery Sub-agents are discovered from: Built-in agents (General, Explorer)
- ~/.ante/agents/
directory User-defined agents are loaded alongside the built-in ones. All available agents are registered at session initialization time. Previous Model & Provider Catalog Available models and providers supported by Ante Next On this page - Built-in sub-agents
- General
- Explorer
- Creating custom sub-agents
- Frontmatter fields
- How sub-agents work
- Discovery
Assistant Responses are generated using AI and may contain mistakes. Sub-Agents - Ante

---

## Related Documentation

- [Agent Organization](./agent-organization.md)
- [Core Concepts](../reference/core-concepts.md)
- [Architecture](../advanced/architecture.md)
