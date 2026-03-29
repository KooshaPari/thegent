// Auto-generated TypeScript declarations for hitl
// Source: generate-api-docs.py

export declare class HITLManager {
  constructor();
  approve(request_id: string): void;
  is_approved(request_id: string): void;
  request_approval(request_id: string, action: string, context: Record<(str, Any)>): void;
}

export declare function approve(request_id: string): void;
export declare function is_approved(request_id: string): void;
export declare function request_approval(request_id: string, action: string, context: Record<(str, Any)>): void;
