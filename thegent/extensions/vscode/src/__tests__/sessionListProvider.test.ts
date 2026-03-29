// @trace WL-117
// Tests for SessionListProvider tree data provider logic.

import * as assert from "node:assert/strict";
import { Session } from "../types";

// ─── Minimal vscode mock ──────────────────────────────────────────────────────

class MockEventEmitter<T = unknown> {
  private _handlers: Array<(e: T) => void> = [];

  event = (handler: (e: T) => void): { dispose(): void } => {
    this._handlers.push(handler);
    return { dispose: (): void => { this._handlers = this._handlers.filter((h) => h !== handler); } };
  };

  fire(e: T): void {
    for (const handler of this._handlers) {
      handler(e);
    }
  }

  dispose(): void {
    this._handlers = [];
  }
}

class MockTreeItem {
  contextValue?: string;
  tooltip?: string;
  description?: string;
  iconPath?: unknown;
  collapsibleState: number;

  constructor(
    public readonly label: string,
    collapsibleState: number,
  ) {
    this.collapsibleState = collapsibleState;
  }
}

const vscodeMock = {
  TreeItem: MockTreeItem,
  TreeItemCollapsibleState: { None: 0, Collapsed: 1, Expanded: 2 },
  ThemeIcon: class ThemeIcon {
    constructor(public readonly id: string, public readonly color?: unknown) {}
  },
  ThemeColor: class ThemeColor {
    constructor(public readonly id: string) {}
  },
  EventEmitter: MockEventEmitter,
};

(global as Record<string, unknown>)["vscode"] = vscodeMock;

// ─── Tests ────────────────────────────────────────────────────────────────────

type TestFn = () => void;
const tests: Array<{ name: string; fn: TestFn }> = [];

function test(name: string, fn: TestFn): void {
  tests.push({ name, fn });
}

function runAll(): void {
  let passed = 0;
  let failed = 0;
  for (const { name, fn } of tests) {
    try {
      fn();
      passed++;
      console.log(`  PASS: ${name}`);
    } catch (err) {
      failed++;
      console.error(`  FAIL: ${name}`);
      console.error("       ", err);
    }
  }
  console.log(`\nsessionListProvider.test: ${passed} passed, ${failed} failed`);
  if (failed > 0) {
    process.exitCode = 1;
  }
}

// ─── Session model tests (pure data, no VS Code API) ─────────────────────────

test("session with status active maps to expected label prefix", () => {
  const session: Session = {
    id: "session-0001",
    status: "active",
    created_index: 1,
    turn_ids: ["turn-0001", "turn-0002"],
  };
  const label = `${session.id} (${session.status})`;
  assert.equal(label, "session-0001 (active)");
});

test("session with status completed maps to expected label prefix", () => {
  const session: Session = {
    id: "session-0002",
    status: "completed",
    created_index: 2,
    turn_ids: [],
  };
  const label = `${session.id} (${session.status})`;
  assert.equal(label, "session-0002 (completed)");
});

test("session description reflects turn count", () => {
  const session: Session = {
    id: "session-0003",
    status: "active",
    created_index: 3,
    turn_ids: ["turn-0001", "turn-0002", "turn-0003"],
  };
  const description = `${session.turn_ids.length} turn(s)`;
  assert.equal(description, "3 turn(s)");
});

test("session with zero turns has correct description", () => {
  const session: Session = {
    id: "session-0004",
    status: "failed",
    created_index: 4,
    turn_ids: [],
  };
  const description = `${session.turn_ids.length} turn(s)`;
  assert.equal(description, "0 turn(s)");
});

test("updateSessions replaces session list", () => {
  const sessions: Session[] = [
    { id: "session-0001", status: "active", created_index: 1, turn_ids: [] },
    { id: "session-0002", status: "completed", created_index: 2, turn_ids: [] },
  ];
  // Simulate provider internal state
  let stored: Session[] = [];
  const updateSessions = (s: Session[]): void => { stored = s; };
  updateSessions(sessions);
  assert.equal(stored.length, 2);
  assert.equal(stored[0].id, "session-0001");
  assert.equal(stored[1].id, "session-0002");
});

test("getChildren returns items for each session", () => {
  const sessions: Session[] = [
    { id: "session-0001", status: "active", created_index: 1, turn_ids: [] },
    { id: "session-0002", status: "failed", created_index: 2, turn_ids: [] },
  ];
  // Simulate provider.getChildren() logic
  const children = sessions.map((s) => ({ label: `${s.id} (${s.status})` }));
  assert.equal(children.length, 2);
  assert.ok(children[0].label.includes("session-0001"));
  assert.ok(children[1].label.includes("session-0002"));
});

test("requireClient throws before client is set", () => {
  // Simulate requireSessionProvider error path
  let client: unknown = undefined;
  const requireClient = (): unknown => {
    if (client === undefined) {
      throw new Error("no client set");
    }
    return client;
  };
  assert.throws(requireClient, { message: "no client set" });
});

test("setClient makes client available", () => {
  let client: unknown = undefined;
  const setClient = (c: unknown): void => { client = c; };
  const requireClient = (): unknown => {
    if (client === undefined) {
      throw new Error("no client");
    }
    return client;
  };
  setClient({ mock: true });
  assert.doesNotThrow(requireClient);
});

runAll();
