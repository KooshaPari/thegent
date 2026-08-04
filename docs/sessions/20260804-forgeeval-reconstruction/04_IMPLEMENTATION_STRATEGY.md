# Implementation strategy

The foundation lives in `thegent.forge_eval`, separate from stub legacy
namespaces. Immutable Pydantic models make schemas serializable and safe to
share between a future runner, judge adapter, profiler, and Tracera envelope
bridge. The bundled catalog contains only explicit synthetic fixtures and a
deterministic assertion-packet runner. It records durable local JSONL evidence
but never executes a model, shells out, calls a provider, or emits a judge score.
