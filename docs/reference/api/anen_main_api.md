# anen_main API Reference

> **Source**: `src/thegent/anen_main.py`

Anen CLI: Antigma-backed interactive harness with dex/clode/roid-style aliases.

---

## anen_composer

```python
anen_composer(ctx: typer.Context) -> None
```

---

## anen_doctor

```python
anen_doctor(fix: bool)
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

## default_anen

```python
default_anen(ctx: typer.Context)
```

Default anen behavior: flash model (gemini-3-flash).

---

## install_links

```python
install_links(bin_dir: Path, force: bool)
```

Install/update fanta/antigma -&gt; thegent-shims under ~/.local/bin.

---

