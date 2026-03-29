// Auto-generated TypeScript declarations for runner
// Source: generate-api-docs.py

export declare class MAIFRunner {
  constructor();
  record_run_end(run_id: string, status: string, output_summary: string): void;
  record_run_start(run_id: string, owner: string, prompt: string, agent: string): void;
}

export declare function record_run_end(run_id: string, status: string, output_summary: string): void;
export declare function record_run_start(run_id: string, owner: string, prompt: string, agent: string): void;
