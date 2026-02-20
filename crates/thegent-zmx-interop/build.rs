//! build.rs for thegent-zmx-interop
//!
//! When the `zmx-native` feature is enabled, this script attempts to locate
//! and link `libzmx` on the host system.  If it cannot find the library it
//! emits a compile-time warning so the build still succeeds (the crate falls
//! back to the subprocess path at runtime).
//!
//! Search order:
//!   1. `pkg-config zmx` (preferred, distro-agnostic)
//!   2. Well-known install prefixes: /usr/local/lib, /usr/lib, /opt/homebrew/lib
//!   3. `ZMX_LIB_DIR` environment variable (user override)

fn main() {
    // Only link libzmx when the feature is active.
    #[cfg(feature = "zmx-native")]
    link_zmx();

    // Tell Cargo to re-run build.rs when the env var changes.
    println!("cargo:rerun-if-env-changed=ZMX_LIB_DIR");
    println!("cargo:rerun-if-changed=build.rs");
}

#[cfg(feature = "zmx-native")]
fn link_zmx() {
    // --- 1. Try pkg-config ---
    if try_pkg_config() {
        return;
    }

    // --- 2. Try known prefixes ---
    let search_dirs: Vec<std::path::PathBuf> = {
        let mut dirs = vec![
            std::path::PathBuf::from("/usr/local/lib"),
            std::path::PathBuf::from("/usr/lib"),
            std::path::PathBuf::from("/opt/homebrew/lib"),
            std::path::PathBuf::from("/usr/local/lib64"),
        ];

        // --- 3. ZMX_LIB_DIR env override ---
        if let Ok(dir) = std::env::var("ZMX_LIB_DIR") {
            dirs.insert(0, std::path::PathBuf::from(dir));
        }

        dirs
    };

    for dir in &search_dirs {
        let candidate_a = dir.join("libzmx.a");
        let candidate_so = dir.join("libzmx.so");
        let candidate_dylib = dir.join("libzmx.dylib");

        if candidate_a.exists() || candidate_so.exists() || candidate_dylib.exists() {
            println!("cargo:rustc-link-search=native={}", dir.display());
            println!("cargo:rustc-link-lib=static=zmx");
            eprintln!("cargo:warning=Found libzmx in {}", dir.display());
            return;
        }
    }

    // Library not found — emit a warning but do not fail the build.
    // The `zmx-native` feature will activate the FFI declarations; if the
    // linker cannot find the symbols it will fail at link time with a clear
    // message pointing back here.
    eprintln!(
        "cargo:warning=libzmx not found. \
         Set ZMX_LIB_DIR=/path/to/libzmx or install zmx to one of: {:?}",
        search_dirs
    );
}

/// Attempt to locate libzmx via pkg-config.
/// Returns `true` if the library was found and link flags emitted.
#[cfg(feature = "zmx-native")]
fn try_pkg_config() -> bool {
    // pkg-config crate is not a build-dep to keep the dep tree minimal.
    // We shell out directly instead.
    let output = std::process::Command::new("pkg-config")
        .args(["--libs", "--cflags", "zmx"])
        .output();

    match output {
        Ok(out) if out.status.success() => {
            let flags = String::from_utf8_lossy(&out.stdout);
            for flag in flags.split_whitespace() {
                if let Some(path) = flag.strip_prefix("-L") {
                    println!("cargo:rustc-link-search=native={path}");
                } else if let Some(lib) = flag.strip_prefix("-l") {
                    println!("cargo:rustc-link-lib={lib}");
                }
            }
            eprintln!("cargo:warning=Found libzmx via pkg-config");
            true
        }
        _ => false,
    }
}
