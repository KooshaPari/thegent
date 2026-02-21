// Auto-generated usage examples for transactions
// Source: generate-api-docs.py

import { TransactionManager, TransactionOperation, add_op, apply_multi_file_transaction } from "./transactions";

// Create a TransactionManager instance
const transactionmanager = new TransactionManager("example_run_id");
transactionmanager.add_op("example_description", undefined as unknown as Callable, undefined as unknown as Callable);

// Create a TransactionOperation instance
const transactionoperation = new TransactionOperation();

// Call add_op
add_op(undefined as unknown as any, "example_description", undefined as unknown as Callable, undefined as unknown as Callable);
// Call apply_multi_file_transaction
apply_multi_file_transaction(undefined as unknown as Array<(tuple<(Path, str)], str)>>, undefined as unknown as any, false, "example_commit_message");
