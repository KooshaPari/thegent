/// Hook dispatcher CLI entry point.
/// Reads events from stdin, evaluates governance contracts, outputs gate results.
const std = @import("std");
const event_mod = @import("event.zig");
const dispatcher_mod = @import("dispatcher.zig");
const contracts_mod = @import("contracts.zig");

const posix = std.posix;

fn writeAll(fd: posix.fd_t, data: []const u8) void {
    var offset: usize = 0;
    while (offset < data.len) {
        const written = posix.write(fd, data[offset..]) catch return;
        offset += written;
    }
}

fn writeFmt(fd: posix.fd_t, comptime fmt: []const u8, args: anytype) void {
    var buf: [4096]u8 = undefined;
    const slice = std.fmt.bufPrint(&buf, fmt, args) catch return;
    writeAll(fd, slice);
}

pub fn main() void {
    const STDOUT = posix.STDOUT_FILENO;
    const STDERR = posix.STDERR_FILENO;

    var args = std.process.args();
    _ = args.next(); // skip program name

    const subcommand = args.next() orelse {
        writeAll(STDERR, "Usage: hook-dispatcher-zig <validate|dispatch|version>\n");
        std.process.exit(1);
    };

    if (std.mem.eql(u8, subcommand, "version")) {
        writeFmt(STDOUT, "hook-dispatcher-zig v1.0.0 (Zig {s})\n", .{@import("builtin").zig_version_string});
        return;
    }

    if (std.mem.eql(u8, subcommand, "validate")) {
        const event_type_str = args.next() orelse {
            writeAll(STDERR, "Usage: hook-dispatcher-zig validate <EventType>\n");
            std.process.exit(1);
        };

        const ev_type = event_mod.EventType.fromString(event_type_str) catch {
            writeFmt(STDERR, "Unknown event type: {s}\n", .{event_type_str});
            std.process.exit(1);
        };

        writeFmt(STDOUT, "VALID: {s} (code={})\n", .{ ev_type.toString(), @intFromEnum(ev_type) });
        return;
    }

    if (std.mem.eql(u8, subcommand, "dispatch")) {
        var d = dispatcher_mod.Dispatcher.init();
        d.start();

        // Read from stdin line by line
        var buf: [65536]u8 = undefined;
        var pos: usize = 0;

        while (true) {
            const n = posix.read(posix.STDIN_FILENO, buf[pos..]) catch break;
            if (n == 0) break;
            pos += n;

            // Process complete lines
            while (std.mem.indexOf(u8, buf[0..pos], "\n")) |nl| {
                const line = buf[0..nl];
                processLine(&d, line, STDOUT, STDERR);

                // Shift remaining data
                const remaining = pos - nl - 1;
                if (remaining > 0) {
                    std.mem.copyForwards(u8, buf[0..remaining], buf[nl + 1 .. pos]);
                }
                pos = remaining;
            }
        }

        // Process any remaining data without newline
        if (pos > 0) {
            processLine(&d, buf[0..pos], STDOUT, STDERR);
        }

        d.shutdown();
        writeFmt(STDOUT, "Processed {} events, {} gates passed, {} gates failed\n", .{
            d.events_processed,
            d.gates_passed,
            d.gates_failed,
        });
        return;
    }

    writeFmt(STDERR, "Unknown subcommand: {s}\n", .{subcommand});
    std.process.exit(1);
}

fn processLine(d: *dispatcher_mod.Dispatcher, line: []const u8, stdout: posix.fd_t, stderr: posix.fd_t) void {
    var sid: [36]u8 = undefined;
    @memset(&sid, '0');

    if (std.mem.indexOf(u8, line, "\t")) |tab_pos| {
        const ev_str = line[0..tab_pos];
        const payload = line[tab_pos + 1 ..];
        const ev_type = event_mod.EventType.fromString(ev_str) catch {
            writeFmt(stderr, "Unknown event: {s}\n", .{ev_str});
            return;
        };
        const ev = event_mod.HookEvent.init(ev_type, sid, payload);
        d.submit(ev) catch |err| {
            writeFmt(stderr, "Submit error: {}\n", .{err});
            return;
        };

        if (d.processNext()) |processed| {
            writeFmt(stdout, "  PASS: {s}\n", .{processed.event_type.toString()});
        }
    }
}

// Re-export tests from all modules
test {
    _ = @import("event.zig");
    _ = @import("dispatcher.zig");
    _ = @import("contracts.zig");
}
