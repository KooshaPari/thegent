// Auto-generated usage examples for fast_websocket
// Source: generate-api-docs.py

import { FastWebSocket, close_sync, connect_sync, recv_sync, send_sync, websocket_connect_sync } from "./fast_websocket";

// Create a FastWebSocket instance
const fastwebsocket = new FastWebSocket("example_url");
fastwebsocket.close_sync();
fastwebsocket.connect_sync();
fastwebsocket.recv_sync();
fastwebsocket.send_sync(undefined as unknown as any);

// Call close_sync
close_sync(undefined as unknown as any);
// Call connect_sync
connect_sync(undefined as unknown as any);
// Call recv_sync
recv_sync(undefined as unknown as any);
// Call send_sync
send_sync(undefined as unknown as any, undefined as unknown as any);
// Call websocket_connect_sync
websocket_connect_sync("example_url");
