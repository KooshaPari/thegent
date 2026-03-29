// @trace WL-117
// Shared wire-format types for thegent agent-server JSON-RPC 2.0 over stdio.

export const JSONRPC_VERSION = "2.0" as const;

// ─── JSON-RPC primitives ─────────────────────────────────────────────────────

export interface JsonRpcRequest<TParams = Record<string, unknown>> {
  jsonrpc: "2.0";
  id: string | number;
  method: string;
  params?: TParams;
}

export interface JsonRpcSuccess<TResult = Record<string, unknown>> {
  jsonrpc: "2.0";
  id: string | number;
  result: TResult;
}

export interface JsonRpcFailure {
  jsonrpc: "2.0";
  id: string | number | null;
  error: {
    code: number;
    message: string;
    data?: Record<string, unknown>;
  };
}

export type JsonRpcResponse<TResult = Record<string, unknown>> =
  | JsonRpcSuccess<TResult>
  | JsonRpcFailure;

export interface JsonRpcNotification<TParams = Record<string, unknown>> {
  jsonrpc: "2.0";
  method: string;
  params?: TParams;
}

// ─── Protocol methods ─────────────────────────────────────────────────────────

export const PROTOCOL_METHODS = {
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
} as const;

export type ProtocolMethod = (typeof PROTOCOL_METHODS)[keyof typeof PROTOCOL_METHODS];

// ─── Session types ────────────────────────────────────────────────────────────

export type SessionStatus = "active" | "paused" | "completed" | "failed";

export interface Session {
  id: string;
  status: SessionStatus;
  created_index: number;
  turn_ids: string[];
}

// ─── Turn types ───────────────────────────────────────────────────────────────

export type TurnStatus =
  | "in_progress"
  | "awaiting_approval"
  | "completed"
  | "cancelled"
  | "rejected";

export interface Turn {
  id: string;
  session_id: string;
  status: TurnStatus;
  input: string;
  approval_id?: string | null;
  tool_call_id?: string | null;
}

// ─── Approval types ───────────────────────────────────────────────────────────

export type ApprovalStatus = "requested" | "granted" | "rejected" | "cancelled";

export interface Approval {
  id: string;
  status: ApprovalStatus;
}

// ─── Notification param types ─────────────────────────────────────────────────

export interface TurnStartedParams {
  session_id: string;
  turn_id: string;
}

export interface TurnCompletedParams {
  session_id: string;
  turn_id: string;
  status: TurnStatus;
}

export interface AgentMessageDeltaParams {
  session_id: string;
  turn_id: string;
  delta: string;
}

export interface ToolCallStartedParams {
  session_id: string;
  turn_id: string;
  tool_call_id: string;
  tool_name: string;
}

export interface ToolCallCompletedParams {
  session_id: string;
  turn_id: string;
  tool_call_id: string;
  output: string;
}

export interface ApprovalRequestedParams {
  approval_id: string;
  session_id: string;
  turn_id: string;
  diff?: string;
}

// ─── RunResult type (for context budget) ─────────────────────────────────────

export interface RunResult {
  session_id: string;
  turn_id: string;
  context_usage_ratio: number; // 0.0–1.0
  output?: string;
}

// ─── Type guards ──────────────────────────────────────────────────────────────

export function isJsonRpcSuccess<T = Record<string, unknown>>(
  response: JsonRpcResponse<T>,
): response is JsonRpcSuccess<T> {
  return !("error" in response);
}

export function isJsonRpcFailure(response: JsonRpcResponse): response is JsonRpcFailure {
  return "error" in response;
}

export function isJsonRpcNotification(
  msg: unknown,
): msg is JsonRpcNotification {
  if (typeof msg !== "object" || msg === null) {
    return false;
  }
  const m = msg as Record<string, unknown>;
  return (
    m["jsonrpc"] === JSONRPC_VERSION &&
    typeof m["method"] === "string" &&
    !("id" in m)
  );
}

export function isJsonRpcResponse(
  msg: unknown,
): msg is JsonRpcResponse {
  if (typeof msg !== "object" || msg === null) {
    return false;
  }
  const m = msg as Record<string, unknown>;
  return m["jsonrpc"] === JSONRPC_VERSION && "id" in m;
}
