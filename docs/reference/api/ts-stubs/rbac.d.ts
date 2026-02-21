// Auto-generated TypeScript declarations for rbac
// Source: generate-api-docs.py

export declare class Permission extends StrEnum {
}

export declare class RBACManager {
  constructor();
  check_access(role: Role, operation: string, lane: string): void;
  has_permission(role: Role, permission: Permission): void;
}

export declare class Role extends StrEnum {
}

export declare function check_access(role: Role, operation: string, lane: string): void;
export declare function has_permission(role: Role, permission: Permission): void;
