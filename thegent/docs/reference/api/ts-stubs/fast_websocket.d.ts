// Auto-generated TypeScript declarations for fast_websocket
// Source: generate-api-docs.py

export declare class FastWebSocket {
  constructor(url: string);
  close_sync(): void;
  connect_sync(): void;
  recv_sync(): void;
  send_sync(data: any): void;
}

export declare function close_sync(): void;
export declare function connect_sync(): void;
export declare function recv_sync(): void;
export declare function send_sync(data: any): void;
export declare function websocket_connect_sync(url: string): void;
