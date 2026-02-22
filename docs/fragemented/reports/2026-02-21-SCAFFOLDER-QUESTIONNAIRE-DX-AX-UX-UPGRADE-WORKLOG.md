# Scaffolder Questionnaire DX/AX/UX Upgrade Worklog

Date: 2026-02-21
Status: Completed
Work Item: WL-140

## Scope Delivered

1. Rebuilt `initialize-project` questionnaire with project-shape-aware fields and guardrail validators.
2. Migrated template path/variable usage from mixed Cookiecutter/Copier style to Copier-native syntax.
3. Upgraded generated project `CLAUDE.md` to include questionnaire snapshot and DX/AX/UX contracts.
4. Upgraded template README with a project-type recommendation matrix.
5. Verified generation by running Copier smoke renders.

## DX/AX/UX Outcomes

### DX

- Questionnaire now catches invalid combinations before generation.
- Generated instructions are aligned with selected runtime and governance profile.

### AX

- Agents receive project-shape context directly in generated `CLAUDE.md`.
- Reduced ambiguity in where to enforce runtime, quality, and interface guarantees.

### UX

- Better defaults and matrix guidance produce fewer broken starter projects.
- Generated outputs include concrete quickstart and behavior expectations.

## Validation Performed

1. `uvx copier --version`
2. `uvx copier copy --defaults templates/initialize-project <tmpdir>`
3. `rg -n "\{\{|\{%" <tmpdir> -g '*.md'` (no unresolved template directives in markdown outputs)

## Follow-up Automation (WL-141)

1. Added `scripts/smoke_initialize_project_template.sh` with preset profiles:
   - `cli_tool`, `service_api`, `event_worker`, `web_app`, `library_sdk`, `all`.
2. Added Task wrappers:
   - `task smoke:initialize-project-template`
   - `task smoke:initialize-project-template:all`
3. Added CI quality-job smoke gate:
   - `task smoke:initialize-project-template`

## Preset Bootstrap CLI (WL-142)

1. Added `thegent sys setup project scaffold <destination> --profile <preset>` in `src/thegent/cli/apps/project.py`.
2. Added profile registry and Copier data-file generation for deterministic scaffolding.
3. Added focused CLI tests in `tests/test_project_tenancy.py` for:
   - invalid profile rejection,
   - non-empty destination rejection,
   - Copier invocation payload shape.
4. Executed one end-to-end scaffold run with `--profile cli_tool` and confirmed generated outputs.

## Preset Discovery UX (WL-143)

1. Added `thegent sys setup project scaffold-profiles` for quick preset discovery.
2. Added `--json` output mode for automation and scripting.
3. Improved invalid-profile scaffold errors to include valid preset names.
4. Added test coverage for profile listing (text + json).

## Advanced Scaffold Controls (WL-144)

1. Added `--dry-run` to preview scaffold payload without filesystem writes.
2. Added `--register` to register scaffolded project tenancy immediately.
3. Added `--tenant` override for tenancy registration.
4. Added tests validating dry-run bypasses Copier execution and registration creates tenancy record.

## Files Touched

- `templates/initialize-project/copier.yml`
- `templates/initialize-project/README.md`
- `templates/initialize-project/{{ project_name }}/CLAUDE.md`
- `templates/claude/CLAUDE.md.template`
- `docs/research/2026-02-21-SCAFFOLDER-QUESTIONNAIRE-DX-AX-UX-WEB-RESEARCH.md`
- `docs/plans/2026-02-21-SCAFFOLDER-QUESTIONNAIRE-DX-AX-UX-IMPLEMENTATION-PLAN.md`
- `docs/reports/2026-02-21-SCAFFOLDER-QUESTIONNAIRE-DX-AX-UX-UPGRADE-WORKLOG.md`
