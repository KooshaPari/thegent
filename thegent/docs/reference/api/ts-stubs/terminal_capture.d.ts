// Auto-generated TypeScript declarations for terminal_capture
// Source: generate-api-docs.py

export declare class CaptureResult {
}

export declare class TerminalCapture {
  capture_by_pid(pid: number, n: number): void;
  capture_last_n_lines(n: number, pane_id: any): void;
}

export declare function capture_by_pid(pid: number, n: number): void;
export declare function capture_last_n_lines(n: number, pane_id: any): void;
