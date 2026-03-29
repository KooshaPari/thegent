// Auto-generated TypeScript declarations for always_write_dumps
// Source: generate-api-docs.py

export declare class ConversationDumper {
  constructor(docs_dir: string);
  dump_conversation(conversation_id: string, content: string): void;
  list_dumps(): void;
}

export declare function dump_conversation(conversation_id: string, content: string): void;
export declare function list_dumps(): void;
