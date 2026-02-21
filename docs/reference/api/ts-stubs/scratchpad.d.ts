// Auto-generated TypeScript declarations for scratchpad
// Source: generate-api-docs.py

export declare class AIScratchpad {
  constructor(state_path: any);
  add_line(line: string): void;
  clear(): void;
  delete_last(): void;
  get_content(): void;
  set_metadata(key: string, value: string): void;
}

export declare class ScratchpadState extends BaseModel {
}

export declare function add_line(line: string): void;
export declare function clear(): void;
export declare function delete_last(): void;
export declare function get_content(): void;
export declare function set_metadata(key: string, value: string): void;
