// Auto-generated usage examples for fast_toml_parser
// Source: generate-api-docs.py

import { FastTOMLParser, backend, dump, dumps, get_toml_parser, load, loads, toml_dump, toml_dumps, toml_load, toml_loads } from "./fast_toml_parser";

// Create a FastTOMLParser instance
const fasttomlparser = new FastTOMLParser(false);
fasttomlparser.backend();
fasttomlparser.dump(undefined as unknown as Record<(str, Any)>, undefined as unknown as any);
fasttomlparser.dumps(undefined as unknown as Record<(str, Any)>);
fasttomlparser.load(undefined as unknown as any);
fasttomlparser.loads("example_s");

// Call backend
backend(undefined as unknown as any);
// Call dump
dump(undefined as unknown as any, undefined as unknown as Record<(str, Any)>, undefined as unknown as any);
// Call dumps
dumps(undefined as unknown as any, undefined as unknown as Record<(str, Any)>);
// Call get_toml_parser
get_toml_parser(false);
// Call load
load(undefined as unknown as any, undefined as unknown as any);
// Call loads
loads(undefined as unknown as any, "example_s");
// Call toml_dump
toml_dump(undefined as unknown as Record<(str, Any)>, undefined as unknown as any);
// Call toml_dumps
toml_dumps(undefined as unknown as Record<(str, Any)>);
// Call toml_load
toml_load(undefined as unknown as any);
// Call toml_loads
toml_loads("example_s");
