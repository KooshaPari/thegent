# alerting API Reference

> **Source**: `src/thegent/routing/alerting.py`

Alerting integration for LiteLLM routing.

Provides alert management for routing events including budget exceeded,
high latency, and provider errors. Supports webhook notifications.

---

## Alert

Routing alert.

### Methods

#### Alert.to_json

Serialize alert to JSON dict.

```python
to_json(self)
```

---

## AlertManager

Manage routing alerts with webhook support.

### Methods

#### AlertManager.__init__

Initialize alert manager.

Args:
    webhook_url: Optional webhook URL for alert delivery.
    min_severity: Minimum severity level to send (info, warning, critical).

```python
__init__(self, webhook_url, min_severity)
```

#### AlertManager.alert_budget_exceeded

Create and send budget exceeded alert.

Args:
    daily_spend: Current daily spend in USD.
    budget: Configured budget limit in USD.

Returns:
    The created Alert.

```python
alert_budget_exceeded(self, daily_spend, budget)
```

#### AlertManager.alert_cooldown_triggered

Create and send cooldown triggered alert.

Args:
    model: The model in cooldown.
    provider: The provider.
    cooldown_seconds: Duration of cooldown.
    reason: Why cooldown was triggered.

Returns:
    The created Alert.

```python
alert_cooldown_triggered(self, model, provider, cooldown_seconds, reason)
```

#### AlertManager.alert_high_latency

Create and send high latency alert.

Args:
    model: The model that had high latency.
    latency_ms: Observed latency in milliseconds.
    threshold_ms: Configured threshold in milliseconds.
    provider: Optional provider name.

Returns:
    The created Alert.

```python
alert_high_latency(self, model, latency_ms, threshold_ms, provider)
```

#### AlertManager.alert_provider_error

Create and send provider error alert.

Args:
    provider: The provider that had an error.
    error: Error message or type.
    model: The model being used.
    is_rate_limit: Whether this was a rate limit error.

Returns:
    The created Alert.

```python
alert_provider_error(self, provider, error, model, is_rate_limit)
```

#### AlertManager.clear_pending_alerts

Clear pending alerts list.

```python
clear_pending_alerts(self)
```

#### AlertManager.get_pending_alerts

Get list of alerts that weren't sent (no webhook configured).

```python
get_pending_alerts(self)
```

#### AlertManager.send_alert

Send alert to configured webhook.

Args:
    alert: The alert to send.

Returns:
    True if sent successfully, False otherwise.

```python
send_alert(self, alert)
```

#### AlertManager.webhook_url

Configured webhook URL.

```python
webhook_url(self)
```

---

## alert_budget_exceeded

Create and send budget exceeded alert.

Args:
    daily_spend: Current daily spend in USD.
    budget: Configured budget limit in USD.

Returns:
    The created Alert.

```python
alert_budget_exceeded(self, daily_spend, budget)
```

---

## alert_cooldown_triggered

Create and send cooldown triggered alert.

Args:
    model: The model in cooldown.
    provider: The provider.
    cooldown_seconds: Duration of cooldown.
    reason: Why cooldown was triggered.

Returns:
    The created Alert.

```python
alert_cooldown_triggered(self, model, provider, cooldown_seconds, reason)
```

---

## alert_high_latency

Create and send high latency alert.

Args:
    model: The model that had high latency.
    latency_ms: Observed latency in milliseconds.
    threshold_ms: Configured threshold in milliseconds.
    provider: Optional provider name.

Returns:
    The created Alert.

```python
alert_high_latency(self, model, latency_ms, threshold_ms, provider)
```

---

## alert_provider_error

Create and send provider error alert.

Args:
    provider: The provider that had an error.
    error: Error message or type.
    model: The model being used.
    is_rate_limit: Whether this was a rate limit error.

Returns:
    The created Alert.

```python
alert_provider_error(self, provider, error, model, is_rate_limit)
```

---

## clear_pending_alerts

Clear pending alerts list.

```python
clear_pending_alerts(self)
```

---

## get_alert_manager

Get global alert manager instance.

Initializes with settings from config on first call.

---

## get_pending_alerts

Get list of alerts that weren't sent (no webhook configured).

```python
get_pending_alerts(self)
```

---

## reset_alert_manager

Reset the global alert manager (useful for testing).

---

## send_alert

Send alert to configured webhook.

Args:
    alert: The alert to send.

Returns:
    True if sent successfully, False otherwise.

```python
send_alert(self, alert)
```

---

## to_json

Serialize alert to JSON dict.

```python
to_json(self)
```

---

## webhook_url

Configured webhook URL.

```python
webhook_url(self)
```

---

