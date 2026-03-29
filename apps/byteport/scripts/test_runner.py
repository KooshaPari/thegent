#!/usr/bin/env python3
"""
BytePort Test Runner
====================

Unified test runner for all BytePort test suites:
- Backend Go tests with testify
- Frontend React/Next.js tests with Vitest
- E2E tests with Playwright

Usage:
    ./scripts/test_runner.py --all              # Run all tests
    ./scripts/test_runner.py --backend          # Backend only
    ./scripts/test_runner.py --frontend         # Frontend only
    ./scripts/test_runner.py --e2e              # E2E only
    ./scripts/test_runner.py --backend --frontend --coverage
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


class TestRunner:
    """Orchestrates test execution across BytePort services."""
    
    def __init__(self, root_dir: Path):
        self.root = root_dir
        self.backend_dir = root_dir / "backend" / "api"
        self.frontend_dir = root_dir / "frontend" / "web-next"
        self.results: List[Tuple[str, bool]] = []
    
    def run_backend_tests(self, coverage: bool = False) -> bool:
        """Run Go backend tests."""
        print("\n" + "=" * 60)
        print("🧪 Running Backend Tests (Go + testify)")
        print("=" * 60)
        
        if not self.backend_dir.exists():
            print(f"❌ Backend directory not found: {self.backend_dir}")
            return False
        
        cmd = ["go", "test"]
        
        if coverage:
            cmd.extend(["-race", "-coverprofile=coverage.out", "-covermode=atomic"])
        
        cmd.extend(["-v", "./..."])
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.backend_dir,
                env={
                    **subprocess.os.environ,
                    "GOCACHE": str(self.backend_dir / ".gocache"),
                    "GOMODCACHE": str(self.backend_dir / ".gomodcache"),
                }
            )
            
            success = result.returncode == 0
            
            if success:
                print("\n✅ Backend tests passed!")
                if coverage:
                    print("\n📊 Generating coverage report...")
                    subprocess.run(
                        ["go", "tool", "cover", "-html=coverage.out", "-o=coverage.html"],
                        cwd=self.backend_dir
                    )
                    print(f"   Coverage report: {self.backend_dir}/coverage.html")
            else:
                print("\n❌ Backend tests failed!")
            
            return success
        
        except FileNotFoundError:
            print("❌ Go not found in PATH. Please install Go.")
            return False
        except Exception as e:
            print(f"❌ Error running backend tests: {e}")
            return False
    
    def run_frontend_tests(self, coverage: bool = False, watch: bool = False) -> bool:
        """Run frontend Vitest tests."""
        print("\n" + "=" * 60)
        print("🧪 Running Frontend Tests (Vitest + Testing Library)")
        print("=" * 60)
        
        if not self.frontend_dir.exists():
            print(f"❌ Frontend directory not found: {self.frontend_dir}")
            return False
        
        # Check if node_modules exists
        if not (self.frontend_dir / "node_modules").exists():
            print("⚠️  node_modules not found. Installing dependencies...")
            install_result = subprocess.run(
                ["pnpm", "install", "--frozen-lockfile"],
                cwd=self.frontend_dir
            )
            if install_result.returncode != 0:
                print("❌ Failed to install dependencies")
                return False
        
        if watch:
            cmd = ["pnpm", "test"]
        elif coverage:
            cmd = ["pnpm", "test:coverage"]
        else:
            cmd = ["pnpm", "test:run"]
        
        try:
            result = subprocess.run(cmd, cwd=self.frontend_dir)
            
            success = result.returncode == 0
            
            if success:
                print("\n✅ Frontend tests passed!")
                if coverage:
                    print(f"\n📊 Coverage report: {self.frontend_dir}/coverage/index.html")
            else:
                print("\n❌ Frontend tests failed!")
            
            return success
        
        except FileNotFoundError:
            print("❌ pnpm not found. Please install pnpm.")
            return False
        except Exception as e:
            print(f"❌ Error running frontend tests: {e}")
            return False
    
    def run_e2e_tests(self) -> bool:
        """Run Playwright E2E tests."""
        print("\n" + "=" * 60)
        print("🧪 Running E2E Tests (Playwright)")
        print("=" * 60)
        
        if not self.frontend_dir.exists():
            print(f"❌ Frontend directory not found: {self.frontend_dir}")
            return False
        
        # Check if Playwright is installed
        if not (self.frontend_dir / "node_modules" / "@playwright").exists():
            print("⚠️  Playwright not found. Installing...")
            install_result = subprocess.run(
                ["pnpm", "playwright", "install", "--with-deps", "chromium"],
                cwd=self.frontend_dir
            )
            if install_result.returncode != 0:
                print("❌ Failed to install Playwright")
                return False
        
        try:
            result = subprocess.run(
                ["pnpm", "test:e2e"],
                cwd=self.frontend_dir,
                env={**subprocess.os.environ, "CI": "true"}
            )
            
            success = result.returncode == 0
            
            if success:
                print("\n✅ E2E tests passed!")
            else:
                print("\n❌ E2E tests failed!")
                print(f"   See report: {self.frontend_dir}/playwright-report/index.html")
            
            return success
        
        except FileNotFoundError:
            print("❌ pnpm not found. Please install pnpm.")
            return False
        except Exception as e:
            print(f"❌ Error running E2E tests: {e}")
            return False
    
    def print_summary(self):
        """Print summary of all test results."""
        print("\n" + "=" * 60)
        print("📋 Test Summary")
        print("=" * 60)
        
        if not self.results:
            print("No tests were run.")
            return
        
        for suite, passed in self.results:
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{suite:20} {status}")
        
        print("=" * 60)
        
        all_passed = all(passed for _, passed in self.results)
        if all_passed:
            print("🎉 All tests passed!")
        else:
            print("💥 Some tests failed!")
        
        return all_passed


def main():
    parser = argparse.ArgumentParser(
        description="BytePort Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Test suite selection
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--backend", action="store_true", help="Run backend Go tests")
    parser.add_argument("--frontend", action="store_true", help="Run frontend Vitest tests")
    parser.add_argument("--e2e", action="store_true", help="Run E2E Playwright tests")
    
    # Options
    parser.add_argument("--coverage", action="store_true", help="Generate coverage reports")
    parser.add_argument("--watch", action="store_true", help="Watch mode for frontend tests")
    
    args = parser.parse_args()
    
    # Determine project root
    script_dir = Path(__file__).resolve().parent
    root_dir = script_dir.parent
    
    runner = TestRunner(root_dir)
    
    # Default to all if nothing specified
    if not (args.all or args.backend or args.frontend or args.e2e):
        args.all = True
    
    # Run selected test suites
    if args.all or args.backend:
        result = runner.run_backend_tests(coverage=args.coverage)
        runner.results.append(("Backend Tests", result))
    
    if args.all or args.frontend:
        result = runner.run_frontend_tests(coverage=args.coverage, watch=args.watch)
        runner.results.append(("Frontend Tests", result))
    
    if args.all or args.e2e:
        result = runner.run_e2e_tests()
        runner.results.append(("E2E Tests", result))
    
    # Print summary and exit
    all_passed = runner.print_summary()
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
