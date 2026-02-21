// Auto-generated TypeScript declarations for lanes
// Source: generate-api-docs.py

export declare class Lane extends StrEnum {
}

export declare class LaneModel {
  check_capacity(lane: string, active_count: number, total_capacity: number): void;
  get_priority(lane: string): void;
  get_urgency(lane: string): void;
  is_protected(lane: string): void;
  sort_tasks(tasks: Array<Record<(str, Any)>>): void;
}

export declare function check_capacity(lane: string, active_count: number, total_capacity: number): void;
export declare function get_priority(lane: string): void;
export declare function get_urgency(lane: string): void;
export declare function is_protected(lane: string): void;
export declare function sort_tasks(tasks: Array<Record<(str, Any)>>): void;
