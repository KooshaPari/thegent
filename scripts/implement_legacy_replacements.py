#!/usr/bin/env python3
"""
Implementation script for high-priority legacy replacements
"""
import re
from pathlib import Path

def replace_lazy_static(file_path):
    """Replace lazy_static with std::sync::OnceLock"""
    try:
        content = file_path.read_text()
        original = content
        
        # Remove lazy_static dependency
        content = re.sub(r'lazy_static\s*=\s*"[^"]+"\s*\n', '', content)
        content = re.sub(r'lazy_static\s*=\s*\{[^}]+\}\s*\n', '', content)
        
        if content != original:
            file_path.write_text(content)
            print(f"✓ Removed lazy_static from {file_path}")
            return True
        return False
    except Exception as e:
        print(f"✗ Error updating {file_path}: {e}")
        return False

def replace_md5(file_path):
    """Replace md5 with sha2 or blake3"""
    try:
        content = file_path.read_text()
        original = content
        
        # Check if blake3 is already present
        has_blake3 = 'blake3' in content.lower()
        
        # Remove md5
        content = re.sub(r'md5\s*=\s*"[^"]+"\s*\n', '', content)
        content = re.sub(r'md5\s*=\s*\{[^}]+\}\s*\n', '', content)
        
        # Add sha2 if not present (safer default than blake3)
        if 'sha2' not in content.lower() and 'md5' not in content.lower():
            # Find [dependencies] section and add sha2
            deps_match = re.search(r'(\[dependencies\]\s*\n)', content)
            if deps_match:
                insert_pos = deps_match.end()
                content = content[:insert_pos] + 'sha2 = "0.10"\n' + content[insert_pos:]
        
        if content != original:
            file_path.write_text(content)
            print(f"✓ Replaced md5 with sha2 in {file_path}")
            return True
        return False
    except Exception as e:
        print(f"✗ Error updating {file_path}: {e}")
        return False

def replace_hex(file_path):
    """Replace hex with base16ct"""
    try:
        content = file_path.read_text()
        original = content
        
        # Replace hex = "0.4" with base16ct = "1.0"
        content = re.sub(r'hex\s*=\s*"0\.4"', 'base16ct = "1.0"', content)
        content = re.sub(r'hex\s*=\s*"0\.4\.\d+"', 'base16ct = "1.0"', content)
        
        if content != original:
            file_path.write_text(content)
            print(f"✓ Replaced hex with base16ct in {file_path}")
            return True
        return False
    except Exception as e:
        print(f"✗ Error updating {file_path}: {e}")
        return False

def upgrade_thiserror(file_path):
    """Upgrade thiserror to 2.0"""
    try:
        content = file_path.read_text()
        original = content
        
        # Replace thiserror = "1.0" with "2.0"
        content = re.sub(r'thiserror\s*=\s*"1\.0"', 'thiserror = "2.0"', content)
        content = re.sub(r'thiserror\s*=\s*"1\.0\.\d+"', 'thiserror = "2.0"', content)
        
        if content != original:
            file_path.write_text(content)
            print(f"✓ Upgraded thiserror to 2.0 in {file_path}")
            return True
        return False
    except Exception as e:
        print(f"✗ Error updating {file_path}: {e}")
        return False

def replace_lib_pq(go_mod_path):
    """Replace lib/pq with pgx/v5 in go.mod"""
    try:
        content = go_mod_path.read_text()
        original = content
        
        # Remove lib/pq
        content = re.sub(r'github\.com/lib/pq\s+v[\d.]+\s*\n', '', content)
        
        # Add pgx/v5 if not present
        if 'github.com/jackc/pgx/v5' not in content:
            # Find require block and add pgx
            require_match = re.search(r'(require\s*\([^)]*)', content, re.DOTALL)
            if require_match:
                insert_pos = require_match.end() - 1  # Before closing paren
                content = content[:insert_pos] + '\tgithub.com/jackc/pgx/v5 v5.8.0\n' + content[insert_pos:]
        
        if content != original:
            go_mod_path.write_text(content)
            print(f"✓ Replaced lib/pq with pgx/v5 in {go_mod_path}")
            return True
        return False
    except Exception as e:
        print(f"✗ Error updating {go_mod_path}: {e}")
        return False

def main():
    base_path = Path("/Users/kooshapari/temp-PRODVERCEL/485/kush")
    
    print("🔧 Implementing High-Priority Legacy Replacements")
    print("=" * 80)
    
    # Rust replacements
    print("\n📦 RUST REPLACEMENTS")
    print("-" * 80)
    
    cargo_files = [f for f in base_path.rglob("Cargo.toml") 
                   if ".venv" not in str(f) and "venv" not in str(f)]
    
    lazy_static_count = 0
    md5_count = 0
    hex_count = 0
    thiserror_count = 0
    
    for cargo_file in cargo_files:
        try:
            content = cargo_file.read_text()
            if 'lazy_static' in content:
                if replace_lazy_static(cargo_file):
                    lazy_static_count += 1
            if 'md5' in content and 'md5-simd' not in content:
                if replace_md5(cargo_file):
                    md5_count += 1
            if re.search(r'hex\s*=\s*"0\.4', content):
                if replace_hex(cargo_file):
                    hex_count += 1
            if re.search(r'thiserror\s*=\s*"1\.', content):
                if upgrade_thiserror(cargo_file):
                    thiserror_count += 1
        except Exception as e:
            print(f"✗ Error processing {cargo_file}: {e}")
    
    print(f"\n✅ Rust replacements:")
    print(f"   - lazy_static removed: {lazy_static_count} files")
    print(f"   - md5 → sha2: {md5_count} files")
    print(f"   - hex → base16ct: {hex_count} files")
    print(f"   - thiserror 1.0 → 2.0: {thiserror_count} files")
    
    # Go replacements
    print("\n📦 GO REPLACEMENTS")
    print("-" * 80)
    
    go_mod_files = [f for f in base_path.rglob("go.mod")
                    if ".venv" not in str(f) and "venv" not in str(f)]
    
    lib_pq_count = 0
    for go_mod in go_mod_files:
        try:
            content = go_mod.read_text()
            if 'github.com/lib/pq' in content:
                if replace_lib_pq(go_mod):
                    lib_pq_count += 1
        except Exception as e:
            print(f"✗ Error processing {go_mod}: {e}")
    
    print(f"\n✅ Go replacements:")
    print(f"   - lib/pq → pgx/v5: {lib_pq_count} files")
    
    print("\n" + "=" * 80)
    print("⚠️  IMPORTANT: Code changes required!")
    print("=" * 80)
    print("\nAfter dependency updates, you must update source code:")
    print("\n1. lazy_static → std::sync::OnceLock:")
    print("   - Update imports and usage patterns")
    print("   - See LEGACY_MODERN_ALTERNATIVES_REPORT.md for examples")
    print("\n2. md5 → sha2:")
    print("   - Update hash function calls")
    print("   - Change Md5::digest() to Sha256::digest()")
    print("\n3. hex → base16ct:")
    print("   - Update encoding/decoding calls")
    print("   - Change hex::encode() to base16ct::lower::encode_string()")
    print("\n4. thiserror 1.0 → 2.0:")
    print("   - Mostly drop-in, check changelog for breaking changes")
    print("\n5. lib/pq → pgx/v5:")
    print("   - Update database connection code")
    print("   - Change sql.Open() to pgx.Connect()")
    print("   - Update query patterns")
    print("\nRun 'cargo check' and 'go build' to identify code changes needed.")

if __name__ == "__main__":
    main()
