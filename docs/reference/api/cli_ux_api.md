# cli_ux API Reference

> **Source**: `src/thegent/infra/cli_ux.py`

CLI UX improvements: command suggestions, interactive prompts, and better help.

This module provides utilities for improving the command-line user experience
with suggestions, better formatting, and interactive elements.

---

## display_command_examples

```python
display_command_examples(command: str, examples: list[dict[(str, str)]])
```

Display command examples in a table.

**Parameters**:

- `command`: Command name
- `examples`: List of example dicts with 'description' and 'command' keys

---

## display_command_suggestion

```python
display_command_suggestion(command: str, suggestions: list[str])
```

Display command suggestions in a helpful format.

**Parameters**:

- `command`: The command that was not found
- `suggestions`: List of suggested commands

---

## format_command_help

```python
format_command_help(command: str, description: str, examples: Any)
```

Format command help with examples.

**Parameters**:

- `command`: Command name
- `description`: Command description
- `examples`: List of example usage strings

**Returns**: Formatted help string

---

## format_error_with_suggestion

```python
format_error_with_suggestion(error: Exception, command: Any)
```

Format an error with command suggestions if applicable.

**Parameters**:

- `error`: The error that occurred
- `command`: The command that caused the error (if applicable)

---

## interactive_confirm

```python
interactive_confirm(message: str, default: bool)
```

Interactive confirmation prompt with better formatting.

**Parameters**:

- `message`: Confirmation message
- `default`: Default value

**Returns**: True if confirmed, False otherwise

---

## print_command_header

```python
print_command_header(command: str, description: str)
```

Print a formatted command header.

**Parameters**:

- `command`: Command name
- `description`: Command description

---

## print_section_header

```python
print_section_header(title: str)
```

Print a formatted section header.

**Parameters**:

- `title`: Section title

---

## suggest_command

```python
suggest_command(command: str, commands: Any)
```

Suggest similar commands for a typo.

**Parameters**:

- `command`: The command that was not found
- `commands`: List of available commands (default: THGENT_COMMANDS)

**Returns**: List of suggested commands, sorted by similarity

---

