// Auto-generated TypeScript declarations for priority_queue
// Source: generate-api-docs.py

export declare class QueuedRun {
  from_lane(run_id: string, lane_name: string, metadata: any): void;
}

export declare class RunPriorityQueue {
  constructor();
  cancel(run_id: string): void;
  drain(): void;
  empty(): void;
  full(): void;
  get(block: boolean, timeout: any): void;
  get_nowait(): void;
  peek(): void;
  put(run: QueuedRun, block: boolean, timeout: any): void;
  put_nowait(run: QueuedRun): void;
  qsize(): void;
}

export declare function cancel(run_id: string): void;
export declare function drain(): void;
export declare function empty(): void;
export declare function from_lane(run_id: string, lane_name: string, metadata: any): void;
export declare function full(): void;
export declare function get(block: boolean, timeout: any): void;
export declare function get_nowait(): void;
export declare function make_priority_queue(maxsize: number): void;
export declare function peek(): void;
export declare function put(run: QueuedRun, block: boolean, timeout: any): void;
export declare function put_nowait(run: QueuedRun): void;
export declare function qsize(): void;
