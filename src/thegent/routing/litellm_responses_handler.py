"""LiteLLM Router Responses API handler for Codex CLI compatibility."""

import json
import logging
import os
from typing import Any

from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from starlette.websockets import WebSocket

from thegent.routing.litellm_router import get_litellm_router

_log = logging.getLogger(__name__)


def _responses_input_to_messages(input_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert Responses API input items to Chat Completions messages."""
    messages: list[dict[str, Any]] = []
    for item in input_items:
        if not isinstance(item, dict):
            continue
        if item.get("type") == "message":
            role = item.get("role", "user")
            content = item.get("content")
            if isinstance(content, list):
                parts = []
                for c in content:
                    if isinstance(c, dict) and c.get("type") == "text":
                        parts.append(c.get("text", ""))
                content = "\n".join(parts) if parts else ""
            elif not isinstance(content, str):
                content = str(content) if content else ""
            messages.append({"role": role, "content": content})
    return messages


def _responses_to_chat_completions(body: dict[str, Any]) -> dict[str, Any]:
    """Transform Responses API request to Chat Completions format."""
    input_items = body.get("input", [])
    if not isinstance(input_items, list):
        input_items = []
    messages = _responses_input_to_messages(input_items)
    if not messages:
        messages = [{"role": "user", "content": ""}]
    
    return {
        "model": body.get("model", ""),
        "messages": messages,
        "stream": body.get("stream", False),
        "temperature": body.get("temperature"),
        "max_tokens": body.get("max_output_tokens") or body.get("max_tokens"),
    }


def _chat_completions_to_responses(chunk: dict[str, Any]) -> dict[str, Any] | None:
    """Transform Chat Completions SSE chunk to Responses API format."""
    choices = chunk.get("choices", [])
    if not choices:
        return None
    delta = choices[0].get("delta", {})
    content = delta.get("content", "")
    if not content:
        return None  # Skip empty chunks
    
    return {
        "type": "response.output_item.added",
        "item": {
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": content}],
        },
    }


async def handle_responses_request(request: Request) -> Response:
    """Handle Responses API HTTP POST request via LiteLLM Router."""
    try:
        body = await request.body()
        data = json.loads(body) if body else {}
        
        # Translate Responses API → Chat Completions
        chat_request = _responses_to_chat_completions(data)
        model = chat_request["model"]
        stream = chat_request.get("stream", False)
        
        # Get LiteLLM Router
        router = get_litellm_router()
        
        if stream:
            return await handle_responses_stream(request, chat_request, router)
        else:
            # Non-streaming request
            from litellm import completion
            
            response = completion(
                model=model,
                messages=chat_request["messages"],
                **{k: v for k, v in chat_request.items() if k not in ("model", "messages", "stream")}
            )
            
            # Translate response back to Responses API format
            content = response.choices[0].message.content if response.choices else ""
            responses_data = {
                "output": [
                    {
                        "type": "message",
                        "role": "assistant",
                        "content": [{"type": "text", "text": content}],
                    }
                ]
            }
            
            return Response(
                content=json.dumps(responses_data),
                status_code=200,
                headers={"Content-Type": "application/json"},
            )
            
    except Exception as e:
        _log.error("Error handling Responses API request: %s", e, exc_info=True)
        return Response(
            content=json.dumps({"error": {"message": str(e)}}),
            status_code=500,
            headers={"Content-Type": "application/json"},
        )


async def handle_responses_stream(
    request: Request, chat_request: dict[str, Any], router
) -> StreamingResponse:
    """Handle Responses API streaming request via LiteLLM Router."""
    from litellm import acompletion
    
    async def stream():
        try:
            model = chat_request["model"]
            messages = chat_request["messages"]
            
            async for chunk in router.acompletion(
                model=model,
                messages=messages,
                stream=True,
                **{k: v for k, v in chat_request.items() if k not in ("model", "messages", "stream")}
            ):
                # Translate Chat Completions → Responses API
                responses_event = _chat_completions_to_responses(chunk.model_dump() if hasattr(chunk, 'model_dump') else chunk)
                if responses_event:
                    yield f"data: {json.dumps(responses_event)}\n\n"
            
            # Send completion event
            yield "data: {\"type\": \"response.completed\"}\n\n"
            
        except Exception as e:
            _log.error("Error in Responses API stream: %s", e, exc_info=True)
            yield f"data: {{\"error\": {{\"message\": \"{str(e)}\"}}}}\n\n"
    
    return StreamingResponse(
        stream(),
        status_code=200,
        headers={
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


async def handle_responses_websocket(websocket: WebSocket) -> None:
    """Handle Responses API WebSocket request via LiteLLM Router."""
    import asyncio
    
    await websocket.accept()
    
    try:
        # Receive request
        data = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)
        
        # Translate to Chat Completions
        chat_request = _responses_to_chat_completions(data)
        model = chat_request["model"]
        messages = chat_request["messages"]
        
        # Get router
        router = get_litellm_router()
        
        # Stream response
        async for chunk in router.acompletion(
            model=model,
            messages=messages,
            stream=True,
            **{k: v for k, v in chat_request.items() if k not in ("model", "messages", "stream")}
        ):
            responses_event = _chat_completions_to_responses(chunk.model_dump() if hasattr(chunk, 'model_dump') else chunk)
            if responses_event:
                await websocket.send_json(responses_event)
        
        # Send completion event
        await websocket.send_json({"type": "response.completed"})
        
    except Exception as e:
        _log.error("Error in Responses API WebSocket: %s", e, exc_info=True)
        await websocket.send_json({"error": {"message": str(e)}})
    finally:
        await websocket.close(1000)
