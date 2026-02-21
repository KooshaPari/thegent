// Auto-generated TypeScript declarations for sandboxing
// Source: generate-api-docs.py

export declare class AutonomyEnforcer {
  classify_operation(command: string, target: string): void;
}

export declare class SandboxProvider {
  constructor();
  wrap_command(command: Array<string>, tier: number): void;
}

export declare function classify_operation(command: string, target: string): void;
export declare function wrap_command(command: Array<string>, tier: number): void;
