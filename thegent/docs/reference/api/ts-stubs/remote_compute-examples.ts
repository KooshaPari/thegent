// Auto-generated usage examples for remote_compute
// Source: generate-api-docs.py

import { RemoteComputeClient, execute_remote, transfer_files } from "./remote_compute";

// Create a RemoteComputeClient instance
const remotecomputeclient = new RemoteComputeClient("example_remote_host", 0);
remotecomputeclient.execute_remote("example_command", undefined as unknown as any);
remotecomputeclient.transfer_files("example_local_path", "example_remote_path");

// Call execute_remote
execute_remote(undefined as unknown as any, "example_command", undefined as unknown as any);
// Call transfer_files
transfer_files(undefined as unknown as any, "example_local_path", "example_remote_path");
