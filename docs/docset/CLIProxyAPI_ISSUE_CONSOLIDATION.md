# CLIProxyAPI Issue Consolidation - Decision Matrix

**Generated:** 2026-02-22  
**Source:** 961 GitHub issues from CLIProxyAPI + CLIProxyAPIPlus  
**Purpose:** Consolidate into actionable thegent work items

---

## Executive Summary

| Category | Total Issues | Already Addressed | High Priority | Medium | Low/Ignore |
|----------|-------------|-------------------|---------------|--------|------------|
| Provider Integration | 27 | ~10 | 5 | 12 | 10 |
| OAuth/Auth | 75 | ~20 | 15 | 30 | 30 |
| Model Support | 88 | ~15 | 10 | 40 | 38 |
| Routing | 4 | 1 | 1 | 2 | 1 |
| Docker/Deployment | 15 | 5 | 3 | 7 | 5 |
| UI/Dashboard | 19 | 5 | 2 | 8 | 9 |
| Streaming | 17 | 5 | 5 | 7 | 5 |
| Translation | 2 | 0 | 1 | 1 | 0 |
| Performance | 1 | 0 | 0 | 1 | 0 |
| Docs | 4 | 2 | 0 | 2 | 2 |

---

## HIGH PRIORITY - Should Implement

### 1. OAuth/Auth (15 items)

| Issue | Title | thegent Status |
|-------|-------|----------------|
| [#1658](https://github.com/router-for-me/CLIProxyAPI/issues/1658) | Qwen Oauth fails | Needs implementation |
| [#1612](https://github.com/router-for-me/CLIProxyAPI/issues/1612) | codex oauth登录流程失败 | Needs implementation |
| [#1611](https://github.com/router-for-me/CLIProxyAPI/issues/1611) | qwen auth 获取到模型但客户端获取不到 | Needs implementation |
| [#232](https://github.com/router-for-me/CLIProxyAPIPlus/issues/232) | Add AMP auth as Kiro | Needs implementation |
| [#177](https://github.com/router-for-me/CLIProxyAPIPlus/issues/177) | Kiro Token 导入失败 | Needs implementation |

### 2. Model Support (10 items)

| Issue | Title | thegent Status |
|-------|-------|----------------|
| [#258](https://github.com/router-for-me/CLIProxyAPIPlus/issues/258) | variant parameter fallback | ✅ DONE |
| [#1671](https://github.com/router-for-me/CLIProxyAPI/issues/1671) | Cannot use Claude Models in Codex CLI | Needs implementation |
| [#1655](https://github.com/router-for-me/CLIProxyAPI/issues/1655) | All credentials for claude-sonnet-4-6 cooling down | Monitor |
| [#1651](https://github.com/router-for-me/CLIProxyAPI/issues/1651) | Claude Sonnet 4.5 deprecated | Monitor |

### 3. Streaming (5 items)

| Issue | Title | thegent Status |
|-------|-------|----------------|
| [#1609](https://github.com/router-for-me/CLIProxyAPI/issues/1609) | handle response.function_call_arguments.done | Needs implementation |
| [#1592](https://github.com/router-for-me/CLIProxyAPI/issues/1592) | Claude Code random cch in x-anthropic | Needs implementation |
| [#1478](https://github.com/router-for-me/CLIProxyAPI/issues/1478) | streaming response empty when translated | Needs implementation |
| [#1407](https://github.com/router-for-me/CLIProxyAPI/issues/1407) | stream disconnected before completion | Needs implementation |
| [#1085](https://github.com/router-for-me/CLIProxyAPI/issues/1085) | Streaming Response Translation Fails | Needs implementation |

### 4. Routing (1 item)

| Issue | Title | thegent Status |
|-------|-------|----------------|
| [#1617](https://github.com/router-for-me/CLIProxyAPI/issues/1617) | Session-Aware Hybrid Routing Strategy | Feature request - evaluate |

### 5. Translation (1 item)

| Issue | Title | thegent Status |
|-------|-------|----------------|
| [#167](https://github.com/router-for-me/CLIProxyAPI/issues/167) | Major Bug in transforming anthropic request to openai | Critical - needs fix |

---

## MEDIUM PRIORITY - Evaluate Later

### Provider Integration (12 items)
- Token refresh logic improvements
- Session title generation
- Provider error handling

### OAuth/Auth (30 items)
- Various OAuth flow fixes
- Token refresh improvements
- Multi-provider auth issues

### Model Support (40 items)
- New model additions
- Model deprecation handling
- Context length issues

### Docker/Deployment (7 items)
- ARM architecture support
- UI standalone service
- Asset bundling

### UI/Dashboard (8 items)
- Account rotation UI
- Provider visibility
- Error display improvements

---

## LOW PRIORITY / IGNORE

### Already Addressed in thegent
- Issues already fixed in CLIProxyAPI that thegent doesn't need
- Platform-specific issues (Windows-only, Linux-only)
- Very niche use cases

### Won't Fix
- Duplicate issues
- Invalid/wontfix
- User environment issues

---

## Existing thegent Plans Mapping

| thegent Plan | Related Issues |
|--------------|----------------|
| `CLIPROXY_API_AND_THGENT_UNIFIED_PLAN.md` | OAuth, provider integration |
| `OPENROUTER_STYLE_ROUTING_AND_CLIPROXY.md` | Routing strategies |
| `LITELLM_CLIPROXY_BIFROST_HARMONY.md` | LiteLLM integration |

---

## Recommended Action Items

### Immediate (This Sprint)
1. ✅ DONE: #258 variant parameter
2. TODO: #1671 Claude in Codex CLI - high impact bug
3. TODO: #1085 streaming translation - high impact

### Next Phase
1. OAuth flow consolidation (15 issues)
2. Model support expansion (10 issues)
3. Streaming fixes (5 issues)

### Backlog
1. Docker improvements
2. UI enhancements  
3. Documentation updates

---

## How to Use This Document

1. **Pick items** from HIGH PRIORITY to add to WORK_STREAM
2. **Mark done** in `cliproxy-github-issues.json` when implemented
3. **Refresh** periodically with `python scripts/scrape_cliproxy_issues.py`

---

## Related Documentation

- [CLIProxyAPI Issue Board](./CLIProxyAPI_ISSUE_BOARD.md)
- [Provider Setup Guide](../guides/PROVIDER_SETUP_GUIDE.md)
- [CLIPROXY_API_AND_THGENT_UNIFIED_PLAN](./plans/CLIPROXY_API_AND_THGENT_UNIFIED_PLAN.md)
