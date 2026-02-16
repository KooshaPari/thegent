# {Project Name} — User Journeys

**Version:** 1.0
**Date:** {Date}

---

## UJ-1: {Title} — {Brief Description of the Happy Path}

**Actor:** {Who or what participates — e.g., System (automated), User + System, User (via tool)}
**Frequency:** {How often this journey occurs — e.g., continuous, daily, on-demand, triggered by event}
**Goal:** {What is accomplished end-to-end}

```
[{Trigger event — time, cron, user action}]
     |
     v
{First action or stage}
  {Sub-action 1}
  {Sub-action 2}
  {Sub-action 3}
     | {result summary}
     v
{Insert/update/store step}
{Log to observability layer}
     |
     v
[{Next trigger or continuation}]
     |
     v
For each {item} with {condition}:
  +-- {Branch/action 1}
  +-- {Branch/action 2}
  +-- {Branch/action 3}
  +-- {Branch/action 4}
     |
     v
Results: {summary of outcomes — counts, categories}
Update {data store}
     |
     v
{Next stage}
  +-- Check {condition 1}: {pass behavior}
  +-- If {condition 2}: {alternative behavior}
  +-- Route by {criterion}:
  |   +-- {Route A}: {flow description}
  |   |    +-- {Step 1}
  |   |    +-- {Step 2}
  |   |    +-- {Verification}
  |   +-- {Route B}: {flow description}
  |   |    +-- {Step 1}
  |   |    +-- {Step 2}
  |   +-- {Route C}: {flow description}
  +-- On success: {success behavior}
  +-- On {error type}: {error behavior}
  +-- On failure: {failure behavior}
     |
     v
[{Periodic/scheduled check}]
     |
     v
{Monitoring/tracking step}
  +-- If {condition}: {auto-action}
  +-- If {other condition}: {escalation}
     |
     v
[{End-of-cycle summary}]
  +-- {Metric 1}: {value}
  +-- {Metric 2}: {value}
  +-- {Status}: {assessment}
```

---

## UJ-2: {Title} — {Human Handoff / Escalation Scenario}

**Actor:** {User + System}
**Trigger:** {Event that initiates this journey — e.g., classification, threshold crossed}
**Goal:** {What the human accomplishes with system support}

```
[{Trigger timestamp}] {Event description}
     |
     v
System {classifies/detects}: {result} (confidence: {N})
System {matches/identifies}: {entity reference}
System {extracts}: {relevant detail}
     |
     v
Notification:
   "{Title} -- {Entity} -- {Detail}
    {Deadline or urgency}
    > {Action prompt}"
     |
     v
System updates: {entity} -> status: {new_status}
     |
     v
[{User sees notification, takes action}]
[{User completes task on their own}]
     |
     v
[Later] {User reports completion via interface}
     |
     v
{Interface} -> {tool}: {update_call}(params)
{Data store} updated. System resumes {monitoring/processing}.
     |
     v
[{Subsequent event}] {Follow-up trigger}
System {classifies}: {result}
System updates: {entity} -> status: {next_status}
Notification with {next action details}
```

---

## UJ-3: {Title} — {On-Demand Review / Queue Management}

**Actor:** {User (via interface/tool)}
**Trigger:** {User asks a question or requests status}
**Goal:** {Review and act on queued items efficiently}

```
{User}: "{Natural language query}"
     |
     v
{Interface} -> {tool}: {query_call}()
     |
     v
Response:
  {HIGH PRIORITY}
  1. {Item type} -- {Entity} -- {urgency detail}
  2. {Item type} -- {Entity} -- {urgency detail}

  {REVIEW QUEUE}
  3. {Item description} (confidence: {N})
  4. {Item description} (score: {N}, {reason for queue})
  5. {Item description} (score: {N}, {reason for queue})

  {FYI}
  6. {N} items auto-processed today
  7. {Recommendation or insight}
     |
     v
{User}: "{Action instructions — resolve, skip, approve specific items}"
     |
     v
{Interface} -> {tool}: {action_1}(params)
{Interface} -> {tool}: {action_2}(params)
{Interface} -> {tool}: {action_3}(params)
     |
     v
System executes actions
{Describe fallback behavior if action fails}
```

