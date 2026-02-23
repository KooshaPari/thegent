# ANTE: Quick Reference and Architecture Diagrams

## 1. QUICK START REFERENCE

### 1.1 Installation and Setup

```bash
# Install from Cargo
cargo install ante

# Verify installation
ante --version

# Get help
ante --help

# Set up credentials (for model providers)
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
# etc.

# Initialize project
ante init [project-name]
```

### 1.2 Common Commands

```bash
# Run a simple task
ante run "Analyze this codebase and suggest improvements"

# Run with specific model
ante run --model claude-4-sonnet "Fix the bug in main.rs"

# Enable streaming
ante run --stream "Implement dark mode feature"

# Set timeout
ante run --timeout 600000 "Build and test the project"  # 10 minutes

# Check agent memory
ante memory ls
ante memory show [topic]
ante memory edit [topic]

# View logs
ante logs [--tail 100]

# Debug mode
ante run --debug "Complex task requiring visibility"
```

### 1.3 Configuration File

```toml
# ante.toml (project configuration)
[agent]
name = "Ante"
model = "claude-4-sonnet"
temperature = 0.7
max_tokens = 4096

[performance]
timeout_ms = 120000        # 2 minutes default
timeout_intensive = 600000 # 10 minutes for builds
parallel_tools = 20        # Max parallel tool calls
context_budget = 200000    # Total tokens

[memory]
enable = true
path = ".ante/memory"
auto_summarize = true
summarize_at_tokens = 150000

[tools]
bash_timeout = 120000
file_read_limit = 2000     # lines
file_edit_safe = true      # require read before edit

[models]
primary = "claude-4-sonnet"
fallback = ["claude-3-5-sonnet", "gpt-4"]
auto_select = true
```

---

## 2. CORE ARCHITECTURE DIAGRAMS

### 2.1 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE LAYER                        │
│                                                                 │
│  CLI Input      │  File System  │  IDE Integration │  API       │
└────────┬────────┴───────┬───────┴────────┬────────┴──────┬──────┘
         │                │                │               │
         └────────────────┼────────────────┼───────────────┘
                          │
         ┌────────────────▼───────────────────────┐
         │   ANTE ORCHESTRATION ENGINE            │
         │                                        │
         │  ┌──────────────────────────────────┐ │
         │  │ Task Parser & Classifier         │ │
         │  │ - Analyze input                  │ │
         │  │ - Determine subagent types       │ │
         │  │ - Estimate resources needed      │ │
         │  └──────────────────────────────────┘ │
         │              │                        │
         │  ┌───────────▼──────────────────────┐ │
         │  │ Subagent Orchestrator            │ │
         │  │ - Spawn subagents                │ │
         │  │ - Manage lifecycle               │ │
         │  │ - Share context                  │ │
         │  │ - Aggregate results              │ │
         │  └──────────────────────────────────┘ │
         │              │                        │
         │  ┌───────────▼──────────────────────┐ │
         │  │ Context Manager                  │ │
         │  │ - Token budgeting                │ │
         │  │ - Memory persistence             │ │
         │  │ - State synchronization          │ │
         │  └──────────────────────────────────┘ │
         │              │                        │
         │  ┌───────────▼──────────────────────┐ │
         │  │ Tool Dispatcher                  │ │
         │  │ - Route to appropriate tool      │ │
         │  │ - Parallel execution             │ │
         │  │ - Error handling & recovery      │ │
         │  └──────────────────────────────────┘ │
         │              │                        │
         └──────────────┼────────────────────────┘
                        │
         ┌──────────────▼──────────────────────────┐
         │   TOOL LAYER                           │
         │                                        │
         │  [File Ops] [Bash] [Git] [Search]    │
         │  [Web] [Tasks] [MCP Servers]         │
         │                                        │
         └──────────────┼──────────────────────────┘
                        │
         ┌──────────────▼──────────────────────────┐
         │   SYSTEM/RESOURCE LAYER                │
         │                                        │
         │  Files  │  Shell  │  Network │ Memory  │
         │                                        │
         └────────────────────────────────────────┘
