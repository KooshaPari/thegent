# Plan: research-pareto-routing

## Objective

Implement intelligent task routing that splits work 80/20: low-risk, repetitive tasks to efficient automated loops, high-risk or novel tasks to strategic operator-led loops, with hysteresis damping to prevent thrashing between routing states.

## Approach

1. Survey existing thegent routing heuristics and identify where Pareto splitting applies
2. Define routing policy tiers (automated vs. operator-led) with explicit risk/reward criteria
3. Implement hysteresis damping to avoid oscillation when task classification is ambiguous
4. Prototype the router with configurable thresholds and observable decision logs
5. Validate through simulation replay and production traffic shadowing
