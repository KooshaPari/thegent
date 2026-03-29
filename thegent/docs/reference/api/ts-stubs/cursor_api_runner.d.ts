// Auto-generated TypeScript declarations for cursor_api_runner
// Source: generate-api-docs.py

export declare class CursorApiRunner extends AgentRunner {
  constructor(settings: any, model: string);
  run(prompt: string, cwd: any, mode: string, timeout: number): void;
}

export declare function run(prompt: string, cwd: any, mode: string, timeout: number): RunResult;
