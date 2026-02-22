# Thegent FastMCP Verification Runbook

**Purpose:** Verify MCP server, tools, resources, and prompts per THGENT_FASTMCP_IMPLEMENTATION_PLAN §9.
**Date:** 2026-02-14

---

## 1. Server Startup

| Item | How to Verify | Pass |
|------|---------------|------|
| `thegent serve` starts | Run `thegent serve`; no errors | ☐ |
| HTTP endpoint responds | `curl http://127.0.0.1:3847/mcp` returns 200 or MCP handshake | ☐ |
| Default bind | Host 127.0.0.1, port 3847, path /mcp | ☐ |

---

## 2. Cursor MCP Config

| Item | How to Verify | Pass |
|------|---------------|------|
| Add thegent server | Cursor → Settings → MCP → Add server | ☐ |
| URL | `http://127.0.0.1:3847/mcp` | ☐ |
| Tools visible | Restart Cursor; thegent_* tools appear in tool list | ☐ |

---

## 3. Core Tools

| Tool | Verification | Pass |
|------|--------------|------|
| `thegent_run` (gemini) | Call with agent=gemini, prompt="Hello"; expect stdout in result | ☐ |
| `thegent_run` (cursor-agent) | Call with agent=cursor-agent, prompt="Hello"; expect output | ☐ |
| `thegent_run` (model-first) | Call with model=gemini-3-flash, prompt="Hi"; expect routing to provider | ☐ |
| `thegent_bg` | Call with agent, prompt; note session_id in result | ☐ |
| `thegent_ps` | After thegent_bg; session appears in list | ☐ |
| `thegent_status` | Call with session_id from thegent_bg; expect status, pid | ☐ |
| `thegent_logs` | Call with session_id; expect log content | ☐ |
| `thegent_wait` | Call with session_id; expect exit_code when done | ☐ |
| `thegent_stop` | Call with session_id; session stops | ☐ |
| `thegent_list_agents` | Returns agent names + backends | ☐ |
| `thegent_list_droids` | Returns droid names (cd optional) | ☐ |
| `thegent_list_models` | Returns by_provider; with provider filter works | ☐ |
| `thegent_list_models` (by_model) | Include contract view shows model→providers | ☐ |
| `thegent_dag_list` | Returns DAG tasks when .factory/dag-session.md exists | ☐ |

---

## 4. Progress Updates (Phase 3)

| Item | How to Verify | Pass |
|------|---------------|------|
| Progress during long run | Run thegent_run with long prompt; check for progress notifications in MCP stream | ☐ |

---

## 5. Resources

| Resource | Verification | Pass |
|----------|--------------|------|
| `thegent://sessions` | Returns session list (JSON) | ☐ |
| `thegent://session/{id}/logs` | After thegent_bg; returns log content | ☐ |
| `thegent://session/{id}/meta` | Returns session metadata | ☐ |
| `thegent://dag` | Returns DAG content when .factory/dag-session.md exists | ☐ |
| `thegent://agents` | Returns agent list | ☐ |
| `thegent://models` | Returns model catalog | ☐ |
| `thegent://meta` | Returns server meta (version, schema versions, operations) | ☐ |

---

## 6. Prompts

| Item | How to Verify | Pass |
|------|---------------|------|
| List prompts | MCP prompts/list includes thegent_* prompts | ☐ |
| Render prompt | Call thegent_run_agent with agent, prompt; verify output | ☐ |

---

## 7. CLI Parity

| Item | Verification | Pass |
|------|--------------|------|
| `thegent run` | CLI run works; same as MCP thegent_run (sync) | ☐ |
| `thegent bg` | CLI bg works; session appears in thegent_ps | ☐ |
| `thegent list-models` | CLI returns scraped catalog | ☐ |
| `thegent list-models --by-model` | Unified view model→providers | ☐ |

---

## 8. Contract & Discovery

| Item | Verification | Pass |
|------|--------------|------|
| thegent://meta | Exposes route_schema_version, output_parser_schema_version | ☐ |
| thegent://meta | Exposes operations list | ☐ |
| list_models include_contract | Returns structured contract metadata | ☐ |

---

## Summary

- **Total items:** 30+
- **Pass:** Count checked ☑
- **Fail:** Document any failures with remediation notes below.

### Failure Log

| Item | Failure | Remediation |
|------|---------|-------------|
| | | |


---
## See also

- [WORK_STREAM.md](reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](plans/00-MASTER-INDEX.md) — plan index
