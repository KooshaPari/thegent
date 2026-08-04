# Research

## Repository evidence

- `src/thegent/evals` and `src/thegent/bench` are generated/stub-level modules.
- `benchmark/tbench_validate.py` shells out to Terminal-Bench and therefore is
  unsuitable for a deterministic foundation test.
- The project already uses Pydantic 2 and pytest requirement markers.

## Provenance boundary

The requirements were reconstructed from the identified historical Forge
session. No historical source tree or result file was found in a reachable
current checkout, so this foundation is new work, not a restoration claim.
