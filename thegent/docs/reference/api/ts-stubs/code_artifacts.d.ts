// Auto-generated TypeScript declarations for code_artifacts
// Source: generate-api-docs.py

export declare class CodeChangeArtifact extends BaseArtifact {
  create(maif: MAIFArtifact, file_path: string, change_type: CodeChangeType, language: any): void;
}

export declare class CodeChangeType extends str, Enum {
}

export declare class FileOperationArtifact extends BaseArtifact {
  create(maif: MAIFArtifact, operation_type: FileOperationType, source_path: string, dest_path: any): void;
}

export declare class FileOperationType extends str, Enum {
}

export declare function create(maif: MAIFArtifact, operation_type: FileOperationType, source_path: string, dest_path: any): void;
