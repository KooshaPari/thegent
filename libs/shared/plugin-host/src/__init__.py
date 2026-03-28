# Plugin Host — Shared Interface

Provides a plugin system where the host defines ports (traits/interfaces) and plugins implement them.
Plugins are discovered via entry points and loaded dynamically.

## Usage

```python
from shared.plugin_host import PluginHost, PluginContext

host = PluginHost()
host.register_port(MyPortInterface)

# Load plugins from entry points
host.discover_plugins("myapp.plugins")

# Execute plugin by port
result = host.execute("my_port_name", payload={"key": "value"})
```

## Architecture

```
PluginHost
├── Ports registry (what plugins must implement)
├── Plugin registry (discovered plugins and their ports)
└── Execution engine (call plugins by port name)

Plugin
├── name
├── version
└── ports (which ports this plugin implements)
```

## Port Definition Example

```python
from shared.plugin_host import port

@port
class ConfigLoader:
    def load(self, path: str) -> dict:
        ...
```

## Lifecycle

1. **Register ports** - Define interfaces plugins must implement
2. **Discover plugins** - Load plugins from entry points
3. **Validate plugins** - Ensure plugins implement required ports
4. **Execute plugins** - Call plugin methods via port
5. **Unload plugins** - Cleanup when done
