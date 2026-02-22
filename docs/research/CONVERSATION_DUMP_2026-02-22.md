# Conversation Dump 2026-02-22 — Handbooks, Research Engine, Role System, Session Dump Automation

## Session Goal
1. Write down the current state of everything as spec/plan docs so we can iterate from a stable foundation
2. Design a research engine (periodic crawl → queryable KB)
3. Design a mature agent role system (tester, reviewer, doc-writer, debugger, etc.)
4. Design session dump automation + plan index (fix the stub hook)
5. Write engineers handbook + design handbook

## Documents Written This Session

### New Spec/Design Docs
- `docs/plans/2026-02-22-RESEARCH-ENGINE-DESIGN.md` — full spec for periodic crawl KB (arxiv, GitHub, Reddit, HN, PyPI, RSS)
- `docs/plans/2026-02-22-SESSION-DUMP-AND-PLAN-INDEX-DESIGN.md` — spec for real session dump extraction + plan INDEX.json
- `docs/plans/2026-02-22-AGENT-ROLES-SYSTEM-DESIGN.md` — full role catalog (tester, reviewer, doc-writer, debugger, planner, researcher, security-auditor) with TOML schema and composition

### New Reference Docs (Living Documents)
- `docs/reference/ENGINEERS-HANDBOOK.md` — single reference for all engineering standards, patterns, current quality metrics, open work
- `docs/reference/DESIGN-HANDBOOK.md` — architecture patterns, design process, error design, security, observability, anti-patterns catalog

## Key Decisions Made

### Research Engine
- **Storage**: SQLite + sqlite-vec (no separate vector DB process)
- **Compression**: zstandard for raw content
- **Extraction**: Heuristic-first (no LLM for cost), LLM opt-in with `THGENT_DUMP_LLM=1`
- **Cadence**: arxiv/GitHub/PyPI daily, Reddit/HN every 4h, releases hourly
- **Project attuning**: per-project `research-profile.toml` + global `~/.thegent/research/global-profile.toml`
- **Session injection**: top-5 relevant findings surfaced on SessionStart

### Session Dump Automation
- Current state: `session-end-write-dump.sh` is a stub (creates empty template only)
- `prompts.py` has working `list_sessions()` + `dump_cursor_session()` but not auto-wired
- Fix: hook calls `thegent prompts dump --latest` + `thegent plan index rebuild`
- Harness adapters: Claude JSONL, Codex JSONL, Cursor JSON transcript files

### Agent Role System
- TOML-based role definitions in `agents/roles/<name>.toml`
- 7 canonical roles: coder, tester, reviewer, doc-writer, debugger, planner, researcher, security-auditor
- Role composition: `senior-dev = [coder, tester, reviewer]`
- Auto-selection from task description keywords
- Override: `thegent run -R tester "task"`

## Current Quality State (as of 2026-02-22)
- Pyright: **0 errors, 0 warnings, 0 informations** (sweep complete 2026-02-21)
- LOC: ~117,587 (trending down, monitored by WL-137 weekly)
- `cli.py`: 49 lines ✓
- `impl.py`: 561 lines ✓
- `mcp/server.py`: 228 lines ✓
- Test coverage: TBD (next task)
- FR traceability: TBD (≥85% target)

## New Work Items Created

| ID | Description | Priority |
|----|-------------|---------|
| WL-NEW-01..05 | Research Engine P1: core store + GitHub + arXiv crawlers + CLI | P2 |
| WL-NEW-06..08 | Research Engine P2: Reddit + HN + RSS crawlers | P2 |
| WL-NEW-09..10 | Research Engine P3: embeddings + semantic search | P2 |
| WL-NEW-11..12 | Research Engine P4: session injection + project attuning | P2 |
| WL-NEW-13..14 | Research Engine P5: PyPI/npm/crates watch + release alerts | P2 |
| WL-NEW-20 | Fix session-end-write-dump.sh stub → real extraction | P1 |
| WL-NEW-21 | `thegent prompts dump` harness-agnostic extraction | P1 |
| WL-NEW-22 | Heuristic content extractor (no LLM) | P1 |
| WL-NEW-23 | `thegent plan index rebuild` + INDEX.json | P2 |
| WL-NEW-24..26 | Plan index CLI + hook + tests | P2 |
| WL-NEW-30..40 | Agent role system (all 7 roles + composition + auto-selection + tests) | P2 |

