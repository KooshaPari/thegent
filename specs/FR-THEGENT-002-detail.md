# FR-THEGENT-002: Policy Engine

---
id: FR-THEGENT-002
title: Policy Engine
status: specified
priority: P0
category: core
owner: thegent-core-team
source: thegent/specs
---

## Description

Implement a flexible policy engine that allows users to define custom routing constraints and preferences, enforcing privacy requirements, budget limits, and compliance rules.

## User Story

**As a** compliance officer,  
**I want** to define policies that enforce HIPAA-compliant routing,  
**So that** patient data never leaves on-device processing.

## Acceptance Criteria

- [ ] **AC-1**: Policy schema supports privacy, budget, latency, and custom constraints
- [ ] **AC-2**: Policy evaluation completes in < 5ms
- [ ] **AC-3**: Policy violations are logged with full context
- [ ] **AC-4**: Multiple policies can be combined (AND/OR logic)
- [ ] **AC-5**: Policy changes apply without router restart

## Story Points

**8 points** (Constraint satisfaction with multiple policy types)

## Sprint Planning

| Sprint | Deliverable | Story Points |
|--------|-------------|--------------|
| 1 | Policy schema and parser | 3 |
| 2 | Constraint evaluation engine | 3 |
| 3 | Policy composition (AND/OR) | 2 |

## Dependencies

- **FR-THEGENT-001**: Router core (for policy enforcement point)
- **FR-THEGENT-006**: Metrics (for budget tracking)

## Technical Notes

### Policy Schema
```rust
pub struct Policy {
    pub name: String,
    pub constraints: Vec<Constraint>,
    pub action: PolicyAction,
}

pub enum Constraint {
    Privacy { data_classification: DataClass },
    Budget { max_cost_usd: f64, period: Duration },
    Latency { max_ms: u64 },
    Custom { expression: String },
}

pub enum PolicyAction {
    Allow,
    Deny,
    RequireTier(Tier),
    LogOnly,
}
```

### Example Policy
```yaml
policy:
  name: hipaa_compliant
  constraints:
    - type: privacy
      data_classification: phi
  action:
    type: require_tier
    tier: local
```

## Test Plan

```rust
#[trace_to("FR-THEGENT-002")]
#[test]
fn test_hipaa_policy_blocks_cloud_routing() {
    // Given: PHI data classification
    // When: policy evaluated for cloud tier
    // Then: denies routing
}

#[trace_to("FR-THEGENT-002")]
#[test]
fn test_budget_policy_tracks_spend() {
    // Given: $100 daily budget policy
    // When: $90 already spent
    // Then: routes to cheaper tier
}
```

## Work Packages

| WP ID | Description | Owner | Status |
|-------|-------------|-------|--------|
| WP-THEGENT-002-1 | Policy schema definition | @dev-3 | planned |
| WP-THEGENT-002-2 | Constraint evaluator | @dev-2 | planned |
| WP-THEGENT-002-3 | Policy composition logic | @dev-3 | planned |

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Unit tests ≥80% coverage
- [ ] Integration tests with real policies
- [ ] Policy validation tool
- [ ] Documentation (policy DSL, examples)
- [ ] FR annotations in test files

---

**Last Updated:** 2026-04-04  
**Epic:** thegent Router Implementation
