#!/usr/bin/env python3
"""Provider smoke matrix with CLIProxy preflight/startup.

Runs a cheapest-like model probe per provider against /v1/responses.
If CLIProxy is not reachable, this script starts it with the configured binary/config.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import httpx


def _score_model(model_id: str) -> tuple[int, int, str]:
    s = model_id.lower()
    pri = 9
    if any(k in s for k in ("nano", "small", "lite", "mini", "flash")):
        pri = 0
    elif "haiku" in s:
        pri = 1
    elif any(k in s for k in ("sonnet", "base")):
        pri = 2
    elif any(k in s for k in ("pro", "max", "opus", "ultra", "thinking", "reasoner")):
        pri = 5
    return (pri, len(s), s)


def _reachable(base_url: str, api_key: str) -> bool:
    try:
        r = httpx.get(
            f"{base_url.rstrip('/')}/models",
            headers={"authorization": f"Bearer {api_key}"},
            timeout=3,
        )
        return bool(r.status_code == 200)
    except Exception:
        return False


def _start_proxy(binary: str, config_path: str, startup_timeout: int) -> subprocess.Popen[bytes]:
    proc = subprocess.Popen(
        [binary, "-config", config_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
        env=os.environ.copy(),
    )
    deadline = time.time() + startup_timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"CLIProxy exited early with code {proc.returncode}")
        time.sleep(0.5)
    return proc


def _run_matrix(base_url: str, api_key: str, input_text: str) -> dict[str, Any]:
    headers = {"authorization": f"Bearer {api_key}"}
    models_resp = httpx.get(f"{base_url.rstrip('/')}/models", headers=headers, timeout=15)
    models_resp.raise_for_status()
    data = models_resp.json().get("data", [])

    by_provider: dict[str, list[str]] = defaultdict(list)
    for model in data:
        provider = model.get("owned_by") or "unknown"
        model_id = model.get("id")
        if isinstance(model_id, str):
            by_provider[provider].append(model_id)

    selected = {provider: sorted(model_ids, key=_score_model)[0] for provider, model_ids in by_provider.items() if model_ids}

    rows: list[dict[str, Any]] = []
    for provider, model_id in sorted(selected.items()):
        try:
            r = httpx.post(
                f"{base_url.rstrip('/')}/responses",
                headers={**headers, "content-type": "application/json"},
                json={"model": model_id, "input": input_text},
                timeout=60,
            )
            detail = ""
            if r.status_code != 200:
                detail = r.text.replace("\n", " ")[:180]
            rows.append(
                {
                    "provider": provider,
                    "model": model_id,
                    "status_code": r.status_code,
                    "ok": r.status_code == 200,
                    "detail": detail,
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "provider": provider,
                    "model": model_id,
                    "status_code": None,
                    "ok": False,
                    "detail": str(exc)[:180],
                }
            )

    passed = sum(1 for row in rows if row["ok"])
    return {"provider_count": len(rows), "passed": passed, "failed": len(rows) - passed, "rows": rows}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run CLIProxy provider smoke matrix with proxy preflight.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8317/v1")
    parser.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY", "sk-test"))
    parser.add_argument("--proxy-binary", default=os.environ.get("THGENT_CLIPROXY_BINARY", "cli-proxy-api-plus"))
    parser.add_argument(
        "--proxy-config",
        default=os.environ.get("THGENT_CLIPROXY_CONFIG", str(Path.home() / ".config" / "thegent" / "cliproxy-config.yaml")),
    )
    parser.add_argument("--startup-timeout", type=int, default=8)
    parser.add_argument("--input", default="reply with exactly: ok")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when any provider probe fails.")
    args = parser.parse_args()

    started_proc: subprocess.Popen[bytes] | None = None
    if not _reachable(args.base_url, args.api_key):
        started_proc = _start_proxy(args.proxy_binary, args.proxy_config, args.startup_timeout)
        if not _reachable(args.base_url, args.api_key):
            if started_proc.poll() is None:
                started_proc.terminate()
            raise RuntimeError(f"CLIProxy is not reachable at {args.base_url} after startup preflight.")

    try:
        result = _run_matrix(args.base_url, args.api_key, args.input)
        print(json.dumps(result, indent=2))
        if args.strict and result["failed"] > 0:
            return 1
        return 0
    finally:
        if started_proc is not None and started_proc.poll() is None:
            started_proc.terminate()


if __name__ == "__main__":
    raise SystemExit(main())
