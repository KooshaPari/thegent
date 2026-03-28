# CLI Framework

Shared CLI component interfaces and base types for the Phenotype ecosystem.

## Modules

- `src/command.py` - Base command interface
- `src/parser.py` - Argument parsing with flags and positional args
- `src/registry.py` - Command registration
- `src/help.py` - Help text generation

## Usage

```python
from cli_framework import BaseCommand, CommandRegistry, command

# Define a command using the decorator
@command("greet", "Print a greeting")
class GreetCommand(BaseCommand):
    def __init__(self):
        self.add_flag("name", short="n", description="Name to greet")
        self.add_flag("verbose", short="v", description="Verbose output")

    def execute(self, args: list[str]) -> int:
        name = self.get_flag("name") or "World"
        print(f"Hello, {name}!")
        return 0

# Register and run
registry = CommandRegistry()
registry.register(GreetCommand)
registry.run("greet", ["--name", "Alice"])
```

## Standards

- All commands must implement `BaseCommand`
- Use the `@command` decorator for automatic registration
- Commands are registered at module load time

## Migration from Inline CLI Code

If you have duplicated CLI code in your repos, migrate like this:

**Before (duplicated pattern):**
```python
# In your_repo/src/commands.py
class MyCommand:
    name = "my-command"
    def execute(self, args):
        # ... implementation
```

**After (using lib):**
```python
# In your_repo/src/commands.py
# REPLACED: Use libs/cli-framework instead
# from libs.cli_framework import BaseCommand, command
```

Then import from `libs.cli_framework` in your main CLI entry point.

## Integration Points

Consuming repos should import from:
```python
# Import path for consuming repos
from libs.cli_framework import BaseCommand, CommandRegistry
```
