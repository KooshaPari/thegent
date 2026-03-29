// Auto-generated TypeScript declarations for distributed_coordination
// Source: generate-api-docs.py

export declare class DistributedResourceCoordination {
  constructor();
  coordinate(resource: string): void;
  register_coordinator(name: string, coordinator: any): void;
}

export declare function coordinate(resource: string): void;
export declare function register_coordinator(name: string, coordinator: any): void;
