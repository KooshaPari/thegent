"use strict";
// @trace WL-117
// Main VS Code extension entry point — thegent agent-server MCP client + session UI.
// Connects via child_process.spawn('thegent', ['agent-server']) + stdout/stdin JSONL pipes.
// Fails fast: no fallback code paths. Surfaces all errors to the user.
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
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const agentServerClient_1 = require("./agentServerClient");
const sessionListProvider_1 = require("./sessionListProvider");
const contextBudgetStatusBar_1 = require("./contextBudgetStatusBar");
const approvalWebviewPanel_1 = require("./approvalWebviewPanel");
// ─── Extension state ──────────────────────────────────────────────────────────
let _client;
let _sessionProvider;
let _statusBar;
// ─── Helpers ──────────────────────────────────────────────────────────────────
function getConfig() {
    const config = vscode.workspace.getConfiguration("thegent");
    const command = config.get("agentServerCommand", "thegent");
    const args = config.get("agentServerArgs", ["agent-server"]);
    return { command, args };
}
function requireClient() {
    if (_client === undefined) {
        throw new agentServerClient_1.AgentServerConnectionError("Not connected to thegent agent-server. Run 'thegent: Start New Session' first.");
    }
    return _client;
}
function requireSessionProvider() {
    if (_sessionProvider === undefined) {
        throw new Error("SessionListProvider not initialized");
    }
    return _sessionProvider;
}
function connectClient(context, extensionUri) {
    const { command, args } = getConfig();
    let client;
    try {
        client = agentServerClient_1.AgentServerClient.spawn(command, args);
    }
    catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        throw new agentServerClient_1.AgentServerConnectionError(`Failed to spawn '${command} ${args.join(" ")}': ${msg}`);
    }
    const provider = requireSessionProvider();
    provider.setClient(client);
    // Wire notifications
    client.on("approval/requested", (params) => {
        approvalWebviewPanel_1.ApprovalWebviewPanel.show(params, client, extensionUri);
    });
    client.on("context/budgetUpdated", (result) => {
        _statusBar?.update(result.context_usage_ratio);
    });
    client.on("disconnected", () => {
        void vscode.window.showWarningMessage("thegent agent-server disconnected. Reconnect by starting a new session.");
        _client = undefined;
    });
    // Surface stderr to output channel
    const outputChannel = vscode.window.createOutputChannel("thegent");
    context.subscriptions.push(outputChannel);
    client.stderr.on("data", (chunk) => {
        outputChannel.append(chunk.toString("utf8"));
    });
    _client = client;
    return client;
}
// ─── Command handlers ─────────────────────────────────────────────────────────
async function cmdStart(context, extensionUri) {
    let client = _client;
    if (client === undefined) {
        client = connectClient(context, extensionUri);
    }
    const session = await client.startSession();
    await requireSessionProvider().fetchAndRefresh();
    void vscode.window.showInformationMessage(`thegent: session started — ${session.id}`);
}
async function cmdListSessions() {
    const client = requireClient();
    const sessions = await client.listSessions();
    requireSessionProvider().updateSessions(sessions);
}
async function cmdResume(item) {
    const client = requireClient();
    let sessionId;
    if (item instanceof sessionListProvider_1.SessionTreeItem) {
        sessionId = item.session.id;
    }
    else {
        const input = await vscode.window.showInputBox({
            prompt: "Enter session ID to resume",
            placeHolder: "session-0001",
        });
        if (input === undefined || input.trim() === "") {
            return;
        }
        sessionId = input.trim();
    }
    const session = await client.resumeSession(sessionId);
    await requireSessionProvider().fetchAndRefresh();
    void vscode.window.showInformationMessage(`thegent: resumed session ${session.id} (status: ${session.status})`);
}
// ─── Activate ─────────────────────────────────────────────────────────────────
function activate(context) {
    const provider = new sessionListProvider_1.SessionListProvider();
    _sessionProvider = provider;
    const statusBar = new contextBudgetStatusBar_1.ContextBudgetStatusBar();
    _statusBar = statusBar;
    statusBar.show();
    // Register tree view
    const treeView = vscode.window.createTreeView("thegentSessions", {
        treeDataProvider: provider,
        showCollapseAll: false,
    });
    context.subscriptions.push(treeView);
    context.subscriptions.push(statusBar);
    context.subscriptions.push({ dispose: () => provider.dispose() });
    // Register commands
    const startCmd = vscode.commands.registerCommand("thegent.start", () => {
        void cmdStart(context, context.extensionUri).catch((err) => {
            const msg = err instanceof agentServerClient_1.AgentServerConnectionError ||
                err instanceof agentServerClient_1.AgentServerProtocolError
                ? err.message
                : String(err);
            void vscode.window.showErrorMessage(`thegent: ${msg}`);
        });
    });
    const listCmd = vscode.commands.registerCommand("thegent.listSessions", () => {
        void cmdListSessions().catch((err) => {
            const msg = err instanceof agentServerClient_1.AgentServerConnectionError ||
                err instanceof agentServerClient_1.AgentServerProtocolError
                ? err.message
                : String(err);
            void vscode.window.showErrorMessage(`thegent: ${msg}`);
        });
    });
    const resumeCmd = vscode.commands.registerCommand("thegent.resume", (item) => {
        void cmdResume(item).catch((err) => {
            const msg = err instanceof agentServerClient_1.AgentServerConnectionError ||
                err instanceof agentServerClient_1.AgentServerProtocolError
                ? err.message
                : String(err);
            void vscode.window.showErrorMessage(`thegent: ${msg}`);
        });
    });
    // Legacy scaffold commands (keep for backwards compat with existing test assertions)
    const startSessionCmd = vscode.commands.registerCommand("thegent.startSession", () => {
        void cmdStart(context, context.extensionUri).catch((err) => {
            const msg = err instanceof Error ? err.message : String(err);
            void vscode.window.showErrorMessage(`thegent: ${msg}`);
        });
    });
    const submitTurnCmd = vscode.commands.registerCommand("thegent.submitTurn", () => {
        void (async () => {
            const client = requireClient();
            const sessions = await client.listSessions();
            if (sessions.length === 0) {
                void vscode.window.showErrorMessage("thegent: no active sessions — start one first");
                return;
            }
            const sessionId = sessions[sessions.length - 1].id;
            const input = await vscode.window.showInputBox({
                prompt: `Submit turn to session ${sessionId}`,
                placeHolder: "Enter your prompt",
            });
            if (input === undefined || input.trim() === "") {
                return;
            }
            await client.submitTurn(sessionId, input.trim());
            await provider.fetchAndRefresh();
        })().catch((err) => {
            const msg = err instanceof Error ? err.message : String(err);
            void vscode.window.showErrorMessage(`thegent: ${msg}`);
        });
    });
    const showSessionsCmd = vscode.commands.registerCommand("thegent.showSessions", () => {
        void cmdListSessions().catch((err) => {
            const msg = err instanceof Error ? err.message : String(err);
            void vscode.window.showErrorMessage(`thegent: ${msg}`);
        });
    });
    context.subscriptions.push(startCmd, listCmd, resumeCmd, startSessionCmd, submitTurnCmd, showSessionsCmd);
}
// ─── Deactivate ───────────────────────────────────────────────────────────────
function deactivate() {
    _client?.dispose();
    _client = undefined;
    _sessionProvider = undefined;
    _statusBar = undefined;
}
//# sourceMappingURL=extension.js.map