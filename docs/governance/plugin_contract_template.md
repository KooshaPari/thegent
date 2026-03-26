# Plugin / extension contract template

**Purpose:** Hexagonal and polyrepo systems that expose **plugins** or **adapters** must publish a **versioned contract** before shipping multiple implementations.

Use this as a checklist when adding a new extension point. Align with `plugin_architecture_governance.md` (thegent) and ADR-006 patterns where applicable.

---

## 1. Identity

| Field | Value |
|-------|--------|
| **Extension point name** | e.g. `auth.Provider`, `cache.Backend` |
| **Contract version** | SemVer: `1.0.0` |
| **Stability** | `experimental` \| `beta` \| `stable` |

## 2. Wire / API surface

- **Input schema:** JSON Schema, Protobuf, OpenAPI fragment, or language types — **one source of truth** (SDD).
- **Output schema:** Same.
- **Error model:** Stable error codes + optional detail; no free-form strings as the only contract.

## 3. Behavioral invariants

- List **SHALL** / **MUST NOT** rules (idempotency, timeouts, max payload size).
- **Compatibility:** additive changes = minor bump; breaking = major bump.

## 4. Lifecycle

- **Registration:** how a plugin registers (CLI flag, manifest, compile-time, dynamic load).
- **Discovery:** list/describe command or registry endpoint.
- **Deprecation:** minimum notice period + migration path.

## 5. Security & isolation

- Trust boundary (same process, subprocess, WASM).
- Secret handling (no logging tokens).
- Resource limits (CPU, memory, network).

## 6. Testing requirements

- Contract tests against **golden** inputs/outputs.
- At least one **fake** / **in-memory** implementation for CI.

## 7. Version matrix

| Contract version | Min host version | Notes |
|------------------|------------------|--------|
| 1.0.0 | app ≥ x.y | |

---

**Handoff:** Link this section from the repo `README.md` or `docs/architecture/` and add an ADR if the extension point is org-wide.
