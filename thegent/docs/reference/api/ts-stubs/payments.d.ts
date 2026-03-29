// Auto-generated TypeScript declarations for payments
// Source: generate-api-docs.py

export declare class PaymentBridge {
  constructor(provider: string);
  initiate_settlement(agent_id: string, amount: number): void;
  verify_liquidity(agent_id: string): void;
}

export declare class Settlement extends BaseModel {
}

export declare function initiate_settlement(agent_id: string, amount: number): void;
export declare function verify_liquidity(agent_id: string): void;
