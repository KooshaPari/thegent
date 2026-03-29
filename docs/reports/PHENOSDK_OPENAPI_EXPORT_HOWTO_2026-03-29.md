# phenoSDK — export OpenAPI (Wave A)

Base install of `pheno-sdk` does **not** include **FastAPI**; `create_app()` fails with `ModuleNotFoundError: fastapi` after a minimal `uv sync`.

## One-off snapshot (local)

From `repos/worktrees/phenoSDK/main`:

```bash
uv pip install 'fastapi>=0.115.0' 'orjson>=3.9.0'
uv run python -c "
from pheno.adapters.api.app import create_app
import json
app = create_app()
path = 'artifacts/openapi.json'
import pathlib
pathlib.Path('artifacts').mkdir(exist_ok=True)
pathlib.Path(path).write_text(json.dumps(app.openapi(), indent=2))
print('wrote', path)
"
```

Commit the JSON **only** inside a dedicated phenoSDK branch or a Phenotype `contracts/` package — do not commit `artifacts/` to the monorepo unless policy allows.

## Product fix (upstream phenoSDK)

Add an optional extra, e.g. `api = ["fastapi>=...", "orjson>=..."]`, and document `pip install pheno-sdk[api]` for REST contract generation.
