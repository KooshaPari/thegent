// Auto-generated TypeScript declarations for remote_executor
// Source: generate-api-docs.py

export declare class RemoteExecutor {
  constructor(nodes: any, ssh_user: any);
  available_nodes(): void;
  execute(task: RemoteTask): void;
}

export declare class RemoteExecutorError extends Exception {
}

export declare class RemoteResult {
}

export declare class RemoteTask {
}

export declare function available_nodes(): void;
export declare function execute(task: RemoteTask): void;
