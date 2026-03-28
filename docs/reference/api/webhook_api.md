# webhook API Reference

> **Source**: `src/thegent/utils/routing_impl/guardrails/webhook.py`

GW-53: Webhook guardrail — POST to external URL for verdict.

Sends request data to a webhook URL, expects {verdict: "allow"|"block", transformedData?: {...}}.

# @trace FR-GUARD-053

---

## WebhookGuardrailConfig

---

## WebhookVerdict

---

## call_webhook_guardrail

```python
call_webhook_guardrail(config: WebhookGuardrailConfig, payload: dict)
```

POST payload to the webhook URL and return its verdict.

On timeout or any connection error the ``config.on_failure`` verdict is
returned so that routing can proceed (or block) as configured.

**Parameters**:

- `config`: Webhook configuration including URL, timeout, secret, and
on-failure policy.
- `payload`: JSON-serialisable dict to POST as the request body.

**Returns**: WebhookVerdict with ``verdict`` ("allow" or "block"),
optional ``transformed_data`` from the response, and an ``error``
string when the call failed.

---

