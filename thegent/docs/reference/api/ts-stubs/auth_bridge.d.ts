// Auto-generated TypeScript declarations for auth_bridge
// Source: generate-api-docs.py

export declare class AuthBridge {
  constructor(config: any);
  bridge_saml_response(saml_response: string): void;
}

export declare class SSOConfig extends BaseModel {
}

export declare function bridge_saml_response(saml_response: string): void;
