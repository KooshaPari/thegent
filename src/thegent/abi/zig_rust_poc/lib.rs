// lib.rs
// SY-008: Zig-Rust C ABI Interop POC.
// Provides a Rust wrapper for calling exported Zig functions.

extern "C" {
    fn zig_add(a: i32, b: i32) i32;
}

pub fn rust_add(a: i32, b: i32) i32 {
    unsafe {
        zig_add(a, b)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_zig_add() {
        let a = 10;
        let b = 20;
        let result = rust_add(a, b);
        assert_eq!(result, 30);
    }
}
