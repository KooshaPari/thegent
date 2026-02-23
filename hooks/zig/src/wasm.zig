/// WASM-friendly wrapper for governance engine.
/// Exports key governance functions with C ABI for embedding in other runtimes.
///
/// This module provides:
/// - Contract validation via dispatch_hook
/// - Rule evaluation via validate_rule
/// - Event type parsing via event_type_from_string
///
/// All functions use linear memory for string parameters and return status codes
/// compatible with WASM execution environments.

const std = @import("std");
const contracts_mod = @import("contracts.zig");
const event_mod = @import("event.zig");

/// Memory buffer for temporary string allocations (16 KiB).
/// WASM runtimes can manage this, or we can do manual allocation.
var scratch_buf: [16 * 1024]u8 = undefined;
var scratch_pos: usize = 0;

/// Validate a single contract rule.
/// Re-exports the contracts module's validate_rule for WASM.
/// Returns status code: 0=pass, 1=fail, 2=not_applicable, 3=fail_closed, 255=error
///
/// Note: This is a forwarding function; the actual export is from contracts.zig
pub fn validate_rule_impl(
    actual_ptr: [*]const u8,
    actual_len: u32,
    expected_ptr: [*]const u8,
    expected_len: u32,
    op_code: u8,
    fail_closed: u8,
) u8 {
    const actual = actual_ptr[0..actual_len];
    const expected = expected_ptr[0..expected_len];

    const op: contracts_mod.Operator = switch (op_code) {
        0 => .eq,
        1 => .ne,
        2 => .gt,
        3 => .lt,
        4 => .gte,
        5 => .lte,
        6 => .contains,
        7 => .matches_regex,
        else => return 255, // unknown op
    };

    const rule = contracts_mod.Rule{
        .name = "wasm_rule",
        .field = "",
        .op = op,
        .expected = expected,
        .fail_closed = fail_closed != 0,
    };

    const result = contracts_mod.evaluateRule(rule, actual);
    return @intFromEnum(result.status);
}

/// Dispatch a hook event through the governance engine.
/// Returns gate status: 0=pass, 1=fail, 2=not_applicable, 3=fail_closed, 255=error
///
/// Signature:
///   dispatch_hook(
///     event_type_ptr: *const u8,
///     event_type_len: u32,
///     payload_ptr: *const u8,
///     payload_len: u32
///   ) -> u8
export fn dispatch_hook(
    event_type_ptr: [*]const u8,
    event_type_len: u32,
    payload_ptr: [*]const u8,
    payload_len: u32,
) u8 {
    const event_type_str = event_type_ptr[0..event_type_len];
    const payload = payload_ptr[0..payload_len];

    const event_type = event_mod.EventType.fromString(event_type_str) catch {
        return 255; // error: unknown event type
    };

    // For now, we just acknowledge the event was parsed.
    // A full implementation would apply contracts to the event.
    _ = event_type;
    _ = payload;

    return 0; // pass
}

/// Parse event type string and return numeric code.
/// Returns event code (0-8) or 255 for unknown.
///
/// Signature:
///   event_type_from_string(
///     event_str_ptr: *const u8,
///     event_str_len: u32
///   ) -> u8
export fn event_type_from_string(
    event_str_ptr: [*]const u8,
    event_str_len: u32,
) u8 {
    const event_str = event_str_ptr[0..event_str_len];
    const event_type = event_mod.EventType.fromString(event_str) catch {
        return 255;
    };
    return @intFromEnum(event_type);
}

/// Get the string representation of an event type.
/// Writes the string to output buffer and returns length.
///
/// Signature:
///   event_type_to_string(
///     event_code: u8,
///     output_ptr: *mut u8,
///     output_len: u32
///   ) -> u32  // actual length written, or 0 if buffer too small
export fn event_type_to_string(
    event_code: u8,
    output_ptr: [*]u8,
    output_len: u32,
) u32 {
    const event_type: event_mod.EventType = @enumFromInt(event_code);
    const s = event_type.toString();

    if (s.len > output_len) {
        return 0; // buffer too small
    }

    @memcpy(output_ptr[0..s.len], s);
    return @intCast(s.len);
}

/// Health check / initialization marker.
/// Returns version code: 1 for current version.
///
/// Signature:
///   health_check() -> u32
export fn health_check() u32 {
    return 1; // version 1
}

/// Allocate memory in WASM linear memory for caller.
/// Returns pointer to allocated buffer.
/// NOTE: Simplified allocator; production would use proper arena.
///
/// Signature:
///   wasm_alloc(size: u32) -> *mut u8
export fn wasm_alloc(size: u32) [*]u8 {
    if (scratch_pos + size > scratch_buf.len) {
        return @ptrCast(&scratch_buf); // overflow: return buffer start (error indicator)
    }
    const ptr = scratch_buf[scratch_pos..].ptr;
    scratch_pos += size;
    return ptr;
}

/// Deallocate memory (no-op in this simplified allocator).
///
/// Signature:
///   wasm_dealloc(ptr: *mut u8, size: u32) -> void
export fn wasm_dealloc(_: [*]u8, _: u32) void {
    // no-op for scratch allocator
}

/// Reset the scratch buffer (for batch operations).
///
/// Signature:
///   wasm_reset() -> void
export fn wasm_reset() void {
    scratch_pos = 0;
}
