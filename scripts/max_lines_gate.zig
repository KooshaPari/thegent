const std = @import("std");

const Config = struct {
    max_lines: usize = 500,
    warn_lines: usize = 350,
    exts: []const []const u8,
    excludes: []const []const u8,
};

fn hasAllowedExt(path: []const u8, exts: []const []const u8) bool {
    for (exts) |ext| {
        if (std.mem.endsWith(u8, path, ext)) return true;
    }
    return false;
}

fn isExcluded(path: []const u8, excludes: []const []const u8) bool {
    for (excludes) |prefix| {
        if (std.mem.startsWith(u8, path, prefix)) return true;
    }
    return false;
}

fn countLines(allocator: std.mem.Allocator, abs_path: []const u8) !usize {
    const bytes = try std.fs.cwd().readFileAlloc(allocator, abs_path, 1024 * 1024 * 20);
    defer allocator.free(bytes);
    if (bytes.len == 0) return 0;
    var n: usize = 0;
    for (bytes) |b| {
        if (b == '\n') n += 1;
    }
    if (bytes[bytes.len - 1] != '\n') n += 1;
    return n;
}

fn runGitList(allocator: std.mem.Allocator, argv: []const []const u8) ![]u8 {
    var proc = std.process.Child.init(argv, allocator);
    proc.stdout_behavior = .Pipe;
    proc.stderr_behavior = .Pipe;
    try proc.spawn();

    const out = try proc.stdout.?.readToEndAlloc(allocator, 1024 * 1024 * 20);
    const err_out = try proc.stderr.?.readToEndAlloc(allocator, 1024 * 1024);
    defer allocator.free(err_out);

    const term = try proc.wait();
    switch (term) {
        .Exited => |code| if (code != 0) {
            std.debug.print("MAX_LINES_GATE FAIL: git command failed: {s}\n", .{err_out});
            allocator.free(out);
            std.process.exit(2);
        },
        else => {
            std.debug.print("MAX_LINES_GATE FAIL: git command terminated unexpectedly\n", .{});
            allocator.free(out);
            std.process.exit(2);
        },
    }
    return out;
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    const scope_all = blk: {
        if (std.process.getEnvVarOwned(allocator, "MAX_LINES_SCOPE")) |scope| {
            defer allocator.free(scope);
            break :blk std.mem.eql(u8, scope, "all");
        } else |_| {
            break :blk false;
        }
    };

    const out = if (scope_all)
        try runGitList(allocator, &[_][]const u8{ "git", "ls-files", "-z" })
    else blk: {
        const staged = try runGitList(allocator, &[_][]const u8{ "git", "diff", "--cached", "--name-only", "--diff-filter=ACMRTUXB", "-z" });
        if (staged.len > 0) break :blk staged;
        allocator.free(staged);

        const changed = try runGitList(allocator, &[_][]const u8{ "git", "diff", "--name-only", "--diff-filter=ACMRTUXB", "-z" });
        break :blk changed;
    };
    defer allocator.free(out);

    const cfg = Config{
        .exts = &[_][]const u8{ ".py", ".rs", ".go", ".zig", ".mojo", ".ts", ".tsx", ".js", ".jsx", ".sh", ".zsh", ".bash" },
        .excludes = &[_][]const u8{ ".git/", "node_modules/", "dist/", "build/", "target/", ".venv/", "__pycache__/", "docs/.vitepress/dist/", "docs-dist/", ".shadow-" },
    };

    var checked: usize = 0;
    var warns: usize = 0;
    var fails: usize = 0;

    var it = std.mem.splitScalar(u8, out, 0);
    while (it.next()) |entry| {
        if (entry.len == 0) continue;
        if (isExcluded(entry, cfg.excludes)) continue;
        if (!hasAllowedExt(entry, cfg.exts)) continue;

        const lines = countLines(allocator, entry) catch |e| {
            if (e == error.FileNotFound) continue;
            std.debug.print("MAX_LINES_GATE FAIL: cannot read {s}: {s}\n", .{ entry, @errorName(e) });
            std.process.exit(2);
        };
        checked += 1;

        if (lines > cfg.max_lines) {
            std.debug.print("[FAIL] {s}: {d} lines (max {d})\n", .{ entry, lines, cfg.max_lines });
            fails += 1;
        } else if (lines > cfg.warn_lines) {
            std.debug.print("[WARN] {s}: {d} lines (>{d})\n", .{ entry, lines, cfg.warn_lines });
            warns += 1;
        }
    }

    std.debug.print(
        "MAX_LINES_GATE summary: checked={d} warn={d} fail={d} max={d} warn_at={d}\n",
        .{ checked, warns, fails, cfg.max_lines, cfg.warn_lines },
    );

    if (fails > 0) std.process.exit(1);
}
