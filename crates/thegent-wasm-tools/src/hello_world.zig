// Hello World Wasm Tool Example
// Compile with: zig build wasm32-wasi release

const std = @import("std");

// Export functions for Wasm
export fn greet(name_ptr: usize, name_len: usize) usize {
    // Simple greeting function
    // In real implementation, would read from Wasm memory
    _ = name_ptr;
    _ = name_len;
    return 0; // Return offset in Wasm memory
}

export fn process_input(input_ptr: usize, input_len: usize) usize {
    // Process input and return result offset
    _ = input_ptr;
    _ = input_len;
    return 0;
}

export fn get_capabilities() u32 {
    // Return capability bitmask
    // Bit 0: can_read_memory
    // Bit 1: can_write_memory  
    // Bit 2: can_network
    return 0b111;
}

// Memory allocation (required for Wasm)
var arena = std.heap.ArenaAllocator.init(std.heap.page_allocator);

export fn alloc(size: usize) usize {
    const allocator = arena.allocator();
    const ptr = allocator.alloc(u8, size) catch return 0;
    return @intFromPtr(ptr.ptr);
}

export fn dealloc(ptr: usize, size: usize) void {
    _ = ptr;
    _ = size;
    // In a real implementation, would free the memory
}
