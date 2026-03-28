# json_schema API Reference

> **Source**: `src/thegent/utils/routing_impl/guardrails/json_schema.py`

GW-52: JSON schema output validation guardrail.

Validates LLM response content against a JSON schema provided in the request.

# @trace FR-GUARD-052

---

## SchemaValidationResult

---

## extract_llm_response_content

```python
extract_llm_response_content(response: dict)
```

Extract the assistant message content from an OpenAI-style response dict.

Returns the content string from ``response["choices"][0]["message"]["content"]``
or an empty string if the path does not exist.

**Parameters**:

- `response`: Parsed LLM response dict.

**Returns**: Content string, or ``""`` on any missing key.

---

## extract_response_schema

```python
extract_response_schema(body: dict)
```

Extract a JSON schema from an OpenAI-style request body.

Returns the schema dict if ``response_format.type == "json_schema"`` and a
``schema`` key is present.  Returns ``None`` otherwise.

**Parameters**:

- `body`: The parsed request body dict.

**Returns**: Schema dict or ``None``.

---

## validate_json_output

```python
validate_json_output(content: str, schema: dict)
```

Validate LLM response content string against a JSON schema.

Parses ``content`` as JSON.  If parsing succeeds and ``jsonschema`` is
available, validates the parsed object against ``schema``.  When
``jsonschema`` is not installed only JSON-parse validity is checked.

**Parameters**:

- `content`: Raw text from the LLM response.
- `schema`: JSON Schema dict to validate against.

**Returns**: SchemaValidationResult with ``valid``, ``errors``, and ``parsed``.

---