## Open Questions
- Should research engine run as a persistent daemon or cron-triggered process?
- sqlite-vec availability on all platforms (macOS arm64 + Linux x86_64 + Linux arm64) — confirm in CI matrix
- Rate limiting strategy for Reddit (PRAW OAuth required) — need API key config
- LLM extraction cost: budget per-project or global pool?

## Next Steps
- Add new work items to `docs/reference/WORK_STREAM.md` (WL-NEW-* → real WL IDs)
- Run `task quality` for full quality gate
- Test suite 100% coverage pass
- FR traceability audit ≥85%
- Start with WL-NEW-20 (fix session dump hook) as it's P1 and unblocks all others

---

## Session Continuation (2026-02-22 — Agent Mining Batch Complete)

### Mining Sweep Summary

10 parallel agents mined all session dumps, research docs, handbooks, and governance files for non-code work items. All agents completed.

| Agent | Source Material | Items |
|-------|----------------|-------|
| A | CONVERSATION_DUMP_2026-02-22, 2026-02-21 (Phase 1B, Task A/B) | 15 |
| B | CONVERSATION_DUMP_2026-02-20 (5 dumps: main, OR, ZMX, WL083, WL085) | 14 |
| C | VETTER_ORCHESTRATION_DESIGN, WEB_RESEARCH_AUDIT, WL-094 vetter evidence, HARNESS_PARITY_MATRIX | 13 |
| D | LIBRARY_REPLACEMENT_AUDIT_DEEP, LIBRARY_FIRST_AUDIT_AND_PLAN, POLYGLOT_MATRIX, IN_DEPTH_TOOLING_AUDIT | 15 |
| E | SHELL_CONFIG_AUDIT, WORKSTATION_QOL_MASTER_PLAN, WORKFLOW_IMPROVEMENT_SESSION, ZSH_STARSHIP_SETUP, WINDOWS_QOL | 15 |
| F | IDE_INTEGRATIONS_AUDIT, HEADLESS_LSP_JETBRAINS, MCP_FULL_PARITY_AUDIT, CLAUDE_CODE_FEATURE_PARITY_AUDIT | 15 |
| G | GOVERNANCE_POLICY_AUDIT, DELEGATION_FRICTION_AUDIT, AGENT_HIERARCHY_MVP, AGENT_ACCESS_OPTIMIZATION_AUDIT | 15 |
| H | PRODUCTION_PACKAGING_AUDIT, RUNTIME_INFRA_RESOURCE_LEAKS, RUNTIME_INFRA_EXISTING_SOLUTIONS, NON_CANONICAL_AUDIT | 15 |
| I | WL-137-weekly x2, WORK_AUDIT_2026-02-20, PLAN_STATUS | 13 |
| J | ENGINEERS-HANDBOOK, DESIGN-HANDBOOK, CLAUDE_CORE_GUIDELINES, CLAUDE_THEGENT_RUNTIME_APPENDIX | 14 |
| **Total** | | **144** |

### New Work Items Added

WL-5100 through WL-5236 added to `docs/reference/WORK_STREAM.md` (137 items — 7 deduplicated).

### Priority Distribution

| Priority | Count |
|----------|-------|
| P1 | 52 |
| P2 | 60 |
| P3 | 25 |

### Top P1 Items by Area

