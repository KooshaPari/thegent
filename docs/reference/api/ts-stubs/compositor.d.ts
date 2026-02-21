// Auto-generated TypeScript declarations for compositor
// Source: generate-api-docs.py

export declare class CacheStats extends TypedDict {
}

export declare class Compositor {
  constructor(ttl: number, error_ttl: number, maxsize: number);
  add_panel(panel: Panel): void;
  cache_stats(): void;
  errored_panels(): void;
  get_panel(name: string): void;
  invalidate(panel_name: any): void;
  panel_names(): void;
  recover_all(): void;
  recover_panel(name: string): void;
  remove_panel(name: string): void;
  render(): void;
  render_all(): void;
  render_panel(name: string): void;
}

export declare class CompositorProfiler {
  constructor();
  clear(): void;
  get_average(panel_id: any): void;
  get_slowest(n: number): void;
  record(profile: RenderProfile): void;
  record_count(): void;
  report(): void;
}

export declare class Panel {
  has_error(): void;
  recover(): void;
  render(): void;
}

export declare class RenderProfile {
}

export declare function add_panel(panel: Panel): void;
export declare function cache_stats(): void;
export declare function clear(): void;
export declare function errored_panels(): void;
export declare function get_average(panel_id: any): void;
export declare function get_panel(name: string): void;
export declare function get_slowest(n: number): void;
export declare function has_error(): void;
export declare function invalidate(panel_name: any): void;
export declare function panel_names(): void;
export declare function record(profile: RenderProfile): void;
export declare function record_count(): void;
export declare function recover(): void;
export declare function recover_all(): void;
export declare function recover_panel(name: string): void;
export declare function remove_panel(name: string): void;
export declare function render(): void;
export declare function render_all(): void;
export declare function render_panel(name: string): void;
export declare function report(): void;
