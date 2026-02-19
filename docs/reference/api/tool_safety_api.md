# tool_safety API Reference

> **Source**: `src/thegent/verification/tool_safety.py`

WP-25002: Safety Invariants for Tool Composition.
Analyzes chains of tool calls to ensure safety properties are maintained.
Prevents "compositional escalation" where benign tools combined produce unsafe effects.

---

## SafetyViolation

Details of a detected safety invariant violation.

**Inherits from**: `BaseModel`

---

## ToolSafetyChecker

Verifies safety invariants across tool execution chains.

### Methods

#### ToolSafetyChecker.__init__

```python
__init__(self)
```

#### ToolSafetyChecker.analyze_chain

Analyze a sequence of tool calls for safety violations.

```python
analyze_chain(self, tool_chain)
```

#### ToolSafetyChecker.check_pre_flight

Pre-flight check for a proposed tool chain.

```python
check_pre_flight(self, proposed_chain)
```

---

## analyze_chain

Analyze a sequence of tool calls for safety violations.

```python
analyze_chain(self, tool_chain)
```

---

## check_pre_flight

Pre-flight check for a proposed tool chain.

```python
check_pre_flight(self, proposed_chain)
```

---

