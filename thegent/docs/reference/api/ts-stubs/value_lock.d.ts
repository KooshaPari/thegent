// Auto-generated TypeScript declarations for value_lock
// Source: generate-api-docs.py

export declare class LockedPrinciple extends BaseModel {
}

export declare class ValueLock {
  constructor(lock_path: string);
  lock_principle(principle_id: string, description: string): void;
  validate_change(principle_id: string, new_description: string): void;
}

export declare function lock_principle(principle_id: string, description: string): void;
export declare function validate_change(principle_id: string, new_description: string): void;
