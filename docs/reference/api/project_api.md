# project API Reference

> **Source**: `src/thegent/cli/apps/project.py`

Project CLI app - project management commands.

---

## install_callback

```python
install_callback(ctx: typer.Context, target: Optional[str], mode: Optional[str], dry_run: bool, verbose: bool, url: Optional[str], install_service: bool)
```

Legacy install command - routes to thegent.install.run_install.

---

## install_project

```python
install_project(mode: str, project: str, template: str, name: str, tenant: str, json: bool, reconcile: bool, register: bool, install_runtime: bool, dry_run: bool, legacy_mode: str)
```

Install/brownfield project migration.

---

## project_migrate

Entry point for project migration (used by CLI tests).

---

## project_scaffold

Entry point for project scaffolding (used by CLI tests).

---

## scaffold_brownfield_cmd

```python
scaffold_brownfield_cmd(project: str, mode: str, template: str, name: str, tenant: str, json: bool, register: bool, install_runtime: bool, dry_run: bool, reconcile: bool)
```

Scaffold brownfield project.

---

## scaffold_greenfield_cmd

```python
scaffold_greenfield_cmd(destination: str, profile: str, name: str, description: str, include_act: bool, include_qa_tools: bool, include_pm_tools: bool, language: str, register: bool, install_runtime: bool, tenant: str, dry_run: bool, json: bool)
```

Scaffold new greenfield project.

---

