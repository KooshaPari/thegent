// @trace WL-117
// stdio client for `thegent agent-server` — JSON-RPC 2.0 over child_process pipes.
// Fails fast and loudly: no fallbacks, no silent error handling.

import * as child_process from "child_process";
import { EventEmitter } from "events";
import {
  JSONRPC_VERSION,
  JsonRpcRequest,
  JsonRpcResponse,
  JsonRpcNotification,
  JsonRpcFailure,
  PROTOCOL_METHODS,
  Session,
  Turn,
  Approval,
  RunResult,
  isJsonRpcNotification,
  isJsonRpcResponse,
  isJsonRpcSuccess,
  ApprovalRequestedParams,
  TurnStartedParams,
  TurnCompletedParams,
  AgentMessageDeltaParams,
  ToolCallStartedParams,
  ToolCallCompletedParams,
} from "./types";

// ─── Error classes ────────────────────────────────────────────────────────────

export class AgentServerConnectionError extends Error {
  constructor(message: string) {
    super(`AgentServerConnectionError: ${message}`);
    this.name = "AgentServerConnectionError";
  }
}

export class AgentServerProtocolError extends Error {
  public readonly code: number;
  public readonly data: Record<string, unknown> | undefined;

  constructor(code: number, message: string, data?: Record<string, unknown>) {
    super(`AgentServerProtocolError(${code}): ${message}`);
    this.name = "AgentServerProtocolError";
    this.code = code;
    this.data = data;
  }
}

// ─── Internal pending request tracking ───────────────────────────────────────

interface PendingRequest {
  resolve: (response: JsonRpcResponse) => void;
  reject: (error: AgentServerProtocolError) => void;
}

// ─── Notification event map ───────────────────────────────────────────────────

export interface AgentServerEvents {
  "turn/started": (params: TurnStartedParams) => void;
  "turn/completed": (params: TurnCompletedParams) => void;
  "item/agentMessage/delta": (params: AgentMessageDeltaParams) => void;
  "item/toolCall/started": (params: ToolCallStartedParams) => void;
  "item/toolCall/completed": (params: ToolCallCompletedParams) => void;
  "approval/requested": (params: ApprovalRequestedParams) => void;
  "context/budgetUpdated": (result: RunResult) => void;
  disconnected: () => void;
}

// ─── Client ───────────────────────────────────────────────────────────────────

export class AgentServerClient extends EventEmitter {
  private readonly _proc: child_process.ChildProcessWithoutNullStreams;
  private readonly _pending: Map<string | number, PendingRequest> = new Map();
  private _nextId = 1;
  private _lineBuffer = "";
  private _disposed = false;

  constructor(proc: child_process.ChildProcessWithoutNullStreams) {
    super();
    this._proc = proc;

    this._proc.stdout.on("data", (chunk: Buffer) => {
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
        pending.reject(
          new AgentServerProtocolError(-1, "agent-server process closed unexpectedly"),
        );
      }
      this.emit("disconnected");
    });

    this._proc.on("error", (err: Error) => {
      throw new AgentServerConnectionError(
        `child process error: ${err.message}`,
      );
    });

