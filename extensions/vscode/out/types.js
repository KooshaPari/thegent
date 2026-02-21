"use strict";
// @trace WL-117
// Shared wire-format types for thegent agent-server JSON-RPC 2.0 over stdio.
Object.defineProperty(exports, "__esModule", { value: true });
exports.PROTOCOL_METHODS = exports.JSONRPC_VERSION = void 0;
exports.isJsonRpcSuccess = isJsonRpcSuccess;
exports.isJsonRpcFailure = isJsonRpcFailure;
exports.isJsonRpcNotification = isJsonRpcNotification;
exports.isJsonRpcResponse = isJsonRpcResponse;
exports.JSONRPC_VERSION = "2.0";
// ─── Protocol methods ─────────────────────────────────────────────────────────
exports.PROTOCOL_METHODS = {
    healthCheck: "health/check",
    configRead: "config/read",
    sessionStart: "session/start",
    sessionResume: "session/resume",
    sessionList: "session/list",
    sessionRead: "session/read",
    turnSubmit: "turn/submit",
    turnCancel: "turn/cancel",
    approvalGrant: "approval/grant",
    approvalReject: "approval/reject",
};
// ─── Type guards ──────────────────────────────────────────────────────────────
function isJsonRpcSuccess(response) {
    return !("error" in response);
}
function isJsonRpcFailure(response) {
    return "error" in response;
}
function isJsonRpcNotification(msg) {
    if (typeof msg !== "object" || msg === null) {
        return false;
    }
    const m = msg;
    return (m["jsonrpc"] === exports.JSONRPC_VERSION &&
        typeof m["method"] === "string" &&
        !("id" in m));
}
function isJsonRpcResponse(msg) {
    if (typeof msg !== "object" || msg === null) {
        return false;
    }
    const m = msg;
    return m["jsonrpc"] === exports.JSONRPC_VERSION && "id" in m;
}
//# sourceMappingURL=types.js.map