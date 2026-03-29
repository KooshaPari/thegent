// Auto-generated usage examples for alerting
// Source: generate-api-docs.py

import { Alert, AlertManager, alert_budget_exceeded, alert_cooldown_triggered, alert_high_latency, alert_provider_error, clear_pending_alerts, get_alert_manager, get_pending_alerts, reset_alert_manager, send_alert, to_json, webhook_url } from "./alerting";

// Create a Alert instance
const alert = new Alert();
alert.to_json();

// Create a AlertManager instance
const alertmanager = new AlertManager(undefined as unknown as any, "example_min_severity");
alertmanager.alert_budget_exceeded(0, 0);
alertmanager.alert_cooldown_triggered("example_model", "example_provider", 0, "example_reason");
alertmanager.alert_high_latency("example_model", 0, 0, undefined as unknown as any);
alertmanager.alert_provider_error("example_provider", "example_error", "example_model", false);
alertmanager.clear_pending_alerts();
alertmanager.get_pending_alerts();
alertmanager.send_alert(undefined as unknown as Alert);
alertmanager.webhook_url();

// Call alert_budget_exceeded
alert_budget_exceeded(undefined as unknown as any, 0, 0);
// Call alert_cooldown_triggered
alert_cooldown_triggered(undefined as unknown as any, "example_model", "example_provider", 0, "example_reason");
// Call alert_high_latency
alert_high_latency(undefined as unknown as any, "example_model", 0, 0, undefined as unknown as any);
// Call alert_provider_error
alert_provider_error(undefined as unknown as any, "example_provider", "example_error", "example_model", false);
// Call clear_pending_alerts
clear_pending_alerts(undefined as unknown as any);
// Call get_alert_manager
get_alert_manager();
// Call get_pending_alerts
get_pending_alerts(undefined as unknown as any);
// Call reset_alert_manager
reset_alert_manager();
// Call send_alert
send_alert(undefined as unknown as any, undefined as unknown as Alert);
// Call to_json
to_json(undefined as unknown as any);
// Call webhook_url
webhook_url(undefined as unknown as any);
