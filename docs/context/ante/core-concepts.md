# ANTE: Core Concepts & Protocol

> Extracted from Ante docs. Fetched 2026-02-20

Ante home page

Search...



Navigation

Concepts

Core Concepts & Protocol
Concepts
Core Concepts & Protocol
Ante’s fundamental abstractions, and the Op/Evt message protocol that connects them
Ante models agent interactions as a hierarchy of concepts, connected by a typed message-passing protocol.
​

Concept hierarchy

Copy

Ask AI
Project
 └── Session
      └── Task
           └── Turn
                └── Step

Concept
Description
Project
A git repo or root directory. Can have multiple sessions.
Session
One episode of interaction between user and Ante. Manages dialog state, token usage, and context compaction.
Task
One piece of work the user wants to accomplish. Can span multiple turns.
Turn
One back-and-forth with the agent. Starts with user input, ends with agent message or approval request.
Step
One interaction from agent with LLM. Handles tool calls and other mechanics.

Generally, if there is no approval interruption, one task consists of one turn.
​

Protocol: Ops and Events
Ante uses a message-passing protocol between the client (TUI or headless runner) and the daemon. Operations (Op) flow from client to daemon, and events (Evt) flow from daemon to client.
​

Message IDs
Every message has a custom Id type with a 4-byte prefix for tracing:
op_ — operations
evt_ — events
ses_ — sessions
step_ — steps
​

Operations reference
Op
Fields
Description
NewSession
model, provider, policy, streaming, config
Initialize a new session
UserInput
String
Submit a user prompt
ApprovalResponse
allow/deny
Respond to tool approval request
SlashCommand
skill name, args
Invoke a skill
OfflineMode
OfflineModeOp
Offline mode operations
Interrupt
—
Abort the current task
Shutdown
—
Clean shutdown
​

Events reference
Evt
Fields
Description
SessionInit
metadata
Session is ready
TaskStarted
id
A new task has begun
TaskFinished
id, error, is_interrupted
Task completed or failed
AgentMessage
String
Text response from agent
Thinking
String
Chain-of-thought content
MessageDelta
String
Streaming content chunk
ToolCallStarted
tool_use
Tool execution began
ToolCallFinished
result
Tool execution completed
ToolCallCancelled
—
Tool execution was cancelled
RequestApproval
tool_use
Agent needs permission
UsageUpdate
tokens, cost
Token/cost tracking
Info
String
Informational message
Error
String
Error message
​

Flow examples
​

Basic UI flow
A single user input followed by a 2-turn task:









