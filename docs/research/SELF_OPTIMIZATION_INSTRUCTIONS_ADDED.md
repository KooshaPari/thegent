# Self-Optimization Instructions Added to CLAUDE.md

**Date:** 2026-02-17  
**Action:** Added comprehensive self-optimization section to CLAUDE.md

---

## Section Added: "Self-Optimization and Automatic Evolution"

### Key Instructions

1. **Automatic Friction Detection**:
   - Identify friction points while working
   - Document in `docs/research/FRICTION_POINTS_IDENTIFIED.md`
   - Assess impact (High/Medium/Low)

2. **Immediate Delegation**:
   - Don't wait for user to ask
   - Delegate agents to fix friction points immediately
   - Use `thegent free --bg` for parallel fixes

3. **Prioritize Complexity Reduction**:
   - High: Reduce verbosity and complexity
   - Medium: Improve visibility and prevent errors

4. **Session Monitoring**:
   - Use `thegent plan wait-next` to keep session active
   - Use `thegent wait <session_id>` for agent completion
   - Use `thegent plan loop` for continuous work
   - Don't finish conversation when work continues

---

## Examples Added

- Verbose commands → shortcuts
- Multi-step operations → unified commands
- Parameter mismatches → validation
- No visibility → status commands

---

## Integration Points

- **UX/DX Friction Reduction** - Extended with self-optimization
- **Proactive Governance Evolution** - Similar pattern for workflow
- **Agent Memory** - Record friction points via `thegent_memory_add`

---

**Status:** ✅ **CLAUDE.MD UPDATED WITH SELF-OPTIMIZATION INSTRUCTIONS**
