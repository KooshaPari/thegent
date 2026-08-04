# Implementation strategy

The foundation lives in `thegent.forge_eval`, separate from stub legacy
namespaces. Immutable Pydantic models make schemas serializable and safe to
share between a future runner, judge adapter, profiler, and Tracera envelope
bridge. The bundled catalog contains only explicit synthetic fixtures and a
deterministic assertion-packet runner. It records durable local JSONL evidence
but never executes a model, shells out, calls a provider, or emits a judge score.

`ConcurrentProfiler` is the adapter-neutral profiling boundary. It receives
versioned tasks and an async executor supplied later by a harness integration.
It uses `time.perf_counter`, an `asyncio.Semaphore`, task-local timeouts, and
stable input-order output. It records only sanitized exception class names,
never executor output or exception messages.
