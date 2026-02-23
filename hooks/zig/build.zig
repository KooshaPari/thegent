const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    // Only build native dispatcher for non-WASM targets
    const is_wasm_target = target.result.cpu.arch == .wasm32;

    if (!is_wasm_target) {
        // Native dispatcher binary
        const dispatcher = b.addExecutable(.{
            .name = "hook-dispatcher-zig",
            .root_module = b.createModule(.{
                .root_source_file = b.path("src/main.zig"),
                .target = target,
                .optimize = optimize,
            }),
        });
        b.installArtifact(dispatcher);
    }

    // WASM governance engine (primary WASM target)
    if (is_wasm_target) {
        const wasm_engine = b.addExecutable(.{
            .name = "governance-wasm",
            .root_module = b.createModule(.{
                .root_source_file = b.path("src/wasm.zig"),
                .target = target,
                .optimize = .ReleaseSmall,
            }),
        });
        wasm_engine.entry = .disabled;
        wasm_engine.rdynamic = true;
        b.installArtifact(wasm_engine);

        // WASM library target for contract validation (legacy)
        const wasm_lib = b.addExecutable(.{
            .name = "hook-contracts",
            .root_module = b.createModule(.{
                .root_source_file = b.path("src/contracts.zig"),
                .target = target,
                .optimize = .ReleaseSmall,
            }),
        });
        wasm_lib.entry = .disabled;
        wasm_lib.rdynamic = true;
        b.installArtifact(wasm_lib);

        // WASM-specific build step
        const wasm_step = b.step("wasm", "Build WASM governance engine");
        wasm_step.dependOn(&wasm_engine.step);
    }

    // Unit tests (native target only)
    if (!is_wasm_target) {
        const unit_tests = b.addTest(.{
            .root_module = b.createModule(.{
                .root_source_file = b.path("src/main.zig"),
                .target = target,
                .optimize = optimize,
            }),
        });
        const run_unit_tests = b.addRunArtifact(unit_tests);

        const contract_tests = b.addTest(.{
            .root_module = b.createModule(.{
                .root_source_file = b.path("src/contracts.zig"),
                .target = target,
                .optimize = optimize,
            }),
        });
        const run_contract_tests = b.addRunArtifact(contract_tests);

        // WASM wrapper tests (native target)
        const wasm_tests = b.addTest(.{
            .root_module = b.createModule(.{
                .root_source_file = b.path("src/wasm.zig"),
                .target = target,
                .optimize = optimize,
            }),
        });
        const run_wasm_tests = b.addRunArtifact(wasm_tests);

        const test_step = b.step("test", "Run unit tests");
        test_step.dependOn(&run_unit_tests.step);
        test_step.dependOn(&run_contract_tests.step);
        test_step.dependOn(&run_wasm_tests.step);
    }
}
