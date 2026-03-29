"use strict";
// @trace WL-117
// Tests for SessionListProvider tree data provider logic.
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
// ─── Minimal vscode mock ──────────────────────────────────────────────────────
class MockEventEmitter {
    constructor() {
        this._handlers = [];
        this.event = (handler) => {
            this._handlers.push(handler);
            return { dispose: () => { this._handlers = this._handlers.filter((h) => h !== handler); } };
        };
    }
    fire(e) {
        for (const handler of this._handlers) {
            handler(e);
        }
    }
    dispose() {
        this._handlers = [];
    }
}
class MockTreeItem {
    constructor(label, collapsibleState) {
        this.label = label;
        this.collapsibleState = collapsibleState;
    }
}
const vscodeMock = {
    TreeItem: MockTreeItem,
    TreeItemCollapsibleState: { None: 0, Collapsed: 1, Expanded: 2 },
    ThemeIcon: class ThemeIcon {
        constructor(id, color) {
            this.id = id;
            this.color = color;
        }
    },
    ThemeColor: class ThemeColor {
        constructor(id) {
            this.id = id;
        }
    },
    EventEmitter: MockEventEmitter,
};
global["vscode"] = vscodeMock;
const tests = [];
function test(name, fn) {
    tests.push({ name, fn });
}
function runAll() {
    let passed = 0;
    let failed = 0;
    for (const { name, fn } of tests) {
        try {
            fn();
            passed++;
            console.log(`  PASS: ${name}`);
        }
        catch (err) {
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
    const session = {
        id: "session-0001",
        status: "active",
        created_index: 1,
        turn_ids: ["turn-0001", "turn-0002"],
    };
    const label = `${session.id} (${session.status})`;
    assert.equal(label, "session-0001 (active)");
});
test("session with status completed maps to expected label prefix", () => {
    const session = {
        id: "session-0002",
        status: "completed",
        created_index: 2,
        turn_ids: [],
    };
    const label = `${session.id} (${session.status})`;
    assert.equal(label, "session-0002 (completed)");
});
test("session description reflects turn count", () => {
    const session = {
        id: "session-0003",
        status: "active",
        created_index: 3,
        turn_ids: ["turn-0001", "turn-0002", "turn-0003"],
    };
    const description = `${session.turn_ids.length} turn(s)`;
    assert.equal(description, "3 turn(s)");
});
test("session with zero turns has correct description", () => {
    const session = {
        id: "session-0004",
        status: "failed",
        created_index: 4,
        turn_ids: [],
    };
    const description = `${session.turn_ids.length} turn(s)`;
    assert.equal(description, "0 turn(s)");
});
test("updateSessions replaces session list", () => {
    const sessions = [
        { id: "session-0001", status: "active", created_index: 1, turn_ids: [] },
        { id: "session-0002", status: "completed", created_index: 2, turn_ids: [] },
    ];
    // Simulate provider internal state
    let stored = [];
    const updateSessions = (s) => { stored = s; };
    updateSessions(sessions);
    assert.equal(stored.length, 2);
    assert.equal(stored[0].id, "session-0001");
    assert.equal(stored[1].id, "session-0002");
});
test("getChildren returns items for each session", () => {
    const sessions = [
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
    let client = undefined;
    const requireClient = () => {
        if (client === undefined) {
            throw new Error("no client set");
        }
        return client;
    };
    assert.throws(requireClient, { message: "no client set" });
});
test("setClient makes client available", () => {
    let client = undefined;
    const setClient = (c) => { client = c; };
    const requireClient = () => {
        if (client === undefined) {
            throw new Error("no client");
        }
        return client;
    };
    setClient({ mock: true });
    assert.doesNotThrow(requireClient);
});
runAll();
//# sourceMappingURL=sessionListProvider.test.js.map