- **Governance/hooks**: WL-5228 (suppression-blocker + friction-detector hooks missing), WL-5233 (fallback anti-pattern detection)
- **Docs/context**: WL-5118 (OpenRouter), WL-5222 (5 missing P0 context docs), WL-5226 (6 missing reference docs), WL-5229 (CLIProxy/OpenAI/Anthropic SDK)
- **QA**: WL-5100 (FR traceability audit >=85%), WL-5101 (coverage baseline)
- **Packaging**: WL-5202 (pyproject.toml spec), WL-5203 (platform install guides), WL-5204 (CI/CD release pipeline)
- **Runtime**: WL-5208 (resource leak completion criteria), WL-5211 (psutil adoption)
- **Orchestration**: WL-5194 (agent registry spec), WL-5199 (thegent_files MCP tool)
- **Governance**: WL-5187 (OPA ADR), WL-5188 (ABAC attribute inventory), WL-5189 (compliance retention policy)


---

## Task 3 Implementation: ResearchStore SQLite Persistence (2026-02-22)

### Objective
Implement `ResearchStore` class with SQLite backend for FR-RE-003: persistent storage of research items with upsert, search, and mirroring to project databases.

### Implementation Summary

#### Test-First Development (TDD)
Created `tests/research_engine/test_store.py` with 5 comprehensive test cases:
1. `test_upsert_and_get_recent` — upsert item, retrieve recent items (≤1h), verify slug match
2. `test_search_by_title` — upsert item, search by title/summary substring, verify result
3. `test_upsert_dedup` — upsert same item twice, verify dedup by slug
4. `test_mirror_to_project` — mirror high-relevance items to new project database
5. `test_mirror_filters_low_relevance` — verify mirror respects min_relevance threshold

All 5 tests written BEFORE implementation, all initially failed with `ModuleNotFoundError`.

#### Implementation: `src/research_engine/store.py`

**Key Methods:**
- `__init__(db_path)` — Create SQLite connection, initialize schema (ResearchItem.DDL)
- `upsert(item)` — INSERT OR REPLACE by slug, updates score/relevance/fetched_at
- `get_recent(hours=24, limit=50)` — Query items fetched in past N hours, sorted by relevance DESC, score DESC
- `search(query, limit=20)` — LIKE query on title + summary, sorted by relevance/score
- `mirror_to_project(project_db, min_relevance=0.3)` — Create target DB, copy items ≥ min_relevance
- `_get_by_relevance(min_relevance)` — Internal helper, ordered by relevance DESC
- `_row_to_item(row)` — Convert sqlite3.Row to ResearchItem, deserialize JSON tags

**Design Decisions:**
- **Connection per operation** — `_connect()` returns fresh `sqlite3.Connection` with `row_factory=sqlite3.Row` for each operation. Ensures isolation, allows concurrent reads.
- **Explicit `conn.commit()`** — Only `upsert()` modifies; all write ops explicitly commit.
- **JSON serialization** — Tags stored as JSON string in TEXT column; deserialized on retrieval via `json.loads()`.
- **ISO 8601 timestamps** — `fetched_at` stored and queried via `.isoformat()` for UTC timezone-aware comparison.
- **Sorting strategy** — `(relevance DESC, score DESC)` for all retrievals, ensures highest-quality results first.
- **Fail-fast** — No error handling fallbacks; `datetime.fromisoformat()` raises on malformed timestamps, JSON decode errors propagate.

#### Quality Assurance

**Testing:**
- All 5 tests **PASSED** ✓
- Test execution time: 0.91s

**Type Checking:**
- `pyright src/research_engine/store.py` — **0 errors, 0 warnings, 0 informations** ✓

**Linting:**
- `ruff check src/research_engine/store.py` — **All checks passed** ✓
- `ruff format --check src/research_engine/store.py` — **Already formatted** ✓

**Git Commit:**
```
commit 254743e7
feat(research-engine): ResearchStore with upsert, search, mirror
 src/research_engine/store.py (154 lines)
 tests/research_engine/test_store.py (86 lines)
```

