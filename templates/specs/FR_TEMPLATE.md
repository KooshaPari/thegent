# {Project Name} — Functional Requirements Specification

**Version:** 1.0
**Date:** {Date}

---

## FR Categories

- **FR-{CAT1}**: {Category 1 Name}
- **FR-{CAT2}**: {Category 2 Name}
- **FR-{CAT3}**: {Category 3 Name}
- **FR-{CAT4}**: {Category 4 Name}

---

## FR-{CAT1}: {Category 1 Name}

### FR-{CAT1}-001: {Requirement Title}
**Traces to:** E{x}.{y}.{z}, E{x}.{y}.{z}
**Priority:** P0

**Description:** The system SHALL {formal requirement statement describing what the system must do}.

**Input:** {Description of inputs — parameters, data sources, triggers}
**Output:** {Description of outputs — records created, state changes, side effects}

**Constraints:**
- {Constraint 1 — e.g., each record SHALL conform to schema X}
- {Constraint 2 — e.g., operation SHALL be idempotent}
- {Constraint 3 — e.g., source-specific fields SHALL be stored in metadata column}

### FR-{CAT1}-002: {Requirement Title}
**Traces to:** E{x}.{y}.{z}
**Priority:** P0

**Description:** The system SHALL {requirement}.

**Required parameters:**
- `{param_1}`: {description and constraints}
- `{param_2}`: {description and constraints}
- `{param_3}`: {description and constraints}

### FR-{CAT1}-003: {Requirement Title}
**Traces to:** E{x}.{y}.{z}, E{x}.{y}.{z}
**Priority:** P1

**Description:** The system SHALL {requirement}.

**{Algorithm/Logic specification}:**
- {Step or rule 1}
- {Step or rule 2}
- {Step or rule 3}

**Behavior on {edge case}:** {What happens — e.g., skip insert, log, escalate}

---

## FR-{CAT2}: {Category 2 Name}

### FR-{CAT2}-001: {Requirement Title}
**Traces to:** E{x}.{y}.{z}
**Priority:** P0

**Description:** The system SHALL {requirement}.

**Schema (`{config/path}`):**
```json
{
  "{section}": {
    "{field_1}": "{value_or_type}",
    "{field_2}": "{value_or_type}"
  },
  "{section_2}": {
    "{field_1}": {"{sub_field}": "{type}", "{sub_field}": "{type}"}
  }
}
```

### FR-{CAT2}-002: {Requirement Title}
**Traces to:** E{x}.{y}.{z}
**Priority:** P0

**Description:** The system SHALL {requirement}.

**Output schema:**
```json
{
  "{field_1}": ["{value_1}", "{value_2}"],
  "{field_2}": "{type}",
  "{field_3}": "{type}"
}
```

**Constraints:** {Processing constraints — e.g., SHALL complete in <5s per item}

### FR-{CAT2}-003: {Requirement Title}
**Traces to:** E{x}.{y}.{z}, E{x}.{y}.{z}
**Priority:** P0

**Description:** The system SHALL {requirement using formal weighted/scored logic}.

**Dimensions and default weights:**

| Dimension | Weight | Computation |
|-----------|--------|-------------|
| {dimension_1} | {weight} | {formula or description} |
| {dimension_2} | {weight} | {formula or description} |
| {dimension_3} | {weight} | {formula or description} |

**Formula:** `{mathematical formula}`
**Override rules:** {Conditions that bypass normal computation — e.g., deal-breakers}

---

## FR-{CAT3}: {Category 3 Name}

### FR-{CAT3}-001: {Requirement Title}
**Traces to:** E{x}.{y}.{z}
**Priority:** P0

**Description:** The system SHALL {requirement — multi-step process}.

**Steps:**
1. {Step 1}
2. {Step 2}
3. {Step 3}
4. On success: {success behavior}
5. On failure: {failure behavior — retry, escalate, log}

### FR-{CAT3}-002: {Requirement Title}
**Traces to:** E{x}.{y}.{z}
**Priority:** P0

**Description:** The system SHALL enforce the following constraints:

| Constraint | Limit | Scope |
|-----------|-------|-------|
| {constraint_1} | {limit} | {scope — e.g., rolling window, per domain} |
| {constraint_2} | {limit} | {scope} |
| {constraint_3} | {limit} | {scope} |

**Behavior when limit hit:** {Queue, delay, escalate — never silently drop}

---

## FR-{CAT4}: {Category 4 Name}

### FR-{CAT4}-001: {Requirement Title — e.g., Tool/API Manifest}
**Traces to:** E{x}.{y}.{z}
**Priority:** P0

**Description:** The system SHALL expose the following {tools/endpoints/interfaces}:

**Read {tools/endpoints}:**
| {Name} | Description | Parameters |
|--------|-------------|------------|
| `{name_1}` | {description} | {param list} |
| `{name_2}` | {description} | {param list} |

**Write {tools/endpoints}:**
| {Name} | Description | Parameters |
|--------|-------------|------------|
| `{name_1}` | {description} | {param list} |
| `{name_2}` | {description} | {param list} |

### FR-{CAT4}-002: {Requirement Title — e.g., State Machine}
**Traces to:** E{x}.{y}.{z}
**Priority:** P0

**Description:** {Entity} status transitions SHALL follow this state machine:

```
{state_1} → {state_2} → {state_3} → {state_4}
                                        │
                    ┌───────────────────┤
                    │         │         │
                    ▼         ▼         ▼
               {state_5}  {state_6}  {state_7}
```

**Invalid transitions SHALL be rejected** with an error logged.

---

<!--
FR Guidelines:
  - Use SHALL for mandatory requirements, SHOULD for recommended, MAY for optional
  - Every FR must trace to at least one Epic/Story (Traces to: E{x}.{y}.{z})
  - Include concrete schemas, formulas, and constraints — not vague prose
  - Specify behavior for edge cases and failure modes explicitly
  - Group related FRs under category prefixes (FR-{CAT}-{NNN})
  - Priority: P0 = must-have for launch, P1 = important, P2 = nice-to-have
-->