```

### 2.2 Subagent Orchestration Flow

```
        User Request
             │
             ▼
    ┌─────────────────┐
    │ Parse & Classify│
    │  (Task Type)    │
    └────────┬────────┘
             │
      ┌──────┴──────┬──────────┐
      │             │          │
      ▼             ▼          ▼
   Explore      Analyze     Execute
   Subagent     Subagent    Subagent
      │             │          │
      │ ┌───────────┼──────────┤ Parallel
      │ │           │          │ Execution
      ├─┤           ├─────────┤ (if possible)
      │ │           │          │
      │ ├───────────┤──────────┤
      │ │           │          │
      └─┴───────────┴──────────┘
             │
             ▼
    ┌─────────────────────┐
    │ Aggregate Results   │
    │ Merge Context       │
    │ Synthesize Response │
    └────────┬────────────┘
             │
             ▼
        User Response
```

### 2.3 Context Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│ Total Token Budget: 200,000 tokens                      │
│                                                         │
│ ┌──────────────────────────────────────────────────┐  │
│ │ System Context (10,000 tokens)                   │  │
│ │ - Environment variables, paths                   │  │
│ │ - Tool capabilities and constraints              │  │
│ │ - Session state and history                      │  │
│ └──────────────────────────────────────────────────┘  │
│                                                         │
│ ┌──────────────────────────────────────────────────┐  │
│ │ Project Context (20,000 tokens)                  │  │
│ │ - Repository structure                           │  │
│ │ - Architecture and design patterns               │  │
│ │ - Recent changes and dependencies                │  │
│ └──────────────────────────────────────────────────┘  │
│                                                         │
│ ┌──────────────────────────────────────────────────┐  │
│ │ Active Work Context (50,000 tokens)              │  │
│ │ - Current task details                           │  │
│ │ - Related files and code snippets                │  │
│ │ - Intermediate results                           │  │
│ └──────────────────────────────────────────────────┘  │
│                                                         │
│ ┌──────────────────────────────────────────────────┐  │
│ │ Subagent Context 1 (30,000 tokens)               │  │
│ │ - Task-specific filtered context                 │  │
│ │ - Tool access restrictions                       │  │
│ └──────────────────────────────────────────────────┘  │
│                                                         │
│ ┌──────────────────────────────────────────────────┐  │
│ │ Subagent Context 2 (30,000 tokens)               │  │
│ │ - Different task scope                           │  │
│ │ - Specialized instructions                       │  │
│ └──────────────────────────────────────────────────┘  │
│                                                         │
│ ┌──────────────────────────────────────────────────┐  │
│ │ Reserved (30,000 tokens)                         │  │
│ │ - Final response buffer                          │  │
│ │ - Contingency/overflow                           │  │
│ └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 2.4 Tool Routing Decision Tree

```
                Tool Request
                     │
                     ▼
            ┌────────────────────┐
            │ What operation?    │
            └────┬───┬───┬───┬───┘
                 │   │   │   │
         ┌───────┘   │   │   └────┬─────────┐
         │           │   │        │         │
         ▼           ▼   ▼        ▼         ▼
      [Read]    [Search] [Exec] [Git]    [Web]
         │           │      │      │       │
         ▼           ▼      ▼      ▼       ▼
      ┌───┐  ┌─────┴────┐  │  ┌────────┐  │
      │   │  │          │  │  │        │  │
      ▼   ▼  ▼          ▼  │  ▼        ▼  ▼
    [Read] [Glob] [Grep] │ │ [Bash] [Git] [WebFetch]
           │       │      │ │              │
           │       │      │ └──────┬───────┘
           │       │      │        │
           └───┬───┘      │    Parallel Exec?
               │          │        │
               ▼          ▼        ▼
         ┌──────────┐  [Bash]  [Yes/No]
         │ Parallel?│  [Background]
         └──┬───┬───┘
            │   └──────────┐
         [Yes] [No]        │
            │       │      │
            ▼       ▼      ▼
        [Parallel] [Serial] [BashOutput Polling]
         Execution   Chain
