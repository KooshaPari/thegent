# Core Concepts & Protocol

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

Concepts

Core Concepts & Protocol

[Ante Preview](/start/overview)

[Ante Preview](/start/overview)

Concepts

# Core Concepts & Protocol

Ante’s fundamental abstractions, and the Op/Evt message protocol that connects them

Ante models agent interactions as a hierarchy of concepts, connected by a typed message-passing protocol.

## 

​

Concept hierarchy

Copy

Ask AI
    
    
    Project
     └── Session
          └── Task
               └── Turn
                    └── Step
    

Concept| Description  
---|---  
**Project**|  A git repo or root directory. Can have multiple sessions.  
**Session**|  One episode of interaction between user and Ante. Manages dialog state, token usage, and context compaction.  
**Task**|  One piece of work the user wants to accomplish. Can span multiple turns.  
**Turn**|  One back-and-forth with the agent. Starts with user input, ends with agent message or approval request.  
**Step**|  One interaction from agent with LLM. Handles tool calls and other mechanics.  
  
Generally, if there is no approval interruption, one task consists of one turn.

## 

​

Protocol: Ops and Events

Ante uses a message-passing protocol between the client (TUI or headless runner) and the daemon. Operations (`Op`) flow from client to daemon, and events (`Evt`) flow from daemon to client.

### 

​

Message IDs

Every message has a custom `Id` type with a 4-byte prefix for tracing:

  * `op_` — operations
  * `evt_` — events
  * `ses_` — sessions
  * `step_` — steps

## 

​

Operations reference

Op| Fields| Description  
---|---|---  
`NewSession`| model, provider, policy, streaming, config| Initialize a new session  
`UserInput`| String| Submit a user prompt  
`ApprovalResponse`| allow/deny| Respond to tool approval request  
`SlashCommand`| skill name, args| Invoke a skill  
`OfflineMode`| OfflineModeOp| Offline mode operations  
`Interrupt`| —| Abort the current task  
`Shutdown`| —| Clean shutdown  
  
## 

​

Events reference

Evt| Fields| Description  
---|---|---  
`SessionInit`| metadata| Session is ready  
`TaskStarted`| id| A new task has begun  
`TaskFinished`| id, error, is_interrupted| Task completed or failed  
`AgentMessage`| String| Text response from agent  
`Thinking`| String| Chain-of-thought content  
`MessageDelta`| String| Streaming content chunk  
`ToolCallStarted`| tool_use| Tool execution began  
`ToolCallFinished`| result| Tool execution completed  
`ToolCallCancelled`| —| Tool execution was cancelled  
`RequestApproval`| tool_use| Agent needs permission  
`UsageUpdate`| tokens, cost| Token/cost tracking  
`Info`| String| Informational message  
`Error`| String| Error message  
  
## 

​

Flow examples

### 

​

Basic UI flow

A single user input followed by a 2-turn task:

"LLM Provider""Daemon""UI"LLMTaskSessionCoreUserLLMTaskSessionCoreUserTurn 1Turn 2Op::NewSession1Create session2Evt::SessionInit3Op::UserInput4Start task5Evt::TaskStarted6prompt7response (exec)8Evt::RequestApproval9Op::ApprovalResponse(allow)10Evt::ToolCallStarted11exec12Evt::ToolCallFinished13stdout14response (patch)15apply patch (auto-approved)16success17response (msg + completed)18Evt::AgentMessage19Evt::TurnComplete20Evt::TaskFinished21

### 

​

Task interruption

Interrupting a task and continuing with additional user input:

"LLM Provider""Daemon""UI"LLMTask2Task1SessionUserLLMTask2Task1SessionUserOp::UserInput1Start task2Evt::TaskStarted3prompt4response (exec)5exec (auto-approved)6Evt::TurnComplete7stdout8response (exec)9exec (auto-approved)10Op::Interrupt11Evt::Error("interrupted")12Op::UserInput w/ last_response_id13Start task14Evt::TaskStarted15prompt + Task1 last_response_id16response (exec)17exec (auto-approved)18Evt::TurnComplete19stdout20msg + completed21Evt::AgentMessage22Evt::TurnComplete23Evt::TaskFinished24

## 

​

Context management

Ante automatically manages context windows:

  * **Token budget** — Each turn tracks token usage against the model’s context limit
  * **Auto-compaction** — When the dialog approaches the context limit, Ante uses the LLM to summarize the conversation history, preserving important context while freeing tokens
  * **Tool result trimming** — Large tool outputs are automatically trimmed to fit within budget

## 

​

Permissions

Ante has a permission system that gates tool execution:

Policy| Behavior  
---|---  
`Default`| Tools marked `requires_approval` prompt the user before execution  
`Yolo`| All tools execute without approval  
  
In the TUI, you approve or deny each tool call interactively. In headless mode, `--yolo` is implied (all tools auto-approved). Tools like `Bash` and `Write` require approval by default, while read-only tools like `Read`, `Glob`, and `Grep` do not.

[Previous](/start/eval)[ArchitectureAnte's client-daemon architecture, provider system, and tool frameworkNext](/concepts/architecture)

[Powered by](https://www.mintlify.com?utm_campaign=poweredBy&utm_medium=referral&utm_source=antigmalabs)

On this page

  * Concept hierarchy
  * Protocol: Ops and Events
  * Message IDs
  * Operations reference
  * Events reference
  * Flow examples
  * Basic UI flow
  * Task interruption
  * Context management
  * Permissions

Assistant

Responses are generated using AI and may contain mistakes.

Core Concepts & Protocol - Ante

