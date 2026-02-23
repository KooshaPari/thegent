/// Lock-free hook event dispatcher.
/// Uses a single-producer single-consumer ring buffer for event queueing.
/// Guarantees deterministic event ordering (FIFO within priority class).
const std = @import("std");
const event_mod = @import("event.zig");
const contracts_mod = @import("contracts.zig");

const EventType = event_mod.EventType;
const HookEvent = event_mod.HookEvent;
const GateResult = event_mod.GateResult;
const GateStatus = event_mod.GateStatus;

pub const QUEUE_CAPACITY = 1024;

/// Lock-free SPSC ring buffer for hook events.
pub const EventQueue = struct {
    buffer: [QUEUE_CAPACITY]?HookEvent,
    head: std.atomic.Value(usize),
    tail: std.atomic.Value(usize),

    pub fn init() EventQueue {
        return .{
            .buffer = [_]?HookEvent{null} ** QUEUE_CAPACITY,
            .head = std.atomic.Value(usize).init(0),
            .tail = std.atomic.Value(usize).init(0),
        };
    }

    /// Push an event. Returns false if queue is full.
    pub fn push(self: *EventQueue, ev: HookEvent) bool {
        const tail = self.tail.load(.acquire);
        const next_tail = (tail + 1) % QUEUE_CAPACITY;
        if (next_tail == self.head.load(.acquire)) {
            return false; // full
        }
        self.buffer[tail] = ev;
        self.tail.store(next_tail, .release);
        return true;
    }

    /// Pop an event. Returns null if queue is empty.
    pub fn pop(self: *EventQueue) ?HookEvent {
        const head = self.head.load(.acquire);
        if (head == self.tail.load(.acquire)) {
            return null; // empty
        }
        const ev = self.buffer[head];
        self.buffer[head] = null;
        self.head.store((head + 1) % QUEUE_CAPACITY, .release);
        return ev;
    }

    /// Current number of events in the queue.
    pub fn len(self: *const EventQueue) usize {
        const head = self.head.load(.acquire);
        const tail = self.tail.load(.acquire);
        if (tail >= head) return tail - head;
        return QUEUE_CAPACITY - head + tail;
    }

    pub fn isEmpty(self: *const EventQueue) bool {
        return self.head.load(.acquire) == self.tail.load(.acquire);
    }
};

/// Hook dispatcher lifecycle state.
pub const DispatcherState = enum {
    idle,
    running,
    shutting_down,
    stopped,
};

/// The hook dispatcher: receives events, evaluates contracts, emits gate results.
pub const Dispatcher = struct {
    queue: EventQueue,
    state: DispatcherState,
    events_processed: u64,
    gates_passed: u64,
    gates_failed: u64,

    pub fn init() Dispatcher {
        return .{
            .queue = EventQueue.init(),
            .state = .idle,
            .events_processed = 0,
            .gates_passed = 0,
            .gates_failed = 0,
        };
    }

    pub fn start(self: *Dispatcher) void {
        self.state = .running;
    }

    pub fn shutdown(self: *Dispatcher) void {
        self.state = .shutting_down;
        // Drain remaining events
        while (self.queue.pop()) |_| {
            self.events_processed += 1;
        }
        self.state = .stopped;
    }

    /// Submit an event for processing.
    pub fn submit(self: *Dispatcher, ev: HookEvent) !void {
        if (self.state != .running) {
            return error.DispatcherNotRunning;
        }
        if (!self.queue.push(ev)) {
            return error.QueueFull;
        }
    }

    /// Process the next event in the queue. Returns the event or null.
    pub fn processNext(self: *Dispatcher) ?HookEvent {
        if (self.state != .running) return null;
        const ev = self.queue.pop() orelse return null;
        self.events_processed += 1;
        return ev;
    }

    /// Process next event and evaluate rules against it.
    pub fn processNextWithRules(
        self: *Dispatcher,
        rules: []const contracts_mod.Rule,
        values: []const []const u8,
    ) ?struct { event: HookEvent, pass_count: u32, fail_closed_count: u32 } {
        const ev = self.processNext() orelse return null;
        const agg = contracts_mod.evaluateRules(rules, values);
        self.gates_passed += agg.pass_count;
        self.gates_failed += agg.fail_count + agg.fail_closed_count;
        return .{
            .event = ev,
            .pass_count = agg.pass_count,
            .fail_closed_count = agg.fail_closed_count,
        };
    }
};

/// Format a gate result as shell-compatible output (matches governance-gates.sh format).
pub fn formatGateResult(result: GateResult, buf: []u8) []u8 {
    const prefix: []const u8 = switch (result.status) {
        .pass => "  PASS: ",
        .fail => "  FAIL: ",
        .not_applicable => "  N/A:  ",
        .fail_closed => "  FAIL: ",
    };

    var pos: usize = 0;
    const total_needed = prefix.len + result.name.len + 3 + result.reason.len + 1;
    if (total_needed > buf.len) return buf[0..0];

    @memcpy(buf[pos .. pos + prefix.len], prefix);
    pos += prefix.len;
    @memcpy(buf[pos .. pos + result.name.len], result.name);
    pos += result.name.len;

    if (result.status != .pass) {
        const sep = " - ";
        @memcpy(buf[pos .. pos + sep.len], sep);
        pos += sep.len;
        @memcpy(buf[pos .. pos + result.reason.len], result.reason);
        pos += result.reason.len;
    }

    buf[pos] = '\n';
    pos += 1;
    return buf[0..pos];
}

