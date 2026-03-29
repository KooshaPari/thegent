// Auto-generated TypeScript declarations for file_index
// Source: generate-api-docs.py

export declare class FileIndex {
  constructor(ttl: any);
  build(root: string, exclude_dirs: any): void;
  find(pattern: string, root: any): void;
  find_by_ext(ext: string, root: any): void;
  find_by_name(name: string, root: any): void;
  invalidate(root: any): void;
  is_cached(root: string): void;
}

export declare function build(root: string, exclude_dirs: any): void;
export declare function find(pattern: string, root: any): void;
export declare function find_by_ext(ext: string, root: any): void;
export declare function find_by_name(name: string, root: any): void;
export declare function invalidate(root: any): void;
export declare function is_cached(root: string): void;
