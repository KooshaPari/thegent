# server_research_tools API Reference

> **Source**: `src/thegent/mcp/server_research_tools.py`

Research MCP tool registration helpers.

---

## register_research_tools

Register ddg/reddit/scrape/deep-research/suggest_prompt MCP tools.

---

## thegent_deep_research

```python
thegent_deep_research(query: str, subreddits: Any)
```

Perform deep research using the Deep Research Protocol (DRP).

Bypasses blocks by using custom headers and direct API calls.

**Parameters**:

- `query`: Search query string
- `subreddits`: Comma-separated list of subreddits to prioritize

---

## thegent_reddit_search

```python
thegent_reddit_search(query: str, num_results: int)
```

Search Reddit for discussions and community insights.

Uses Reddit API (if configured) or site-specific search.

**Parameters**:

- `query`: Search query string
- `num_results`: Max results to return (min: 1, max: 20, default: 5)

---

