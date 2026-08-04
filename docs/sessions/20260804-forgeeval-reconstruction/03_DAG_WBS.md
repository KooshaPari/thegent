# DAG and work breakdown

```text
[provenance boundary]
          |
          v
[versioned contracts] --> [offline unit tests]
          |
          +--> [task catalog fixtures] --> [isolated harness adapter]
          |                                  |
          |                                  v
          +--> [profile collector] ------> [fresh result evidence]
                                             |
                                             v
                                  [optional judge integration]
```

1. Complete the contract foundation and its tests. (this change)
2. Add task-catalog fixtures with source/license provenance.
3. Implement an isolated Forgecode adapter after a clean worktree and harness
   contract are confirmed.
4. Add opt-in OpenRouter judge integration using environment-only credentials.
5. Emit fresh signed result artifacts and, only then, compare candidate models.
