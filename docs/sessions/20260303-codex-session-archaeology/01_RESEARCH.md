# Research

## Data Sources
- Codex rollouts: `~/.codex/sessions/**/rollout-*.jsonl`
- Other stores: `~/.factory`, `~/.cursor`, `~/.claude`
- Desktop app stores: `~/Library/Application Support/Codex|Claude|Cursor`

## Last-14d Store Counts
| Store | Recent file count |
|---|---:|
| `/Users/kooshapari/.codex` | 7712 |
| `/Users/kooshapari/.factory` | 5338 |
| `/Users/kooshapari/.cursor` | 2885 |
| `/Users/kooshapari/.claude` | 12296 |
| `/Users/kooshapari/Library/Application Support/Codex` | 157 |
| `/Users/kooshapari/Library/Application Support/Claude` | 1 |
| `/Users/kooshapari/Library/Application Support/Cursor` | 3 |

## HeliosCLI Surfaces Confirmed
- Protocol thread list filters include `cwd`, `search_term`, `archived`:
  - `heliosCLI/codex-rs/app-server-protocol/src/protocol/v2.rs`
- Backend thread list processing:
  - `heliosCLI/codex-rs/app-server/src/codex_message_processor.rs`
- Resume picker search/sort UI and `BackTab` handling currently not bound to scope cycle:
  - `heliosCLI/codex-rs/tui/src/resume_picker.rs`

## Heuristics Used
- Session classified completed if `task_complete` event exists.
- Session classified unfinished if no `task_complete` and terminal error/abort/disconnect signal present.
- Cross-session resolution inferred by same `cwd` + time proximity + user-message token similarity.
