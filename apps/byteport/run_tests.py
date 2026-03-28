#!/usr/bin/env python3
"""
BytePort Test Runner
===================

Comprehensive test runner for all BytePort test suites.

Usage:
    python run_tests.py                  # Run all tests
    python run_tests.py --unit           # Run unit tests only
    python run_tests.py --e2e             # Run E2E tests only
    python run_tests.py --backend         # Run backend tests only
    python run_tests.py --frontend       # Run frontend tests only
    python run_tests.py --watch           # Run tests in watch mode
    python run_tests.py --coverage       # Run tests with coverage
"""

import argparse
import asyncio
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("test-runner")

# Root directory
BYTEPORT_ROOT = Path(__file__).resolve().parent
BACKEND_API_DIR = BYTEPORT_ROOT / "backend" / "api"
FRONTEND_DIR = BYTEPORT_ROOT / "frontend" / "web-next"

class TestResult:
    def __init__(self, name: str, success: bool, duration: float, output: str = ""):
        self.name = name
        self.success = success
        self.duration = duration
        self.output = output

class TestRunner:
    def __init__(self):
        self.results: List[TestResult] = []
        
    def run_command(self, cmd: List[str], cwd: Optional[Path] = None, env: Optional[Dict[str, str]] = None) -> TestResult:
        """Run a command and capture the result."""
        start_time = time.time()
        cmd_str = " ".join(cmd)
        logger.info(f"🏃 Running: {cmd_str}")
        
        try:
            process = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                env=env
            )
            
            duration = time.time() - start_time
            success = process.returncode == 0
            
            output = ""
            if process.stdout:
                output += f"STDOUT:\n{process.stdout}\n"
            if process.stderr:
                output += f"STDERR:\n{process.stderr}\n"
            
            result = TestResult(cmd_str, success, duration, output)
            
            if success:
                logger.info(f"✅ {cmd_str} - {duration:.2f}s")
            else:
                logger.error(f"❌ {cmd_str} - {duration:.2f}s")
                logger.error(f"Exit code: {process.returncode}")
                if process.stderr:
                    logger.error(f"Error: {process.stderr.strip()}")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ {cmd_str} - Failed to execute: {e}")
            return TestResult(cmd_str, False, duration, str(e))

    def run_backend_tests(self, coverage: bool = False) -> List[TestResult]:
        """Run Go backend tests."""
        logger.info("🔧 Running backend tests...")
        results = []
        
        # Set up Go environment
        import os
        env = os.environ.copy()
        env.update({
            "GOCACHE": str(BACKEND_API_DIR / ".gocache"),
            "GOMODCACHE": str(BACKEND_API_DIR / ".gomodcache"),
        })
        
        # Basic test command
        cmd = ["go", "test", "./..."]
        if coverage:
            cmd.extend(["-coverprofile=coverage.out", "-v"])
        else:
            cmd.append("-v")
        
        result = self.run_command(cmd, cwd=BACKEND_API_DIR, env=env)
        results.append(result)
        
        # Run specific test suites
        test_packages = [
            "./repositories/...",
            ".",  # handlers tests
        ]
        
        for package in test_packages:
            cmd = ["go", "test", package, "-v"]
            result = self.run_command(cmd, cwd=BACKEND_API_DIR, env=env)
            results.append(result)
        
        return results

    def run_frontend_tests(self, coverage: bool = False, watch: bool = False) -> List[TestResult]:
        """Run frontend tests with Vitest."""
        logger.info("⚛️ Running frontend tests...")
        results = []
        
        # Check if pnpm is available
        pnpm_available = subprocess.run(["which", "pnpm"], capture_output=True).returncode == 0
        package_manager = "pnpm" if pnpm_available else "npm"
        
        # Run tests
        if watch:
            cmd = [package_manager, "test"]  # Interactive watch mode
        elif coverage:
            cmd = [package_manager, "run", "test:coverage"]
        else:
            cmd = [package_manager, "run", "test:run"]
        
        result = self.run_command(cmd, cwd=FRONTEND_DIR)
        results.append(result)
        
        return results

    def run_e2e_tests(self, headed: bool = False, ui: bool = False) -> List[TestResult]:
        """Run E2E tests with Playwright."""
        logger.info("🎭 Running E2E tests...")
        results = []
        
        # Check if pnpm is available
        pnpm_available = subprocess.run(["which", "pnpm"], capture_output=True).returncode == 0
        package_manager = "pnpm" if pnpm_available else "npm"
        
        # Prepare test command
        if ui:
            cmd = [package_manager, "run", "test:e2e:ui"]
        elif headed:
            cmd = [package_manager, "run", "test:e2e:headed"]
        else:
            cmd = [package_manager, "run", "test:e2e"]
        
        result = self.run_command(cmd, cwd=FRONTEND_DIR)
        results.append(result)
        
        return results

    def print_summary(self):
        """Print test results summary."""
        logger.info("=" * 60)
        logger.info("📊 Test Results Summary")
        logger.info("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        total_duration = sum(r.duration for r in self.results)
        
        logger.info(f"Total tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Total duration: {total_duration:.2f}s")
        
        if failed_tests > 0:
            logger.info("")
            logger.error("Failed tests:")
            for result in self.results:
                if not result.success:
                    logger.error(f"  ❌ {result.name}")
                    if result.output:
                        # Show first few lines of error output
                        lines = result.output.split('\n')[:5]
                        for line in lines:
                            if line.strip():
                                logger.error(f"    {line}")
        
        logger.info("=" * 60)
        
        return failed_tests == 0

    async def run_all_tests(self, 
                          unit_only: bool = False, 
                          e2e_only: bool = False,
                          backend_only: bool = False,
                          frontend_only: bool = False,
                          coverage: bool = False,
                          watch: bool = False,
                          headed: bool = False,
                          ui: bool = False) -> bool:
        """Run the specified test suites."""
        
        logger.info("🧪 BytePort Test Runner Starting...")
        logger.info(f"Root directory: {BYTEPORT_ROOT}")
        
        # Determine which tests to run
        run_backend = not (e2e_only or frontend_only)
        run_frontend = not (e2e_only or backend_only)
        run_e2e = not (unit_only or backend_only or frontend_only)
        
        # Override for specific flags
        if backend_only:
            run_backend, run_frontend, run_e2e = True, False, False
        elif frontend_only:
            run_backend, run_frontend, run_e2e = False, True, False
        elif e2e_only:
            run_backend, run_frontend, run_e2e = False, False, True
        
        # Run tests
        if run_backend:
            backend_results = self.run_backend_tests(coverage=coverage)
            self.results.extend(backend_results)
        
        if run_frontend:
            frontend_results = self.run_frontend_tests(coverage=coverage, watch=watch)
            self.results.extend(frontend_results)
        
        if run_e2e:
            e2e_results = self.run_e2e_tests(headed=headed, ui=ui)
            self.results.extend(e2e_results)
        
        # Print summary
        success = self.print_summary()
        
        return success

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="BytePort Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Run unit tests only (backend + frontend)"
    )
    
    parser.add_argument(
        "--e2e",
        action="store_true",
        help="Run E2E tests only"
    )
    
    parser.add_argument(
        "--backend",
        action="store_true",
        help="Run backend tests only"
    )
    
    parser.add_argument(
        "--frontend",
        action="store_true",
        help="Run frontend tests only"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run tests with coverage reporting"
    )
    
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Run frontend tests in watch mode"
    )
    
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run E2E tests in headed mode (visible browser)"
    )
    
    parser.add_argument(
        "--ui",
        action="store_true",
        help="Run E2E tests with Playwright UI"
    )
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    try:
        success = asyncio.run(runner.run_all_tests(
            unit_only=args.unit,
            e2e_only=args.e2e,
            backend_only=args.backend,
            frontend_only=args.frontend,
            coverage=args.coverage,
            watch=args.watch,
            headed=args.headed,
            ui=args.ui
        ))
        
        if success:
            logger.info("🎉 All tests passed!")
            sys.exit(0)
        else:
            logger.error("💥 Some tests failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n👋 Test run interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()