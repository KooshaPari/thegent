# Cross-Surface Command Map

Mapping of commands across CLI, MCP, and API surfaces.

## Server Operations

| Action | CLI | MCP | API |
|--------|-----|-----|-----|
| Start | `helios run` | `server.start()` | `POST /server/start` |
| Stop | `helios stop` | `server.stop()` | `POST /server/stop` |
| Restart | `helios restart` | `server.restart()` | `POST /server/restart` |
| Status | `helios status` | `server.status()` | `GET /server/status` |

## Provider Management

| Action | CLI | MCP | API |
|--------|-----|-----|-----|
| List | `helios providers list` | `providers.list()` | `GET /providers` |
| Add | `helios providers add <name>` | `providers.add(name)` | `POST /providers` |
| Remove | `helios providers remove <name>` | `providers.remove(name)` | `DELETE /providers/{id}` |
| Get | `helios providers get <name>` | `providers.get(name)` | `GET /providers/{id}` |

## Auth Operations

| Action | CLI | MCP | API |
|--------|-----|-----|-----|
| Login | `helios login <provider>` | `auth.login(provider)` | `POST /auth/login` |
| Logout | `helios logout <provider>` | `auth.logout(provider)` | `POST /auth/logout` |
| Refresh | `helios auth refresh` | `auth.refresh()` | `POST /auth/refresh` |
| Status | `helios auth status` | `auth.status()` | `GET /auth/status` |

## Model Operations

| Action | CLI | MCP | API |
|--------|-----|-----|-----|
| List | `helios models list` | `models.list()` | `GET /models` |
| Get | `helios models get <model>` | `models.get(model)` | `GET /models/{id}` |
| Search | `helios models search <query>` | `models.search(query)` | `GET /models/search?q=` |

## Config Operations

| Action | CLI | MCP | API |
|--------|-----|-----|-----|
| Get | `helios config get <key>` | `config.get(key)` | `GET /config/{key}` |
| Set | `helios config set <key> <value>` | `config.set(key, value)` | `PUT /config/{key}` |
| List | `helios config list` | `config.list()` | `GET /config` |
| Export | `helios config export` | `config.export()` | `GET /config/export` |
| Import | `helios config import <file>` | `config.import(file)` | `POST /config/import` |
