# Plan for Next 50 Work Stream Items

Generated: 2026-02-18

## Summary
- Total available items: 66
- Ready items: 46
- Blocked items: 20
- Selected for plan: 50 items

## Items by Category

### Developer Experience (2 items)

1. **dx-improve-file-reading-efficiency** (P2)
   - Use offset/limit for targeted file reading
   - Source: FRICTION_LOG.md

2. **ux-improve-error-messages** (P2)
   - Make error messages actionable with suggested fixes
   - Source: FRICTION_LOG.md


### Documentation (7 items)

1. **vitepress-playwright-setup** (P1)
   - Set up Playwright for browser recordings
   - Source: VITEPRESS_RICH_DOCUMENTATION_IMPLEMENTATION_PLAN.md

2. **docgen-code-annotation** (P2)
   - Implement code annotation component
   - Source: DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md

3. **docgen-openapi** (P2)
   - Add OpenAPI/Swagger integration
   - Source: DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md

4. **docgen-versioning** (P2)
   - Implement version switcher
   - Source: DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md

5. **docgen-analytics** (P2)
   - Add Google Analytics / Plausible integration
   - Source: DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md

6. **docgen-watch-mode** (P2)
   - Implement watch mode for auto-regeneration
   - Source: DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md

7. **docgen-code-validator** (P2)
   - Code example validation
   - Source: DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md


### Governance/Cost (3 items)

1. **gov-wp-3008-dlq** (P2)
   - EscalationQueue + DLQ integration (deferred)
   - Source: GOVERNANCE_WP_GAPS.md

2. **cost-wp-y4** (P2)
   - Per-run cost aggregation (orchestration/cost.py)
   - Source: COST_ROUTING_DEFERRED.md

3. **gov-wp-3003-enhance** (P3)
   - Emit governance.override.expired (optional)
   - Source: GOVERNANCE_WP_GAPS.md


### Implementation (1 items)

1. **impl-concurrency-cli** (P1)
   - Add CLI command to view/adjust concurrency limit (thegent concurrency show/set)
   - Source: This session


### Phases/Scratch (5 items)

1. **phase13-compliance-profile** (P2)
   - Compliance profile mapping (EU-AI-ACT, US-SEC, SOX, GDPR)
   - Source: phase13-compliance-profile-mapping.md
   - Depends: WP-13002

2. **phase13-policy-federation** (P2)
   - Policy federation surface map (FederatedPolicyEngine)
   - Source: phase13-policy-federation-surface-map.md

3. **phase14-cost-sensing** (P2)
   - Cost sensing and learning test matrix (AL-001–AL-006)
   - Source: phase14-cost-sensing-test-matrix.md
   - Depends: WP-5003

4. **phase14-autonomous-learning** (P2)
   - Autonomous learning surface map
   - Source: phase14-autonomous-learning-surface-map.md
   - Depends: WP-5003

5. **phase15-enterprise-lifecycle** (P2)
   - Enterprise lifecycle and compliance surface map
   - Source: phase15-enterprise-lifecycle-surface-map.md


### Research (10 items)

1. **research-remote-compute-impl** (P2)
   - Implement thegent run --remote (Phase 4 compute offload)
   - Source: CONVERSATION_DUMP_2026-02-16.md §4

2. **research-library-diskcache** (P2)
   - Replace scrapers cache with diskcache (1 file)
   - Source: PACKAGE_REPLACEMENT_IMPLEMENTATION_PLAN.md
   - Depends: ✅ Complete

3. **research-library-psutil** (P2)
   - Add psutil for resource monitoring (2 files)
   - Source: PACKAGE_REPLACEMENT_IMPLEMENTATION_PLAN.md
   - Depends: ✅ Complete

4. **research-phase13-cost-sensitivity** (P2)
   - Cost-sensitivity experiment framework
   - Source: PHASE_DOCUMENTS_EXPANDED.md
   - Depends: WP-5003, research-economic-governance

5. **research-phase14-autonomous-learning** (P2)
   - Autonomous learning surface map
   - Source: PHASE_DOCUMENTS_EXPANDED.md
   - Depends: WP-5001, research-pareto-routing

6. **research-governance-escalation-dlq** (P2)
   - Integrate escalation queue with DLQ
   - Source: GOVERNANCE_WP_GAPS_EXPANDED.md
   - Depends: WP-3008, WP-2002

