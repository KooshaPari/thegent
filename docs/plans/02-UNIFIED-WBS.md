# 02 — Unified Work Breakdown Structure

> Cross-ref: [00-MASTER-INDEX](./00-MASTER-INDEX.md) | [01-STATE](./01-PROJECT-STATE.md) | [03-DAG](./03-UNIFIED-DAG.md) | [04-REQ](./04-REQUIREMENTS.md) | [10-DISPATCH](./10-SUBAGENT-DISPATCH.md)
> **Multi-agent**: Before picking work, read [WORK_STREAM](../reference/WORK_STREAM.md) (canonical) or [WBS_AGENT_PROGRESS](../reference/WBS_AGENT_PROGRESS.md) — claim items to prevent overlap.

---

## Phase 0-21: Core Infrastructure (COMPLETE)
*(See history for details)*

---

## Phase 22: Universal Context Injection & Agent OS Parity (Wider)

| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-22001 | Dynamic Context Injection (Live Files) | DONE | P1 | — | — | 12-18 | execution.py |
| WP-22002 | Cross-Platform Tool Parity (CLI/TUI) | DONE | P2 | — | — | 15-20 | cli_impl.py |
| WP-22003 | Global Agent State Sync (SyncLoop) | DONE | P2 | WP-15001 | — | 18-24 | discovery/sync.py |

## Phase 23: Quantum-Safe Governance & Hardware-Bound Identity (Deeper)

| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-23001 | PQC (Post-Quantum Crypto) Signatures | DONE | P1 | WP-3002 | — | 20-30 | security/quantum_safe.py |
| WP-23002 | Hardware-Bound Identity (TPM/SecureEnclave) | DONE | P2 | WP-15002 | — | 25-35 | security/hardware_id.py |
| WP-23003 | Attestable Execution Environments (TEE) | DONE | P1 | — | — | 30-45 | governance/tee_check.py |

## Phase 24: Swarm Intelligence & Recursive Self-Improvement (Wider)

| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-24001 | Swarm Consensus Protocol (Byzantine) | DONE | P1 | WP-9003 | — | 25-35 | orchestration/swarm_consensus.py |
| WP-24002 | Recursive Tool Discovery & Adaptation | DONE | P2 | — | — | 20-30 | agents/tool_adapter.py |
| WP-24003 | Swarm Memory Consolidation | DONE | P1 | MEM-AUD-01 | — | 15-20 | orchestration/swarm_memory.py |

## Phase 25: Formal Verification of Autonomous Loops (Deeper)

| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-25001 | Liveness Proofs for Agent Loops | DONE | P1 | WP-18001 | — | 30-40 | verification/liveness.py |
| WP-25002 | Safety Invariants for Tool Composition | DONE | P1 | WP-18002 | — | 25-35 | verification/tool_safety.py |
| WP-25003 | Automated Spec-to-Code Traceability | DONE | P2 | — | — | 15-20 | verification/traceability.py |

## Phase 26: Global Agent Mesh & Economic Exchange (Wider)

| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-26001 | Global Mesh Networking (Tailscale/libp2p) | DONE | P1 | WP-13001 | — | 25-35 | discovery/mesh.py |
| WP-26002 | Agent Micro-Payment Protocol | DONE | P2 | WP-19004 | — | 20-30 | economy/payments.py |
| WP-26003 | Decentralized Reputation System | DONE | P2 | WP-24001 | — | 15-20 | economy/reputation.py |

## Phase 27: Neural-Symbolic Synthesis & ZK-Governance (Deeper)

| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-27001 | Neural-Symbolic Program Synthesis | DONE | P1 | WP-20002 | — | 30-45 | agents/synthesis.py |
| WP-27002 | ZK-Proofs for Context Integrity | DONE | P1 | WP-23001 | — | 35-50 | verification/zkp.py |
| WP-27003 | Formal Verification of Schema Evolution | DONE | P2 | WP-18004 | — | 20-25 | verification/schema_formal.py |

## Phase 28: Adversarial Resilience & Autonomous Red-Teaming (Wider)

| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-28001 | Autonomous Red-Teaming Agent | DONE | P1 | — | — | 25-35 | agents/red_team.py |
| WP-28002 | Semantic Firewall for Model Output | DONE | P1 | WP-3001 | — | 20-30 | governance/semantic_firewall.py |
| WP-28003 | Poison Pill Detection in Swarm Memory | PENDING | P2 | WP-24003 | — | 18-24 | orchestration/swarm_memory.py |

