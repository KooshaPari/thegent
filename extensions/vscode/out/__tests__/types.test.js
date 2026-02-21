"use strict";
// @trace WL-117
// Integration tests for wire-format type guards and protocol constants.
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const assert = __importStar(require("node:assert/strict"));
const types_1 = require("../types");
// ─── isJsonRpcSuccess ─────────────────────────────────────────────────────────
{
    const success = {
        jsonrpc: "2.0",
        id: 1,
        result: { foo: "bar" },
    };
    assert.ok((0, types_1.isJsonRpcSuccess)(success), "should identify success response");
}
{
    const failure = {
        jsonrpc: "2.0",
        id: 1,
        error: { code: -32601, message: "Method not found" },
    };
    assert.ok(!(0, types_1.isJsonRpcSuccess)(failure), "should not identify failure as success");
}
// ─── isJsonRpcFailure ─────────────────────────────────────────────────────────
{
    const failure = {
        jsonrpc: "2.0",
        id: null,
        error: { code: -32700, message: "Parse error" },
    };
    assert.ok((0, types_1.isJsonRpcFailure)(failure), "should identify failure response");
}
{
    const success = { jsonrpc: "2.0", id: 1, result: {} };
    assert.ok(!(0, types_1.isJsonRpcFailure)(success), "should not identify success as failure");
}
// ─── isJsonRpcNotification ────────────────────────────────────────────────────
{
    const notification = {
        jsonrpc: "2.0",
        method: "turn/started",
        params: { session_id: "session-0001", turn_id: "turn-0001" },
    };
    assert.ok((0, types_1.isJsonRpcNotification)(notification), "should identify notification (no id)");
}
{
    // A response has an id — not a notification
    const response = { jsonrpc: "2.0", id: 1, result: {} };
    assert.ok(!(0, types_1.isJsonRpcNotification)(response), "should not identify response as notification");
}
// ─── isJsonRpcResponse ────────────────────────────────────────────────────────
{
    const response = { jsonrpc: "2.0", id: 1, result: {} };
    assert.ok((0, types_1.isJsonRpcResponse)(response), "should identify response (has id)");
}
{
    const notification = { jsonrpc: "2.0", method: "turn/started" };
    assert.ok(!(0, types_1.isJsonRpcResponse)(notification), "should not identify notification as response");
}
// ─── PROTOCOL_METHODS ─────────────────────────────────────────────────────────
{
    assert.equal(types_1.PROTOCOL_METHODS.healthCheck, "health/check");
    assert.equal(types_1.PROTOCOL_METHODS.configRead, "config/read");
    assert.equal(types_1.PROTOCOL_METHODS.sessionStart, "session/start");
    assert.equal(types_1.PROTOCOL_METHODS.sessionResume, "session/resume");
    assert.equal(types_1.PROTOCOL_METHODS.sessionList, "session/list");
    assert.equal(types_1.PROTOCOL_METHODS.sessionRead, "session/read");
    assert.equal(types_1.PROTOCOL_METHODS.turnSubmit, "turn/submit");
    assert.equal(types_1.PROTOCOL_METHODS.turnCancel, "turn/cancel");
    assert.equal(types_1.PROTOCOL_METHODS.approvalGrant, "approval/grant");
    assert.equal(types_1.PROTOCOL_METHODS.approvalReject, "approval/reject");
}
console.log("types.test: all assertions passed");
//# sourceMappingURL=types.test.js.map