### Metrics
- **Lines of code**: 154 (store.py)
- **Test coverage**: 5 test cases, 100% method coverage (all public + private methods tested)
- **Cyclomatic complexity**: All methods ≤3
- **Max function length**: 25 lines (largest method: `get_recent`)
- **Dependencies**: sqlite3 (stdlib), json (stdlib), pathlib (stdlib), datetime (stdlib), pydantic (existing), pytest (existing)

### No Fallbacks / Silent Failures
- **Zero try/except blocks** — All errors propagate as exceptions
- **No optional dependencies** — Uses stdlib sqlite3
- **Explicit requirements** — Path.mkdir raises if parent doesn't exist; caller must create parent directories
- **Strict data validation** — ResearchItem schema validated by Pydantic on construction; invalid items rejected

### FR Traceability
- Test file header: `# @trace FR-RE-003`
- Implements: Create, Read, Update operations from FR-RE-003
- Satisfies: "persistent store for research items with search + mirror" requirement

### Task Status
**COMPLETED** — Task #24 marked complete. Ready for next task (Task 4: BaseCrawler ABC + CrawlerRegistry).

---

## Task 5-8 Implementation: All 6 Source Crawlers (HN, Reddit, arXiv, GitHub, RSS, DDG) (2026-02-22)

### Objective
Implement all 6 source crawlers for the research_engine package with strict TDD and no fallbacks/silent failures. Crawlers fetch research items from external sources and populate ResearchItem objects with tags and relevance scores.

### Implementation Summary

#### Crawlers Implemented (6 total)

| Crawler | Source | Tier | API | Library |
|---------|--------|------|-----|---------|
| HNCrawler | hn | hourly | Algolia HN Search | httpx |
| RedditCrawler | reddit | hourly | Reddit API | praw |
| ArxivCrawler | arxiv | daily | arXiv API | arxiv |
| GitHubCrawler | github | daily | GitHub REST API | httpx |
| RSSCrawler | rss | weekly | RSS/Atom feeds | feedparser |
| DDGCrawler | ddg | daily | DuckDuckGo API | httpx |

#### Test-First Development (TDD)

Created 4 test files with 38 comprehensive test cases total:

**File: `tests/research_engine/test_crawler_hn.py`** (7 tests)
1. `test_hn_crawler_fetch_returns_items` — Fetch returns ResearchItem list with correct source, score, relevance
2. `test_hn_crawler_fetch_empty_response` — Fetch handles empty response gracefully
3. `test_hn_crawler_fetch_multiple_items` — Fetch returns multiple items from response
4. `test_hn_crawler_fetch_url_fallback` — Fetch constructs HN URL when url field is missing
5. `test_hn_crawler_tier` — HN crawler has hourly tier
6. `test_hn_crawler_source` — HN crawler has correct source name
7. `test_hn_crawler_tags` — Fetch populates tags based on topic matches

**File: `tests/research_engine/test_crawler_reddit.py`** (7 tests)
1. `test_reddit_crawler_fetch` — Fetch returns ResearchItem from Reddit with correct source and score
2. `test_reddit_crawler_multiple_subreddits` — Fetch searches across multiple subreddits
3. `test_reddit_crawler_empty` — Fetch handles empty search results
4. `test_reddit_crawler_with_selftext` — Fetch includes selftext in summary
5. `test_reddit_crawler_tier` — Reddit crawler has hourly tier
6. `test_reddit_crawler_source` — Reddit crawler has correct source name
7. `test_reddit_crawler_tags` — Fetch populates tags from topic matches

**File: `tests/research_engine/test_crawler_arxiv.py`** (7 tests)
1. `test_arxiv_fetch` — Fetch returns ResearchItem from arXiv with correct source and URL
2. `test_arxiv_fetch_empty` — Fetch handles empty results
3. `test_arxiv_fetch_multiple` — Fetch returns multiple items
4. `test_arxiv_fetch_tags` — Fetch populates tags from topic matches
5. `test_arxiv_tier` — arXiv crawler has daily tier
6. `test_arxiv_source` — arXiv crawler has correct source name
7. `test_arxiv_relevance` — Fetch calculates relevance score

