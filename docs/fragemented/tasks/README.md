# Task Documentation

This directory contains documentation for individual tasks in the Taskfile.

## Structure

Each task should have a markdown file with:
- Description
- Usage examples
- Dependencies
- Common issues
- Related tasks

## Example

See `setup.md` for an example task documentation.

## Adding Documentation

1. Create a file named `<task-name>.md` in this directory
2. Follow the template below
3. Update the task-help script to reference it

## Template

```markdown
# Task: <task-name>

## Description

Brief description of what this task does.

## Usage

\`\`\`bash
task <task-name>
task <task-name> --option value
\`\`\`

## Examples

\`\`\`bash
# Example 1
task <task-name>

# Example 2
task <task-name> --flag
\`\`\`

## Dependencies

- `task:dependency1`
- `task:dependency2`

## Common Issues

### Issue 1
**Problem**: Description of issue
**Solution**: How to fix it

## Related Tasks

- `task:related1`
- `task:related2`
```
