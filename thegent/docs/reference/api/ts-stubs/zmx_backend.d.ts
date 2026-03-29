// Auto-generated TypeScript declarations for zmx_backend
// Source: generate-api-docs.py

export declare class SessionBackend extends Protocol {
  attach(session_name: string): void;
  available(): void;
  capture(session_name: string, last_lines: number): void;
  create(session_name: string, cmd: Array<string>): void;
  kill(session_name: string): void;
  list(): void;
  name(): void;
}

export declare class ZmxBackend {
  constructor(zmx_bin: string);
  attach(session_name: string): void;
  available(): void;
  capture(session_name: string, last_lines: number): void;
  create(session_name: string, cmd: Array<string>): void;
  kill(session_name: string): void;
  list(): void;
  name(): void;
}

export declare class ZmxSession {
}

export declare function attach(session_name: string): void;
export declare function available(): void;
export declare function capture(session_name: string, last_lines: number): void;
export declare function create(session_name: string, cmd: Array<string>): void;
export declare function kill(session_name: string): void;
export declare function list(): void;
export declare function name(): string;
export declare function resolve_session_backend(backend_override: any): void;
