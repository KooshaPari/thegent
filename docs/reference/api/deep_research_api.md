# deep_research API Reference

> **Source**: `src/thegent/tools/deep_research.py`

## arxiv_search

```python
arxiv_search(query: str, max_results: int)
```

Search Arxiv using their API.

---

## ddg_html_search

```python
ddg_html_search(query: str)
```

Perform a DuckDuckGo HTML search and extract results.

---

## github_search

```python
github_search(query: str, max_results: int)
```

Search GitHub repositories using their API.

---

## perform_deep_research

```python
perform_deep_research(query: str, subreddits: Any)
```

Execute the full Deep Research Protocol.

---

## reddit_json_search

```python
reddit_json_search(query: str, subreddit: Any, limit: int)
```

Search Reddit using the .json API.

---

## run_curl

```python
run_curl(url: str, user_agent: str)
```

Run curl with a specific user agent and return the output.

---