---

## UJ-4: {Title} — {Content/Output Review and Edit}

**Actor:** {User (via interface/tool)}
**Trigger:** {User wants to review generated content before use}
**Goal:** {Quality-check and optionally edit output}

```
{User}: "{Request to preview content for specific entity}"
     |
     v
{Interface} -> {tool}: {preview_call}(entity_id, type)
     |
     v
{Interface} displays: {content summary}
  - {Configuration used}: {value}
  - {Key modifications}: {list of changes from base}
  - {Related content}: {references or connections}
     |
     v
{User}: "{Edit instructions — specific changes requested}"
     |
     v
{Interface} -> {tool}: {edit_call}(entity_id, edits="{instructions}")
     |
     v
System regenerates with edits applied
{Interface} shows updated preview
     |
     v
{User}: "{Approval}"
     |
     v
{Interface} -> {tool}: {approve_call}(entity_id)
{Entity} moves to {next stage} queue
```

---

## UJ-5: {Title} — {System Startup / Cold Start}

**Actor:** {User}
**Trigger:** {First run or restart}
**Goal:** {All services running, system operational}

```
{User}: opens terminal
     |
     v
$ {start command}
     |
     v
{Process manager} starts:
  +-- {service_1} .. [{status}] -> [{healthy}] (port {N})
  +-- {service_2} .. [{status}] -> [{healthy}] (port {N})
  +-- health checks pass
     |
     v
{Service 1}: {startup validation}
  +-- {Check 1}: {pass behavior}
  +-- {Check 2}: {pass behavior}
     |
     v
{Service 2}: {startup validation}
  +-- {Subsystem 1}: active ({detail})
  +-- {Subsystem 2}: active ({detail})
  +-- {Subsystem N}: active ({detail})
     |
     v
$ {status command}
  {service_1}: {healthy indicator}
  {service_2}: {healthy indicator}
  {key metric}: {value}
  {key metric}: {value}
     |
     v
System is operational. {User action after startup.}
```

---

## UJ-6: {Title} — {Error Recovery / Interruption Handling}

**Actor:** {System -> User -> System}
**Trigger:** {Error or interruption detected during automated flow}
**Goal:** {User resolves blocker, system resumes}

```
[{Timestamp}] System executing {operation} for {entity}
     |
     v
{Step 1}: {detail} -> {status}
{Step 2}: {detail} -> {status}
{Step 3}: {detail} -> {ERROR DETECTED}
     |
     v
System: {captures state — screenshot, form data, context}
System: {pauses — does not close or navigate away}
System: {saves progress}
     |
     v
Notification:
   "{Error Type} -- {Context}
    {Actionable instruction}
    > {Action prompt}"
     |
     v
[{User takes manual action to resolve}]
     |
     v
System: detects resolution ({how detection works})
System: resumes from saved state
System: verifies completion
System: updates {entity} -> status: {completed}
System: logs {event type} to {observability layer}
     |
     v
System resumes normal operation
```

---

{Additional user journeys as needed. Common patterns:}

{UJ-N: Deep Dive / Research — user requests comprehensive analysis}
{UJ-N: Decision Support — system provides context for a human decision}
{UJ-N: Configuration Change — user adjusts parameters/thresholds}
{UJ-N: Batch Operation — user triggers bulk action}

<!--
User Journey Guidelines:
  - UJ-1 should always be the happy path (zero/minimal human involvement)
  - Use ASCII flowchart notation: [triggers], arrows, +-- branches
  - Include timestamps where timing matters
  - Show the exact tool/API calls that execute each step
  - Show notification text verbatim (what the user actually sees)
  - Cover: happy path, escalation, on-demand review, content review, startup, error recovery
  - Each UJ is self-contained — readable without cross-referencing others
  - Actor + Trigger + Goal header on every journey
-->
