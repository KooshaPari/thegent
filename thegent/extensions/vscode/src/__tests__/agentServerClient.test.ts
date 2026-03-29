// @trace WL-117
// Integration tests for AgentServerClient — uses an in-process mock child process
// that speaks the JSON-RPC 2.0 JSONL protocol.

import * as assert from "node:assert/strict";
import { EventEmitter, Readable, Writable } from "node:stream";
import { AgentServerClient, AgentServerProtocolError, AgentServerConnectionError } from "../agentServerClient";

// ─── Mock child process ───────────────────────────────────────────────────────

interface MockChildProc {
  stdout: Readable;
  stderr: Readable;
  stdin: Writable;
  on(event: string, listener: (...args: unknown[]) => void): MockChildProc;
  emit(event: string, ...args: unknown[]): boolean;
}

function buildMockProc(): {
  proc: MockChildProc;
  sendToClient: (line: string) => void;
  receivedLines: string[];
  triggerClose: () => void;
} {
  const receivedLines: string[] = [];
  const emitter = new EventEmitter();

  // Simulated stdout that we control
  const stdout = new Readable({ read(): void { /* no-op */ } });
  const stderr = new Readable({ read(): void { /* no-op */ } });

  const stdin = new Writable({
    write(
      chunk: Buffer | string,
      _encoding: string,
      callback: (err?: Error | null) => void,
    ): void {
      const str = typeof chunk === "string" ? chunk : chunk.toString("utf8");
      for (const line of str.split("\n")) {
        if (line.trim().length > 0) {
          receivedLines.push(line.trim());
        }
      }
      callback();
    },
  });

  const proc: MockChildProc = {
    stdout,
    stderr,
    stdin,
    on(event: string, listener: (...args: unknown[]) => void): MockChildProc {
      emitter.on(event, listener);
      return proc;
    },
    emit(event: string, ...args: unknown[]): boolean {
      return emitter.emit(event, ...args);
    },
  };

  function sendToClient(line: string): void {
    stdout.push(line + "\n");
  }

  function triggerClose(): void {
    emitter.emit("close");
  }

  return { proc, sendToClient, receivedLines, triggerClose };
}

// ─── Test runner ──────────────────────────────────────────────────────────────

type TestFn = () => Promise<void> | void;
const tests: Array<{ name: string; fn: TestFn }> = [];

function test(name: string, fn: TestFn): void {
  tests.push({ name, fn });
}

