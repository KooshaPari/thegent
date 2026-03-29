// Auto-generated TypeScript declarations for identity_proxy
// Source: generate-api-docs.py

export declare class SSHIdentityProxy {
  constructor(proxy_socket_path: string);
  get_env(): void;
  start(): void;
  stop(): void;
}

export declare function get_env(): void;
export declare function start(): void;
export declare function stop(): void;