## Phase 29: Ethical Alignment & Value-Lock (Deeper)

| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-29001 | Value-Lock (Immutable Ethical Constraints) | DONE | P1 | WP-20004 | — | 30-40 | governance/value_lock.py |
| WP-29002 | Societal Impact Simulation | PENDING | P2 | WP-14001 | — | 20-30 | planning/impact_sim.py |
| WP-29003 | Human-in-the-Loop Moral Arbitration | DONE | P1 | — | — | 15-25 | ux/moral_ui.py |

## Phase 30: Global Agent Market & Liquidity (Wider)

| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-30001 | Agent Service Registry (Global) | DONE | P1 | WP-11001 | — | 15-20 | discovery/market.py |
| WP-30002 | Task Bidding & Auction Protocol | DONE | P2 | WP-30001 | — | 12-18 | discovery/market.py |
| WP-30003 | Micro-payment Settlement Bridge | DONE | P2 | WP-26002 | — | 18-24 | economy/payments.py |

## Phase 31: Autonomous Infrastructure & Edge (Deeper)

| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-31001 | Self-Provisioning Infra Bridge | DONE | P1 | — | — | 20-30 | infra/provisioner.py |
| WP-31002 | Containerized Agent Sandboxes (Wasm) | DONE | P1 | — | — | 25-35 | infra/sandbox.py |
| WP-31003 | Infra Drift Self-Correction Loop | DONE | P2 | WP-31001 | — | 15-20 | infra/drift_corrector.py |

## Phase 32: Bio-Digital Depth & Sensory Context (Deeper)

| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-32001 | Sensory Context Bridge (Audio/Video) | PENDING | P2 | — | — | 25-35 | context/sensory.py |
| WP-32002 | Bio-Digital Confidence Calibration | PENDING | P3 | WP-4008 | — | 30-40 | agents/bio_feedback.py |
| WP-32003 | Homomorphic Encryption for Context | DONE | P2 | WP-21002 | — | 35-45 | security/homomorphic.py |

## Phase 33: Universal Black-Box Agent Control (UBBAC) (Deeper)

| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-33001 | Universal External Proxy (Donut Bridge) | DONE | P1 | — | — | 25-35 | agents/black_box_proxy.py |
| WP-33002 | Behavioral Steering via Semantic Injection | DONE | P1 | — | — | 20-30 | governance/control_vectors.py |
| WP-33003 | External Policy Enforcement (The Cage) | DONE | P1 | — | — | 30-40 | infra/cage.py |
| WP-33004 | Black-Box Probing & Fingerprinting | DONE | P2 | — | — | 15-20 | agents/probing.py |

---

## Phase 34: Inter-Galactic Agent Networking & Delay-Tolerant Control (Wider)

| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-34001 | Delay-Tolerant Networking (DTN) Bridge | DONE | P3 | WP-26001 | — | 30-45 | discovery/galactic.py |
| WP-34002 | Asynchronous State Reconciler (Long Lag) | DONE | P3 | WP-34001 | — | 25-35 | discovery/galactic.py |
| WP-34003 | Light-Speed Compensation Planning | PENDING | P3 | WP-14001 | — | 20-30 | planning/galactic_sim.py |

## Phase 35: Planetary-Scale Resource Scheduling (Wider)

| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-35001 | Global Compute Arbitrage Engine | DONE | P2 | WP-30001 | — | 25-35 | economy/arbitrage.py |
| WP-35002 | Cross-Region Latency-Aware Scheduling | PENDING | P2 | WP-31001 | — | 20-30 | infra/scheduler.py |
| WP-35003 | Geo-Distributed Data Sovereignty Guard | DONE | P1 | WP-19001 | — | 15-25 | security/geo_guard.py |

## Phase 36: Bio-Digital & Molecular Storage (Deeper)

| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-36001 | Simulated DNA Data Encoding Bridge | DONE | P3 | — | — | 40-60 | context/dna_storage.py |
| WP-36002 | Biological Feedback Confidence Injection | PENDING | P3 | WP-32002 | — | 30-40 | agents/bio_digital.py |
| WP-36003 | Molecular Computing Simulation sandbox | PENDING | P3 | WP-31002 | — | 50-70 | infra/molecular.py |

## Phase 37: Recursive Meta-Cognition & Agent Autopoiesis (Deeper)

| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-37001 | Self-Authoring Agent Architectures | DONE | P1 | WP-27001 | — | 60-100 | agents/autopoiesis.py |
| WP-37002 | Recursive Cognitive Refactoring | DONE | P1 | WP-20003 | — | 45-75 | agents/refactoring.py |
| WP-37003 | Infinite Plan Evolution Loop | DONE | P1 | WP-18004 | — | 50-80 | planning/evolution.py |

