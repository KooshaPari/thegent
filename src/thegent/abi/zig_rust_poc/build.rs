// build.rs
// SY-008: Zig-Rust C ABI Interop POC.
// Compiles the Zig code into a static library for linking into Rust.

use std::process::Command;
use std::env;
use std::path::PathBuf;

fn main() {
    let out_dir = env::var("OUT_DIR").unwrap();
    let out_path = PathBuf::from(out_dir);

    // Compile main.zig to a static library (.a or .lib)
    let output = Command::new("zig")
        .args(&["build-lib", "main.zig", "-static", "-femit-bin", out_path.join("libmain.a").to_str().unwrap()])
        .status()
        .expect("Failed to execute zig build-lib");

    if !output.success() {
        panic!("Zig compilation failed");
    }

    // Tell Rust where to find the static library
    println!("cargo:rustc-link-search=native={}", out_path.to_str().unwrap());
    println!("cargo:rustc-link-lib=static=main");

    // Standard Rust link flags for C libraries
    println!("cargo:rerun-if-changed=main.zig");
}
