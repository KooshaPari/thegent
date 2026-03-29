# phenoSDK — export OpenAPI (Wave A)

## Committed snapshot (this monorepo)

**`docs/reports/data/phenosdk_openapi_snapshot_2026-03-29.json`** (~41KB), generated from `create_app().openapi()` after worktree fixes.

## Install

Worktree `pyproject.toml` defines **`pheno-sdk[api]`** (`fastapi`, `orjson`, `uvicorn`); `all` includes `api`.

```bash
cd repos/worktrees/phenoSDK/main
uv sync --extra api
```

## Upstream fixes in worktree (push to `KooshaPari/phenoSDK`)

`app.openapi()` failed until **runtime imports** replaced `TYPE_CHECKING`-only imports for:

- `application/dtos/{user,deployment,service,configuration}.py` — `datetime` + domain entities
- `adapters/api/routes/{users,deployments,services,configurations}.py` — use case classes used in `Annotated[..., Depends]`
- `adapters/api/dependencies.py` — `Container`

## Regenerate

```bash
cd repos/worktrees/phenoSDK/main
uv sync --extra api
mkdir -p artifacts
uv run python -c "
from pheno.adapters.api.app import create_app
import json
from pathlib import Path
app = create_app()
Path('artifacts/openapi.json').write_text(json.dumps(app.openapi(), indent=2))
"
# optional: copy into monorepo docs/reports/data/
```
