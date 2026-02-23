# Enhanced Session Scraper Plan (WL-156)

## WL-156 Implementation / Status (2026-02-22)

**Status:** Ready for implementation  
**Owner:** WL-156  
**Scope:** Triggered snapshot capture + normalized event emission for session scraping  
**Blockers:** None

### Trigger Schema (input contract)

```json
{
  "event_name": "session.scraper.snapshot.requested",
  "version": "v1",
  "required": [
    "event_id",
    "occurred_at",
    "trigger",
    "project_root"
  ],
  "properties": {
    "event_id": "uuid-v4",
    "occurred_at": "ISO-8601 UTC",
    "trigger": "manual|hook:pre-commit|hook:post-test|timer:15m|session:end",
    "project_root": "absolute path",
    "tags": "string[]",
    "since": "optional ISO-8601 UTC lower bound",
    "max_prompts": "optional int, default 200"
  }
}
```

### Emitted Event Schema (output contract)

```json
{
  "event_name": "session.scraper.snapshot.created",
  "version": "v1",
  "required": [
    "event_id",
    "request_event_id",
    "occurred_at",
    "snapshot_id",
    "snapshot_path",
    "summary"
  ],
  "properties": {
    "event_id": "uuid-v4",
    "request_event_id": "uuid-v4",
    "occurred_at": "ISO-8601 UTC",
    "snapshot_id": "snapshot-YYYYMMDDTHHMMSSffffffZ",
    "snapshot_path": "docs/dumps/session-snapshots/YYYY-MM-DD/*.json",
    "summary": {
      "prompts": "int",
      "commands": "int",
      "files": "int",
      "facts": "int",
      "decisions": "int",
      "tags": "int",
      "sources": "string[]"
    }
  }
}
```

```json
{
  "event_name": "session.scraper.snapshot.failed",
  "version": "v1",
  "required": [
    "event_id",
    "request_event_id",
    "occurred_at",
    "error_code",
    "error_message"
  ],
  "properties": {
    "event_id": "uuid-v4",
    "request_event_id": "uuid-v4",
    "occurred_at": "ISO-8601 UTC",
    "error_code": "SCRAPER_IO|SCRAPER_PARSE|SCRAPER_RUNTIME",
    "error_message": "string",
    "partial_snapshot_path": "optional path"
  }
}
```

### Immediate Next Coding Steps

1. Add `SessionScrapeRequestEvent`, `SessionSnapshotCreatedEvent`, and `SessionSnapshotFailedEvent` `TypedDict` contracts in `thegent/src/thegent/orchestration/state/session_scraper.py`.
2. Add `emit_snapshot_event(...)` in `thegent/src/thegent/orchestration/state/session_scraper.py` and call it from `persist_snapshot(...)` success/failure branches.
3. Add trigger normalization (`manual`, `hook:*`, `timer:*`, `session:end`) in `collect_snapshot(...)` to enforce the schema above.
4. Add unit tests in `thegent/tests/test_unit_session_scraper.py` that validate emitted payload shape for both `snapshot.created` and `snapshot.failed`.
5. Add one batch regression in `thegent/tests/test_unit_session_scraper_batch6.py` that verifies `request_event_id` propagation from request -> created/failed events.