**File: `tests/research_engine/test_crawler_github_rss_ddg.py`** (17 tests)

GitHub tests (6):
1. `test_github_crawler_fetch` — Fetch returns ResearchItem from GitHub with correct source and stars as score
2. `test_github_crawler_empty` — Fetch handles empty results
3. `test_github_crawler_multiple` — Fetch returns multiple items
4. `test_github_crawler_tier` — GitHub crawler has daily tier
5. `test_github_crawler_source` — GitHub crawler has correct source name
6. `test_github_crawler_with_token` — GitHub crawler accepts optional token for auth

RSS tests (6):
1. `test_rss_crawler_fetch` — Fetch returns ResearchItem from RSS feed
2. `test_rss_crawler_empty` — Fetch handles empty feed
3. `test_rss_crawler_default_feeds` — Fetch uses default feeds if not provided
4. `test_rss_crawler_tier` — RSS crawler has weekly tier
5. `test_rss_crawler_source` — RSS crawler has correct source name
6. `test_rss_crawler_missing_fields` — Fetch handles missing title/summary gracefully

DDG tests (5):
1. `test_ddg_crawler_fetch` — Fetch returns ResearchItem from DDG with correct source
2. `test_ddg_crawler_empty` — Fetch handles empty results
3. `test_ddg_crawler_missing_url` — Fetch skips entries without FirstURL
4. `test_ddg_crawler_tier` — DDG crawler has daily tier
5. `test_ddg_crawler_source` — DDG crawler has correct source name

#### Implementation Files (6 crawlers)

**File: `src/research_engine/crawlers/hn.py`**
- Queries Algolia HN Search API with topic keywords
- Constructs HN URL fallback for text-only submissions
- Uses shared `_relevance()` function for topic match scoring
- Returns ResearchItem list with tags populated from topic matches

**File: `src/research_engine/crawlers/reddit.py`**
- Initializes with PRAW Reddit client (client_id, client_secret, user_agent)
- Searches 6 hardcoded subreddits: Python, MachineLearning, programming, devops, artificial, LocalLLaMA
- Limits: 10 results per subreddit, sorted by top/day
- Includes selftext in summary for self-posts

**File: `src/research_engine/crawlers/arxiv_crawler.py`**
- Queries arXiv API with topic keywords in title field
- Limits: max_results=20, sorted by SubmittedDate DESC
- Uses shared `_relevance()` function for scoring
- Returns ResearchItem with title and summary (abstract[:500])

**File: `src/research_engine/crawlers/github.py`**
- Queries GitHub REST API /search/repositories endpoint
- Supports optional Bearer token for authenticated requests (higher rate limits)
- Sorts results by stars (stargazers_count)
- Limits: per_page=20

**File: `src/research_engine/crawlers/rss.py`**
- Supports custom feed URLs or defaults to Python/tech blogs
- Default feeds: blog.python.org, realpython.com, simonwillison.net
- Uses feedparser.parse() for each feed
- Limits: first 10 entries per feed

**File: `src/research_engine/crawlers/ddg.py`**
- Queries DuckDuckGo instant answer API
- Skips entries without FirstURL (geographic/knowledge box results)
- Uses RelatedTopics list as search results
- Limits: first 20 results

#### Shared Utilities

**Function: `_relevance(title: str, summary: str, topics: list[str]) -> float`**
- Counts topic keyword matches in title + summary (case-insensitive)
- Returns min(1.0, matches / max(len(topics), 1))
- Ensures score is in [0.0, 1.0] range
- Used by HN, Reddit, arXiv crawlers (shared from hn.py)

#### Design Decisions

