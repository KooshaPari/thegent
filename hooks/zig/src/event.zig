/// Hook event types matching the governance hook pipeline.
/// Each variant corresponds to a lifecycle point in the agent session.
const std = @import("std");

pub const EventType = enum(u8) {
    session_start = 0,
    session_end = 1,
    pre_tool_use = 2,
    post_tool_use = 3,
    stop = 4,
    user_prompt_submit = 5,
    pre_compact = 6,
    notification = 7,
    post_agent_run = 8,

    pub fn fromString(s: []const u8) !EventType {
        const map = .{
            .{ "SessionStart", EventType.session_start },
            .{ "SessionEnd", EventType.session_end },
            .{ "PreToolUse", EventType.pre_tool_use },
            .{ "PostToolUse", EventType.post_tool_use },
            .{ "Stop", EventType.stop },
            .{ "UserPromptSubmit", EventType.user_prompt_submit },
            .{ "PreCompact", EventType.pre_compact },
            .{ "Notification", EventType.notification },
            .{ "PostAgentRun", EventType.post_agent_run },
        };
        inline for (map) |entry| {
            if (std.mem.eql(u8, s, entry[0])) return entry[1];
        }
        return error.UnknownEvent;
    }

    pub fn toString(self: EventType) []const u8 {
        return switch (self) {
            .session_start => "SessionStart",
            .session_end => "SessionEnd",
            .pre_tool_use => "PreToolUse",
            .post_tool_use => "PostToolUse",
            .stop => "Stop",
            .user_prompt_submit => "UserPromptSubmit",
            .pre_compact => "PreCompact",
            .notification => "Notification",
            .post_agent_run => "PostAgentRun",
        };
    }
};

/// A hook event with associated payload.
pub const HookEvent = struct {
    event_type: EventType,
    session_id: [36]u8,
    timestamp_ns: u64,
    payload_len: u32,
    payload: []const u8,

    pub fn init(event_type: EventType, session_id: [36]u8, payload: []const u8) HookEvent {
        return .{
            .event_type = event_type,
            .session_id = session_id,
            .timestamp_ns = @truncate(@as(u128, @bitCast(std.time.nanoTimestamp()))),
            .payload_len = @intCast(payload.len),
            .payload = payload,
        };
    }
};

/// Gate result status for governance checks.
pub const GateStatus = enum(u8) {
    pass = 0,
    fail = 1,
    not_applicable = 2,
    fail_closed = 3,
};

/// Result of evaluating a single governance gate.
pub const GateResult = struct {
    name: []const u8,
    status: GateStatus,
    reason: []const u8,
};

// --- Tests ---

test "EventType round-trip" {
    const events = [_]EventType{
        .session_start,
        .session_end,
        .pre_tool_use,
        .post_tool_use,
        .stop,
        .user_prompt_submit,
        .pre_compact,
        .notification,
        .post_agent_run,
    };

    for (events) |ev| {
        const s = ev.toString();
        const parsed = try EventType.fromString(s);
        try std.testing.expectEqual(ev, parsed);
    }
}

test "EventType unknown returns error" {
    const result = EventType.fromString("InvalidEvent");
    try std.testing.expectError(error.UnknownEvent, result);
}

test "HookEvent init sets fields" {
    var sid: [36]u8 = undefined;
    @memset(&sid, 'x');
    const payload = "test payload";
    const ev = HookEvent.init(.stop, sid, payload);
    try std.testing.expectEqual(EventType.stop, ev.event_type);
    try std.testing.expectEqual(@as(u32, 12), ev.payload_len);
    try std.testing.expect(ev.timestamp_ns > 0);
}
