// Auto-generated TypeScript declarations for native_governance_scan
// Source: generate-api-docs.py

export declare class GovernanceViolation {
}

export declare class NativeGovernanceScanner {
  check_contract(contract_id: string, path: string): void;
  check_contract_content(contract_id: string, content: string): void;
  scan_content(content: string): void;
  scan_file(path: string): void;
}

export declare function check_contract(contract_id: string, path: string): void;
export declare function check_contract_content(contract_id: string, content: string): void;
export declare function scan_content(content: string): void;
export declare function scan_file(path: string): void;
