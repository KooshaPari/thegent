# README

Source: docs/specs/skills/README.md

---

# Skills Domain Technical Specification

## Overview

Skills are reusable agent capabilities that can be discovered, loaded, and composed.

## Components

### Skill Types

| Type | Purpose | Implementation |
|------|---------|----------------|
| Terminal | Shell operations | `skills/terminal.py` |
| Discovery | Finding capabilities | `skills/discovery.py` |
| Scratchpad | Temporary storage | `skills/scratchpad.py` |
| Human | Human-in-loop | `skills/human.py` |

### Skill Loading

```
class SkillLoader:
    def discover(self) -> list[Skill]: ...
    def load(self, name: str) -> Skill: ...
    def validate(self, skill: Skill) -> bool: ...
```

## Discovery

- Dynamic skill detection
- Capability matching
- Version compatibility

## Performance

| Metric | Target |
|--------|--------|
| Load time | <50ms |
| Discovery | <100ms |