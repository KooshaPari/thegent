// main.zig
// SY-008: Zig-Rust C ABI Interop POC.
// Provides a simple addition function exported with the C ABI.

const std = @import("std");

export fn zig_add(a: i32, b: i32) i32 {
    return a + b;
}

pub fn main() !void {
    const a = 10;
    const b = 20;
    const result = zig_add(a, b);
    std.debug.print("Zig: {d} + {d} = {d}\n", .{ a, b, result });
}
