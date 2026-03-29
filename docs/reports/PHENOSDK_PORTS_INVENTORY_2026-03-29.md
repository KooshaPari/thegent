# phenoSDK `src/pheno/ports` inventory (Wave A kickoff)

**Tree:** `repos/worktrees/phenoSDK/main/src/pheno/ports`  
**AgilePlus:** `phenosdk-wave-a-contracts`

## Top-level modules (Python)

| Module / package | Role (from naming) |
|------------------|--------------------|
| `__init__.py` | Package exports |
| `authentication.py` | Auth port |
| `auth/` | Auth sub-ports (`providers.py`) |
| `database.py` | Persistence port |
| `inference.py` | LLM / model inference port |
| `messaging.py` | Message bus / queue port |
| `observability.py` | Metrics/tracing port |
| `registry.py` | Service or plugin registry |
| `stream.py` | Streaming I/O |
| `tunnels.py`, `tunneling.py` | Network tunnel abstractions |
| `port_allocation.py` | Dynamic port allocation |
| `mcp/` | MCP: `provider.py`, `session_manager.py`, `tool_registry.py`, `resource_provider.py`, `monitoring.py` |

## Next steps (Wave A)

1. For each port: list **implementing adapters** under `src/pheno/adapters` and `infra` (ripgrep `implements` / type hints / registration).
2. Choose **contract artifact** per boundary: start with **MCP** and **database** if external consumers exist.
3. Extract **DTOs** that cross process boundaries into a small `pheno-contracts` package or OpenAPI/Proto definitions in `Phenotype/repos` template libs.

## Command hints

```bash
rg "class.*Port|Protocol" repos/worktrees/phenoSDK/main/src/pheno/ports --type py
rg "ports\." repos/worktrees/phenoSDK/main/src/pheno/adapters --type py | head -40
```
