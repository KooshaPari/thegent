// Auto-generated TypeScript declarations for cross_project
// Source: generate-api-docs.py

export declare class CrossProjectIpc {
  constructor(agent_id: string, project_root: string);
  ack(msg_id: string): void;
  broadcast(topic: string, payload: Record<string, unknown>): void;
  list_pending(): void;
  receive(timeout: number): void;
  receive_broadcast(timeout: number): void;
  receive_topic(topic: string, timeout: number): void;
  reply(original: IpcMessage, payload: Record<string, unknown>): void;
  send(recipient: string, topic: string, payload: Record<string, unknown>): void;
}

export declare class CrossProjectIpcServer {
  constructor(ipc: CrossProjectIpc);
  register(topic: string, handler: Callable<(Any, None)>): void;
  run(max_iterations: any): void;
  set_default_handler(handler: Callable<(Any, None)>): void;
  stop(): void;
}

export declare class IpcMessage {
  from_dict(data: Record<string, unknown>): void;
  from_json(text: string): void;
  to_json(): void;
}

export declare function ack(msg_id: string): void;
export declare function broadcast(topic: string, payload: Record<string, unknown>): void;
export declare function from_dict(data: Record<string, unknown>): void;
export declare function from_json(text: string): void;
export declare function list_pending(): void;
export declare function receive(timeout: number): void;
export declare function receive_broadcast(timeout: number): void;
export declare function receive_topic(topic: string, timeout: number): void;
export declare function register(topic: string, handler: Callable<(Any, None)>): void;
export declare function reply(original: IpcMessage, payload: Record<string, unknown>): void;
export declare function run(max_iterations: any): void;
export declare function send(recipient: string, topic: string, payload: Record<string, unknown>): void;
export declare function set_default_handler(handler: Callable<(Any, None)>): void;
export declare function stop(): void;
export declare function to_json(): void;
