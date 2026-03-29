// Auto-generated usage examples for schema
// Source: generate-api-docs.py

import { DecisionRecord, SessionRecord, ToolCallRecord, TraceFile, TraceRecord, delete, from_dict, get_file_size, read_records, to_dict, validate_record, write_record } from "./schema";

// Create a DecisionRecord instance
const decisionrecord = new DecisionRecord();
decisionrecord.from_dict(undefined as unknown as Record<(str, Any)>);
decisionrecord.to_dict();

// Create a SessionRecord instance
const sessionrecord = new SessionRecord();
sessionrecord.from_dict(undefined as unknown as Record<(str, Any)>);
sessionrecord.to_dict();

// Create a ToolCallRecord instance
const toolcallrecord = new ToolCallRecord();
toolcallrecord.from_dict(undefined as unknown as Record<(str, Any)>);
toolcallrecord.to_dict();

// Create a TraceFile instance
const tracefile = new TraceFile("example_path", undefined as unknown as any);
tracefile.delete();
tracefile.get_file_size();
tracefile.read_records();
tracefile.write_record(undefined as unknown as any);

// Create a TraceRecord instance
const tracerecord = new TraceRecord();
tracerecord.from_dict(undefined as unknown as Record<(str, Any)>);

// Call delete
delete(undefined as unknown as any);
// Call from_dict
from_dict(undefined as unknown as Record<(str, Any)>);
// Call get_file_size
get_file_size(undefined as unknown as any);
// Call read_records
read_records(undefined as unknown as any);
// Call to_dict
to_dict(undefined as unknown as any);
// Call validate_record
validate_record(undefined as unknown as any);
// Call write_record
write_record(undefined as unknown as any, undefined as unknown as any);
