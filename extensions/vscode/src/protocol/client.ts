// @trace WL-117
// Protocol client interfaces — re-exported from types for backwards compatibility.

export type {
  JsonRpcRequest,
  JsonRpcSuccess,
  JsonRpcFailure,
  JsonRpcResponse,
} from "../types";

export { PROTOCOL_METHODS } from "../types";

// ─── ProtocolClient interface (used by tests and external consumers) ──────────

export interface ProtocolClient {
  healthCheck(): Promise<{ status: string; service: string; transport: string }>;
  readConfig(): Promise<{ server: string; transport: string; supported_methods: string[] }>;
}
