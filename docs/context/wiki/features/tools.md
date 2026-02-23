# Tools

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
Ante home page Search... ⌘K Ask AI Search... Navigation Reference Tools Ante Preview Ante Preview Reference # Tools Reference for all built-in tools available to the agent
Tools are the capabilities available to the agent during a session. Each tool has a name, description, input schema, and an approval requirement. ## ​ File I/O ​ Read Read file contents. Supports text files, images (PNG, JPG), PDFs, and Jupyter notebooks. Approval required
: No - Key inputs
: file_path (absolute path), optional offset and limit for large files ### ​ Write Create or overwrite a file. Approval required
: Yes - Key inputs
: file_path , content ### ​ Edit Perform exact string replacements in files. Finds old_string
and replaces it with new_string . - Approval required
: Yes - Key inputs
: file_path , old_string , new_string , optional replace_all ### ​ Glob Find files matching a glob pattern (e.g., **/*.rs
, src/**/*.ts ). - Approval required
: No - Key inputs
: pattern , optional path (search directory) ### ​ Grep Search file contents with regex patterns. Built on ripgrep. Approval required
: No - Key inputs
: pattern (regex), optional path , glob filter, type filter, output_mode ## ​ Shell ​ Bash Execute shell commands with optional timeout (default 2 minutes, max 10 minutes). Approval required
: Yes - Key inputs
: command , optional description , timeout ### ​ BashOutput Read output from a running or completed background shell. Approval required
: No - Key inputs
: id (shell identifier) ### ​ KillShell Terminate a background shell process. Approval required
: No - Key inputs
: id (shell identifier) ## ​ Builtin ​ Task Spawn a sub-agent to handle complex, multi-step tasks autonomously. Approval required
: No - Key inputs
: prompt , subagent_type ### ​ TodoWrite Manage a task list for tracking progress on multi-step work. Approval required
: No - Key inputs
: todos (list of items with id, content, status) ### ​ WebFetch Fetch content from a URL and process it. Approval required
: No - Key inputs
: url , prompt (what to extract) ### ​ WebSearch Search the web and return results. Approval required
: No - Key inputs
: query ## ​ Tool filtering Control which tools are available in a session: Copy Ask AI # Only allow these tools ante --allowed-tools Read Glob Grep "analyze the code" # Remove these tools ante --disallowed-tools Bash Write "read-only analysis"
Supports ToolMatcher syntax for fine-grained control: Copy Ask AI # Allow Bash but only for specific patterns ante --allowed-tools "Read" "Bash(cargo test)" "Bash(cargo clippy)" Previous Memory Persistent auto-memory that carries context across conversations On this page - File I/O
- Read
- Write
- Edit
- Glob
- Grep
- Shell
- Bash
- BashOutput
- KillShell
- Builtin
- Task
- TodoWrite
- WebFetch
- WebSearch
- Tool filtering
Assistant Responses are generated using AI and may contain mistakes. Tools - Ante

---

## Related Documentation

- [Skills](./skills.md)
- [Architecture](../advanced/architecture.md)
