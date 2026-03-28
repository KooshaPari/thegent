# Known Issues

1. Child-agent thread capacity
- Runtime refused new child-agent spawns (`max 6`), so execution used direct orchestration.

2. Heuristic false positives/negatives
- Completion detection uses event signatures and may miss edge-case terminal patterns.

3. Correlation uncertainty
- `resolved_elsewhere` uses similarity heuristics and should be treated as high-confidence but not proof.

4. Non-repo temp agent paths
- The remaining temp-agent cwd paths are non-actionable noise and have been filtered from the unresolved queue.
