"use strict";
// @trace WL-117
// TreeDataProvider for the thegent Sessions side panel.
// Displays sessions with status icons and supports inline Resume command.
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
exports.SessionListProvider = exports.SessionTreeItem = void 0;
const vscode = __importStar(require("vscode"));
// ─── Tree item ────────────────────────────────────────────────────────────────
class SessionTreeItem extends vscode.TreeItem {
    constructor(session) {
        super(`${session.id} (${session.status})`, vscode.TreeItemCollapsibleState.None);
        this.session = session;
        this.contextValue = "session";
        this.tooltip = `Session: ${session.id}\nStatus: ${session.status}\nTurns: ${session.turn_ids.length}`;
        this.iconPath = SessionTreeItem._iconForStatus(session.status);
        this.description = `${session.turn_ids.length} turn(s)`;
    }
    static _iconForStatus(status) {
        switch (status) {
            case "active":
                return new vscode.ThemeIcon("sync~spin", new vscode.ThemeColor("charts.green"));
            case "paused":
                return new vscode.ThemeIcon("debug-pause", new vscode.ThemeColor("charts.yellow"));
            case "completed":
                return new vscode.ThemeIcon("check", new vscode.ThemeColor("charts.blue"));
            case "failed":
                return new vscode.ThemeIcon("error", new vscode.ThemeColor("charts.red"));
        }
    }
}
exports.SessionTreeItem = SessionTreeItem;
// ─── Provider ─────────────────────────────────────────────────────────────────
class SessionListProvider {
    constructor() {
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
        this._sessions = [];
        this._client = undefined;
    }
    setClient(client) {
        this._client = client;
    }
    refresh() {
        this._onDidChangeTreeData.fire(undefined);
    }
    async fetchAndRefresh() {
        if (this._client === undefined) {
            throw new Error("SessionListProvider: no client set — call setClient() first");
        }
        this._sessions = await this._client.listSessions();
        this.refresh();
    }
    updateSessions(sessions) {
        this._sessions = sessions;
        this.refresh();
    }
    getTreeItem(element) {
        return element;
    }
    getChildren(_element) {
        // Flat list — no nested children for sessions
        return this._sessions.map((s) => new SessionTreeItem(s));
    }
    dispose() {
        this._onDidChangeTreeData.dispose();
    }
}
exports.SessionListProvider = SessionListProvider;
//# sourceMappingURL=sessionListProvider.js.map