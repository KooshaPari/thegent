# Initialize-Project Template

This template provides a unified way to scaffold new projects with all the necessary tooling.

## Usage

### Prerequisites

Install copier:
```bash
pip install copier
```

### Initialize a New Project

```bash
# Copy the template to a new directory
copier copy thegent/templates/initialize-project ./my-new-project

# Or with all options specified
copier copy thegent/templates/initialize-project ./my-new-project \
  --project-name="my-project" \
  --project-description="A description" \
  --language="python" \
  --include-docs=true \
  --include-ci=true
```

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `project_name` | str | my-project | Name of the project |
| `project_description` | str | A new project | One-line description |
| `author` | str | "" | Author name |
| `language` | str | python | Primary language (python, typescript, go, bash) |
| `include_docs` | bool | true | Include VitePress docsite |
| `include_ci` | bool | true | Include GitHub Actions CI |
| `include_docker` | bool | false | Include Docker setup |
| `include_hooks` | bool | true | Include pre-commit hooks |

## What Gets Created

Based on selected options, creates:

- `CLAUDE.md` - Project-specific agent instructions
- `Taskfile.yml` - Build automation with language-specific tasks
- `.gitignore` - Language-appropriate gitignore
- `.env.example` - Environment variable template
- `docs/` - VitePress docsite (if include_docs=true)
- `.github/workflows/ci.yml` - CI workflow (if include_ci=true)
- `hooks/` - Pre-commit hooks (if include_hooks=true)
- Docker files (if include_docker=true)

## Manual Template Selection

Instead of using copier, you can manually select templates:

```bash
# CLAUDE.md template
cp thegent/templates/claude/CLAUDE.md.template ./CLAUDE.md

# Language-specific Taskfile
cp thegent/templates/python/Taskfile.python.yml ./Taskfile.yml

# Quality templates
cp thegent/templates/quality/ruff.toml ./ruff.toml
cp thegent/templates/quality/pyproject.template.toml ./pyproject.toml

# VitePress
cp -r thegent/templates/vitepress-full/* ./docs/.vitepress/
```
