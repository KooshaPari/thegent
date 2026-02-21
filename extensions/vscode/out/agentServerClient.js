"use strict";
// @trace WL-117
// stdio client for `thegent agent-server` — JSON-RPC 2.0 over child_process pipes.
// Fails fast and loudly: no fallbacks, no silent error handling.
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
exports.AgentServerClient = exports.AgentServerProtocolError = exports.AgentServerConnectionError = void 0;
const child_process = __importStar(require("child_process"));
const events_1 = require("events");
const types_1 = require("./types");
// ─── Error classes ────────────────────────────────────────────────────────────
class AgentServerConnectionError extends Error {
    constructor(message) {
        super(`AgentServerConnectionError: ${message}`);
        this.name = "AgentServerConnectionError";
    }
}
exports.AgentServerConnectionError = AgentServerConnectionError;
class AgentServerProtocolError extends Error {
    constructor(code, message, data) {
        super(`AgentServerProtocolError(${code}): ${message}`);
        this.name = "AgentServerProtocolError";
        this.code = code;
        this.data = data;
    }
}
exports.AgentServerProtocolError = AgentServerProtocolError;
// ─── Client ───────────────────────────────────────────────────────────────────
class AgentServerClient extends events_1.EventEmitter {
    constructor(proc) {
        super();
        this._pending = new Map();
        this._nextId = 1;
        this._lineBuffer = "";
        this._disposed = false;
        this._proc = proc;
        this._proc.stdout.on("data", (chunk) => {
            this._lineBuffer += chunk.toString("utf8");
            const lines = this._lineBuffer.split("\n");
            // Last element is incomplete line (or empty string after final \n)
            this._lineBuffer = lines.pop() ?? "";
            for (const line of lines) {
                const trimmed = line.trim();
                if (trimmed.length > 0) {
                    this._handleLine(trimmed);
                }
            }
        });
        this._proc.on("close", () => {
            this._disposed = true;
            // Reject all pending requests — process is gone, fail loudly
            for (const [id, pending] of this._pending.entries()) {
                this._pending.delete(id);
                pending.reject(new AgentServerProtocolError(-1, "agent-server process closed unexpectedly"));
            }
            this.emit("disconnected");
        });
        this._proc.on("error", (err) => {
            throw new AgentServerConnectionError(`child process error: ${err.message}`);
        });
        this._proc.stderr.on("data", (_chunk) => {
            // stderr output from agent-server is informational — not thrown,
            // but NOT suppressed: surface to extension output channel if available.
            // Callers may listen to this._proc.stderr directly.
        });
    }
    // ─── Factory ──────────────────────────────────────────────────────────────
    static spawn(command, args) {
        const proc = child_process.spawn(command, [...args], {
            stdio: ["pipe", "pipe", "pipe"],
            shell: false,
        });
        return new AgentServerClient(proc);
    }
    // ─── Dispose ──────────────────────────────────────────────────────────────
    dispose() {
        if (this._disposed) {
            return;
        }
        this._disposed = true;
        this._proc.stdin.end();
    }
    // ─── Stderr access (for output channels) ─────────────────────────────────
    get stderr() {
        return this._proc.stderr;
    }
    // ─── Internal message handling ────────────────────────────────────────────
    _handleLine(line) {
        let parsed;
        try {
            parsed = JSON.parse(line);
        }
        catch {
            throw new AgentServerProtocolError(-32700, `Parse error: invalid JSON from agent-server: ${line}`);
        }
        if (typeof parsed !== "object" ||
            parsed === null ||
            Array.isArray(parsed)) {
            throw new AgentServerProtocolError(-32600, `Invalid message shape from agent-server: ${line}`);
        }
        if ((0, types_1.isJsonRpcNotification)(parsed)) {
            this._handleNotification(parsed);
            return;
        }
        if ((0, types_1.isJsonRpcResponse)(parsed)) {
            this._handleResponse(parsed);
            return;
        }
        throw new AgentServerProtocolError(-32600, `Unrecognized message from agent-server: ${line}`);
    }
    _handleNotification(notification) {
        const params = notification.params ?? {};
        switch (notification.method) {
            case "turn/started":
                this.emit("turn/started", params);
                break;
            case "turn/completed":
                this.emit("turn/completed", params);
                break;
            case "item/agentMessage/delta":
                this.emit("item/agentMessage/delta", params);
                break;
            case "item/toolCall/started":
                this.emit("item/toolCall/started", params);
                break;
            case "item/toolCall/completed":
                this.emit("item/toolCall/completed", params);
                break;
            case "approval/requested":
                this.emit("approval/requested", params);
                break;
            default:
                // Unknown notifications are not silent — throw so callers notice
                throw new AgentServerProtocolError(-32601, `Unknown notification method: ${notification.method}`);
        }
    }
    _handleResponse(response) {
        const id = response.id;
        if (id === null || id === undefined) {
            return;
        }
        const pending = this._pending.get(id);
        if (pending === undefined) {
            throw new AgentServerProtocolError(-32000, `Unexpected response id from agent-server: ${String(id)}`);
        }
        this._pending.delete(id);
        if ("error" in response) {
            const failure = response;
            pending.reject(new AgentServerProtocolError(failure.error.code, failure.error.message, failure.error.data));
        }
        else {
            pending.resolve(response);
        }
    }
    // ─── Request / Response ───────────────────────────────────────────────────
    _sendRequest(method, params) {
        if (this._disposed) {
            throw new AgentServerConnectionError("Client is disposed — cannot send requests");
        }
        const id = this._nextId++;
        const request = {
            jsonrpc: types_1.JSONRPC_VERSION,
            id,
            method,
            ...(params !== undefined ? { params } : {}),
        };
        return new Promise((resolve, reject) => {
            this._pending.set(id, { resolve, reject });
            const line = JSON.stringify(request) + "\n";
            this._proc.stdin.write(line, "utf8", (err) => {
                if (err != null) {
                    this._pending.delete(id);
                    reject(new AgentServerConnectionError(`stdin write error: ${err.message}`));
                }
            });
        });
    }
    _requireSuccess(resp, methodName) {
        if (!(0, types_1.isJsonRpcSuccess)(resp)) {
            throw new AgentServerProtocolError(-1, `${methodName} returned failure`);
        }
        return resp.result;
    }
    // ─── Protocol methods ─────────────────────────────────────────────────────
    async healthCheck() {
        const resp = await this._sendRequest(types_1.PROTOCOL_METHODS.healthCheck);
        return this._requireSuccess(resp, "health/check");
    }
    async readConfig() {
        const resp = await this._sendRequest(types_1.PROTOCOL_METHODS.configRead);
        return this._requireSuccess(resp, "config/read");
    }
    async startSession() {
        const resp = await this._sendRequest(types_1.PROTOCOL_METHODS.sessionStart);
        const result = this._requireSuccess(resp, "session/start");
        return result.session;
    }
    async resumeSession(sessionId) {
        const resp = await this._sendRequest(types_1.PROTOCOL_METHODS.sessionResume, {
            session_id: sessionId,
        });
        const result = this._requireSuccess(resp, "session/resume");
        return result.session;
    }
    async listSessions() {
        const resp = await this._sendRequest(types_1.PROTOCOL_METHODS.sessionList);
        const result = this._requireSuccess(resp, "session/list");
        return result.sessions;
    }
    async readSession(sessionId) {
        const resp = await this._sendRequest(types_1.PROTOCOL_METHODS.sessionRead, {
            session_id: sessionId,
        });
        return this._requireSuccess(resp, "session/read");
    }
    async submitTurn(sessionId, input, requiresApproval = false) {
        const resp = await this._sendRequest(types_1.PROTOCOL_METHODS.turnSubmit, {
            session_id: sessionId,
            input,
            requires_approval: requiresApproval,
        });
        return this._requireSuccess(resp, "turn/submit");
    }
    async cancelTurn(turnId) {
        const resp = await this._sendRequest(types_1.PROTOCOL_METHODS.turnCancel, {
            turn_id: turnId,
        });
        const result = this._requireSuccess(resp, "turn/cancel");
        return result.turn;
    }
    async grantApproval(approvalId) {
        const resp = await this._sendRequest(types_1.PROTOCOL_METHODS.approvalGrant, {
            approval_id: approvalId,
        });
        return this._requireSuccess(resp, "approval/grant");
    }
    async rejectApproval(approvalId) {
        const resp = await this._sendRequest(types_1.PROTOCOL_METHODS.approvalReject, {
            approval_id: approvalId,
        });
        return this._requireSuccess(resp, "approval/reject");
    }
    // ─── Context budget update helper ─────────────────────────────────────────
    notifyContextBudget(result) {
        this.emit("context/budgetUpdated", result);
    }
}
exports.AgentServerClient = AgentServerClient;
//# sourceMappingURL=agentServerClient.js.map