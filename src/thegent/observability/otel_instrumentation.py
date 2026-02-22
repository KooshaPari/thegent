from collections.abc import Callable, Generator
from contextlib import contextmanager
from functools import wraps
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

# GenAI Semantic Conventions (standardized)
GEN_AI_SYSTEM = "gen_ai.system"
GEN_AI_REQUEST_MODEL = "gen_ai.request.model"
GEN_AI_USAGE_INPUT_TOKENS = "gen_ai.usage.input_tokens"
GEN_AI_USAGE_OUTPUT_TOKENS = "gen_ai.usage.output_tokens"

# thegent-specific span attribute name constants
THEGENT_AGENT = "thegent.agent"
THEGENT_CONFIDENCE = "thegent.confidence"
THEGENT_EXIT_CODE = "thegent.exit_code"
THEGENT_LANE = "thegent.lane"
THEGENT_MODEL = "thegent.model"
THEGENT_PROVIDER = "thegent.provider"
THEGENT_SESSION_ID = "thegent.session_id"


def _setup_otel():
    if not isinstance(trace.get_tracer_provider(), TracerProvider):
        resource = Resource.create({"service.name": "thegent"})
        provider = TracerProvider(resource=resource)

        # Enable console export if otel_console is set
        from thegent.config import ThegentSettings

        if ThegentSettings().otel_console:
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


@contextmanager
def instrument_run_bg_status(
    session_id: str,
    agent: str | None = None,
    lane: str | None = None,
    provider: str | None = None,
    model: str | None = None,
) -> Generator[trace.Span, None, None]:
    """Wrap a background run status update with OTel spans."""
    span_name = "thegent.run_bg_status"
    attributes: dict[str, Any] = {THEGENT_SESSION_ID: session_id}
    if agent is not None:
        attributes[THEGENT_AGENT] = agent
    if lane is not None:
        attributes[THEGENT_LANE] = lane
    if provider is not None:
        attributes[THEGENT_PROVIDER] = provider
    if model is not None:
        attributes[THEGENT_MODEL] = model

    with tracer.start_as_current_span(
        span_name,
        kind=trace.SpanKind.INTERNAL,
        attributes=attributes,
    ) as span:
        yield span


def instrument_run_bg_status_decorator(
    session_id: str,
    agent: str | None = None,
    lane: str | None = None,
    provider: str | None = None,
    model: str | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator that wraps a function with instrument_run_bg_status instrumentation."""

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with instrument_run_bg_status(
                session_id=session_id,
                agent=agent,
                lane=lane,
                provider=provider,
                model=model,
            ):
                return fn(*args, **kwargs)

        return wrapper

    return decorator
