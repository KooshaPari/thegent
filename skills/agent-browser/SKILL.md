# Agent Browser Skill

Use this skill when a task requires authenticated browser automation or repeatable browser journeys.

## Purpose

Treat browser work as a governed workflow:
- keep auth and task journeys explicit
- launch through the dedicated Agent Browser entrypoint
- avoid ad-hoc profile switching during execution

## Required Process

1. Validate environment:
   - `thegent browser doctor`
2. Register or update journey:
   - `thegent browser journey add <name> --url <url> --kind auth|task --notes "..."`
3. Review registered journeys:
   - `thegent browser journey list`
4. Launch a journey:
   - `thegent browser journey open <name> --browser auto --cdp-port 9222`
5. For one-off launches:
   - `thegent browser launch --browser auto --url <url>`

## Rules

- Use only `thegent browser ...` for browser entry in thegent workflows.
- Keep journey names stable and action-oriented (examples: `github-login`, `vercel-deploy`, `billing-review`).
- Do not store secrets in journey notes.
- If browser prerequisites fail, stop and fix via `thegent browser doctor` before proceeding.
