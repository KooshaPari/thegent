// Auto-generated TypeScript declarations for galactic
// Source: generate-api-docs.py

export declare class Bundle {
}

export declare class DTNBridge {
  constructor(node_id: string);
  add_contact(node_id: string, contact_time: number): void;
  process_contacts(): void;
  send_bundle(dest_node: string, payload: Uint8Array): void;
}

export declare function add_contact(node_id: string, contact_time: number): void;
export declare function process_contacts(): void;
export declare function send_bundle(dest_node: string, payload: Uint8Array): void;
