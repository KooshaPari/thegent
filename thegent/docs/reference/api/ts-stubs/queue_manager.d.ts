// Auto-generated TypeScript declarations for queue_manager
// Source: generate-api-docs.py

export declare class QueueManager {
  constructor(queue_file: string, state_file: any);
  get_month_files(month: string, location: any): void;
  get_next_month(): void;
  get_summary(): void;
  get_unprocessed_files(month: any, location: any): void;
  list_months(): void;
  load_queue(): void;
  mark_file_failed(filepath: string): void;
  mark_file_processed(filepath: string): void;
  mark_file_skipped(filepath: string): void;
  mark_month_complete(month: string, location: any): void;
}

export declare class QueueState {
  from_dict(data: Record<string, unknown>): void;
  mark_failed(filepath: string): void;
  mark_processed(filepath: string): void;
  mark_skipped(filepath: string): void;
  to_dict(): void;
}

export declare function from_dict(data: Record<string, unknown>): void;
export declare function get_month_files(month: string, location: any): void;
export declare function get_next_month(): void;
export declare function get_summary(): void;
export declare function get_unprocessed_files(month: any, location: any): void;
export declare function list_months(): void;
export declare function load_queue(): void;
export declare function mark_failed(filepath: string): void;
export declare function mark_file_failed(filepath: string): void;
export declare function mark_file_processed(filepath: string): void;
export declare function mark_file_skipped(filepath: string): void;
export declare function mark_month_complete(month: string, location: any): void;
export declare function mark_processed(filepath: string): void;
export declare function mark_skipped(filepath: string): void;
export declare function to_dict(): void;
