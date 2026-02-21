// Auto-generated TypeScript declarations for alerting
// Source: generate-api-docs.py

export declare class Alert {
  to_json(): void;
}

export declare class AlertManager {
  constructor(webhook_url: any, min_severity: string);
  alert_budget_exceeded(daily_spend: number, budget: number): void;
  alert_cooldown_triggered(model: string, provider: string, cooldown_seconds: number, reason: string): void;
  alert_high_latency(model: string, latency_ms: number, threshold_ms: number, provider: any): void;
  alert_provider_error(provider: string, error: string, model: string, is_rate_limit: boolean): void;
  clear_pending_alerts(): void;
  get_pending_alerts(): void;
  send_alert(alert: Alert): void;
  webhook_url(): void;
}

export declare function alert_budget_exceeded(daily_spend: number, budget: number): void;
export declare function alert_cooldown_triggered(model: string, provider: string, cooldown_seconds: number, reason: string): void;
export declare function alert_high_latency(model: string, latency_ms: number, threshold_ms: number, provider: any): void;
export declare function alert_provider_error(provider: string, error: string, model: string, is_rate_limit: boolean): void;
export declare function clear_pending_alerts(): void;
export declare function get_alert_manager(): void;
export declare function get_pending_alerts(): void;
export declare function reset_alert_manager(): void;
export declare function send_alert(alert: Alert): void;
export declare function to_json(): void;
export declare function webhook_url(): void;
