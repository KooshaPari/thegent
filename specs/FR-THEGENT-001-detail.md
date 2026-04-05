# FR-THEGENT-001: Router Core Implementation

---
id: FR-THEGENT-001
title: Router Core Implementation
status: specified
priority: P0
category: core
owner: thegent-core-team
source: thegent/specs
---

## Description

Implement the core request routing engine for thegent that intelligently distributes ML inference requests across local, edge, and cloud tiers based on latency, cost, and policy constraints.

## User Story

**As a** developer running ML inference workloads,  
**I want** requests to automatically route to the optimal execution tier,  
**So that** I get the best balance of latency, cost, and privacy without manual configuration.

## Acceptance Criteria

- [ ] **AC-1**: Router can classify requests by latency requirements (real-time, batch, background)
- [ ] **AC-2**: Router maintains tier capacity awareness (GPU availability, queue depth)
- [ ] **AC-3**: Router makes routing decisions in < 10ms
- [ ] **AC-4**: Router supports hot-reloading of routing configuration
- [ ] **AC-5**: Router provides decision rationale in response headers

## Story Points

**8 points** (Complex routing logic with multiple constraints)

## Sprint Planning

| Sprint | Deliverable | Story Points |
|--------|-------------|--------------|
| 1 | Request classification engine | 3 |
| 2 | Tier capacity tracking | 3 |
| 3 | Routing decision engine | 2 |

## Dependencies

- **FR-THEGENT-005**: Health checks (for tier availability)
- **FR-THEGENT-006**: Metrics collection (for capacity tracking)
- **FR-THEGENT-002**: Policy engine (for policy-based routing)

## Technical Notes

### Architecture
```rust
pub struct Router {
    tier_manager: TierManager,
    policy_engine: PolicyEngine,
    metrics: Arc<MetricsCollector>,
}

impl Router {
    pub async fn route(&self, request: InferenceRequest) -> RouteDecision {
        // Classification
        let latency_class = self.classify_latency(&request);
        
        // Tier selection
        let available_tiers = self.tier_manager.available_tiers().await;
        let optimal_tier = self.select_optimal_tier(latency_class, available_tiers);
        
        // Decision with rationale
        RouteDecision::new(optimal_tier).with_rationale("latency_class: P0, tier_capacity: 80%")
    }
}
```

### Configuration
```yaml
router:
  classification:
    realtime_ms: 100
    batch_ms: 5000
    background_ms: 60000
  
  tiers:
    local:
      priority: 1
      max_latency_ms: 50
    edge:
      priority: 2
      max_latency_ms: 500
    cloud:
      priority: 3
      max_latency_ms: 2000
```

## Test Plan

```rust
#[cfg(test)]
mod router_tests {
    #[trace_to("FR-THEGENT-001")]
    #[test]
    fn test_realtime_request_routes_to_local() {
        // Given: realtime latency requirement
        // When: route decision made
        // Then: selects local tier
    }
    
    #[trace_to("FR-THEGENT-001")]
    #[test]
    fn test_batch_request_considers_cost() {
        // Given: batch workload
        // When: multiple tiers available
        // Then: selects cheapest capable tier
    }
}
```

## Work Packages

| WP ID | Description | Owner | Status |
|-------|-------------|-------|--------|
| WP-THEGENT-001-1 | Request classification | @dev-1 | planned |
| WP-THEGENT-001-2 | Tier capacity tracking | @dev-2 | planned |
| WP-THEGENT-001-3 | Routing decision engine | @dev-1 | planned |

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Unit tests ≥80% coverage
- [ ] Integration tests with all 3 tiers
- [ ] Performance benchmark < 10ms decision time
- [ ] Documentation (API, architecture)
- [ ] FR annotations in test files
- [ ] Security review (input validation)

---

**Last Updated:** 2026-04-04  
**Epic:** thegent Router Implementation
