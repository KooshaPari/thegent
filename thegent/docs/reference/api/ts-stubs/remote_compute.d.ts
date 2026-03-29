// Auto-generated TypeScript declarations for remote_compute
// Source: generate-api-docs.py

export declare class RemoteComputeClient {
  constructor(remote_host: string, remote_port: number);
  execute_remote(command: string, cwd: any): void;
  transfer_files(local_path: string, remote_path: string): void;
}

export declare function execute_remote(command: string, cwd: any): void;
export declare function transfer_files(local_path: string, remote_path: string): void;
