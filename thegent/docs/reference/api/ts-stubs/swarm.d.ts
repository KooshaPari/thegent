// Auto-generated TypeScript declarations for swarm
// Source: generate-api-docs.py

export declare class ACLMessage extends BaseModel {
}

export declare class Blackboard {
  constructor(namespace: string);
  list_keys(): void;
  post(key: string, value: any): void;
  read(key: string): void;
}

export declare class ConsensusManager {
  resolve_by_confidence(proposals: Array<Record<(str, Any)>>): void;
  resolve_by_vote(proposals: Array<Record<(str, Any)>>): void;
}

export declare class NegotiationEngine {
  constructor(blackboard: Blackboard);
  resolve_conflict(proposals: Array<ACLMessage>): void;
}

export declare function list_keys(): void;
export declare function post(key: string, value: any): void;
export declare function read(key: string): void;
export declare function resolve_by_confidence(proposals: Array<Record<(str, Any)>>): void;
export declare function resolve_by_vote(proposals: Array<Record<(str, Any)>>): void;
export declare function resolve_conflict(proposals: Array<ACLMessage>): void;
