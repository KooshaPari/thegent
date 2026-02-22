# Merged Fragmented Markdown

## Source: changes/research-maif-artifacts/design.md

# Research: MAIF Action Artifacts — Design

**Status**: Architecture Ready | **Version**: 1.0 | **Date**: 2026-02-18

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Component Design](#2-component-design)
3. [Data Model](#3-data-model)
4. [API Design](#4-api-design)
5. [Integration Points](#5-integration-points)
6. [Error Handling](#6-error-handling)
7. [Performance & Scalability](#7-performance--scalability)
8. [Security Considerations](#8-security-considerations)

---

## 1. System Architecture

### High-Level Block Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    thegent Agent System                     │
└─────────────────────────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
    CodeChange   FileOp        Decision
        │             │             │
        └─────────────┼─────────────┘
                      │
            ┌─────────▼─────────┐
            │ Action Dispatcher │
            └────────┬──────────┘
                     │
            ┌────────▼──────────┐
            │ MAIF Artifact Gen │ ← Generate with timestamp, signature
            └────────┬──────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
   L1 (Memory)  L2 (Disk)    L3/L4 (Supermemory)
   Hot Cache    Warm Cache    Long-term + Immutable
```

### Layers & Responsibilities

| Layer | System | Role |
|-------|--------|------|
| **L1** | In-memory cache (LRU) | Hot artifacts for current session |
| **L2** | Local disk cache | Warm artifacts for replay |
| **L3** | Supermemory Knowledge Graph | Context relationships for replay |
| **L4** | Supermemory Documents API | Immutable artifact storage |

---

## 2. Component Design

### 2.1 MAIF Artifact Generator

**Responsibility**: Create signed artifacts from agent actions.

```python
# thegent/src/thegent/maif/artifact_generator.py

class MAIFArtifactGenerator:
    def __init__(self, signer: SigningKey):
        self.signer = signer
        self.last_hash: dict[str, str] = {}  # session_id -> last_artifact_hash

    def create_artifact(
        self,
        action_type: ActionType,
        agent_id: str,
        session_id: str,
        input_data: bytes,
        output_data: bytes,
        metadata: dict | None = None,
    ) -> MAIFArtifact:
        """Create a signed MAIF artifact with hash chain."""
        prev_hash = self.last_hash.get(session_id, "")

        artifact = MAIFArtifact(
            id=uuid.uuid4().hex,
            timestamp=int(time.time()),
            action_type=action_type,
            agent_id=agent_id,
            session_id=session_id,
            input_hash=self._hash(input_data),
            output_hash=self._hash(output_data),
            previous_hash=prev_hash,
            metadata=metadata or {},
        )

        # Sign the artifact
        artifact_bytes = self._serialize(artifact)
        artifact.signature = self.signer.sign(artifact_bytes).hex()

        # Update hash chain
        self.last_hash[session_id] = self._hash(artifact_bytes)

        return artifact

    def _hash(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def _serialize(self, artifact: MAIFArtifact) -> bytes:
        # Deterministic serialization for hashing
        return json.dumps(
            artifact.model_dump(exclude={"signature"}),
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
```

### 2.2 Hash Chain Validator

**Responsibility**: Verify artifact chains and detect tampering.

```python
# thegent/src/thegent/maif/hash_chain.py

class HashChainValidator:
    def __init__(self):
        self.chain_heads: dict[str, str] = {}  # session_id -> latest_artifact_hash

    def verify_chain(
        self,
        artifacts: list[MAIFArtifact],
    ) -> tuple[bool, str]:
        """Verify integrity of artifact chain."""
        session_id = artifacts[0].session_id

        for i, artifact in enumerate(artifacts):
            # Check previous hash matches
            if i == 0:
                expected_prev = ""
            else:
                expected_prev = self._hash(
                    self._serialize(artifacts[i - 1])
                )

            if artifact.previous_hash != expected_prev:
                return False, f"Artifact {i}: hash chain broken"

            # Verify signature
            if not self._verify_signature(artifact):
                return False, f"Artifact {i}: signature invalid"

        # Update chain head
        self.chain_heads[session_id] = self._hash(
            self._serialize(artifacts[-1])
        )

        return True, "OK"

    def _verify_signature(self, artifact: MAIFArtifact) -> bool:
        """Verify artifact signature."""
        artifact_copy = artifact.model_copy()
        artifact_copy.signature = ""

        message = self._serialize(artifact_copy)
        signature_bytes = bytes.fromhex(artifact.signature)

        # Verify with public key
        return self._public_key.verify(message, signature_bytes)

    def _hash(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def _serialize(self, artifact: MAIFArtifact) -> bytes:
        return json.dumps(
            artifact.model_dump(exclude={"signature"}),
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
```

### 2.3 MAIF Storage (L4 Integration)

**Responsibility**: Persist artifacts to Supermemory L4.

```python
# thegent/src/thegent/maif/storage.py

class MAIFStorage:
    def __init__(self, supermemory_client: SupermemoryClient):
        self.client = supermemory_client
        self.local_cache = {}  # Fallback cache

    async def store(self, artifact: MAIFArtifact) -> str:
        """Store artifact in L4 with fallback to local cache."""
        try:
            # Try L4 first
            doc_id = await self.client.store_document(
                artifact.model_dump(),
                metadata={
                    "session_id": artifact.session_id,
                    "agent_id": artifact.agent_id,
                    "timestamp": artifact.timestamp,
                    "action_type": artifact.action_type.value,
                },
            )
            return doc_id
        except Exception as e:
            logger.warning(f"L4 store failed: {e}, falling back to local cache")
            # Fallback to local cache
            local_id = artifact.id
            self.local_cache[local_id] = artifact
            return local_id

    async def retrieve(\n        self,\n        artifact_id: str,\n    ) -> MAIFArtifact | None:\n        \"\"\"Retrieve artifact from L4 or fallback cache.\"\"\"\n        try:\n            # Try L4 first\n            doc = await self.client.get_document(artifact_id)\n            return MAIFArtifact.model_validate(doc)\n        except Exception:\n            # Fallback to local cache\n            return self.local_cache.get(artifact_id)\n    \n    async def retrieve_by_session(\n        self,\n        session_id: str,\n    ) -> list[MAIFArtifact]:\n        \"\"\"Retrieve all artifacts for a session.\"\"\"\n        try:\n            docs = await self.client.query(\n                f\"session_id:{session_id}\",\n                limit=10000,\n            )\n            return [\n                MAIFArtifact.model_validate(doc)\n                for doc in docs\n            ]\n        except Exception:\n            # Fallback to local cache filtering\n            return [\n                a for a in self.local_cache.values()\n                if a.session_id == session_id\n            ]\n```

### 2.4 Action Hooks

**Responsibility**: Intercept actions and trigger artifact creation.

```bash
# hooks/maif-artifact-hooks.sh

#!/bin/bash

# Hook: PostToolUse for Write/Edit/Delete operations
# Creates MAIF artifacts for file changes

source "$(dirname "$0")/lib/common.sh"

ARTIFACT_GENERATOR="${CLAUDE_PLUGIN_ROOT}/thegent_maif_gen"

main() {
    local tool_name="$1"
    local tool_result="$2"

    case "$tool_name" in
        Write)
            create_artifact "FileOperation" "write" "$tool_result"
            ;;
        Edit)
            create_artifact "FileOperation" "edit" "$tool_result"
            ;;
        Bash)
            # Only for significant system calls
            if is_significant_call "$tool_result"; then
                create_artifact "SystemCall" "bash" "$tool_result"
            fi
            ;;
    esac
}

create_artifact() {
    local action_type="$1"
    local operation="$2"
    local result="$3"

    python3 "$ARTIFACT_GENERATOR" \\
        --action-type "$action_type" \\
        --operation "$operation" \\
        --result "$result" \\
        --session-id "${CLAUDE_SESSION_ID}" \\
        --agent-id "${CLAUDE_AGENT_ID}" \\
        || echo "Artifact creation failed (non-fatal)"
}

is_significant_call() {
    local result="$1"
    # Filter out trivial calls (ls, pwd, etc.)
    [[ "$result" =~ (mkdir|rm|cp|mv|git|pytest|build) ]]
}

main "$@"
```

---

## 3. Data Model

### 3.1 MAIFArtifact Struct

```python
# thegent/src/thegent/maif/models.py

from enum import Enum
from typing import Optional
from pydantic import BaseModel

class ActionType(str, Enum):
    CODE_CHANGE = "code_change"
    FILE_OPERATION = "file_operation"
    SYSTEM_CALL = "system_call"
    DECISION = "decision"
    ERROR = "error"

class MAIFArtifact(BaseModel):
    id: str
    timestamp: int  # Unix epoch seconds
    action_type: ActionType
    agent_id: str
    session_id: str

    input_hash: str  # SHA-256 hex
    output_hash: str  # SHA-256 hex

    signature: str  # Hex-encoded RSA-2048 signature
    previous_hash: str  # Hash of previous artifact

    metadata: dict = {}

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "id": "a1b2c3d4e5f6g7h8i9j0",
                    "timestamp": 1708259184,
                    "action_type": "file_operation",
                    "agent_id": "agent-1",
                    "session_id": "session-xyz",
                    "input_hash": "abc123...",
                    "output_hash": "def456...",
                    "signature": "sig789...",
                    "previous_hash": "prev0ab...",
                    "metadata": {"file": "/path/to/file.py", "bytes": 1024},
                }
            ]
        }
```

### 3.2 Serialization Format

**For Hashing & Signing**: Deterministic JSON (sorted keys, compact spacing)

```json
{
  "action_type": "file_operation",
  "agent_id": "agent-1",
  "id": "a1b2c3d4e5f6g7h8i9j0",
  "input_hash": "abc123...",
  "metadata": {"file": "/path/to/file.py"},
  "output_hash": "def456...",
  "previous_hash": "prev0ab...",
  "session_id": "session-xyz",
  "timestamp": 1708259184
}
```

---

## 4. API Design

### 4.1 Artifact Creation

```python
# thegent_maif_gen CLI or function

async def create_artifact(
    action_type: ActionType,
    agent_id: str,
    session_id: str,
    input_data: bytes,
    output_data: bytes,
    metadata: dict | None = None,
) -> MAIFArtifact:
    """Create and store a MAIF artifact."""
    generator = MAIFArtifactGenerator(signer=get_signing_key())
    artifact = generator.create_artifact(
        action_type, agent_id, session_id, input_data, output_data, metadata
    )

    storage = MAIFStorage(supermemory_client)
    await storage.store(artifact)

    return artifact
```

### 4.2 Chain Verification

```python
async def verify_artifact_chain(
    session_id: str,
) -> tuple[bool, list[str]]:
    """Verify artifact chain for a session. Returns (is_valid, errors)."""
    storage = MAIFStorage(supermemory_client)
    artifacts = await storage.retrieve_by_session(session_id)

    validator = HashChainValidator()
    is_valid, message = validator.verify_chain(artifacts)

    errors = [] if is_valid else [message]
    return is_valid, errors
```

### 4.3 Audit Query

```python
async def query_artifacts(
    session_id: str | None = None,
    agent_id: str | None = None,
    timestamp_start: int | None = None,
    timestamp_end: int | None = None,
    limit: int = 1000,
) -> list[MAIFArtifact]:
    """Query artifacts by filters."""
    storage = MAIFStorage(supermemory_client)

    # Build query (Supermemory syntax)
    filters = []
    if session_id:
        filters.append(f"session_id:{session_id}")
    if agent_id:
        filters.append(f"agent_id:{agent_id}")
    if timestamp_start:
        filters.append(f"timestamp>={timestamp_start}")
    if timestamp_end:
        filters.append(f"timestamp<={timestamp_end}")

    query = " AND ".join(filters)
    return await storage.retrieve_by_query(query, limit)
```

---

## 5. Integration Points

### 5.1 Integration with Supermemory

- **L3 Integration**: Store decision context (relationships) in Knowledge Graph
- **L4 Integration**: Store immutable artifacts in Documents API
- **Metadata**: Use Supermemory metadata for indexing (session_id, agent_id, timestamp, action_type)

### 5.2 Integration with Simulation (WP-4007)

- Replay engine retrieves artifacts from L4
- Reconstructs context from L3
- Determines if replay is deterministic

### 5.3 Integration with Audit System

- Audit queries artifacts by session/agent/time
- Verifies chain integrity
- Generates compliance reports

---

## 6. Error Handling

### 6.1 Artifact Creation Failures

| Failure | Impact | Handling |
|---------|--------|----------|
| Signer unavailable | Critical | Queue for retry, alert |
| Supermemory L4 unavailable | High | Fallback to local cache, circuit breaker |
| Input/output data too large | Medium | Chunk and store separately |
| Hash collision (impossible) | Low | Alert, investigate |

### 6.2 Chain Verification Failures

| Failure | Impact | Handling |
|---------|--------|----------|
| Hash mismatch | High | Quarantine session, alert |
| Signature invalid | Critical | Reject artifact, investigate |
| Missing artifact | Medium | Partial chain verification, log gap |

### 6.3 Storage Failures

| Failure | Impact | Handling |
|---------|--------|----------|
| L4 store fails | Medium | Retry with backoff, fallback to L2 |
| L4 retrieve fails | Low | Fallback to L2 cache |
| Network timeout | Medium | Retry, eventual consistency |

---

## 7. Performance & Scalability

### 7.1 Latency Targets

| Operation | Target | Baseline |
|-----------|--------|----------|
| Artifact creation | <1ms | Hashing: 0.1ms, Signing: 0.5ms, Store: 0.4ms |
| Chain verification (1000 artifacts) | <100ms | Hashing: 50ms, Signature verify: 40ms |
| Artifact retrieval | <100ms | L4 query: 80ms |
| Audit query (10k artifacts) | <500ms | L4 query: 400ms |

### 7.2 Storage Scaling

- **Artifact size**: ~1-5KB (JSON + signature)
- **Monthly artifacts (750k)**: ~1-5GB
- **Annual artifacts (9M)**: ~10-50GB
- **Cost** (Supermemory L4): ~$0.002/artifact → ~$1.5k/month

### 7.3 Caching Strategy

- **L1 (in-memory)**: Last 1000 artifacts per session
- **L2 (disk)**: Last 100k artifacts globally
- **L3 (Supermemory L3)**: Session relationships (indexed)
- **L4 (Supermemory L4)**: All artifacts (replicated, immutable)

---

## 8. Security Considerations

### 8.1 Cryptographic Approach

- **Signing**: RSA-2048 or Ed25519 (NIST-approved)
- **Hashing**: SHA-256 (FIPS-approved)
- **Key Management**: Secrets manager (AWS Secrets Manager, HashiCorp Vault)
- **Key Rotation**: Annual rotation, versioned keys

### 8.2 Tamper Detection

- **Hash Chain**: Sequential links detect any tampering
- **Signature Verification**: Rejects forged artifacts
- **Immutable Storage**: L4 prevents post-hoc modification

### 8.3 Access Control

- **Artifact Access**: Scoped to session owner and auditors
- **Chain Access**: Read-only for verification
- **Supermemory**: Project-scoped access via `x-sm-project` header

### 8.4 Data Privacy

- **PII Handling**: Encrypt sensitive metadata
- **Data Residency**: Ensure L4 respects data residency (EU, US, etc.)
- **Retention**: Archival after 30 days, deletion after 1 year (configurable)

---

## References

- [proposal.md](proposal.md) — Business case and scope
- [tasks.md](tasks.md) — Implementation checklist
- [SESSION_RESEARCH_FRAGMENTS_EXPANDED.md § 4](../SESSION_RESEARCH_FRAGMENTS_EXPANDED.md#4-maif-action-artifacts) — Research foundation

---

## Source: changes/research-maif-artifacts/proposal.md

# Research: MAIF Action Artifacts — Proposal

**Status**: Research Complete | **Priority**: High | **Effort**: 8-12 tool calls
**Work Item**: WP-3002 | **Date**: 2026-02-18

---

## Executive Summary

Implement **MAIF (Multi-Agent Immutable Framework) Action Artifacts**: a system for creating cryptographically signed, immutable records of every significant agent action. Artifacts are stored in Supermemory's L4 (Documents API) with hash chain verification for tamper detection, enabling comprehensive audit trails, deterministic replay for debugging, and compliance verification.

**Business Value**:
- **Auditability**: Complete, tamper-proof record of all agent actions
- **Debuggability**: Deterministic replay to understand decision history
- **Compliance**: Hash chain verification for regulatory requirements
- **Cost**: ~$0.002 per artifact (~$1.5k/month at 750k artifacts)

---

## Problem Statement

### Current State

thegent lacks:
1. **Immutable Action Logs**: Agent actions are not cryptographically signed or tamper-proof
2. **Deterministic Replay**: No way to replay past decisions to understand why they were made
3. **Audit Trail Gaps**: No hash chain to detect tampering
4. **Compliance Gaps**: No non-repudiation or agent identity verification

### Target State

- Every significant agent action creates a signed MAIF artifact
- Hash chain links artifacts chronologically (any tampering breaks chain)
- Artifacts stored in Supermemory L4 (immutable, replicated)
- Replay engine reconstructs decision context from L3 + L4
- Audit system verifies artifact integrity

---

## Scope

### In-Scope

✅ MAIF artifact structure (signature, hash chain, metadata)
✅ Storage in Supermemory L4
✅ Hash chain creation and verification
✅ Artifact creation hooks (CodeChange, FileOperation, SystemCall, Decision, Error)
✅ Basic audit and retrieval APIs
✅ Integration with Supermemory L3/L4

### Out-of-Scope

❌ Advanced forensics (chain repair, multi-signature, threshold signatures)
❌ Replay simulation engine (separate WP-4007)
❌ Compliance-specific extensions (GxP, HIPAA audits)
❌ Performance optimization for extreme scale (>10M artifacts/day)

---

## Design Approach

### High-Level Architecture

```
Agent Actions
    │
    ├─ CodeChange → Artifact creation
    ├─ FileOperation → Artifact creation
    ├─ SystemCall → Artifact creation
    ├─ Decision → Artifact creation
    └─ Error → Artifact creation
    │
    ▼
MAIF Artifact (signed, hash chain)
    │
    ▼
Supermemory L4 (immutable storage)
    │
    ├─ Retrieve for audit
    ├─ Verify hash chain
    └─ Replay decision (via L3 context)
```

### Key Components

| Component | Purpose | Location |
|-----------|---------|----------|
| `MAIFArtifact` struct | Artifact definition | `thegent-maif/src/lib.rs` |
| `MAIFStorage` | L4 storage & retrieval | `thegent/src/maif/storage.py` |
| `HashChain` | Hash chain management | `thegent/src/maif/hash_chain.py` |
| `ArtifactHooks` | Action → artifact conversion | `hooks/maif-artifact-hooks.sh` |
| `AuditAPI` | Artifact querying | `thegent/src/maif/audit.py` |

### Hash Chain Mechanism

```
Artifact 1: hash_chain_1 = H(input₁ || output₁ || prev_hash=0)
    ↓ (signed)
Artifact 2: hash_chain_2 = H(input₂ || output₂ || prev_hash=hash_chain_1)
    ↓ (signed)
Artifact 3: hash_chain_3 = H(input₃ || output₃ || prev_hash=hash_chain_2)
```

Any tampering breaks the chain forward (all subsequent artifacts invalidate).

---

## Success Criteria

- [ ] MAIF artifact structure defined and implemented
- [ ] Cryptographic signing working (RSA-2048 or Ed25519)
- [ ] Hash chain creation and verification functional
- [ ] All significant actions create artifacts (>80% coverage)
- [ ] Supermemory L4 storage operational
- [ ] Artifact retrieval and audit API working
- [ ] Chain integrity verification <10ms latency
- [ ] Artifact creation overhead <1ms per action
- [ ] Zero new security vulnerabilities
- [ ] Comprehensive test coverage (>90%)
- [ ] Integration tests with Supermemory passing

---

## Acceptance Criteria (Functional)

1. **Artifact Creation**: On each significant action (code change, file operation, system call, decision), create and sign MAIF artifact
2. **Hash Chain**: Each artifact references previous artifact's hash; chain is immutable
3. **Storage**: Artifacts persisted in Supermemory L4 with redundancy
4. **Verification**: `verify(artifact, previous_artifact)` returns true iff hash chain valid
5. **Audit**: Retrieve artifacts by session, agent, timestamp; verify chain integrity
6. **Performance**: All operations meet latency targets (<1ms create, <10ms verify)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Hash chain broken (data corruption)** | High | Immutable L4 storage, periodic integrity checks, alerts |
| **Storage failure** | High | Local queue, retry with exponential backoff, fallback to L2 |
| **Signature verification expensive** | Medium | Batch verification, caching, hardware acceleration |
| **Supermemory API unavailable** | Medium | Fallback to local storage, queue for later sync |
| **Replay non-deterministic** | Low | Separate concern (WP-4007); mark non-replayable |

---

## Related Work

**Depends On**:
- WP-5001-SM: Supermemory integration (L4 Documents API)
- WP-5001: Lifecycle loop optimization

**Enables**:
- WP-4007: Simulation & replay engine (uses artifacts)
- WP-AUDIT: Audit system (uses artifact chain)
- WP-COMPLIANCE: Regulatory compliance module

**References**:
- [SESSION_RESEARCH_FRAGMENTS_EXPANDED.md § 4](../SESSION_RESEARCH_FRAGMENTS_EXPANDED.md#4-maif-action-artifacts)
- [Supermemory.ai Documentation](https://supermemory.ai/docs)

---

## References & Context

See [design.md](design.md) for technical architecture and [tasks.md](tasks.md) for implementation checklist.

---

## Source: changes/research-maif-artifacts/tasks.md

---
task_id: research-maif-artifacts
status: in_progress
---

# Research: MAIF Action Artifacts — Implementation Tasks

**Status**: Ready for Implementation | **Effort**: 8-12 tool calls | **Timeline**: 2-3 weeks

---

## Task Breakdown

### Phase 1: Foundation (Tool Calls: 1-3)

#### Task 1.1: Core Data Model

**Goal**: Define and implement MAIF artifact structures
**Effort**: 1-2 tool calls

**Subtasks**:
- [ ] Create `thegent/src/thegent/maif/models.py` with Pydantic models:
  - `ActionType` enum
  - `MAIFArtifact` dataclass
  - Validation rules
- [ ] Define serialization format (deterministic JSON)
- [ ] Add unit tests for model validation

**Acceptance**: `pytest tests/maif/test_models.py` passes with 100% coverage

**Dependencies**: None

---

#### Task 1.2: Cryptographic Foundation

**Goal**: Set up signing and hashing infrastructure
**Effort**: 1-2 tool calls

**Subtasks**:
- [ ] Generate RSA-2048 key pair (or use existing)
- [ ] Create `thegent/src/thegent/maif/crypto.py`:
  - `SigningKey` class (RSA-2048 signing)
  - `VerifyingKey` class (signature verification)
  - Deterministic hash function (SHA-256)
- [ ] Add tests for sign/verify round-trip
- [ ] Set up key storage in secrets manager

**Acceptance**: `pytest tests/maif/test_crypto.py` passes; sign→verify succeeds

**Dependencies**: None

---

### Phase 2: Artifact Generation & Storage (Tool Calls: 4-7)

#### Task 2.1: Artifact Generator

**Goal**: Create MAIF artifacts from actions
**Effort**: 2 tool calls

**Subtasks**:
- [ ] Implement `MAIFArtifactGenerator` class (design § 2.1):
  - `create_artifact()` method
  - Hash chain tracking per session
  - Signature generation
- [ ] Add unit tests:
  - Artifact creation
  - Hash chain correctness
  - Signature verification
- [ ] Performance test: artifact creation <1ms

**Acceptance**: `pytest tests/maif/test_artifact_generator.py` passes; latency <1ms

**Dependencies**: Task 1.1, 1.2

---

#### Task 2.2: Hash Chain Validator

**Goal**: Verify artifact integrity and detect tampering
**Effort**: 1-2 tool calls

**Subtasks**:
- [ ] Implement `HashChainValidator` class (design § 2.2):
  - `verify_chain()` method
  - Signature verification per artifact
  - Chain continuity checking
- [ ] Add unit tests:
  - Valid chain (should pass)
  - Tampered artifacts (should fail)
  - Broken chains (should fail)
  - Signature verification failures
- [ ] Performance test: verify 1000 artifacts <100ms

**Acceptance**: `pytest tests/maif/test_hash_chain.py` passes; latency <100ms

**Dependencies**: Task 1.1, 1.2, 2.1

---

#### Task 2.3: L4 Storage Integration

**Goal**: Persist artifacts to Supermemory Documents API
**Effort**: 2 tool calls

**Subtasks**:
- [ ] Implement `MAIFStorage` class (design § 2.3):
  - `store()` method (L4 with fallback to L2)
  - `retrieve()` method (L4 with fallback)
  - `retrieve_by_session()` method
  - `retrieve_by_query()` method
- [ ] Implement fallback logic:
  - Local in-memory cache (L1)
  - Local disk cache (L2)
  - Circuit breaker (fail after 3 consecutive failures)
- [ ] Add integration tests with Supermemory mock
- [ ] Performance test: store <200ms, retrieve <100ms

**Acceptance**: Integration tests pass; fallback works; latency met

**Dependencies**: Task 2.1, 2.2; Supermemory client available

---

### Phase 3: Hook Integration (Tool Calls: 8-9)

#### Task 3.1: Action Hooks

**Goal**: Intercept actions and create artifacts
**Effort**: 1-2 tool calls

**Subtasks**:
- [ ] Create `hooks/maif-artifact-hooks.sh` (design § 2.4):
  - PostToolUse hook for Write/Edit/Delete
  - Conditional creation for Bash (significant calls only)
  - Filter trivial operations (ls, pwd, echo)
- [ ] Add `thegent_maif_gen` CLI entrypoint
- [ ] Add logging and error handling
- [ ] Test hook integration:
  - Create artifact on Write → verify artifact exists
  - Filter trivial Bash calls → verify no artifacts
  - Supermemory unavailable → verify fallback to L2

**Acceptance**: Hooks fire correctly; artifacts created for all significant actions

**Dependencies**: Task 2.1, 2.2, 2.3

---

### Phase 4: APIs & Queries (Tool Calls: 10-11)

#### Task 4.1: Public APIs

**Goal**: Expose artifact creation and verification APIs
**Effort**: 1-2 tool calls

**Subtasks**:
- [ ] Create `thegent/src/thegent/maif/api.py`:
  - `create_artifact()` function (design § 4.1)
  - `verify_artifact_chain()` function (design § 4.2)
  - `query_artifacts()` function (design § 4.3)
- [ ] Add FastAPI endpoints (if MCP integration required):
  - `POST /maif/artifacts` — Create artifact
  - `GET /maif/artifacts/{id}` — Retrieve artifact
  - `GET /maif/artifacts?session_id=X` — Query by session
  - `POST /maif/verify?session_id=X` — Verify chain
- [ ] Add async/await support throughout
- [ ] Add comprehensive docstrings with examples

**Acceptance**: All endpoints functional; tests pass; 95%+ coverage

**Dependencies**: All Phase 1-3 tasks

---

### Phase 5: Testing & Validation (Tool Calls: 12)

#### Task 5.1: Integration Tests

**Goal**: Validate end-to-end workflow
**Effort**: 1 tool call

**Subtasks**:
- [ ] Create `tests/maif/test_integration.py`:
  - End-to-end: action → artifact creation → storage → retrieval → verification
  - Concurrent artifacts (multiple sessions)
  - Failure scenarios (L4 unavailable, corrupted artifacts)
  - Performance benchmarks (10k artifacts)
- [ ] Create `tests/maif/test_e2e_hooks.py`:
  - Hook integration (Write → artifact)
  - Hook filtering (trivial Bash calls)
  - Error handling (hook failures non-fatal)
- [ ] Load test: 1000 artifacts/second creation rate
- [ ] Verify >90% code coverage

**Acceptance**: All integration tests pass; coverage >90%; load test meets targets

**Dependencies**: All Phase 1-4 tasks

---

## Detailed Subtasks by Component

### Component: `MAIFArtifactGenerator`

| Subtask | Effort | Blocker? |
|---------|--------|----------|
| Create class skeleton | 0.5 calls | No |
| Implement `create_artifact()` | 1 call | No |
| Implement hash chain tracking | 0.5 calls | No |
| Implement signature generation | 1 call | Yes (crypto) |
| Add unit tests | 1 call | No |
| Performance benchmarking | 0.5 calls | No |

**Total**: 4.5 calls

---

### Component: `HashChainValidator`

| Subtask | Effort | Blocker? |
|---------|--------|----------|
| Create class skeleton | 0.5 calls | No |
| Implement `verify_chain()` | 1 call | No |
| Implement signature verification | 1 call | Yes (crypto) |
| Add unit tests (happy path) | 1 call | No |
| Add unit tests (failure cases) | 1 call | No |
| Performance benchmarking | 0.5 calls | No |

**Total**: 5 calls

---

### Component: `MAIFStorage`

| Subtask | Effort | Blocker? |
|---------|--------|----------|
| Create class skeleton | 0.5 calls | No |
| Implement L4 store | 1 call | Yes (Supermemory) |
| Implement L4/L2 fallback | 1 call | No |
| Implement retrieval methods | 1.5 calls | No |
| Add integration tests | 1 call | Yes (Supermemory mock) |
| Performance benchmarking | 0.5 calls | No |

**Total**: 5.5 calls

---

### Component: Hooks & CLI

| Subtask | Effort | Blocker? |
|---------|--------|----------|
| Create `maif-artifact-hooks.sh` | 1 call | No |
| Create `thegent_maif_gen` CLI | 1 call | No |
| Test hook integration | 1 call | No |
| Add filtering logic | 0.5 calls | No |
| Add error handling | 0.5 calls | No |

**Total**: 4 calls

---

### Component: APIs & Documentation

| Subtask | Effort | Blocker? |
|---------|--------|----------|
| Create public API functions | 1 call | No |
| Add FastAPI endpoints (optional) | 1 call | No |
| Add docstrings & examples | 0.5 calls | No |
| Integration tests | 1 call | No |

**Total**: 3.5 calls

---

## Verification Checklist

Before marking WP-3002 complete, verify:

### Code Quality
- [ ] All code passes linters (ruff, type checker)
- [ ] Coverage >90% for core modules
- [ ] No security vulnerabilities (bandit, semgrep)
- [ ] Performance benchmarks meet targets
- [ ] Documentation complete (docstrings, API docs)

### Functional
- [ ] Artifact creation with signature works
- [ ] Hash chain verification works
- [ ] Supermemory L4 storage works
- [ ] Fallback to local cache works
- [ ] All hooks fire correctly
- [ ] APIs functional and well-tested

### Integration
- [ ] Works with Supermemory L3/L4
- [ ] Integration with Action Dispatcher
- [ ] Integration with Lifecycle loop
- [ ] No regressions in existing systems

### Performance
- [ ] Artifact creation <1ms
- [ ] Hash chain verification (1000 artifacts) <100ms
- [ ] Storage latency <200ms
- [ ] Query latency <500ms (10k artifacts)
- [ ] Load test: 1000 artifacts/second sustainable

### Security
- [ ] RSA-2048 keys securely stored
- [ ] Signatures verified correctly
- [ ] No key leakage in logs
- [ ] Tamper detection working
- [ ] No PII in unencrypted metadata

### Operational
- [ ] Monitoring/logging in place
- [ ] Error alerts configured
- [ ] Fallback mechanisms tested
- [ ] Circuit breaker working
- [ ] Runbook created

---

## Related Work Items

**Depends On**:
- WP-5001-SM: Supermemory client library
- WP-5001: Lifecycle loop architecture

**Enables**:
- WP-4007: Simulation & replay engine
- WP-AUDIT: Audit system
- WP-COMPLIANCE: Regulatory compliance

**Preconditions**:
- Supermemory L4 API available
- RSA key pair generated
- CI/CD pipeline functional

---

## Success Metrics

| Metric | Target | Pass/Fail |
|--------|--------|-----------|
| Code coverage | >90% | ☐ |
| Test pass rate | 100% | ☐ |
| Artifact creation latency | <1ms | ☐ |
| Hash chain verification latency | <100ms (1k artifacts) | ☐ |
| Supermemory integration | Functional | ☐ |
| Hook integration | All significant actions captured | ☐ |
| Fallback mechanisms | Working | ☐ |
| Security review | Zero critical findings | ☐ |
| Documentation | Complete | ☐ |

---

## Estimated Effort

**Total Tool Calls**: 8-12 (breakdown above by phase)
**Estimated Timeline**: 2-3 weeks (parallel work possible)
**Blocking Dependencies**: Supermemory L4 API, RSA key setup

---

## Implementation Notes

1. **Start with Phase 1**: Get data model and crypto working first
2. **Test as you go**: Write tests for each component before moving to next
3. **Performance benchmarks**: Run latency tests at end of each phase
4. **Integration testing**: Leave comprehensive integration tests for Phase 5
5. **Documentation**: Add docstrings as you implement; don't defer
6. **Security review**: Get security team review before deployment

---

## References

- [proposal.md](proposal.md) — Requirements and scope
- [design.md](design.md) — Technical architecture
- [SESSION_RESEARCH_FRAGMENTS_EXPANDED.md § 4](../SESSION_RESEARCH_FRAGMENTS_EXPANDED.md#4-maif-action-artifacts) — Research foundation
- Design section § 2 for detailed component specs
- Design section § 4 for API contracts

---
