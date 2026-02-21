// Auto-generated usage examples for code_artifacts
// Source: generate-api-docs.py

import { CodeChangeArtifact, CodeChangeType, FileOperationArtifact, FileOperationType, create } from "./code_artifacts";

// Create a CodeChangeArtifact instance
const codechangeartifact = new CodeChangeArtifact();
codechangeartifact.create(undefined as unknown as MAIFArtifact, "example_file_path", undefined as unknown as CodeChangeType, undefined as unknown as any);

// Create a CodeChangeType instance
const codechangetype = new CodeChangeType();

// Create a FileOperationArtifact instance
const fileoperationartifact = new FileOperationArtifact();
fileoperationartifact.create(undefined as unknown as MAIFArtifact, undefined as unknown as FileOperationType, "example_source_path", undefined as unknown as any);

// Create a FileOperationType instance
const fileoperationtype = new FileOperationType();

// Call create
create(undefined as unknown as any, undefined as unknown as MAIFArtifact, undefined as unknown as FileOperationType, "example_source_path", undefined as unknown as any);