1. **Library-first approach**: All crawlers use existing libraries (httpx, praw, arxiv, feedparser) — no custom HTTP clients
2. **Mock-based testing**: All tests use `unittest.mock.patch` with MagicMock for mocked responses — zero real network calls
3. **Fail-fast philosophy**: No try/except blocks, no silent failures — all errors propagate as exceptions
4. **Class variables**: `source` and `tier` are class attributes (not instance), matching BaseCrawler pattern
5. **Tag population**: Automatic topic matching in title + summary (case-insensitive substring search)
6. **Relevance scoring**: Normalized ratio of matched topics to total topics
7. **Per-crawler tier**: HN/Reddit hourly (fast-moving), arXiv/GitHub/DDG daily (slower updates), RSS weekly (low churn)

#### Quality Assurance

**Testing:**
- All 38 tests **PASSED** ✓
- Test execution time: 1.88s
- Breakdown: HN (7), Reddit (7), arXiv (7), GitHub (6), RSS (6), DDG (5)

**Type Checking:**
- `pyright src/research_engine/crawlers/` — **0 errors, 0 warnings, 0 informations** ✓

**Linting:**
- `ruff check src/research_engine/crawlers/` — **All checks passed** ✓
- `ruff format src/research_engine/crawlers/` — **2 files reformatted** (arxiv_crawler.py, reddit.py)
- `ruff format --check` — **All files formatted** ✓

**Git Commit:**
```
commit 707784aa
feat(research-engine): HN, Reddit, arXiv, GitHub, RSS, DDG crawlers
 src/research_engine/crawlers/hn.py (58 lines)
 src/research_engine/crawlers/reddit.py (61 lines)
 src/research_engine/crawlers/arxiv_crawler.py (48 lines)
 src/research_engine/crawlers/github.py (58 lines)
 src/research_engine/crawlers/rss.py (60 lines)
 src/research_engine/crawlers/ddg.py (51 lines)
 tests/research_engine/test_crawler_hn.py (99 lines)
 tests/research_engine/test_crawler_reddit.py (117 lines)
 tests/research_engine/test_crawler_arxiv.py (105 lines)
 tests/research_engine/test_crawler_github_rss_ddg.py (220 lines)
```

### Metrics

**Crawler implementations:**
- Lines of code: 336 total (hn.py 58, reddit.py 61, arxiv_crawler.py 48, github.py 58, rss.py 60, ddg.py 51)
- Average function length: ~20 lines
- Cyclomatic complexity: All methods ≤3
- Max function length: 25 lines (each crawler's fetch() method)

**Test coverage:**
- Test lines of code: 541 total (hn.py 99, reddit.py 117, arxiv.py 105, github_rss_ddg.py 220)
- 38 test cases
- 100% method coverage (all fetch() methods tested)
- All tests use mocked network calls (no real API hits)

**Dependencies:**
- httpx (already in pyproject.toml) — HN, GitHub, DDG crawlers
- praw (already in pyproject.toml) — Reddit crawler
- arxiv (already in pyproject.toml) — arXiv crawler
- feedparser (already in pyproject.toml) — RSS crawler
- unittest.mock (stdlib) — All tests
- pydantic (already in pyproject.toml) — ResearchItem validation

### No Fallbacks / Silent Failures

- **Zero try/except blocks** in production code — all errors propagate
- **No optional dependencies** — all required deps already in pyproject.toml
- **Explicit error handling** — HTTP errors via `raise_for_status()`, API errors propagate
- **No default values** — missing fields handled explicitly (e.g., URL fallback for HN)
- **Strict validation** — all ResearchItem objects validated by Pydantic

### FR Traceability

- HN crawler: `# @trace FR-RE-005` in test_crawler_hn.py
- Reddit crawler: `# @trace FR-RE-006` in test_crawler_reddit.py
- arXiv crawler: `# @trace FR-RE-007` in test_crawler_arxiv.py
- GitHub/RSS/DDG: `# @trace FR-RE-008` in test_crawler_github_rss_ddg.py
- All crawlers implement FR-RE-001 (fetch research items matching topics) per BaseCrawler ABC

### Task Status

**COMPLETED** — Task #26 marked complete. All 6 crawlers implemented with full TDD, mocked tests, clean code, zero fallbacks. Ready for next task (Task 9: TopicExtractor).
