// Auto-generated TypeScript declarations for transactions
// Source: generate-api-docs.py

export declare class TransactionManager {
  constructor(run_id: string);
  add_op(description: string, do: Callable, undo: Callable): void;
}

export declare class TransactionOperation {
}

export declare function add_op(description: string, do: Callable, undo: Callable): void;
export declare function apply_multi_file_transaction(changes: Array<(tuple<(Path, str)], str)>>, cwd: any, git_commit: boolean, commit_message: string): void;
