// Auto-generated usage examples for remote_executor
// Source: generate-api-docs.py

import { RemoteExecutor, RemoteExecutorError, RemoteResult, RemoteTask, available_nodes, execute } from "./remote_executor";

// Create a RemoteExecutor instance
const remoteexecutor = new RemoteExecutor(undefined as unknown as any, undefined as unknown as any);
remoteexecutor.available_nodes();
remoteexecutor.execute(undefined as unknown as RemoteTask);

// Create a RemoteExecutorError instance
const remoteexecutorerror = new RemoteExecutorError();

// Create a RemoteResult instance
const remoteresult = new RemoteResult();

// Create a RemoteTask instance
const remotetask = new RemoteTask();

// Call available_nodes
available_nodes(undefined as unknown as any);
// Call execute
execute(undefined as unknown as any, undefined as unknown as RemoteTask);
