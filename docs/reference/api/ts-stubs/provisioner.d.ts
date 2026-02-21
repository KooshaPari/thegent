// Auto-generated TypeScript declarations for provisioner
// Source: generate-api-docs.py

export declare class InfraProvisioner {
  constructor(provider: string);
  decommission(resource_id: string): void;
  provision(resource_id: string, spec: ResourceSpec): void;
}

export declare class ResourceSpec extends BaseModel {
}

export declare function decommission(resource_id: string): void;
export declare function provision(resource_id: string, spec: ResourceSpec): void;
