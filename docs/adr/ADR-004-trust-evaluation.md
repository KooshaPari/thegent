# ADR-004: Trust Evaluation and Tier Selection

**Date**: 2026-04-05  
**Status**: Accepted  
**Deciders**: Agent  

## Context

thegent executes scripts from various sources with varying trust levels. We need a systematic approach to evaluate trust and select appropriate sandboxing tiers. The challenge is balancing security with usability—too much isolation frustrates users, too little exposes systems to risk.

## Decision Drivers

- **Security**: Malicious scripts must never escape containment
- **Usability**: Trusted scripts should execute with minimal overhead
- **Auditability**: Every execution decision must be traceable
- **Performance**: Trust evaluation should add <10ms latency
- **Transparency**: Users must understand why a particular tier was selected

## Trust Levels Defined

| Level | Source | Verification | Default Tier | Override |
|-------|--------|--------------|--------------|----------|
| **Trusted** | User-owned, verified git | PGP signature | Tier 1 (bubblewrap) | `--tier=bubblewrap` |
| **Community** | GitHub, stars >100 | Optional signature | Tier 2 (gVisor) | `--tier=gvisor` |
| **Untrusted** | Unknown source | None | Tier 3 (Firecracker) | `--tier=firecracker` |
| **Plugin** | WASM module | WASI signature | Tier 4 (WASM) | `--tier=wasm` |
| **Enterprise** | Compliance required | SOC2 audit | Tier 5 (nanovms) | `--tier=nanovms` |

## Trust Evaluation Algorithm

```rust
pub struct TrustEvaluator {
    community_threshold: u32,
    analyzer: Box<dyn StaticAnalyzer>,
    signature_verifier: Box<dyn SignatureVerifier>,
}

impl TrustEvaluator {
    pub async fn evaluate(&self, source: &Source) -> TrustResult {
        let mut signals = Vec::new();
        
        // 1. Source verification
        signals.push(self.verify_source(source).await?);
        
        // 2. Signature check (if present)
        if let Some(sig) = &source.signature {
            signals.push(self.verify_signature(sig).await?);
        }
        
        // 3. Static analysis
        signals.push(self.run_static_analysis(&source.code).await?);
        
        // 4. Historical reputation
        signals.push(self.check_reputation(&source.url).await?);
        
        // Combine signals into decision
        self.compute_trust_level(signals)
    }
}

pub enum TrustSignal {
    SourceVerified(bool),
    SignatureValid(bool),
    StaticAnalysisClean(bool),
    CommunityReputable(bool),
    PreviouslyExecuted(bool),
}

pub struct TrustResult {
    pub level: TrustLevel,
    pub tier: SandboxTier,
    pub confidence: f32,
    pub signals: Vec<TrustSignal>,
    pub reasoning: String,
}
```

## Tier Selection Matrix

| Trust Level | Network Access | Root Access | Memory Limit | vCPUs | Fallback |
|-------------|----------------|-------------|--------------|-------|----------|
| **Trusted** | Limited | No | 1GB | 1 | Tier 0 |
| **Community** | None | No | 512MB | 1 | Tier 1 |
| **Untrusted** | None | No | 256MB | 1 | Tier 2 |
| **Plugin** | None | No | 128MB | 1 | Tier 3 |
| **Enterprise** | None | No | 2GB | 2 | Tier 3 |

## Override Mechanism

Users can override trust decisions via CLI:

```bash
# Force bubblewrap for untrusted script
thegent execute --tier=bubblewrap --trust-override=community ./script.sh

# Force no sandbox for trusted script  
thegent execute --tier=envfilter --trust-override=trusted ./script.sh

# Record override for audit
thegent execute --tier=firecracker --trust-override=community --audit ./script.sh
```

## Consequences

### Positive
- Systematic, auditable trust decisions
- Automatic tier selection reduces user burden
- Fallback tiers prevent execution failures
- Static analysis catches obvious threats

### Negative
- Adds latency to script execution (~10ms)
- May require additional tooling (signing infrastructure)
- Community threshold is subjective

## Implementation Notes

### Phase 1: Basic Trust Signals
- Source URL analysis
- GitHub star lookup (for github.com URLs)
- Simple pattern matching for dangerous commands

### Phase 2: Static Analysis
- Shell script analysis via shellcheck
- Dangerous pattern detection (rm -rf, curl | sh, etc.)
- Network call analysis

### Phase 3: Signature Verification
- PGP signature verification for trusted sources
- WASI signature for WASM plugins
- Certificate chain validation

### Phase 4: Reputation System
- Historical execution database
- Community reporting mechanism
- Automated threat intelligence

## References

- gVisor security model: https://gvisor.dev/docs/security_guide/
- Firecracker threat model: https://github.com/firecracker-microvm/firecracker/blob/master/docs/design_benchmarks.md
- Static analysis for shell: https://www.shellcheck.net/
- Trust frameworks: https://zero-trust-model.security/

---

*This ADR will be updated as implementation progresses*
