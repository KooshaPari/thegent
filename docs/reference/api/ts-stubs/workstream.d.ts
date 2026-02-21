// Auto-generated TypeScript declarations for workstream
// Source: generate-api-docs.py

export declare class WorkItem extends BaseModel {
}

export declare function claim_item(path: string, item_id: string, owner: string): void;
export declare function mark_completed(path: string, item_id: string): void;
export declare function parse_workstream(path: string): void;
