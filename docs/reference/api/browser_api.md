# browser API Reference

> **Source**: `src/thegent/cli/apps/browser.py`

Agent browser stream: launch, doctor, and journey management.

---

## browser_doctor

---

## browser_install

```python
browser_install(force: bool) -> None
```

---

## browser_launch

```python
browser_launch(browser: str, headless: bool, cdp_port: int, url: Any) -> None
```

---

## journey_add

```python
journey_add(name: str, url: str, kind: str, notes: Any) -> None
```

---

## journey_list

---

## journey_open

```python
journey_open(name: str, browser: str, headless: bool, cdp_port: int) -> None
```

---

