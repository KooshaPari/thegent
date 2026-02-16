import os
from collections.abc import Generator
from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource

# TracerProvider may be vendored differently across SDK versions; import safely
try:
    # Some versions expose TracerProvider at this location
    from opentelemetry.sdk.trace import TracerProvider
except Exception:  # pragma: no cover - fallback for differing SDKs
    # Fallback: import the module and use typing.Any to keep mypy happy
    from typing import Any

    TracerProvider = Any  # type: ignore[assignment]
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

# GenAI Semantic Conventions (standardized)
GEN_AI_SYSTEM = "gen_ai.system"
GEN_AI_REQUEST_MODEL = "gen_ai.request.model"
GEN_AI_USAGE_INPUT_TOKENS = "gen_ai.usage.input_tokens"
GEN_AI_USAGE_OUTPUT_TOKENS = "gen_ai.usage.output_tokens"


def _setup_otel():
    if not isinstance(trace.get_tracer_provider(), TracerProvider):
        resource = Resource.create({"service.name": "thegent"})
        provider = TracerProvider(resource=resource)

        # Enable console export if THGENT_OTEL_CONSOLE is set
        if os.environ.get("THGENT_OTEL_CONSOLE") == "1":
            processor = BatchSpanProcessor(ConsoleSpanExporter())
            provider.add_span_processor(processor)

        trace.set_tracer_provider(provider)


_setup_otel()
tracer = trace.get_tracer("thegent.agents")


@contextmanager
def instrument_genai_call(
    agent_name: str,
    model: str,
    run_id: str | None = None,
    chunk_id: str | None = None,
    system: str | None = None,
) -> Generator[trace.Span, None, None]:
    """Wrap an agent call with OTel spans using GenAI semantic conventions."""
    span_name = f"gen_ai.{agent_name}.call"
    attributes = {
        "thegent.agent.name": agent_name,
        GEN_AI_SYSTEM: system or agent_name,
        GEN_AI_REQUEST_MODEL: model,
    }
    if run_id:
        attributes["thegent.run_id"] = run_id
    if chunk_id:
        attributes["thegent.chunk_id"] = chunk_id

    with tracer.start_as_current_span(
        span_name,
        kind=trace.SpanKind.CLIENT,
        attributes=attributes,
    ) as span:
        yield span


def record_usage(span: trace.Span, input_tokens: int, output_tokens: int) -> None:
    """Record token usage on an active span."""
    span.set_attribute(GEN_AI_USAGE_INPUT_TOKENS, input_tokens)
    span.set_attribute(GEN_AI_USAGE_OUTPUT_TOKENS, output_tokens)
