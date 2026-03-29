// Auto-generated usage examples for always_write_dumps
// Source: generate-api-docs.py

import { ConversationDumper, dump_conversation, list_dumps } from "./always_write_dumps";

// Create a ConversationDumper instance
const conversationdumper = new ConversationDumper("example_docs_dir");
conversationdumper.dump_conversation("example_conversation_id", "example_content");
conversationdumper.list_dumps();

// Call dump_conversation
dump_conversation(undefined as unknown as any, "example_conversation_id", "example_content");
// Call list_dumps
list_dumps(undefined as unknown as any);
