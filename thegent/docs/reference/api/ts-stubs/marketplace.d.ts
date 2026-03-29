// Auto-generated TypeScript declarations for marketplace
// Source: generate-api-docs.py

export declare class PluginContract {
}

export declare class PluginVerifier {
  constructor(public_key_dir: any);
  check_permissions(contract: PluginContract, requested_action: string): void;
  verify_contract(contract: PluginContract): void;
}

export declare function check_permissions(contract: PluginContract, requested_action: string): void;
export declare function verify_contract(contract: PluginContract): void;