```

### 2.5 Error Recovery Flow

```
┌──────────────────────┐
│ Operation Executed   │
└──────────┬───────────┘
           │
           ▼
    ┌──────────────┐
    │ Check Result │
    └──┬───────┬──┘
       │       │
    [OK]     [ERROR]
       │       │
       ▼       ▼
    [Success] Classify Error
              │
        ┌─────┼─────┬─────┬─────┐
        │     │     │     │     │
        ▼     ▼     ▼     ▼     ▼
      [T1]  [T2]  [T3]  [T4]  [T5]
      Timeout Context Tool Resource Unknown
               Exhaust Fail Content
               │     │     │     │
               ▼     ▼     ▼     ▼
    ┌─────────────────────────────────┐
    │ Apply Recovery Strategy          │
    │                                 │
    │ T1: ├─ Increase timeout          │
    │     └─ Decompose task            │
    │                                 │
    │ T2: ├─ Summarize context         │
    │     └─ Continue with summary     │
    │                                 │
    │ T3: ├─ Use fallback tool         │
    │     └─ Verify preconditions      │
    │                                 │
    │ T4: ├─ Wait for resource         │
    │     └─ Cleanup and retry         │
    │                                 │
    │ T5: ├─ Escalate to user          │
    │     └─ Request clarification     │
    └──────────┬────────────────────┘
               │
               ▼
        [Retry] or [Escalate]
```

---

## 3. DATA FLOW DIAGRAMS

### 3.1 File Handling Data Flow

```
User Request
    │
    ▼
"Read file X"
    │
    ├─────────────────────────────────────┐
    │                                     │
┌───▼────────┐                            │
│ Prechecks   │                            │
│ - Path ok?  │                            │
│ - Access?   │                            │
└───┬────────┘                            │
    │                                     │
    ▼                                     │
[Read Tool Called]                        │
    │                                     │
    ├─ Offset/Limit applied               │
    ├─ Line numbering added               │
    └─ Image/PDF handling                 │
    │                                     │
    ▼                                     │
Content returned
    │
    ├──────────────────────────────────┐
    │ (User examines content)          │
    │                                  │
    ▼                                  │
"Edit file X at line Y"               │
    │◄─────────────────────────────────┘
    │
    ├─────────────────────┐
    │ Preconditions:      │
    │ - Must read first   │
    │ - Exact match req'd │
    │ - Context preserved │
    └───┬─────────────────┘
        │
        ▼
    [Edit Tool Called]
        │
        ├─ Find exact old_string
        ├─ Replace with new_string
        ├─ Line endings preserved
        └─ Conflict detection
        │
        ▼
    File Updated
        │
        ▼
    [Verify Changes]
    Git status check / Read verification
        │
        ▼
    Success Confirmation
```

### 3.2 Bash Execution Data Flow

```
                Bash Command
                     │
                     ▼
        ┌────────────────────────────┐
        │ Command Classification     │
        │ - Is interactive?          │
        │ - Duration estimate?       │
        │ - Background needed?       │
        └────┬───────────┬───────┬──┘
             │           │       │
        ┌────┴─┐      ┌──┴──┐  ┌┴──────────┐
        │      │      │     │  │           │
        ▼      ▼      ▼     ▼  ▼           ▼
    [Quick] [Long] [BG] [Parallel] [Interactive]
      │        │      │      │           │
      │        │      │      │      [ERROR: Not Supported]
      │        │      │      │           │
      └────┬───┴──┬───┴──┬───┘           │
           │      │      │               │
           ▼      ▼      ▼               │
      [Exec]  [Timeout] [Background Shell]
           │      │       │              │
           │      │       ├─────────────┐│
           │      │       │  shell_id   ││
           │      │       │  tracking   ││
           │      │       │             ││
           ▼      ▼       ▼             ▼▼
        [stdout/stderr returned]  [Output logged]
           │      │       │             │
           └──────┼───────┼─────────────┘
                  │       │
                  ▼       ▼
          [Display Output] [BashOutput polling]
```

### 3.3 Git Operation Flow

```
                Git Operation
                     │
         ┌───────────┼───────────┐
         │           │           │
         ▼           ▼           ▼
     [Status]   [Commit]    [Merge/Rebase]
         │           │           │
         ▼           ▼           ▼
    Check State  ┌──────────┐  ┌──────────┐
         │       │ Stage    │  │ Conflicts│
         │       │ Changes  │  │ Detected │
         │       └────┬─────┘  └────┬─────┘
         │            │             │
         │            ▼             ▼
         │      [Create Commit] [Read Conflict]
         │            │             │
         │            ▼             ▼
         │       [PR Creation]  [User Resolution]
         │            │             │
         │            ▼             ▼
         │      [GitHub Integration] [Edit Conflict]
         │            │             │
         └────────────┼─────────────┘
                      │
                      ▼
             [Operation Result]
                      │
         ┌────────────┼────────────┐
         │            │            │
         ▼            ▼            ▼
     [Success]   [Error]    [Partial Success]
         │            │            │
         └────────────┼────────────┘
                      │
                      ▼
              [Audit Log Entry]
