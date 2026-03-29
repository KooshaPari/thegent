# {Project Name} — Comprehensive System Plan

## 1. Mission Statement

{Single paragraph: What the system does, how it operates, at what scale, and what it optimizes for. Include key constraints (e.g., local/OSS/free, autonomous, agent-driven).}

---

## 2. Magic I/O: The Hard Problems

{These are the areas where automation breaks down — where programs, LLMs, and sometimes even humans struggle. The plan must address each one explicitly or the system fails.}

### M1: {Hard Problem Title}
{2-3 sentences describing WHY this is hard — not just what it is, but why naive approaches fail.}

**Mitigation:** {Concrete approach. Name specific strategies, tools, fallbacks. Not hand-wavy — this should be implementable.}

### M2: {Hard Problem Title}
{Why this is hard}

**Mitigation:** {Concrete approach}

### M3: {Hard Problem Title}
{Why this is hard}

**Mitigation:** {Concrete approach}

{Continue for all identified hard problems. Typical count: 4-8.}

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     {ORCHESTRATOR LAYER}                      │
│  {Key responsibilities of orchestrator}                       │
└──────┬──────────┬──────────┬───────────┬───────────┬────────┘
       │          │          │           │           │
  ┌────▼───┐ ┌───▼────┐ ┌──▼───┐ ┌────▼────┐ ┌────▼─────┐
  │{STAGE1}│ │{STAGE2}│ │{ST3} │ │ {STAGE4}│ │ {STAGE5} │
  │        │ │        │ │      │ │         │ │          │
  │{tool1} │ │{tool1} │ │{t1}  │ │{tool1}  │ │{tool1}   │
  │{tool2} │ │{tool2} │ │{t2}  │ │{tool2}  │ │{tool2}   │
  └────────┘ └────────┘ └──────┘ └─────────┘ └──────────┘
       │          │          │           │           │
       └──────────┴──────────┴───────────┴───────────┘
                              │
                     ┌────────▼────────┐
                     │   {DATA STORE}  │
                     │  {description}  │
                     └────────┬────────┘
                              │
                     ┌────────▼────────┐
                     │  {ESCALATION}   │
                     │  {channels}     │
                     └─────────────────┘