"LLM Provider"
"Daemon"
"UI"
LLM
Task
Session
Core
User
LLM
Task
Session
Core
User
#mermaid-_r_e_-1771584156999{font-family:inherit;font-size:16px;fill:#ccc;}#mermaid-_r_e_-1771584156999 .error-icon{fill:#a44141;}#mermaid-_r_e_-1771584156999 .error-text{fill:#ddd;stroke:#ddd;}#mermaid-_r_e_-1771584156999 .edge-thickness-normal{stroke-width:1px;}#mermaid-_r_e_-1771584156999 .edge-thickness-thick{stroke-width:3.5px;}#mermaid-_r_e_-1771584156999 .edge-pattern-solid{stroke-dasharray:0;}#mermaid-_r_e_-1771584156999 .edge-thickness-invisible{stroke-width:0;fill:none;}#mermaid-_r_e_-1771584156999 .edge-pattern-dashed{stroke-dasharray:3;}#mermaid-_r_e_-1771584156999 .edge-pattern-dotted{stroke-dasharray:2;}#mermaid-_r_e_-1771584156999 .marker{fill:lightgrey;stroke:lightgrey;}#mermaid-_r_e_-1771584156999 .marker.cross{stroke:lightgrey;}#mermaid-_r_e_-1771584156999 svg{font-family:inherit;font-size:16px;}#mermaid-_r_e_-1771584156999 p{margin:0;}#mermaid-_r_e_-1771584156999 .actor{stroke:#ccc;fill:#1f2020;}#mermaid-_r_e_-1771584156999 text.actor>tspan{fill:lightgrey;stroke:none;}#mermaid-_r_e_-1771584156999 .actor-line{stroke:#ccc;}#mermaid-_r_e_-1771584156999 .messageLine0{stroke-width:1.5;stroke-dasharray:none;stroke:lightgrey;}#mermaid-_r_e_-1771584156999 .messageLine1{stroke-width:1.5;stroke-dasharray:2,2;stroke:lightgrey;}#mermaid-_r_e_-1771584156999 #arrowhead path{fill:lightgrey;stroke:lightgrey;}#mermaid-_r_e_-1771584156999 .sequenceNumber{fill:black;}#mermaid-_r_e_-1771584156999 #sequencenumber{fill:lightgrey;}#mermaid-_r_e_-1771584156999 #crosshead path{fill:lightgrey;stroke:lightgrey;}#mermaid-_r_e_-1771584156999 .messageText{fill:lightgrey;stroke:none;}#mermaid-_r_e_-1771584156999 .labelBox{stroke:#ccc;fill:#1f2020;}#mermaid-_r_e_-1771584156999 .labelText,#mermaid-_r_e_-1771584156999 .labelText>tspan{fill:lightgrey;stroke:none;}#mermaid-_r_e_-1771584156999 .loopText,#mermaid-_r_e_-1771584156999 .loopText>tspan{fill:lightgrey;stroke:none;}#mermaid-_r_e_-1771584156999 .loopLine{stroke-width:2px;stroke-dasharray:2,2;stroke:#ccc;fill:#ccc;}#mermaid-_r_e_-1771584156999 .note{stroke:hsl(180, 0%, 18.3529411765%);fill:hsl(180, 1.5873015873%, 28.3529411765%);}#mermaid-_r_e_-1771584156999 .noteText,#mermaid-_r_e_-1771584156999 .noteText>tspan{fill:rgb(183.8476190475, 181.5523809523, 181.5523809523);stroke:none;}#mermaid-_r_e_-1771584156999 .activation0{fill:hsl(180, 1.5873015873%, 28.3529411765%);stroke:#ccc;}#mermaid-_r_e_-1771584156999 .activation1{fill:hsl(180, 1.5873015873%, 28.3529411765%);stroke:#ccc;}#mermaid-_r_e_-1771584156999 .activation2{fill:hsl(180, 1.5873015873%, 28.3529411765%);stroke:#ccc;}#mermaid-_r_e_-1771584156999 .actorPopupMenu{position:absolute;}#mermaid-_r_e_-1771584156999 .actorPopupMenuPanel{position:absolute;fill:#1f2020;box-shadow:0px 8px 16px 0px rgba(0,0,0,0.2);filter:drop-shadow(3px 5px 2px rgb(0 0 0 / 0.4));}#mermaid-_r_e_-1771584156999 .actor-man line{stroke:#ccc;fill:#1f2020;}#mermaid-_r_e_-1771584156999 .actor-man circle,#mermaid-_r_e_-1771584156999 line{stroke:#ccc;fill:#1f2020;stroke-width:2px;}#mermaid-_r_e_-1771584156999 :root{--mermaid-font-family:inherit;}
Turn 1
Turn 2
Op::NewSession
1
Create session
2
Evt::SessionInit
3
Op::UserInput
4
Start task
5
Evt::TaskStarted
6
prompt
7
response (exec)
8
Evt::RequestApproval
9
Op::ApprovalResponse(allow)
10
Evt::ToolCallStarted
11
exec
12
Evt::ToolCallFinished
13
stdout
14
response (patch)
15
apply patch (auto-approved)
16
success
17
response (msg + completed)
18
Evt::AgentMessage
19
Evt::TurnComplete
20
Evt::TaskFinished
21
​

Task interruption
Interrupting a task and continuing with additional user input:









