/// Contract validation engine for governance gates.
/// Evaluates rules defined in JSON contract files against hook event payloads.
/// Compilable to WASM for sandboxed execution.
const std = @import("std");
const event = @import("event.zig");

/// A contract rule that checks a condition against event data.
pub const Rule = struct {
    name: []const u8,
    /// Field path in the payload to check (dot-separated).
    field: []const u8,
    /// Comparison operator.
    op: Operator,
    /// Expected value (string representation).
    expected: []const u8,
    /// Whether a failure should be fail-closed (blocking).
    fail_closed: bool,
};

pub const Operator = enum {
    eq,
    ne,
    gt,
    lt,
    gte,
    lte,
    contains,
    matches_regex,

    pub fn fromString(s: []const u8) !Operator {
        const map = .{
            .{ "eq", Operator.eq },
            .{ "ne", Operator.ne },
            .{ "gt", Operator.gt },
            .{ "lt", Operator.lt },
            .{ "gte", Operator.gte },
            .{ "lte", Operator.lte },
            .{ "contains", Operator.contains },
            .{ "matches_regex", Operator.matches_regex },
        };
        inline for (map) |entry| {
            if (std.mem.eql(u8, s, entry[0])) return entry[1];
        }
        return error.UnknownOperator;
    }
};

/// Evaluate a single rule against a string value.
pub fn evaluateRule(rule: Rule, actual: []const u8) event.GateResult {
    const passed = switch (rule.op) {
        .eq => std.mem.eql(u8, actual, rule.expected),
        .ne => !std.mem.eql(u8, actual, rule.expected),
        .contains => std.mem.indexOf(u8, actual, rule.expected) != null,
        .gt, .lt, .gte, .lte => blk: {
            const a_val = std.fmt.parseInt(i64, actual, 10) catch break :blk false;
            const e_val = std.fmt.parseInt(i64, rule.expected, 10) catch break :blk false;
            break :blk switch (rule.op) {
                .gt => a_val > e_val,
                .lt => a_val < e_val,
                .gte => a_val >= e_val,
                .lte => a_val <= e_val,
                else => unreachable,
            };
        },
        .matches_regex => blk2: {
            // Zig stdlib does not have regex; for WASM we do simple prefix/suffix match.
            if (rule.expected.len >= 2 and rule.expected[0] == '^') {
                const pattern = rule.expected[1..];
                break :blk2 std.mem.startsWith(u8, actual, pattern);
            } else {
                break :blk2 std.mem.indexOf(u8, actual, rule.expected) != null;
            }
        },
    };

    if (passed) {
        return .{
            .name = rule.name,
            .status = .pass,
            .reason = "matched",
        };
    }

    return .{
        .name = rule.name,
        .status = if (rule.fail_closed) .fail_closed else .fail,
        .reason = "value mismatch",
    };
}

/// Evaluate a list of rules, returning aggregate results.
pub fn evaluateRules(rules: []const Rule, values: []const []const u8) struct {
    pass_count: u32,
    fail_count: u32,
    fail_closed_count: u32,
    na_count: u32,
} {
    var pass_count: u32 = 0;
    var fail_count: u32 = 0;
    var fail_closed_count: u32 = 0;
    var na_count: u32 = 0;

    for (rules, 0..) |rule, i| {
        if (i >= values.len) {
            na_count += 1;
            continue;
        }
        const result = evaluateRule(rule, values[i]);
        switch (result.status) {
            .pass => pass_count += 1,
            .fail => fail_count += 1,
            .fail_closed => fail_closed_count += 1,
            .not_applicable => na_count += 1,
        }
    }

    return .{
        .pass_count = pass_count,
        .fail_count = fail_count,
        .fail_closed_count = fail_closed_count,
        .na_count = na_count,
    };
}

// --- WASM exports ---

