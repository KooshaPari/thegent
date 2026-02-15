#!/usr/bin/env python3
"""
FastMCP Verification Runbook (F1–F6).

Verifies:
  F1  Cursor MCP config: tools visible (tools/list)
  F2  thegent_run with gemini returns output (requires API key)
  F3  thegent_bg returns session_id; thegent_ps lists it (requires API key)
  F4  Progress updates during long thegent_run (Phase 3) — manual
  F5  Resources thegent://session/{id}/logs return content
  F6  Prompts render correctly (prompts/list, prompts/get)
  F11 Health route /health

Usage:
  # Start MCP server first: thegent serve (or process-compose up)
  python scripts/verify-fastmcp.py [--url http://127.0.0.1:3847]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from typing import Any

try:
    import httpx
except ImportError:
    sys.exit(1)

MCP_URL = "http://127.0.0.1:3847"
BASE = f"{MCP_URL}/mcp"


def _rpc(method: str, params: dict[str, Any] | None = None, req_id: int = 1) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params or {}}


def _parse_mcp_response(text: str, req_id: int | None = None) -> dict:
    """Parse MCP response: JSON body or SSE (data: {...})."""
    text = (text or "").strip()
    if not text:
        return {}
    # SSE format: event: message\ndata: {...}
    if text.startswith("event:") or "data:" in text:
        for line in text.split("\n"):
            if line.startswith("data:"):
                try:
                    data = json.loads(line[5:].strip())
                    if req_id is not None:
                        # If we have a request ID, look for a response with that ID
                        if data.get("id") == req_id:
                            return data
                        # Otherwise it might be a notification, skip it
                        continue
                    return data
                except json.JSONDecodeError:
                    continue
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


async def check_health(url: str) -> tuple[bool, str]:
    """F11: Health route."""
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{url}/health", timeout=5.0)
            if r.status_code == 200:
                data = r.json()
                if data.get("status") == "ok":
                    return True, "Health OK"
                return False, f"Health unexpected: {data}"
            return False, f"Health status {r.status_code}"
    except Exception as e:
        return False, str(e)


async def list_tools(url: str) -> tuple[bool, list[str], str]:
    """F1: List tools; return (ok, tool_names, message)."""
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{url}/mcp",
                json=_rpc("tools/list"),
                headers={"Accept": "application/json, text/event-stream"},
                timeout=10.0,
            )
            if r.status_code != 200:
                return False, [], f"tools/list status {r.status_code}"
            data = _parse_mcp_response(r.text, req_id=1)
            if "error" in data:
                return False, [], data["error"].get("message", str(data["error"]))
            tools = data.get("result", {}).get("tools", [])
            names = [t.get("name", "") for t in tools if t.get("name")]
            return True, names, f"Found {len(names)} tools"
    except Exception as e:
        return False, [], str(e)


async def list_prompts(url: str) -> tuple[bool, list[str], str]:
    """F6: List prompts."""
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{url}/mcp",
                json=_rpc("prompts/list"),
                headers={"Accept": "application/json, text/event-stream"},
                timeout=10.0,
            )
            if r.status_code != 200:
                return False, [], f"prompts/list status {r.status_code}"
            data = _parse_mcp_response(r.text, req_id=1)
            if "error" in data:
                return False, [], data["error"].get("message", str(data["error"]))
            prompts = data.get("result", {}).get("prompts", [])
            names = [p.get("name", "") for p in prompts if p.get("name")]
            return True, names, f"Found {len(names)} prompts"
    except Exception as e:
        return False, [], str(e)


async def list_resources(url: str) -> tuple[bool, list[str], str]:
    """List resources (for F5 URI check)."""
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{url}/mcp",
                json=_rpc("resources/list"),
                headers={"Accept": "application/json, text/event-stream"},
                timeout=10.0,
            )
            if r.status_code != 200:
                return False, [], f"resources/list status {r.status_code}"
            data = _parse_mcp_response(r.text, req_id=1)
            if "error" in data:
                return False, [], data["error"].get("message", str(data["error"]))
            resources = data.get("result", {}).get("resources", [])
            uris = [res.get("uri", "") for res in resources if res.get("uri")]
            return True, uris, f"Found {len(uris)} resources"
    except Exception as e:
        return False, [], str(e)


async def call_tool(url: str, name: str, arguments: dict[str, Any]) -> tuple[bool, Any, str]:
    """Call a tool; return (ok, result, message)."""
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{url}/mcp",
                json=_rpc("tools/call", {"name": name, "arguments": arguments}),
                headers={"Accept": "application/json, text/event-stream"},
                timeout=300.0,
            )
            if r.status_code != 200:
                return False, None, f"tools/call status {r.status_code}"
            data = _parse_mcp_response(r.text, req_id=1)
            if "error" in data:
                return False, None, data["error"].get("message", str(data["error"]))
            result = data.get("result", {})
            content = result.get("content", [])
            if isinstance(content, list) and content:
                first = content[0]
                if first.get("type") == "text":
                    text = first.get("text", "")
                    try:
                        parsed = json.loads(text)
                        return True, parsed, "OK"
                    except json.JSONDecodeError:
                        return True, text, "OK"
            return True, result, "OK"
    except Exception as e:
        return False, None, str(e)


async def read_resource(url: str, uri: str) -> tuple[bool, str, str]:
    """Read a resource by URI."""
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{url}/mcp",
                json=_rpc("resources/read", {"uri": uri}),
                headers={"Accept": "application/json, text/event-stream"},
                timeout=10.0,
            )
            if r.status_code != 200:
                return False, "", f"resources/read status {r.status_code}"
            data = _parse_mcp_response(r.text, req_id=1)
            if "error" in data:
                return False, "", data["error"].get("message", str(data["error"]))
            result = data.get("result", {})
            contents = result.get("contents", [])
            if contents:
                first = contents[0]
                text = first.get("text") or (first.get("content", [{}])[0].get("text") if first.get("content") else "")
                if text is not None:
                    return True, str(text), "OK"
            return False, "", "No text content in result"
    except Exception as e:
        return False, "", str(e)


async def run_verification(url: str, skip_api_tests: bool = True) -> dict[str, Any]:
    """Run all checks; return results dict."""
    results: dict[str, Any] = {}
    base = url.rstrip("/")

    # F11 Health
    ok, msg = await check_health(base)
    results["F11_health"] = {"ok": ok, "message": msg}

    # F1 Tools visible
    ok, names, msg = await list_tools(base)
    results["F1_tools_visible"] = {"ok": ok, "message": msg, "count": len(names)}
    required_tools = {"thegent_run", "thegent_bg", "thegent_ps"}
    missing = required_tools - set(names)
    if missing:
        results["F1_tools_visible"]["ok"] = False
        results["F1_tools_visible"]["message"] = f"Missing tools: {missing}"
    else:
        results["F1_tools_visible"]["message"] = f"Required tools present: {required_tools}"

    # F6 Prompts
    ok, names, msg = await list_prompts(base)
    results["F6_prompts"] = {"ok": ok, "message": msg, "count": len(names)}
    required_prompts = {"thegent_run_agent", "thegent_create_wbs", "thegent_bg_task"}
    missing_p = required_prompts - set(names)
    if missing_p:
        results["F6_prompts"]["ok"] = False
        results["F6_prompts"]["message"] = f"Missing prompts: {missing_p}"
    else:
        results["F6_prompts"]["message"] = f"Required prompts present: {required_prompts}"

    # Resources (for F5): session logs resource - verify via resources/read (template URIs may not appear in list)
    ok, uris, msg = await list_resources(base)
    results["F5_resources"] = {"ok": ok, "message": msg, "uris": uris}
    has_logs_in_list = any("session" in u and "logs" in u for u in uris)
    # Direct read test: thegent://session/{id}/logs returns content (or "Session not found" for bad id)
    ok_read, content, _msg_read = await read_resource(base, "thegent://session/__verify_test__/logs")
    has_logs_resource = ok_read or ("session" in (content or "").lower() or "not found" in (content or "").lower())
    results["F5_resources"]["has_session_logs"] = has_logs_in_list or has_logs_resource
    if not (has_logs_in_list or has_logs_resource):
        results["F5_resources"]["ok"] = False
    else:
        results["F5_resources"]["ok"] = True
        results["F5_resources"]["message"] = "session logs resource readable" if has_logs_resource else msg

    # F7: Six core resources (sessions, session/meta, session/logs, dag, agents, models)
    f7_uris = [
        "thegent://sessions",
        "thegent://session/__test__/meta",
        "thegent://session/__test__/logs",
        "thegent://dag",
        "thegent://agents",
        "thegent://models",
    ]
    f7_passed = []
    for uri in f7_uris:
        ok_r, content, _ = await read_resource(base, uri)
        if ok_r and content is not None:
            f7_passed.append(uri.split("?")[0].replace("/__test__", "/{id}"))
    results["F7_core_resources"] = {
        "ok": len(f7_passed) >= 6,
        "message": f"{len(f7_passed)}/6 readable" if len(f7_passed) >= 6 else f"Only {len(f7_passed)}/6: {f7_passed}",
    }

    # F2 thegent_run (requires API key; may skip)
    if not skip_api_tests:
        ok, out, msg = await call_tool(base, "thegent_run", {"agent": "gemini", "prompt": "Say hello in one word."})
        results["F2_thegent_run"] = {"ok": ok, "message": msg, "has_output": bool(out)}
    else:
        results["F2_thegent_run"] = {"ok": None, "message": "Skipped (--no-skip-api to run)", "has_output": None}

    # F3 thegent_bg + thegent_ps (requires API key; may skip)
    if not skip_api_tests:
        ok, out, msg = await call_tool(base, "thegent_bg", {"agent": "gemini", "prompt": "Echo test"})
        session_id = None
        if ok and isinstance(out, dict):
            session_id = out.get("session_id") or out.get("content", {}).get("session_id")
        if not session_id and ok and isinstance(out, str):
            try:
                parsed = json.loads(out)
                session_id = parsed.get("session_id")
            except Exception:
                pass
        results["F3_thegent_bg"] = {"ok": ok, "session_id": session_id, "message": msg}
        if session_id:
            ok2, out2, msg2 = await call_tool(base, "thegent_ps", {})
            results["F3_thegent_ps"] = {"ok": ok2, "lists_session": str(session_id) in str(out2), "message": msg2}
        else:
            results["F3_thegent_ps"] = {"ok": None, "message": "No session_id from bg; skip ps"}
    else:
        results["F3_thegent_bg"] = {"ok": None, "message": "Skipped (--no-skip-api to run)"}
        results["F3_thegent_ps"] = {"ok": None, "message": "Skipped"}

    # F5 Read session logs resource (need a real session_id; use thegent_ps first if available)
    if not skip_api_tests and results.get("F3_thegent_bg", {}).get("session_id"):
        sid = results["F3_thegent_bg"]["session_id"]
        uri = f"thegent://session/{sid}/logs"
        ok, content, msg = await read_resource(base, uri)
        results["F5_read_logs"] = {"ok": ok, "message": msg, "content_length": len(content) if ok else 0}
    else:
        results["F5_read_logs"] = {"ok": None, "message": "Skipped (need session from thegent_bg)"}

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="FastMCP verification runbook (F1–F6)")
    parser.add_argument("--url", default=MCP_URL, help="MCP base URL")
    parser.add_argument("--no-skip-api", action="store_true", help="Run thegent_run/thegent_bg (requires API keys)")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    args = parser.parse_args()

    results = asyncio.run(run_verification(args.url, skip_api_tests=not args.no_skip_api))

    if args.json:
        sys.exit(0 if all(r.get("ok") is not False for r in results.values()) else 1)

    for val in results.values():
        val.get("ok")
        val.get("message", "")
    failed = sum(1 for r in results.values() if r.get("ok") is False)
    if failed:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
