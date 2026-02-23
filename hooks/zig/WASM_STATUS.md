# WASM Build Target Status

## Summary

Successfully added WASM build target to the thegent Zig hook engine. The governance engine can now be compiled to WebAssembly for embedding in other runtimes.

**Date**: 2026-02-23
**Status**: OPERATIONAL
**Artifacts**:
- `governance-wasm.wasm` (1.2 KiB, ReleaseSmall)
- `hook-contracts.wasm` (2.3 KiB, ReleaseSmall)

## Build Targets

### Native Build (Default)
```bash
zig build
```
Produces: `hook-dispatcher-zig` (native executable for macOS/Linux)

### WASM Build
```bash
zig build -Dtarget=wasm32-freestanding
```
Produces:
- `governance-wasm.wasm` - Main governance engine wrapper
- `hook-contracts.wasm` - Contract validation module

## WASM Exported Functions

### `governance-wasm.wasm` Exports

1. **dispatch_hook** - Process a hook event through governance engine
   - Signature: `(event_type_ptr: u32, event_type_len: u32, payload_ptr: u32, payload_len: u32) -> u32`
   - Returns: Gate status code (0=pass, 1=fail, 2=not_applicable, 3=fail_closed, 255=error)

2. **event_type_from_string** - Parse event type string to numeric code
   - Signature: `(event_str_ptr: u32, event_str_len: u32) -> u32`
   - Returns: Event code (0-8) or 255 for unknown

3. **event_type_to_string** - Convert event code to string
   - Signature: `(event_code: u32, output_ptr: u32, output_len: u32) -> u32`
   - Returns: Length of string written, or 0 if buffer too small

4. **health_check** - Initialization/health check marker
   - Signature: `() -> u32`
   - Returns: Version code (1 for current version)

5. **wasm_alloc** - Allocate memory in WASM linear memory
   - Signature: `(size: u32) -> u32`
   - Returns: Pointer to allocated buffer

6. **wasm_dealloc** - Deallocate memory (no-op in simplified allocator)
   - Signature: `(ptr: u32, size: u32) -> void`

7. **wasm_reset** - Reset scratch buffer for batch operations
   - Signature: `() -> void`

### `hook-contracts.wasm` Exports

Includes the full contract validation engine with:
- `validate_rule` function for rule evaluation
- Additional internal validation helpers

## Architecture Notes

### Build System
- Uses Zig's standard build system with target-conditional artifact generation
- Native dispatcher (POSIX-dependent) only built for native targets
- WASM artifacts only built when `-Dtarget=wasm32-freestanding` is specified
- ReleaseSmall optimization for minimal binary size

### Memory Management
- Simplified scratch buffer allocator (16 KiB)
- Linear memory shared with WASM runtime
- No external dependencies on Zig's stdlib memory allocation (not available in freestanding)

### Known Limitations
1. **Freestanding Environment**: WASM target runs in freestanding mode, so:
   - No POSIX syscalls available
   - No file I/O
   - No networking
   - Single-threaded only

2. **Scratch Buffer**: 16 KiB fixed allocation for temporary strings
   - Suitable for governance rules and event payloads
   - Caller must reset with `wasm_reset()` between batch operations

3. **Regex Support**: Limited to prefix/suffix matching
   - Full regex engine not available in freestanding WASM
   - Patterns starting with `^` treated as prefix match
   - Other patterns use substring search

## Testing

### Run Tests
```bash
cd hooks/zig
zig build test
```

Includes:
- Unit tests for event types, dispatcher, contracts
- WASM wrapper tests (compiled to native for testing)

## Integration

### Embedding in Other Runtimes

Example (pseudocode - language agnostic):

```javascript
// Load WASM module
const wasmModule = await WebAssembly.instantiate(govWasmBinary);
const wasmMemory = new Uint8Array(wasmModule.instance.exports.memory.buffer);

// Write event type to memory
const eventType = "PreToolUse";
const eventPtr = 0;
wasmMemory.set(new TextEncoder().encode(eventType), eventPtr);

// Call dispatch_hook
const result = wasmModule.instance.exports.dispatch_hook(
  eventPtr,      // event_type_ptr
  eventType.length,  // event_type_len
  payloadPtr,    // payload_ptr
  payloadLen     // payload_len
);

console.log("Gate result:", result); // 0=pass, 1=fail, etc.
```

## Files Changed

- `src/wasm.zig` - NEW: WASM-friendly wrapper with C ABI exports
- `build.zig` - UPDATED: Added conditional WASM build targets and routing
- `WASM_STATUS.md` - NEW: This document

## Verification

```bash
# Verify WASM binaries are valid
file zig-out/bin/*.wasm
# Output: WebAssembly (wasm) binary module version 0x1 (MVP)

# Check native dispatcher still works
./zig-out/bin/hook-dispatcher-zig version
# Output: hook-dispatcher-zig v1.0.0 (Zig 0.15.2)
```

## Future Enhancements

1. **Memory Pool**: Implement proper arena allocator for production WASM
2. **Full Regex**: Link with minimal regex library if size permits
3. **ABI Stability**: Formalize interface for version negotiation
4. **Exports API**: Add metadata export listing all function signatures
5. **WASM Component Model**: Consider migration to Component Model when stable