---

## Phase 38: Multi-Verse Plan Branching & Counterfactuals (Wider)

| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-38001 | Alternate Reality Simulator (Plan Forks) | DONE | P2 | WP-14001 | — | 40-60 | planning/multiverse.py |
| WP-38002 | Counterfactual Impact Analysis | DONE | P2 | WP-38001 | — | 30-45 | planning/multiverse.py |
| WP-38003 | Parallel Timeline State Merging | PENDING | P2 | WP-38001 | — | 50-70 | orchestration/timeline_merge.py |

## Phase 39: Singularity Gates & Formal Super-Alignment (Deeper)

| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-39001 | Super-intelligence Safety Break (Kill-Switch) | DONE | P1 | WP-20004 | — | 25-35 | governance/kill_switch.py |
| WP-39002 | Formal Proof of Ethical Alignment | DONE | P1 | WP-18001 | — | 60-90 | verification/ethics_proof.py |
| WP-39003 | Recursive Reward Modeling Optimization | DONE | P2 | WP-16003 | — | 45-65 | agents/reward_model.py |

## Phase 40: Nano-Swarm & Physical World Bridging (Wider)

| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-40001 | IoT/Robotics Command Bridge | DONE | P2 | — | — | 35-50 | integration/physical.py |
| WP-40002 | Distributed Sensor Mesh Orchestration | PENDING | P2 | WP-26001 | — | 40-60 | infra/sensor_mesh.py |
| WP-40003 | Edge-Agent Low-Power Synchronization | DONE | P2 | WP-34001 | — | 30-45 | discovery/edge_sync.py |

## Phase 41: Trans-Human Agent Symbiosis (Deeper)

| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-41001 | Neural-Link Cognitive Offloading (Sim) | PENDING | P3 | WP-36002 | — | 70-100 | context/neural_sim.py |
| WP-41002 | Human-Agent Co-Consciousness Interface | PENDING | P3 | — | — | 80-120 | ux/symbiosis.py |
| WP-41003 | Legacy Identity Preservation (Digital Twin) | DONE | P2 | WP-15002 | — | 50-80 | agents/digital_twin.py |

---

## Phase 42: Dysonian Compute & Stellar Energy Management (Deeper)

| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-42001 | Stellar Energy Harvesting Bridge (Sim) | PENDING | P3 | WP-31001 | — | 100-150 | infra/dyson.py |
| WP-42002 | Matrioshka Brain Resource Allocation | PENDING | P3 | WP-35001 | — | 120-180 | economy/stellar.py |
| WP-42003 | Cold-Storage Data Archiving (Planet-Scale) | PENDING | P3 | WP-36001 | — | 80-120 | context/planetary.py |

## Phase 43: Time-Dilation Awareness & Relativistic Scheduling (Deeper)

| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-43001 | Relativistic Clock Sync Protocol | DONE | P3 | WP-34001 | — | 60-90 | discovery/relativistic.py |
| WP-43002 | Gravity-Aware Task Scheduling | PENDING | P3 | WP-14001 | — | 70-100 | planning/gravity.py |
| WP-43003 | Inter-Stellar Handoff Compensation | DONE | P3 | WP-34002 | — | 50-80 | discovery/relativistic.py |

## Phase 44: Information Life-forms & Substrate Independence (Wider)

| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-44001 | Pure Information Persona Encoding | DONE | P2 | WP-41003 | — | 90-130 | agents/information_life.py |
| WP-44002 | Cross-Substrate Migration Logic | PENDING | P2 | WP-23002 | — | 100-150 | agents/migration.py |
| WP-44003 | Virtualized Consciousness Bridge | PENDING | P3 | WP-41002 | — | 150-200 | ux/virtual_consciousness.py |

## Phase 45: Universal Omega-Governance (Deeper)

| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-45001 | Entropy-Minimizing Execution Loop | DONE | P1 | WP-37003 | — | 200-300 | planning/omega.py |
| WP-45002 | Universal Safety Invariants (Omega) | DONE | P1 | WP-39002 | — | 250-400 | verification/omega_safety.py |
| WP-45003 | Final State Consensus Protocol | DONE | P1 | WP-24001 | — | 300-500 | orchestration/omega_consensus.py |

---

## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog (claim items here)
- [00-MASTER-INDEX.md](./00-MASTER-INDEX.md) — plan index
