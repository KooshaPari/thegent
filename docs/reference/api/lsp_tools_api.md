# lsp_tools API Reference

> **Source**: `src/thegent/mcp/lsp_tools.py`

WL-109: MCP-facing LSP tool adapters with strict input/output contracts.

---

## Diagnostic

Typed representation of a single LSP diagnostic item.

---

## HoverInfo

Typed representation of LSP hover result for a source position.

---

## LspToolAdapter

Protocol for pluggable LSP backends used by MCP tool wrappers.

**Inherits from**: `Protocol`

### Methods

#### LspToolAdapter.diagnostics

```python
diagnostics(self: Any)
```

---

#### LspToolAdapter.hover

```python
hover(self: Any)
```

---

#### LspToolAdapter.symbol_lookup

```python
symbol_lookup(self: Any)
```

---

---

## SymbolInfo

Typed representation of a single LSP symbol match.

---

## _PythonAstAdapter

Concrete local Python backend for WL-109 default diagnostics/symbol/hover.

### Methods

#### _PythonAstAdapter.diagnostics

```python
diagnostics(self: Any)
```

---

#### _PythonAstAdapter.hover

```python
hover(self: Any)
```

---

#### _PythonAstAdapter.symbol_lookup

```python
symbol_lookup(self: Any)
```

---

---

## _UnavailableAdapter

### Methods

#### _UnavailableAdapter.diagnostics

```python
diagnostics(self: Any)
```

---

#### _UnavailableAdapter.hover

```python
hover(self: Any)
```

---

#### _UnavailableAdapter.symbol_lookup

```python
symbol_lookup(self: Any)
```

---

---

## diagnostics

```python
diagnostics(self: Any) -> list[dict[(str, Any)]]
```

---

## hover

```python
hover(self: Any) -> Any
```

---

## lsp_diagnostics

```python
lsp_diagnostics(file_path: str, adapter: Any)
```

Return normalized diagnostics for a file path.

---

## lsp_hover

```python
lsp_hover(file_path: str, line: int, character: int, adapter: Any)
```

Return normalized hover info for a source position.

---

## lsp_symbol_lookup

```python
lsp_symbol_lookup(symbol_name: str, file_path: Any, adapter: Any)
```

Return normalized symbol lookup results.

---

## symbol_lookup

```python
symbol_lookup(self: Any) -> list[dict[(str, Any)]]
```

---