    this._proc.stderr.on("data", (_chunk: Buffer) => {
      // stderr output from agent-server is informational — not thrown,
      // but NOT suppressed: surface to extension output channel if available.
      // Callers may listen to this._proc.stderr directly.
    });
  }

  // ─── Factory ──────────────────────────────────────────────────────────────

  static spawn(command: string, args: readonly string[]): AgentServerClient {
    const proc = child_process.spawn(command, [...args], {
      stdio: ["pipe", "pipe", "pipe"],
      shell: false,
    }) as child_process.ChildProcessWithoutNullStreams;

    return new AgentServerClient(proc);
  }

  // ─── Dispose ──────────────────────────────────────────────────────────────

  dispose(): void {
    if (this._disposed) {
      return;
    }
    this._disposed = true;
    this._proc.stdin.end();
  }

  // ─── Stderr access (for output channels) ─────────────────────────────────

  get stderr(): NodeJS.ReadableStream {
    return this._proc.stderr;
  }

  // ─── Internal message handling ────────────────────────────────────────────

  private _handleLine(line: string): void {
    let parsed: unknown;
    try {
      parsed = JSON.parse(line);
    } catch {
      throw new AgentServerProtocolError(
        -32700,
        `Parse error: invalid JSON from agent-server: ${line}`,
      );
    }

    if (
      typeof parsed !== "object" ||
      parsed === null ||
      Array.isArray(parsed)
    ) {
      throw new AgentServerProtocolError(
        -32600,
        `Invalid message shape from agent-server: ${line}`,
      );
    }

    if (isJsonRpcNotification(parsed)) {
      this._handleNotification(parsed);
      return;
    }

    if (isJsonRpcResponse(parsed)) {
      this._handleResponse(parsed);
      return;
    }

    throw new AgentServerProtocolError(
      -32600,
      `Unrecognized message from agent-server: ${line}`,
    );
  }

  private _handleNotification(notification: JsonRpcNotification): void {
    const params: unknown = notification.params ?? {};

    switch (notification.method) {
      case "turn/started":
        this.emit("turn/started", params as unknown as TurnStartedParams);
        break;
      case "turn/completed":
        this.emit("turn/completed", params as unknown as TurnCompletedParams);
        break;
      case "item/agentMessage/delta":
        this.emit("item/agentMessage/delta", params as unknown as AgentMessageDeltaParams);
        break;
      case "item/toolCall/started":
        this.emit("item/toolCall/started", params as unknown as ToolCallStartedParams);
        break;
      case "item/toolCall/completed":
        this.emit("item/toolCall/completed", params as unknown as ToolCallCompletedParams);
        break;
      case "approval/requested":
        this.emit("approval/requested", params as unknown as ApprovalRequestedParams);
        break;
      default:
        // Unknown notifications are not silent — throw so callers notice
        throw new AgentServerProtocolError(
          -32601,
          `Unknown notification method: ${notification.method}`,
        );
    }
  }

  private _handleResponse(response: JsonRpcResponse): void {
    const id = response.id;
    if (id === null || id === undefined) {
      return;
    }
    const pending = this._pending.get(id);
    if (pending === undefined) {
      throw new AgentServerProtocolError(
        -32000,
        `Unexpected response id from agent-server: ${String(id)}`,
      );
    }
    this._pending.delete(id);
    if ("error" in response) {
      const failure = response as JsonRpcFailure;
      pending.reject(
        new AgentServerProtocolError(
          failure.error.code,
          failure.error.message,
          failure.error.data,
        ),
      );
    } else {
      pending.resolve(response);
    }
  }

  // ─── Request / Response ───────────────────────────────────────────────────

  private _sendRequest(
    method: string,
    params?: Record<string, unknown>,
  ): Promise<JsonRpcResponse> {
    if (this._disposed) {
      throw new AgentServerConnectionError("Client is disposed — cannot send requests");
    }

    const id = this._nextId++;
    const request: JsonRpcRequest = {
      jsonrpc: JSONRPC_VERSION,
      id,
      method,
      ...(params !== undefined ? { params } : {}),
    };

    return new Promise<JsonRpcResponse>((resolve, reject) => {
      this._pending.set(id, { resolve, reject });
      const line = JSON.stringify(request) + "\n";
      this._proc.stdin.write(line, "utf8", (err?: Error | null) => {
        if (err != null) {
          this._pending.delete(id);
          reject(new AgentServerConnectionError(`stdin write error: ${err.message}`));
        }
      });
    });
  }

  private _requireSuccess<T>(
    resp: JsonRpcResponse,
    methodName: string,
  ): T {
    if (!isJsonRpcSuccess(resp)) {
      throw new AgentServerProtocolError(-1, `${methodName} returned failure`);
    }
    return resp.result as T;
  }

  // ─── Protocol methods ─────────────────────────────────────────────────────

  async healthCheck(): Promise<{ status: string; service: string; transport: string }> {
    const resp = await this._sendRequest(PROTOCOL_METHODS.healthCheck);
    return this._requireSuccess<{ status: string; service: string; transport: string }>(
      resp,
      "health/check",
    );
  }

  async readConfig(): Promise<{ server: string; transport: string; supported_methods: string[] }> {
    const resp = await this._sendRequest(PROTOCOL_METHODS.configRead);
    return this._requireSuccess<{ server: string; transport: string; supported_methods: string[] }>(
      resp,
      "config/read",
    );
  }

  async startSession(): Promise<Session> {
    const resp = await this._sendRequest(PROTOCOL_METHODS.sessionStart);
    const result = this._requireSuccess<{ session: Session }>(resp, "session/start");
    return result.session;
  }

  async resumeSession(sessionId: string): Promise<Session> {
    const resp = await this._sendRequest(PROTOCOL_METHODS.sessionResume, {
      session_id: sessionId,
    });
    const result = this._requireSuccess<{ session: Session }>(resp, "session/resume");
    return result.session;
  }

  async listSessions(): Promise<Session[]> {
    const resp = await this._sendRequest(PROTOCOL_METHODS.sessionList);
    const result = this._requireSuccess<{ sessions: Session[] }>(resp, "session/list");
    return result.sessions;
  }

  async readSession(sessionId: string): Promise<{ session: Session; turns: Turn[] }> {
    const resp = await this._sendRequest(PROTOCOL_METHODS.sessionRead, {
      session_id: sessionId,
    });
    return this._requireSuccess<{ session: Session; turns: Turn[] }>(resp, "session/read");
  }

  async submitTurn(
    sessionId: string,
    input: string,
    requiresApproval = false,
  ): Promise<{ turn: Turn; approval?: Approval }> {
    const resp = await this._sendRequest(PROTOCOL_METHODS.turnSubmit, {
      session_id: sessionId,
      input,
      requires_approval: requiresApproval,
    });
    return this._requireSuccess<{ turn: Turn; approval?: Approval }>(resp, "turn/submit");
  }

  async cancelTurn(turnId: string): Promise<Turn> {
    const resp = await this._sendRequest(PROTOCOL_METHODS.turnCancel, {
      turn_id: turnId,
    });
    const result = this._requireSuccess<{ turn: Turn }>(resp, "turn/cancel");
    return result.turn;
  }

  async grantApproval(approvalId: string): Promise<{ approval: Approval; turn: Turn }> {
    const resp = await this._sendRequest(PROTOCOL_METHODS.approvalGrant, {
      approval_id: approvalId,
    });
    return this._requireSuccess<{ approval: Approval; turn: Turn }>(resp, "approval/grant");
  }

  async rejectApproval(approvalId: string): Promise<{ approval: Approval; turn: Turn }> {
    const resp = await this._sendRequest(PROTOCOL_METHODS.approvalReject, {
      approval_id: approvalId,
    });
    return this._requireSuccess<{ approval: Approval; turn: Turn }>(resp, "approval/reject");
  }

  // ─── Context budget update helper ─────────────────────────────────────────

  notifyContextBudget(result: RunResult): void {
    this.emit("context/budgetUpdated", result);
  }
}
