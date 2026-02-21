"use strict";
// @trace WL-117
// Integration tests for AgentServerClient — uses an in-process mock child process
// that speaks the JSON-RPC 2.0 JSONL protocol.
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
const node_stream_1 = require("node:stream");
const agentServerClient_1 = require("../agentServerClient");
function buildMockProc() {
    const receivedLines = [];
    const emitter = new node_stream_1.EventEmitter();
    // Simulated stdout that we control
    const stdout = new node_stream_1.Readable({ read() { } });
    const stderr = new node_stream_1.Readable({ read() { } });
    const stdin = new node_stream_1.Writable({
        write(chunk, _encoding, callback) {
            const str = typeof chunk === "string" ? chunk : chunk.toString("utf8");
            for (const line of str.split("\n")) {
                if (line.trim().length > 0) {
                    receivedLines.push(line.trim());
                }
            }
            callback();
        },
    });
    const proc = {
        stdout,
        stderr,
        stdin,
        on(event, listener) {
            emitter.on(event, listener);
            return proc;
        },
        emit(event, ...args) {
            return emitter.emit(event, ...args);
        },
    };
    function sendToClient(line) {
        stdout.push(line + "\n");
    }
    function triggerClose() {
        emitter.emit("close");
    }
    return { proc, sendToClient, receivedLines, triggerClose };
}
const tests = [];
function test(name, fn) {
    tests.push({ name, fn });
}
async function runAll() {
    let passed = 0;
    let failed = 0;
    for (const { name, fn } of tests) {
        try {
            await fn();
            passed++;
            console.log(`  PASS: ${name}`);
        }
        catch (err) {
            failed++;
            console.error(`  FAIL: ${name}`);
            console.error("       ", err);
        }
    }
    console.log(`\nagentServerClient.test: ${passed} passed, ${failed} failed`);
    if (failed > 0) {
        process.exitCode = 1;
    }
}
// ─── Tests ────────────────────────────────────────────────────────────────────
test("healthCheck sends correct JSONL request", async () => {
    const { proc, sendToClient, receivedLines } = buildMockProc();
    const client = new agentServerClient_1.AgentServerClient(proc);
    // Respond after receiving
    const promise = client.healthCheck();
    // Wait for the request to be written
    await new Promise((resolve) => setImmediate(resolve));
    assert.ok(receivedLines.length > 0, "should have sent a line");
    const req = JSON.parse(receivedLines[0]);
    assert.equal(req.jsonrpc, "2.0");
    assert.equal(req.method, "health/check");
    sendToClient(JSON.stringify({ jsonrpc: "2.0", id: req.id, result: { status: "ok", service: "thegent-agent-server", transport: "stdio" } }));
    const result = await promise;
    assert.equal(result.status, "ok");
    assert.equal(result.service, "thegent-agent-server");
});
test("startSession returns session object", async () => {
    const { proc, sendToClient, receivedLines } = buildMockProc();
    const client = new agentServerClient_1.AgentServerClient(proc);
    const promise = client.startSession();
    await new Promise((resolve) => setImmediate(resolve));
    const req = JSON.parse(receivedLines[0]);
    assert.equal(req.method, "session/start");
    sendToClient(JSON.stringify({
        jsonrpc: "2.0",
        id: req.id,
        result: { session: { id: "session-0001", status: "active", created_index: 1, turn_ids: [] } },
    }));
    const session = await promise;
    assert.equal(session.id, "session-0001");
    assert.equal(session.status, "active");
});
test("listSessions returns array", async () => {
    const { proc, sendToClient, receivedLines } = buildMockProc();
    const client = new agentServerClient_1.AgentServerClient(proc);
    const promise = client.listSessions();
    await new Promise((resolve) => setImmediate(resolve));
    const req = JSON.parse(receivedLines[0]);
    assert.equal(req.method, "session/list");
    sendToClient(JSON.stringify({
        jsonrpc: "2.0",
        id: req.id,
        result: { sessions: [{ id: "session-0001", status: "active", created_index: 1, turn_ids: [] }] },
    }));
    const sessions = await promise;
    assert.ok(Array.isArray(sessions));
    assert.equal(sessions.length, 1);
    assert.equal(sessions[0].id, "session-0001");
});
test("resumeSession sends session_id param", async () => {
    const { proc, sendToClient, receivedLines } = buildMockProc();
    const client = new agentServerClient_1.AgentServerClient(proc);
    const promise = client.resumeSession("session-0001");
    await new Promise((resolve) => setImmediate(resolve));
    const req = JSON.parse(receivedLines[0]);
    assert.equal(req.method, "session/resume");
    assert.equal(req.params.session_id, "session-0001");
    sendToClient(JSON.stringify({
        jsonrpc: "2.0",
        id: req.id,
        result: { session: { id: "session-0001", status: "active", created_index: 1, turn_ids: [] } },
    }));
    const session = await promise;
    assert.equal(session.id, "session-0001");
});
test("submitTurn sends correct params without approval", async () => {
    const { proc, sendToClient, receivedLines } = buildMockProc();
    const client = new agentServerClient_1.AgentServerClient(proc);
    const promise = client.submitTurn("session-0001", "hello world");
    await new Promise((resolve) => setImmediate(resolve));
    const req = JSON.parse(receivedLines[0]);
    assert.equal(req.method, "turn/submit");
    assert.equal(req.params.session_id, "session-0001");
    assert.equal(req.params.input, "hello world");
    assert.equal(req.params.requires_approval, false);
    sendToClient(JSON.stringify({
        jsonrpc: "2.0",
        id: req.id,
        result: { turn: { id: "turn-0001", session_id: "session-0001", status: "completed", input: "hello world" } },
    }));
    const result = await promise;
    assert.equal(result.turn.id, "turn-0001");
});
test("submitTurn sends requires_approval=true", async () => {
    const { proc, sendToClient, receivedLines } = buildMockProc();
    const client = new agentServerClient_1.AgentServerClient(proc);
    const promise = client.submitTurn("session-0001", "risky", true);
    await new Promise((resolve) => setImmediate(resolve));
    const req = JSON.parse(receivedLines[0]);
    assert.equal(req.params.requires_approval, true);
    sendToClient(JSON.stringify({
        jsonrpc: "2.0",
        id: req.id,
        result: {
            turn: { id: "turn-0002", session_id: "session-0001", status: "awaiting_approval", input: "risky" },
            approval: { id: "approval-0001", status: "requested" },
        },
    }));
    const result = await promise;
    assert.equal(result.turn.status, "awaiting_approval");
    assert.ok(result.approval !== undefined);
    assert.equal(result.approval?.id, "approval-0001");
});
test("cancelTurn sends turn_id param", async () => {
    const { proc, sendToClient, receivedLines } = buildMockProc();
    const client = new agentServerClient_1.AgentServerClient(proc);
    const promise = client.cancelTurn("turn-0001");
    await new Promise((resolve) => setImmediate(resolve));
    const req = JSON.parse(receivedLines[0]);
    assert.equal(req.method, "turn/cancel");
    assert.equal(req.params.turn_id, "turn-0001");
    sendToClient(JSON.stringify({
        jsonrpc: "2.0",
        id: req.id,
        result: { turn: { id: "turn-0001", session_id: "session-0001", status: "cancelled", input: "x" } },
    }));
    const turn = await promise;
    assert.equal(turn.status, "cancelled");
});
test("grantApproval sends approval_id", async () => {
    const { proc, sendToClient, receivedLines } = buildMockProc();
    const client = new agentServerClient_1.AgentServerClient(proc);
    const promise = client.grantApproval("approval-0001");
    await new Promise((resolve) => setImmediate(resolve));
    const req = JSON.parse(receivedLines[0]);
    assert.equal(req.method, "approval/grant");
    assert.equal(req.params.approval_id, "approval-0001");
    sendToClient(JSON.stringify({
        jsonrpc: "2.0",
        id: req.id,
        result: {
            approval: { id: "approval-0001", status: "granted" },
            turn: { id: "turn-0001", session_id: "session-0001", status: "completed", input: "x" },
        },
    }));
    const result = await promise;
    assert.equal(result.approval.status, "granted");
    assert.equal(result.turn.status, "completed");
});
test("rejectApproval sends approval_id", async () => {
    const { proc, sendToClient, receivedLines } = buildMockProc();
    const client = new agentServerClient_1.AgentServerClient(proc);
    const promise = client.rejectApproval("approval-0001");
    await new Promise((resolve) => setImmediate(resolve));
    const req = JSON.parse(receivedLines[0]);
    assert.equal(req.method, "approval/reject");
    assert.equal(req.params.approval_id, "approval-0001");
    sendToClient(JSON.stringify({
        jsonrpc: "2.0",
        id: req.id,
        result: {
            approval: { id: "approval-0001", status: "rejected" },
            turn: { id: "turn-0001", session_id: "session-0001", status: "rejected", input: "x" },
        },
    }));
    const result = await promise;
    assert.equal(result.approval.status, "rejected");
    assert.equal(result.turn.status, "rejected");
});
test("protocol error response rejects promise", async () => {
    const { proc, sendToClient, receivedLines } = buildMockProc();
    const client = new agentServerClient_1.AgentServerClient(proc);
    const promise = client.listSessions();
    await new Promise((resolve) => setImmediate(resolve));
    const req = JSON.parse(receivedLines[0]);
    sendToClient(JSON.stringify({
        jsonrpc: "2.0",
        id: req.id,
        error: { code: -32001, message: "Session not found", data: { session_id: "x" } },
    }));
    await assert.rejects(promise, agentServerClient_1.AgentServerProtocolError);
});
test("approval/requested notification fires event", async () => {
    const { proc, sendToClient } = buildMockProc();
    const client = new agentServerClient_1.AgentServerClient(proc);
    const received = await new Promise((resolve) => {
        client.on("approval/requested", resolve);
        sendToClient(JSON.stringify({
            jsonrpc: "2.0",
            method: "approval/requested",
            params: { approval_id: "approval-0001", session_id: "session-0001", turn_id: "turn-0001" },
        }));
    });
    const params = received;
    assert.equal(params.approval_id, "approval-0001");
    assert.equal(params.session_id, "session-0001");
});
test("turn/started notification fires event", async () => {
    const { proc, sendToClient } = buildMockProc();
    const client = new agentServerClient_1.AgentServerClient(proc);
    const received = await new Promise((resolve) => {
        client.on("turn/started", resolve);
        sendToClient(JSON.stringify({
            jsonrpc: "2.0",
            method: "turn/started",
            params: { session_id: "session-0001", turn_id: "turn-0001" },
        }));
    });
    const params = received;
    assert.equal(params.turn_id, "turn-0001");
});
test("item/agentMessage/delta notification fires event", async () => {
    const { proc, sendToClient } = buildMockProc();
    const client = new agentServerClient_1.AgentServerClient(proc);
    const received = await new Promise((resolve) => {
        client.on("item/agentMessage/delta", resolve);
        sendToClient(JSON.stringify({
            jsonrpc: "2.0",
            method: "item/agentMessage/delta",
            params: { session_id: "s1", turn_id: "t1", delta: "hello" },
        }));
    });
    const params = received;
    assert.equal(params.delta, "hello");
});
test("dispose prevents further requests", async () => {
    const { proc } = buildMockProc();
    const client = new agentServerClient_1.AgentServerClient(proc);
    client.dispose();
    await assert.rejects(client.listSessions(), agentServerClient_1.AgentServerConnectionError);
});
test("process close event rejects pending requests", async () => {
    const { proc, triggerClose } = buildMockProc();
    const client = new agentServerClient_1.AgentServerClient(proc);
    const promise = client.listSessions();
    await new Promise((resolve) => setImmediate(resolve));
    triggerClose();
    await assert.rejects(promise, agentServerClient_1.AgentServerProtocolError);
});
test("context/budgetUpdated event fires from notifyContextBudget", () => {
    const { proc } = buildMockProc();
    const client = new agentServerClient_1.AgentServerClient(proc);
    let receivedRatio;
    client.on("context/budgetUpdated", (result) => {
        receivedRatio = result.context_usage_ratio;
    });
    client.notifyContextBudget({ session_id: "s1", turn_id: "t1", context_usage_ratio: 0.75 });
    assert.equal(receivedRatio, 0.75);
});
// Run
void runAll();
//# sourceMappingURL=agentServerClient.test.js.map