async function runAll(): Promise<void> {
  let passed = 0;
  let failed = 0;
  for (const { name, fn } of tests) {
    try {
      await fn();
      passed++;
      console.log(`  PASS: ${name}`);
    } catch (err) {
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
  const client = new AgentServerClient(proc as never);

  // Respond after receiving
  const promise = client.healthCheck();

  // Wait for the request to be written
  await new Promise<void>((resolve) => setImmediate(resolve));
  assert.ok(receivedLines.length > 0, "should have sent a line");

  const req = JSON.parse(receivedLines[0]) as { jsonrpc: string; id: number; method: string };
  assert.equal(req.jsonrpc, "2.0");
  assert.equal(req.method, "health/check");

  sendToClient(JSON.stringify({ jsonrpc: "2.0", id: req.id, result: { status: "ok", service: "thegent-agent-server", transport: "stdio" } }));
  const result = await promise;
  assert.equal(result.status, "ok");
  assert.equal(result.service, "thegent-agent-server");
});

test("startSession returns session object", async () => {
  const { proc, sendToClient, receivedLines } = buildMockProc();
  const client = new AgentServerClient(proc as never);

  const promise = client.startSession();
  await new Promise<void>((resolve) => setImmediate(resolve));

  const req = JSON.parse(receivedLines[0]) as { id: number; method: string };
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
  const client = new AgentServerClient(proc as never);

  const promise = client.listSessions();
  await new Promise<void>((resolve) => setImmediate(resolve));

  const req = JSON.parse(receivedLines[0]) as { id: number; method: string };
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
  const client = new AgentServerClient(proc as never);

  const promise = client.resumeSession("session-0001");
  await new Promise<void>((resolve) => setImmediate(resolve));

  const req = JSON.parse(receivedLines[0]) as { id: number; method: string; params: { session_id: string } };
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
  const client = new AgentServerClient(proc as never);

  const promise = client.submitTurn("session-0001", "hello world");
  await new Promise<void>((resolve) => setImmediate(resolve));

  const req = JSON.parse(receivedLines[0]) as {
    id: number;
    method: string;
    params: { session_id: string; input: string; requires_approval: boolean };
  };
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
  const client = new AgentServerClient(proc as never);

  const promise = client.submitTurn("session-0001", "risky", true);
  await new Promise<void>((resolve) => setImmediate(resolve));

  const req = JSON.parse(receivedLines[0]) as {
    id: number;
    params: { requires_approval: boolean };
  };
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
  const client = new AgentServerClient(proc as never);

  const promise = client.cancelTurn("turn-0001");
  await new Promise<void>((resolve) => setImmediate(resolve));

  const req = JSON.parse(receivedLines[0]) as {
    id: number;
    method: string;
    params: { turn_id: string };
  };
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
  const client = new AgentServerClient(proc as never);

  const promise = client.grantApproval("approval-0001");
  await new Promise<void>((resolve) => setImmediate(resolve));

  const req = JSON.parse(receivedLines[0]) as {
    id: number;
    method: string;
    params: { approval_id: string };
  };
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
  const client = new AgentServerClient(proc as never);

  const promise = client.rejectApproval("approval-0001");
  await new Promise<void>((resolve) => setImmediate(resolve));

  const req = JSON.parse(receivedLines[0]) as {
    id: number;
    method: string;
    params: { approval_id: string };
  };
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
  const client = new AgentServerClient(proc as never);

  const promise = client.listSessions();
  await new Promise<void>((resolve) => setImmediate(resolve));

  const req = JSON.parse(receivedLines[0]) as { id: number };
  sendToClient(JSON.stringify({
    jsonrpc: "2.0",
    id: req.id,
    error: { code: -32001, message: "Session not found", data: { session_id: "x" } },
  }));

  await assert.rejects(promise, AgentServerProtocolError);
});

test("approval/requested notification fires event", async () => {
  const { proc, sendToClient } = buildMockProc();
  const client = new AgentServerClient(proc as never);

  const received = await new Promise<unknown>((resolve) => {
    client.on("approval/requested", resolve);
    sendToClient(JSON.stringify({
      jsonrpc: "2.0",
      method: "approval/requested",
      params: { approval_id: "approval-0001", session_id: "session-0001", turn_id: "turn-0001" },
    }));
  });

  const params = received as { approval_id: string; session_id: string; turn_id: string };
  assert.equal(params.approval_id, "approval-0001");
  assert.equal(params.session_id, "session-0001");
});

test("turn/started notification fires event", async () => {
  const { proc, sendToClient } = buildMockProc();
  const client = new AgentServerClient(proc as never);

  const received = await new Promise<unknown>((resolve) => {
    client.on("turn/started", resolve);
    sendToClient(JSON.stringify({
      jsonrpc: "2.0",
      method: "turn/started",
      params: { session_id: "session-0001", turn_id: "turn-0001" },
    }));
  });

  const params = received as { session_id: string; turn_id: string };
  assert.equal(params.turn_id, "turn-0001");
});

test("item/agentMessage/delta notification fires event", async () => {
  const { proc, sendToClient } = buildMockProc();
  const client = new AgentServerClient(proc as never);

  const received = await new Promise<unknown>((resolve) => {
    client.on("item/agentMessage/delta", resolve);
    sendToClient(JSON.stringify({
      jsonrpc: "2.0",
      method: "item/agentMessage/delta",
      params: { session_id: "s1", turn_id: "t1", delta: "hello" },
    }));
  });

  const params = received as { delta: string };
  assert.equal(params.delta, "hello");
});

test("dispose prevents further requests", async () => {
  const { proc } = buildMockProc();
  const client = new AgentServerClient(proc as never);
  client.dispose();

  await assert.rejects(client.listSessions(), AgentServerConnectionError);
});

test("process close event rejects pending requests", async () => {
  const { proc, triggerClose } = buildMockProc();
  const client = new AgentServerClient(proc as never);

  const promise = client.listSessions();
  await new Promise<void>((resolve) => setImmediate(resolve));
  triggerClose();

  await assert.rejects(promise, AgentServerProtocolError);
});

test("context/budgetUpdated event fires from notifyContextBudget", () => {
  const { proc } = buildMockProc();
  const client = new AgentServerClient(proc as never);

  let receivedRatio: number | undefined;
  client.on("context/budgetUpdated", (result: { context_usage_ratio: number }) => {
    receivedRatio = result.context_usage_ratio;
  });

  client.notifyContextBudget({ session_id: "s1", turn_id: "t1", context_usage_ratio: 0.75 });
  assert.equal(receivedRatio, 0.75);
});

// Run
void runAll();
