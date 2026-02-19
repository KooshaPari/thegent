# session_scraper API Reference

> **Source**: `src/thegent/orchestration/session_scraper.py`

## SessionScraper

MTSP-18: Session Scraper to extract user prompts and context.
Focuses on terminal panes (tmux) and local history files.

### Methods

#### SessionScraper.__init__

```python
__init__(self, project_root)
```

#### SessionScraper.collect_all_recent_prompts

Unified collection from all available scrapers.

```python
collect_all_recent_prompts(self)
```

#### SessionScraper.scrape_claude_history

Scrape prompts from local Claude history files if they exist.

```python
scrape_claude_history(self)
```

#### SessionScraper.scrape_tmux_prompts

Scrape likely user prompts from active Claude Code tmux panes.

```python
scrape_tmux_prompts(self)
```

---

## collect_all_recent_prompts

Unified collection from all available scrapers.

```python
collect_all_recent_prompts(self)
```

---

## scrape_claude_history

Scrape prompts from local Claude history files if they exist.

```python
scrape_claude_history(self)
```

---

## scrape_tmux_prompts

Scrape likely user prompts from active Claude Code tmux panes.

```python
scrape_tmux_prompts(self)
```

---