export fn validate_rule(
    actual_ptr: [*]const u8,
    actual_len: u32,
    expected_ptr: [*]const u8,
    expected_len: u32,
    op_code: u8,
    fail_closed: u8,
) u8 {
    const actual = actual_ptr[0..actual_len];
    const expected = expected_ptr[0..expected_len];

    const op: Operator = switch (op_code) {
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

    const rule = Rule{
        .name = "wasm_rule",
        .field = "",
        .op = op,
        .expected = expected,
        .fail_closed = fail_closed != 0,
    };

    const result = evaluateRule(rule, actual);
    return @intFromEnum(result.status);
}

// --- Tests ---

test "evaluateRule eq pass" {
    const rule = Rule{
        .name = "test_eq",
        .field = "status",
        .op = .eq,
        .expected = "ok",
        .fail_closed = false,
    };
    const result = evaluateRule(rule, "ok");
    try std.testing.expectEqual(event.GateStatus.pass, result.status);
}

test "evaluateRule eq fail" {
    const rule = Rule{
        .name = "test_eq_fail",
        .field = "status",
        .op = .eq,
        .expected = "ok",
        .fail_closed = true,
    };
    const result = evaluateRule(rule, "error");
    try std.testing.expectEqual(event.GateStatus.fail_closed, result.status);
}

test "evaluateRule ne" {
    const rule = Rule{
        .name = "test_ne",
        .field = "x",
        .op = .ne,
        .expected = "bad",
        .fail_closed = false,
    };
    const result = evaluateRule(rule, "good");
    try std.testing.expectEqual(event.GateStatus.pass, result.status);
}

test "evaluateRule gt" {
    const rule = Rule{
        .name = "test_gt",
        .field = "count",
        .op = .gt,
        .expected = "5",
        .fail_closed = false,
    };
    const result = evaluateRule(rule, "10");
    try std.testing.expectEqual(event.GateStatus.pass, result.status);
}

test "evaluateRule lt fail" {
    const rule = Rule{
        .name = "test_lt_fail",
        .field = "count",
        .op = .lt,
        .expected = "5",
        .fail_closed = false,
    };
    const result = evaluateRule(rule, "10");
    try std.testing.expectEqual(event.GateStatus.fail, result.status);
}

test "evaluateRule contains" {
    const rule = Rule{
        .name = "test_contains",
        .field = "msg",
        .op = .contains,
        .expected = "error",
        .fail_closed = false,
    };
    const result = evaluateRule(rule, "an error occurred");
    try std.testing.expectEqual(event.GateStatus.pass, result.status);
}

test "evaluateRules aggregate" {
    const rules = [_]Rule{
        .{ .name = "r1", .field = "a", .op = .eq, .expected = "x", .fail_closed = false },
        .{ .name = "r2", .field = "b", .op = .eq, .expected = "y", .fail_closed = true },
        .{ .name = "r3", .field = "c", .op = .eq, .expected = "z", .fail_closed = false },
    };
    const values = [_][]const u8{ "x", "wrong", "z" };
    const agg = evaluateRules(&rules, &values);
    try std.testing.expectEqual(@as(u32, 2), agg.pass_count);
    try std.testing.expectEqual(@as(u32, 0), agg.fail_count);
    try std.testing.expectEqual(@as(u32, 1), agg.fail_closed_count);
    try std.testing.expectEqual(@as(u32, 0), agg.na_count);
}

test "evaluateRules more values than rules" {
    const rules = [_]Rule{
        .{ .name = "r1", .field = "a", .op = .eq, .expected = "x", .fail_closed = false },
    };
    const values = [_][]const u8{ "x", "extra" };
    const agg = evaluateRules(&rules, &values);
    try std.testing.expectEqual(@as(u32, 1), agg.pass_count);
}

test "evaluateRules fewer values than rules" {
    const rules = [_]Rule{
        .{ .name = "r1", .field = "a", .op = .eq, .expected = "x", .fail_closed = false },
        .{ .name = "r2", .field = "b", .op = .eq, .expected = "y", .fail_closed = false },
    };
    const values = [_][]const u8{"x"};
    const agg = evaluateRules(&rules, &values);
    try std.testing.expectEqual(@as(u32, 1), agg.pass_count);
    try std.testing.expectEqual(@as(u32, 1), agg.na_count);
}
