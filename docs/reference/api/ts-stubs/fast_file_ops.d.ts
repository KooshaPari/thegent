// Auto-generated TypeScript declarations for fast_file_ops
// Source: generate-api-docs.py

export declare class FastFileOps {
  copy(src: any, dst: any, preserve_metadata: boolean): void;
  copy_tree(src: any, dst: any, ignore: any): void;
  ensure_dir(path: any, mode: number): void;
  get_size(path: any): void;
  move(src: any, dst: any): void;
  remove(path: any, recursive: boolean): void;
}

export declare function copy(src: any, dst: any, preserve_metadata: boolean): void;
export declare function copy_file(src: any, dst: any, preserve_metadata: boolean): void;
export declare function copy_tree(src: any, dst: any, ignore: any): void;
export declare function ensure_dir(path: any, mode: number): void;
export declare function ensure_directory(path: any, mode: number): void;
export declare function get_path_size(path: any): void;
export declare function get_size(path: any): void;
export declare function ignore_func(directory: string, files: Array<string>): Array<string>;
export declare function move(src: any, dst: any): void;
export declare function move_file(src: any, dst: any): void;
export declare function remove(path: any, recursive: boolean): void;
export declare function remove_path(path: any, recursive: boolean): void;