```

### Data Stores
- **{Store 1}** ({backing}): {What it stores}
- **{Store 2}** ({path}): {What it stores}

### Services ({manager} managed)
- `{service_1}` — {description}
- `{service_2}` — {description}
- `{service_3}` — {description}

---

## 4. Data Schema

### Table: `{table_1}`
| Column | Type | Description |
|--------|------|-------------|
| id | AutoID | PK |
| {column} | {Type} | {Description} |
| {column} | {Type} | {Description} |
| created_at | DateTime | |

### Table: `{table_2}`
| Column | Type | Description |
|--------|------|-------------|
| id | AutoID | PK |
| {column} | {Type} | {Description} |

{Continue for all tables...}

---

## 5. Phased WBS with DAG Dependencies

### Phase 0: {Foundation / Setup} [{STATUS}]
| Task ID | Description | Depends On | Est. Wall Clock |
|---------|-------------|------------|-----------------|
| P0.1 | {task description} | — | ~{N} min |
| P0.2 | {task description} | — | ~{N} min |
| P0.3 | {task description} | P0.2 | ~{N} min |
| P0.4 | {task description} | P0.3 | ~{N} min |

**Phase 0 critical path:** {Identify the longest sequential chain}
**Phase 0 parallel:** {Identify tasks that can run concurrently}

### Phase 1: {Core Pipeline / Feature} [{STATUS}]
| Task ID | Description | Depends On | Est. Wall Clock |
|---------|-------------|------------|-----------------|
| P1.1 | {task description} | P0.4 | ~{N} min |
| P1.2 | {task description} | P0.4 | ~{N} min |
| P1.3 | {task description} | P1.1, P1.2 | ~{N} min |

**Phase 1 parallel:** {Tasks that can run concurrently}

### Phase 2: {Enhancement / Intelligence Layer} [{STATUS}]
| Task ID | Description | Depends On | Est. Wall Clock |
|---------|-------------|------------|-----------------|
| P2.1 | {task description} | P0.1 | ~{N} min |
| P2.2 | {task description} | P2.1, P0.4 | ~{N} min |

{Continue for all phases. Typical count: 5-9 phases.}

### Phase N: {Integration Test & Calibration} [{STATUS}]
| Task ID | Description | Depends On | Est. Wall Clock |
|---------|-------------|------------|-----------------|
| PN.1 | {End-to-end test — dry run} | {all prior phases} | ~{N} min |
| PN.2 | {Quality review of outputs} | PN.1 | ~{N} min |
| PN.3 | {Calibrate thresholds/parameters} | PN.2 | ~{N} min |
| PN.4 | {Live test with monitoring} | PN.3 | ~{N} min |

---

## 6. DAG Visualization

```
P0.1 ──────────────────────────────── P2.1 ── {downstream}
P0.2 ── P0.3 ──────────────────────── {downstream}
P0.4 ┐
P0.5 ┤── P0.6 ── P0.7 ─┬── P1.1 ┐
     │                  ├── P1.2 ┤── P1.3
     │                  └── P2.2 ── P2.3
     │
{Continue showing full dependency graph...}
PN.1 ── PN.2 ── PN.3 ── PN.4
```

---

## 7. Human Touchpoints (Minimal)

{List ONLY the unavoidable human interactions. In an agent-driven project, this should be very short.}

| When | What | Why |
|------|------|-----|
| {Task ID} | {Action required} | {Why it cannot be automated} |

During steady-state operation, the user is needed only for:
- {Situation 1}
- {Situation 2}

---

## 8. Steady-State Cadence

```
{HH:MM}  {Activity description}
{HH:MM}  {Activity description}
{HH:MM}  {Activity description — with sub-details}
          - {Detail 1}
          - {Detail 2}
{HH:MM}  {Activity description}
{HH:MM}  {End-of-day summary}
          - {Summary item 1}
          - {Summary item 2}
```

---

## 9. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| {Risk description} | {Low/Medium/High} | {Low/Medium/High} | {Concrete mitigation strategy} |
| {Risk description} | {Low/Medium/High} | {Low/Medium/High} | {Concrete mitigation strategy} |
| {Risk description} | {Low/Medium/High} | {Low/Medium/High} | {Concrete mitigation strategy} |

---

## 10. Tech Stack Summary

| Component | Technology | Why |
|-----------|-----------|-----|
| {Component} | {Technology} | {1-sentence justification — references ADR if applicable} |
| {Component} | {Technology} | {Justification} |
| {Component} | {Technology} | {Justification} |

---

## 11. Agent/Tool Delegation Map

{Which tasks require which tools or agent capabilities}

| Task Range | Why | Context to Pass |
|------------|-----|-----------------|
| {P{x}.{y}–P{x}.{z}} | {Why this range needs specific tooling} | {What context the executing agent needs} |

---

## 12. Open Questions

{Numbered list of unresolved decisions or information gaps. Each should be actionable — not rhetorical.}

1. **{Topic}:** {Specific question with options if known}
2. **{Topic}:** {Specific question}

<!--
Plan Guidelines:
  - Mission statement: one paragraph, concrete targets
  - Hard Problems: identify 4-8, each with concrete mitigation
  - WBS: phased, with task IDs, dependencies, and wall-clock estimates
  - DAG: visualize the dependency graph in ASCII
  - Estimates: agent-driven (tool calls, minutes), never "days" or "weeks"
  - Human touchpoints: minimize and justify each one
  - Risk register: at least 5 risks with concrete mitigations
  - Tech stack: every component justified, references ADRs
-->
