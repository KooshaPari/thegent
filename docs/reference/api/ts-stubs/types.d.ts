// Auto-generated TypeScript declarations for types
// Source: generate-api-docs.py

export declare class Complexity extends StrEnum {
}

export declare class Deliverable extends BaseModel {
}

export declare class Priority extends StrEnum {
}

export declare class SubagentType extends StrEnum {
}

export declare class Task extends BaseModel {
  validate_allowed_agents(v: Array<string>, info: any): void;
  validate_depends(v: Array<string>): void;
}

export declare class TaskMetadata extends BaseModel {
}

export declare class TaskOutput extends BaseModel {
}

export declare class TaskOutputStatus extends StrEnum {
}

export declare class TaskStep extends BaseModel {
}

export declare class TaskVisibility extends StrEnum {
}

export declare function validate_allowed_agents(v: Array<string>, info: any): void;
export declare function validate_depends(v: Array<string>): void;
