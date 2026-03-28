# fanta_main API Reference

> **Source**: `src/thegent/fanta_main.py`

Fanta CLI: Antigma-backed interactive harness with dex/clode/roid-style aliases.

---

## anen_composer

```python
anen_composer(ctx: typer.Context) -> None
```

---

## anen_config

```python
anen_config(legacy: bool)
```

Open interactive config manager (translation layer for existing config backends).

---

## anen_doctor

```python
anen_doctor(fix: bool, dry_run: bool)
```

Run thegent doctor (harness-equiv).

---

## anen_exec

```python
anen_exec(ctx: typer.Context, model: str, prompt: str)
```

Run Antigma headlessly with model alias mapping.

---

## anen_flash

```python
anen_flash(ctx: typer.Context) -> None
```

---

## anen_free

```python
anen_free(ctx: typer.Context) -> None
```

---

## anen_glm

```python
anen_glm(ctx: typer.Context) -> None
```

---

## anen_haiku

```python
anen_haiku(ctx: typer.Context) -> None
```

---

## anen_high

```python
anen_high(ctx: typer.Context) -> None
```

---

## anen_max

```python
anen_max(ctx: typer.Context) -> None
```

---

## anen_mini

```python
anen_mini(ctx: typer.Context) -> None
```

---

## anen_opus

```python
anen_opus(ctx: typer.Context) -> None
```

---

## anen_sonnet

```python
anen_sonnet(ctx: typer.Context) -> None
```

---

## anen_step

```python
anen_step(ctx: typer.Context) -> None
```

---

## anen_ultra

```python
anen_ultra(ctx: typer.Context) -> None
```

---

## anen_xhigh

```python
anen_xhigh(ctx: typer.Context) -> None
```

---

## default_anen

```python
default_anen(ctx: typer.Context)
```

Default fanta behavior: flash model (gemini-3-flash).

---

## install_links

```python
install_links(bin_dir: Path, force: bool)
```

Install/update fanta/antigma -> thegent-shims under ~/.local/bin.

---

