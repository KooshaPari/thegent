// Auto-generated TypeScript declarations for components
// Source: generate-api-docs.py

export declare class FooterStatusBar extends Static {
  render(): void;
  update_pane_info(count: number, focus_id: string): void;
}

export declare class HeaderWidget extends Static {
  constructor(title: string, version: string);
  render(): void;
}

export declare class MetricsPanel extends Container {
  constructor();
  compose(): void;
  update_metric(key: string, value: string): void;
  update_metrics(metrics: Record<(str, str)>): void;
}

export declare class OutputWidget extends ScrollableContainer {
  constructor(title: string);
  clear(): void;
  compose(): void;
  get_line_count(): void;
  write(text: string, style: string, timestamp: boolean): void;
}

export declare class ProgressIndicator extends Static {
  render(): void;
  update_progress(current: number, total: number, message: any): void;
}

export declare class SidebarWidget extends ScrollableContainer {
  constructor();
  add_agent(agent_id: string, name: string, status: string): void;
  compose(): void;
  update_agent_status(agent_id: string, status: string): void;
  update_session_info(session_id: string, start_time: string, uptime: string): void;
}

export declare class StatusWidget extends Container {
  constructor();
  compose(): void;
  start_timer(): void;
  stop_timer(): void;
  update_status(status: string, model: any, tokens: any): void;
  watch_elapsed_time(elapsed: number): void;
  watch_model(model: string): void;
  watch_status(status: string): void;
  watch_tokens_used(tokens: number): void;
}

export declare function add_agent(agent_id: string, name: string, status: string): void;
export declare function clear(): void;
export declare function compose(): void;
export declare function get_line_count(): void;
export declare function render(): void;
export declare function start_timer(): void;
export declare function stop_timer(): void;
export declare function update_agent_status(agent_id: string, status: string): void;
export declare function update_metric(key: string, value: string): void;
export declare function update_metrics(metrics: Record<(str, str)>): void;
export declare function update_pane_info(count: number, focus_id: string): void;
export declare function update_progress(current: number, total: number, message: any): void;
export declare function update_session_info(session_id: string, start_time: string, uptime: string): void;
export declare function update_status(status: string, model: any, tokens: any): void;
export declare function watch_elapsed_time(elapsed: number): void;
export declare function watch_model(model: string): void;
export declare function watch_status(status: string): void;
export declare function watch_tokens_used(tokens: number): void;
export declare function write(text: string, style: string, timestamp: boolean): void;
