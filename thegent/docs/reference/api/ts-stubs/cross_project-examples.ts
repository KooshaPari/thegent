// Auto-generated usage examples for cross_project
// Source: generate-api-docs.py

import { CrossProjectIpc, CrossProjectIpcServer, IpcMessage, ack, broadcast, from_dict, from_json, list_pending, receive, receive_broadcast, receive_topic, register, reply, run, send, set_default_handler, stop, to_json } from "./cross_project";

// Create a CrossProjectIpc instance
const crossprojectipc = new CrossProjectIpc("example_agent_id", "example_project_root");
crossprojectipc.ack("example_msg_id");
crossprojectipc.broadcast("example_topic", undefined as unknown as Record<string, unknown>);
crossprojectipc.list_pending();
crossprojectipc.receive(0);
crossprojectipc.receive_broadcast(0);
crossprojectipc.receive_topic("example_topic", 0);
crossprojectipc.reply(undefined as unknown as IpcMessage, undefined as unknown as Record<string, unknown>);
crossprojectipc.send("example_recipient", "example_topic", undefined as unknown as Record<string, unknown>);

// Create a CrossProjectIpcServer instance
const crossprojectipcserver = new CrossProjectIpcServer(undefined as unknown as CrossProjectIpc);
crossprojectipcserver.register("example_topic", undefined as unknown as Callable<(Any, None)>);
crossprojectipcserver.run(undefined as unknown as any);
crossprojectipcserver.set_default_handler(undefined as unknown as Callable<(Any, None)>);
crossprojectipcserver.stop();

// Create a IpcMessage instance
const ipcmessage = new IpcMessage();
ipcmessage.from_dict(undefined as unknown as Record<string, unknown>);
ipcmessage.from_json("example_text");
ipcmessage.to_json();

// Call ack
ack(undefined as unknown as any, "example_msg_id");
// Call broadcast
broadcast(undefined as unknown as any, "example_topic", undefined as unknown as Record<string, unknown>);
// Call from_dict
from_dict(undefined as unknown as any, undefined as unknown as Record<string, unknown>);
// Call from_json
from_json(undefined as unknown as any, "example_text");
// Call list_pending
list_pending(undefined as unknown as any);
// Call receive
receive(undefined as unknown as any, 0);
// Call receive_broadcast
receive_broadcast(undefined as unknown as any, 0);
// Call receive_topic
receive_topic(undefined as unknown as any, "example_topic", 0);
// Call register
register(undefined as unknown as any, "example_topic", undefined as unknown as Callable<(Any, None)>);
// Call reply
reply(undefined as unknown as any, undefined as unknown as IpcMessage, undefined as unknown as Record<string, unknown>);
// Call run
run(undefined as unknown as any, undefined as unknown as any);
// Call send
send(undefined as unknown as any, "example_recipient", "example_topic", undefined as unknown as Record<string, unknown>);
// Call set_default_handler
set_default_handler(undefined as unknown as any, undefined as unknown as Callable<(Any, None)>);
// Call stop
stop(undefined as unknown as any);
// Call to_json
to_json(undefined as unknown as any);
