// Auto-generated TypeScript declarations for cli_compositor
// Source: generate-api-docs.py

export declare class CliCompositor {
  constructor(console: any);
  add_progress(name: string, total: number, description: string): void;
  add_status_line(name: string, content_fn: Callable<(Any, str)>): void;
  complete_progress(name: string): void;
  progress_panel_names(): void;
  remove_progress(name: string): void;
  remove_status_line(name: string): void;
  render(): void;
  status_panel_names(): void;
  update_progress(name: string, advance: number, description: any): void;
}

export declare class ProgressPanel {
  advance(amount: number, description: any): void;
  complete(): void;
  render(): void;
}

export declare class StatusPanel {
  render(): void;
}

export declare function add_progress(name: string, total: number, description: string): void;
export declare function add_status_line(name: string, content_fn: Callable<(Any, str)>): void;
export declare function advance(amount: number, description: any): void;
export declare function complete(): void;
export declare function complete_progress(name: string): void;
export declare function make_cli_compositor(): void;
export declare function progress_panel_names(): void;
export declare function remove_progress(name: string): void;
export declare function remove_status_line(name: string): void;
export declare function render(): void;
export declare function status_panel_names(): void;
export declare function update_progress(name: string, advance: number, description: any): void;