7. **research-always-write-dumps** (P2)
   - CLAUDE.md: always write conversation dumps to docs/
   - Source: CONVERSATION_DUMP_2026-02-16.md §6

8. **research-agent-hierarchy-implementation** (P2)
   - Implement AgentHierarchyManager (Phase 1)
   - Source: AGENT_HIERARCHY_AND_TEAM_STRUCTURE.md
   - Depends: research-agent-hierarchy-mvp

9. **research-library-md5-sha256** (P3)
   - Replace md5 with sha256 (1 file)
   - Source: PACKAGE_REPLACEMENT_IMPLEMENTATION_PLAN.md
   - Depends: ✅ Complete

10. **research-library-tomlkit** (P3)
   - Add tomlkit to dependencies
   - Source: PACKAGE_REPLACEMENT_IMPLEMENTATION_PLAN.md
   - Depends: ✅ Complete


### Work Packages (18 items)

1. **WP-28003** (P2)
   - Poison Pill Detection in Swarm Memory
   - Source: 02-UNIFIED-WBS.md
   - Depends: WP-24003

2. **WP-29002** (P2)
   - Societal Impact Simulation
   - Source: 02-UNIFIED-WBS.md
   - Depends: WP-14001

3. **WP-32001** (P2)
   - Sensory Context Bridge (Audio/Video)
   - Source: 02-UNIFIED-WBS.md

4. **WP-35002** (P2)
   - Cross-Region Latency-Aware Scheduling
   - Source: 02-UNIFIED-WBS.md
   - Depends: WP-31001

5. **WP-38003** (P2)
   - Parallel Timeline State Merging
   - Source: 02-UNIFIED-WBS.md
   - Depends: WP-38001

6. **WP-40002** (P2)
   - Distributed Sensor Mesh Orchestration
   - Source: 02-UNIFIED-WBS.md
   - Depends: WP-26001

7. **WP-44002** (P2)
   - Cross-Substrate Migration Logic
   - Source: 02-UNIFIED-WBS.md
   - Depends: WP-23002

8. **WP-32002** (P3)
   - Bio-Digital Confidence Calibration
   - Source: 02-UNIFIED-WBS.md
   - Depends: WP-4008

9. **WP-34003** (P3)
   - Light-Speed Compensation Planning
   - Source: 02-UNIFIED-WBS.md
   - Depends: WP-14001

10. **WP-36002** (P3)
   - Biological Feedback Confidence Injection
   - Source: 02-UNIFIED-WBS.md
   - Depends: WP-32002

11. **WP-36003** (P3)
   - Molecular Computing Simulation sandbox
   - Source: 02-UNIFIED-WBS.md
   - Depends: WP-31002

12. **WP-41001** (P3)
   - Neural-Link Cognitive Offloading (Sim)
   - Source: 02-UNIFIED-WBS.md
   - Depends: WP-36002

13. **WP-41002** (P3)
   - Human-Agent Co-Consciousness Interface
   - Source: 02-UNIFIED-WBS.md

14. **WP-42001** (P3)
   - Stellar Energy Harvesting Bridge (Sim)
   - Source: 02-UNIFIED-WBS.md
   - Depends: WP-31001

15. **WP-42002** (P3)
   - Matrioshka Brain Resource Allocation
   - Source: 02-UNIFIED-WBS.md
   - Depends: WP-35001

16. **WP-42003** (P3)
   - Cold-Storage Data Archiving (Planet-Scale)
   - Source: 02-UNIFIED-WBS.md
   - Depends: WP-36001

17. **WP-43002** (P3)
   - Gravity-Aware Task Scheduling
   - Source: 02-UNIFIED-WBS.md
   - Depends: WP-14001

18. **WP-44003** (P3)
   - Virtualized Consciousness Bridge
   - Source: 02-UNIFIED-WBS.md
   - Depends: WP-41002


## Detailed Breakdown

### Priority Distribution
- P1: 2 items
- P2: 30 items
- P3: 14 items

### Recommended Order

1. Start with P1 items in Implementation and Developer Experience categories
2. Follow with Documentation and Research items
3. Complete Governance/Cost and Work Packages
4. Finish with Phases/Scratch items

### Estimated Effort

- Implementation items: 2-4 hours each
- Research items: 1-2 hours each
- Documentation items: 1-3 hours each
- Developer Experience items: 1-2 hours each
- Work Packages: 3-6 hours each

