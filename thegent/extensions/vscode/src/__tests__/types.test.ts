// @trace WL-117
// Integration tests for wire-format type guards and protocol constants.

import * as assert from "node:assert/strict";
import {
  PROTOCOL_METHODS,
  isJsonRpcSuccess,
  isJsonRpcFailure,
  isJsonRpcNotification,
  isJsonRpcResponse,
  JsonRpcSuccess,
  JsonRpcFailure,
  JsonRpcNotification,
} from "../types";

// ─── isJsonRpcSuccess ─────────────────────────────────────────────────────────

{
  const success: JsonRpcSuccess<{ foo: string }> = {
    jsonrpc: "2.0",
    id: 1,
    result: { foo: "bar" },
  };
  assert.ok(isJsonRpcSuccess(success), "should identify success response");
}

{
  const failure: JsonRpcFailure = {
    jsonrpc: "2.0",
    id: 1,
    error: { code: -32601, message: "Method not found" },
  };
  assert.ok(!isJsonRpcSuccess(failure), "should not identify failure as success");
}

// ─── isJsonRpcFailure ─────────────────────────────────────────────────────────

{
  const failure: JsonRpcFailure = {
    jsonrpc: "2.0",
    id: null,
    error: { code: -32700, message: "Parse error" },
  };
  assert.ok(isJsonRpcFailure(failure), "should identify failure response");
}

{
  const success: JsonRpcSuccess = { jsonrpc: "2.0", id: 1, result: {} };
  assert.ok(!isJsonRpcFailure(success), "should not identify success as failure");
}

// ─── isJsonRpcNotification ────────────────────────────────────────────────────

{
  const notification: JsonRpcNotification = {
    jsonrpc: "2.0",
    method: "turn/started",
    params: { session_id: "session-0001", turn_id: "turn-0001" },
  };
  assert.ok(
    isJsonRpcNotification(notification as unknown as Record<string, unknown>),
    "should identify notification (no id)",
  );
}

{
  // A response has an id — not a notification
  const response = { jsonrpc: "2.0", id: 1, result: {} };
  assert.ok(
    !isJsonRpcNotification(response),
    "should not identify response as notification",
  );
}

// ─── isJsonRpcResponse ────────────────────────────────────────────────────────

{
  const response = { jsonrpc: "2.0", id: 1, result: {} };
  assert.ok(isJsonRpcResponse(response), "should identify response (has id)");
}

{
  const notification = { jsonrpc: "2.0", method: "turn/started" };
  assert.ok(!isJsonRpcResponse(notification), "should not identify notification as response");
}

// ─── PROTOCOL_METHODS ─────────────────────────────────────────────────────────

{
  assert.equal(PROTOCOL_METHODS.healthCheck, "health/check");
  assert.equal(PROTOCOL_METHODS.configRead, "config/read");
  assert.equal(PROTOCOL_METHODS.sessionStart, "session/start");
  assert.equal(PROTOCOL_METHODS.sessionResume, "session/resume");
  assert.equal(PROTOCOL_METHODS.sessionList, "session/list");
  assert.equal(PROTOCOL_METHODS.sessionRead, "session/read");
  assert.equal(PROTOCOL_METHODS.turnSubmit, "turn/submit");
  assert.equal(PROTOCOL_METHODS.turnCancel, "turn/cancel");
  assert.equal(PROTOCOL_METHODS.approvalGrant, "approval/grant");
  assert.equal(PROTOCOL_METHODS.approvalReject, "approval/reject");
}

console.log("types.test: all assertions passed");