```

---

## 4. KEY METRICS AND THRESHOLDS

### 4.1 Performance Thresholds

```
Metric                  Yellow Zone    Red Zone       Action
────────────────────────────────────────────────────────────────
Token Usage             150k (75%)     180k (90%)     Warn/Summarize
Context Depth           30 exchanges   50 exchanges   Summarize
File Read Size          2000 lines     (max)          Truncate/Offset
Bash Timeout            60s            120s           Default
Intensive Op Timeout    300s           600s           Max
Background Processes    5-10           20             Cleanup
Parallel Tool Calls     10-15          20             Serialize
Error Rate              5%             10%            Escalate
```

### 4.2 Task Classification Heuristics

```
Task Type          Indicators                    Subagent Type
──────────────────────────────────────────────────────────────
Exploration        "Find", "Search", "Locate"    explore
                   "What files", "Where is"

Analysis           "Explain", "Analyze"          analyze
                   "Compare", "Identify"
                   Multiple file references

Implementation     "Add", "Fix", "Implement"      execute
                   "Create", "Refactor"
                   Code modifications

Complex           Combination of above            Multiple subagents
                   or multiple domains
```

---

## 5. TROUBLESHOOTING QUICK REFERENCE

### 5.1 Common Issues and Solutions

```
Issue                          Symptom              Solution
────────────────────────────────────────────────────────────────
Timeout                        Operation never      Increase timeout
                               completes            Decompose task

Context Exhaustion             Token budget hit     Use auto-memory
                               before completion    Summarize context

File Not Found                 Read tool fails      Use Glob to search
                                                    Check paths

Permission Denied              Bash command fails   Use specialized tool
                                                    Check permissions

Git Conflicts                  Merge fails          Resolve conflicts
                                                    manually

Model Unavailable              API error            Fallback to alt
                                                    Check credentials

Bash Buffering                 Output delayed       Use python3 -u
                                                    Run in background

Shell Limit                     Too many bgd procs   Kill old shells
                                                    Reset KillShell
```

### 5.2 Debugging Techniques

```bash
# Enable verbose logging
ante run --debug "task"

# Check memory state
ante memory show MEMORY.md

# View token usage
ante logs --grep "tokens"

# List active shells
ante shells list

# Kill stuck shell
ante shells kill [shell_id]

# Reset context
ante context reset

# Increase timeout
ante run --timeout 600000 "long_task"

# Test tool availability
ante test-tool [tool_name]
```

---

## 6. GLOSSARY

```
Term                 Definition
─────────────────────────────────────────────────────────────────
Subagent           Specialized agent spawned for specific task type
Context Window      Total tokens available for conversation
Token Budget        Allocation of tokens per operation/subagent
TTL                 Time To Live - timeout for operation
Shell ID            Unique identifier for background process
Precondition        Requirement that must be true before operation
Parser Result       Validation output from test assertions
Failure Mode        Category of error that occurred
Task Classification Automatic determination of required subagent type
Context Propagation Sharing parent context with subagent
State Synchronization Updating parent state from subagent results
Tool Routing        Decision logic for selecting appropriate tool
Materialized Path  Explicit file path vs. glob pattern
Conflict Marker    Git merge conflict markers <<<<< ======= >>>>>
Parser Output       Structured results from validation tests
```

---

## 7. CONTACT AND RESOURCES

**Ante by Antigma Labs**
- GitHub: https://github.com/AntigmaLabs
- Cargo: https://crates.io/crates/ante
- Docs: https://docs.antigma.ai (access-restricted)

**Related Projects**
- TensorZero: https://github.com/AntigmaLabs/tensorzero
- MCP SDK: https://github.com/AntigmaLabs/mcp-sdk
- Terminal-Bench: https://github.com/laude-institute/terminal-bench

**Benchmarks & Leaderboard**
- Terminal-Bench Leaderboard: https://github.com/AntigmaLabs/terminal-bench-leaderboard
- Latest Results: See terminal-bench-core@0.1.1 directory

**Feedback & Help**
- GitHub Issues: https://github.com/AntigmaLabs/ante/issues
- Discussions: https://github.com/AntigmaLabs/discussions

---

**Document Version**: 1.0
**Last Updated**: 2026-02-20
**Ante Version**: v0.1.0
**Status**: Research Complete
