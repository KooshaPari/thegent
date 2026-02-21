// Auto-generated TypeScript declarations for helios_bridge
// Source: generate-api-docs.py

export declare class HeliosShieldBridge {
  constructor();
  connect(): void;
  send_command(command: string): void;
  test_connection(): void;
}

export declare function connect(): void;
export declare function send_command(command: string): void;
export declare function test_connection(): void;
