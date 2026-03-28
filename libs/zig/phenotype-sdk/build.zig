const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const mode = b.standardReleaseOptions(.{});

    // Main SDK library
    const sdk = b.addStaticLibrary(.{
        .name = "phenotype-sdk",
        .root_module = b.createModule(.{
            .source_file = .{ .path = "src/lib.zig" },
        }),
        .target = target,
        .optimize = mode,
    });

    b.installArtifact(sdk);

    // Run tests
    const tests = b.addTest(.{
        .name = "phenotype-sdk-tests",
        .root_module = b.createModule(.{
            .source_file = .{ .path = "src/lib.zig" },
        }),
        .target = target,
        .optimize = mode,
    });

    const test_run = b.addRunArtifact(tests);
    test_run.step.dependOn(&b.step);

    // Add uuid dependency (for demo, would use proper dependency manager)
    _ = tests;
}