// --- Tests ---

test "EventQueue push and pop" {
    var q = EventQueue.init();
    var sid: [36]u8 = undefined;
    @memset(&sid, 'a');

    const ev = HookEvent.init(.stop, sid, "test");
    try std.testing.expect(q.push(ev));
    try std.testing.expectEqual(@as(usize, 1), q.len());

    const popped = q.pop();
    try std.testing.expect(popped != null);
    try std.testing.expectEqual(EventType.stop, popped.?.event_type);
    try std.testing.expect(q.isEmpty());
}

test "EventQueue empty pop returns null" {
    var q = EventQueue.init();
    try std.testing.expect(q.pop() == null);
}

test "EventQueue full returns false" {
    var q = EventQueue.init();
    var sid: [36]u8 = undefined;
    @memset(&sid, 'b');

    // Fill to capacity - 1 (ring buffer uses one slot as sentinel)
    var i: usize = 0;
    while (i < QUEUE_CAPACITY - 1) : (i += 1) {
        try std.testing.expect(q.push(HookEvent.init(.stop, sid, "x")));
    }
    // Next push should fail
    try std.testing.expect(!q.push(HookEvent.init(.stop, sid, "overflow")));
}

test "EventQueue FIFO ordering" {
    var q = EventQueue.init();
    var sid: [36]u8 = undefined;
    @memset(&sid, 'c');

    try std.testing.expect(q.push(HookEvent.init(.session_start, sid, "1")));
    try std.testing.expect(q.push(HookEvent.init(.pre_tool_use, sid, "2")));
    try std.testing.expect(q.push(HookEvent.init(.stop, sid, "3")));

    try std.testing.expectEqual(EventType.session_start, q.pop().?.event_type);
    try std.testing.expectEqual(EventType.pre_tool_use, q.pop().?.event_type);
    try std.testing.expectEqual(EventType.stop, q.pop().?.event_type);
}

test "Dispatcher lifecycle" {
    var d = Dispatcher.init();
    try std.testing.expectEqual(DispatcherState.idle, d.state);

    d.start();
    try std.testing.expectEqual(DispatcherState.running, d.state);

    d.shutdown();
    try std.testing.expectEqual(DispatcherState.stopped, d.state);
}

test "Dispatcher submit and process" {
    var d = Dispatcher.init();
    d.start();

    var sid: [36]u8 = undefined;
    @memset(&sid, 'd');
    try d.submit(HookEvent.init(.stop, sid, "payload"));

    const ev = d.processNext();
    try std.testing.expect(ev != null);
    try std.testing.expectEqual(@as(u64, 1), d.events_processed);
}

test "Dispatcher rejects when not running" {
    var d = Dispatcher.init();
    var sid: [36]u8 = undefined;
    @memset(&sid, 'e');
    const result = d.submit(HookEvent.init(.stop, sid, "x"));
    try std.testing.expectError(error.DispatcherNotRunning, result);
}

test "formatGateResult pass" {
    var buf: [256]u8 = undefined;
    const result = GateResult{
        .name = "test-gate",
        .status = .pass,
        .reason = "ok",
    };
    const output = formatGateResult(result, &buf);
    try std.testing.expect(std.mem.startsWith(u8, output, "  PASS: test-gate\n"));
}

test "formatGateResult fail" {
    var buf: [256]u8 = undefined;
    const result = GateResult{
        .name = "bad-gate",
        .status = .fail,
        .reason = "threshold exceeded",
    };
    const output = formatGateResult(result, &buf);
    try std.testing.expect(std.mem.startsWith(u8, output, "  FAIL: bad-gate - threshold exceeded\n"));
}

test "Dispatcher determinism: same input same output" {
    // Run 10 times with identical input, verify identical processing order
    var i: u32 = 0;
    while (i < 10) : (i += 1) {
        var d = Dispatcher.init();
        d.start();
        var sid: [36]u8 = undefined;
        @memset(&sid, 'f');

        try d.submit(HookEvent.init(.session_start, sid, "a"));
        try d.submit(HookEvent.init(.pre_tool_use, sid, "b"));
        try d.submit(HookEvent.init(.stop, sid, "c"));

        try std.testing.expectEqual(EventType.session_start, d.processNext().?.event_type);
        try std.testing.expectEqual(EventType.pre_tool_use, d.processNext().?.event_type);
        try std.testing.expectEqual(EventType.stop, d.processNext().?.event_type);
        try std.testing.expect(d.processNext() == null);

        d.shutdown();
    }
}
