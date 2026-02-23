#!/usr/bin/env python3
"""
Continuous session monitoring using wait commands.

Monitors all active sessions, using wait commands with auto-timeout handling.
Automatically retries wait commands every 2 minutes to prevent Cursor timeout.
"""

import orjson as json
import subprocess
import sys
import time
from typing import Any


def get_active_sessions() -> list[dict[str, Any]]:
    """Get list of currently running sessions."""
    try:
        result = subprocess.run(
            ["thegent", "ps", "--format", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
        sessions = json.loads(result.stdout)
        # Filter for running sessions only
        return [s for s in sessions if s.get("status") == "running"]
    except Exception as e:
        print(f"Error getting sessions: {e}", file=sys.stderr)
        return []


def wait_for_session(session_id: str, timeout: int = 0) -> tuple[bool, int]:
    """
    Wait for a session to complete.

    Returns:
        (completed, exit_code): True if completed, False if auto-timeout occurred
    """
    try:
        result = subprocess.run(
            ["thegent", "wait", session_id] + (["--timeout", str(timeout)] if timeout > 0 else []),
            capture_output=True,
            text=True,
        )
        exit_code = result.returncode

        # Exit code 2 = auto-timeout, retry needed
        if exit_code == 2:
            return (False, 0)

        # Other exit codes: 0 = success, non-zero = error
        return (True, exit_code)
    except Exception as e:
        print(f"Error waiting for session {session_id}: {e}", file=sys.stderr)
        return (True, 1)


def monitor_continuously(check_interval: float = 5.0):
    """
    Continuously monitor all active sessions.

    Args:
        check_interval: Seconds between checking for new sessions
    """
    monitored_sessions: set[str] = set()
    completed_sessions: dict[str, int] = {}  # session_id -> exit_code

    print("🔍 Starting continuous session monitoring...", flush=True)
    print(f"   Check interval: {check_interval}s", flush=True)
    print("   Auto-timeout: 2 minutes (will retry automatically)\n", flush=True)

    try:
        iteration = 0
        while True:
            iteration += 1
            # Get current active sessions
            active = get_active_sessions()
            active_ids = {s["id"] for s in active}

            # Start monitoring new sessions
            for session in active:
                session_id = session["id"]
                if session_id not in monitored_sessions:
                    print(f"📊 Monitoring session: {session_id}")
                    print(f"   Agent: {session.get('agent', 'unknown')}")
                    print(f"   Owner: {session.get('owner', 'unknown')}")
                    print(f"   PID: {session.get('pid', 'unknown')}")
                    monitored_sessions.add(session_id)

            # Wait for each monitored session (with auto-timeout handling)
            for session_id in list(monitored_sessions):
                if session_id not in active_ids:
                    # Session no longer active, check if it completed
                    if session_id not in completed_sessions:
                        # Final wait to get exit code
                        completed, exit_code = wait_for_session(session_id)
                        completed_sessions[session_id] = exit_code
                        status = "✅ completed" if exit_code == 0 else f"❌ failed (exit {exit_code})"
                        print(f"\n🏁 Session {session_id} {status}\n")
                else:
                    # Session still running, wait with auto-timeout
                    completed, exit_code = wait_for_session(session_id, timeout=0)
                    if completed:
                        # Session completed during wait
                        completed_sessions[session_id] = exit_code
                        monitored_sessions.discard(session_id)
                        status = "✅ completed" if exit_code == 0 else f"❌ failed (exit {exit_code})"
                        print(f"\n🏁 Session {session_id} {status}\n")
                    else:
                        # Auto-timeout occurred, will retry on next iteration
                        print(f"⏱️  Auto-timeout for {session_id} (will retry)...")

            # If no active sessions and all monitored sessions are done, continue monitoring
            # (don't exit - wait for new sessions to appear)
            if not active_ids and not monitored_sessions:
                if iteration % 12 == 0:  # Print every 12 iterations (every minute at 5s interval)
                    print(f"⏳ No active sessions. Waiting for new sessions... (check {iteration})", flush=True)

            # Wait before next check
            time.sleep(check_interval)

    except KeyboardInterrupt:
        print("\n\n⚠️  Monitoring interrupted by user.")
        if monitored_sessions:
            print(f"   Still monitoring: {', '.join(monitored_sessions)}")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during monitoring: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Continuously monitor active sessions using wait commands")
    parser.add_argument(
        "--check-interval",
        type=float,
        default=5.0,
        help="Seconds between checking for new sessions (default: 5.0)",
    )

    args = parser.parse_args()
    monitor_continuously(check_interval=args.check_interval)
