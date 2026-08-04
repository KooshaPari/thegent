# Implementation strategy

The foundation lives in `thegent.forge_eval`, separate from stub legacy
namespaces. Immutable Pydantic models make schemas serializable and safe to
share between a future runner, judge adapter, profiler, and Tracera envelope
bridge. This change does not introduce a runner because doing so would risk
mixing external execution with unverified historical assumptions.