"LLM Provider"
"Daemon"
"UI"
LLM
Task2
Task1
Session
User
LLM
Task2
Task1
Session
User
#mermaid-_r_f_-1771584157000{font-family:inherit;font-size:16px;fill:#ccc;}#mermaid-_r_f_-1771584157000 .error-icon{fill:#a44141;}#mermaid-_r_f_-1771584157000 .error-text{fill:#ddd;stroke:#ddd;}#mermaid-_r_f_-1771584157000 .edge-thickness-normal{stroke-width:1px;}#mermaid-_r_f_-1771584157000 .edge-thickness-thick{stroke-width:3.5px;}#mermaid-_r_f_-1771584157000 .edge-pattern-solid{stroke-dasharray:0;}#mermaid-_r_f_-1771584157000 .edge-thickness-invisible{stroke-width:0;fill:none;}#mermaid-_r_f_-1771584157000 .edge-pattern-dashed{stroke-dasharray:3;}#mermaid-_r_f_-1771584157000 .edge-pattern-dotted{stroke-dasharray:2;}#mermaid-_r_f_-1771584157000 .marker{fill:lightgrey;stroke:lightgrey;}#mermaid-_r_f_-1771584157000 .marker.cross{stroke:lightgrey;}#mermaid-_r_f_-1771584157000 svg{font-family:inherit;font-size:16px;}#mermaid-_r_f_-1771584157000 p{margin:0;}#mermaid-_r_f_-1771584157000 .actor{stroke:#ccc;fill:#1f2020;}#mermaid-_r_f_-1771584157000 text.actor>tspan{fill:lightgrey;stroke:none;}#mermaid-_r_f_-1771584157000 .actor-line{stroke:#ccc;}#mermaid-_r_f_-1771584157000 .messageLine0{stroke-width:1.5;stroke-dasharray:none;stroke:lightgrey;}#mermaid-_r_f_-1771584157000 .messageLine1{stroke-width:1.5;stroke-dasharray:2,2;stroke:lightgrey;}#mermaid-_r_f_-1771584157000 #arrowhead path{fill:lightgrey;stroke:lightgrey;}#mermaid-_r_f_-1771584157000 .sequenceNumber{fill:black;}#mermaid-_r_f_-1771584157000 #sequencenumber{fill:lightgrey;}#mermaid-_r_f_-1771584157000 #crosshead path{fill:lightgrey;stroke:lightgrey;}#mermaid-_r_f_-1771584157000 .messageText{fill:lightgrey;stroke:none;}#mermaid-_r_f_-1771584157000 .labelBox{stroke:#ccc;fill:#1f2020;}#mermaid-_r_f_-1771584157000 .labelText,#mermaid-_r_f_-1771584157000 .labelText>tspan{fill:lightgrey;stroke:none;}#mermaid-_r_f_-1771584157000 .loopText,#mermaid-_r_f_-1771584157000 .loopText>tspan{fill:lightgrey;stroke:none;}#mermaid-_r_f_-1771584157000 .loopLine{stroke-width:2px;stroke-dasharray:2,2;stroke:#ccc;fill:#ccc;}#mermaid-_r_f_-1771584157000 .note{stroke:hsl(180, 0%, 18.3529411765%);fill:hsl(180, 1.5873015873%, 28.3529411765%);}#mermaid-_r_f_-1771584157000 .noteText,#mermaid-_r_f_-1771584157000 .noteText>tspan{fill:rgb(183.8476190475, 181.5523809523, 181.5523809523);stroke:none;}#mermaid-_r_f_-1771584157000 .activation0{fill:hsl(180, 1.5873015873%, 28.3529411765%);stroke:#ccc;}#mermaid-_r_f_-1771584157000 .activation1{fill:hsl(180, 1.5873015873%, 28.3529411765%);stroke:#ccc;}#mermaid-_r_f_-1771584157000 .activation2{fill:hsl(180, 1.5873015873%, 28.3529411765%);stroke:#ccc;}#mermaid-_r_f_-1771584157000 .actorPopupMenu{position:absolute;}#mermaid-_r_f_-1771584157000 .actorPopupMenuPanel{position:absolute;fill:#1f2020;box-shadow:0px 8px 16px 0px rgba(0,0,0,0.2);filter:drop-shadow(3px 5px 2px rgb(0 0 0 / 0.4));}#mermaid-_r_f_-1771584157000 .actor-man line{stroke:#ccc;fill:#1f2020;}#mermaid-_r_f_-1771584157000 .actor-man circle,#mermaid-_r_f_-1771584157000 line{stroke:#ccc;fill:#1f2020;stroke-width:2px;}#mermaid-_r_f_-1771584157000 :root{--mermaid-font-family:inherit;}
Op::UserInput
1
Start task
2
Evt::TaskStarted
3
prompt
4
response (exec)
5
exec (auto-approved)
6
Evt::TurnComplete
7
stdout
8
response (exec)
9
exec (auto-approved)
10
Op::Interrupt
11
Evt::Error("interrupted")
12
Op::UserInput w/ last_response_id
13
Start task
14
Evt::TaskStarted
15
prompt + Task1 last_response_id
16
response (exec)
17
exec (auto-approved)
18
Evt::TurnComplete
19
stdout
20
msg + completed
21
Evt::AgentMessage
22
Evt::TurnComplete
23
Evt::TaskFinished
24
​

Context management
Ante automatically manages context windows:
Token budget — Each turn tracks token usage against the model’s context limit
Auto-compaction — When the dialog approaches the context limit, Ante uses the LLM to summarize the conversation history, preserving important context while freeing tokens
Tool result trimming — Large tool outputs are automatically trimmed to fit within budget
​

Permissions
Ante has a permission system that gates tool execution:
Policy
Behavior
Default
Tools marked requires_approval prompt the user before execution
Yolo
All tools execute without approval
In the TUI, you approve or deny each tool call interactively. In headless mode, --yolo is implied (all tools auto-approved).
Tools like Bash and Write require approval by default, while read-only tools like Read, Glob, and Grep do not.

Previous
Architecture

Next

Powered by



Assistant



Responses are generated using AI and may contain mistakes.
