// Auto-generated TypeScript declarations for replay
// Source: generate-api-docs.py

export declare function replay_diff(session_a: Annotated<(str, Any)>, session_b: Annotated<(str, Any)>, sessions_root: Annotated<(Any, Any)>, output_json: Annotated<(bool, Any)>): void;
export declare function replay_list(sessions_root: Annotated<(Any, Any)>, output_json: Annotated<(bool, Any)>): void;
export declare function replay_run(session_id: Annotated<(str, Any)>, speed: Annotated<(float, Any)>, sessions_root: Annotated<(Any, Any)>, output_json: Annotated<(bool, Any)>, from_event: Annotated<(int, Any)>): void;
