"""Smart pruning logic for agent resource reclamation.

Implements the strategy defined in docs/research/SMART_PRUNING_STRATEGY.md.
"""

import json
import logging
import os
import re
import signal
import sys
import time
from typing import Any

from thegent.skills.terminal import TmuxPane


def pause_process(pid: int):
    """Pause a process (SIGSTOP)."""
    try:
        os.kill(pid, signal.SIGSTOP)
        return True
    except Exception:
        return False


def resume_process(pid: int):
    """Resume a process (SIGCONT)."""
    try:
        os.kill(pid, signal.SIGCONT)
        return True
    except Exception:
        return False


def get_tty_path(tty: str) -> str | None:
    """Get absolute path for TTY."""
    if not tty or tty == "??":
        return None
    if tty.startswith("/"):
        return tty
    return f"/dev/{tty}"


from dataclasses import dataclass
from pathlib import Path

from thegent.cli.commands.impl import ps_impl
from thegent.config import ThegentSettings
from thegent.skills.terminal import capture_tmux_pane, list_tmux_panes, send_to_tmux_pane

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level constants referenced by tests and pruning logic
# ---------------------------------------------------------------------------

IDLE_COUNT_THRESHOLD: int = 2
IDLE_THRESHOLD_SECONDS: float = 60.0

PROTECTED_PROCESS_NAMES: frozenset[str] = frozenset(
    {
        "cursor-agent",
        "thegent",
        "claude",
        "codex",
        "droid",
        "opencode",
        "copilot",
        "gemini",
        "bash",
        "zsh",
        "sh",
        "fish",
        "tcsh",
        "csh",
        "ghostty",
        "terminal",
        "iterm",
        "alacritty",
        "kitty",
        "wezterm",
        "warp",
    }
)


def is_protected_process(name: str) -> bool:
    """Return True if the process name/cmdline matches a protected process."""
    base = os.path.basename(name.split(maxsplit=1)[0]) if name else ""
    return base in PROTECTED_PROCESS_NAMES or any(p in base for p in PROTECTED_PROCESS_NAMES)


# Backward-compatible alias for tests/importers expecting the old private helper name.
_is_protected_process = is_protected_process


@dataclass
class SessionSnapshot:
    """Snapshot of a session's state for idle detection."""

    session_id: str
    last_output: str
    last_check_time: float
    idle_count: int = 0
    docs_verified: bool = False
    complete_signal_detected: bool = False


class SmartPruner:
    """Intelligent agent resource reclaimer."""

    def __init__(self, project_root: Path | None = None) -> None:
        self.settings = ThegentSettings()
        self.project_root = project_root or Path.cwd()
        self.state_file = Path.home() / ".thegent" / "smart_prune_state.json"
        self.snapshots: dict[str, SessionSnapshot] = {}
        self._load_state()

    def _load_state(self):
        """Load snapshots from disk."""
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text())
                for sid, snap in data.items():
                    self.snapshots[sid] = SessionSnapshot(
                        session_id=sid,
                        last_output=snap.get("last_output", ""),
                        last_check_time=snap.get("last_check_time", 0.0),
                        idle_count=snap.get("idle_count", 0),
                        docs_verified=snap.get("docs_verified", False),
                        complete_signal_detected=snap.get("complete_signal_detected", False),
                    )
            except Exception as e:
                logger.warning(f"Failed to load smart prune state: {e}")

    def _save_state(self):
        """Save snapshots to disk."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                sid: {
                    "last_output": snap.last_output,
                    "last_check_time": snap.last_check_time,
                    "idle_count": snap.idle_count,
                    "docs_verified": snap.docs_verified,
                    "complete_signal_detected": snap.complete_signal_detected,
                }
                for sid, snap in self.snapshots.items()
            }
            self.state_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.warning(f"Failed to save smart prune state: {e}")

    def discover_sessions(self) -> list[dict[str, Any]]:
        """Find all active managed and IDE sessions."""
        return ps_impl(scan_ide=True, all=True, status="running", limit=500)

    def check_docs_written(self, session_start_time: float) -> bool:
        """Check if any docs were modified since session start."""
        doc_dirs = [
            self.project_root / "docs" / "research",
            self.project_root / "docs" / "reports",
            self.project_root / "docs" / "dumps",
        ]

        for ddir in doc_dirs:
            if not ddir.exists():
                continue

            for f in ddir.glob("*.md"):
                if f.stat().st_mtime > session_start_time:
                    return True
        return False

    def detect_completion(self, output: str) -> bool:
        """Search output for completion markers."""
        markers = [
            r"Summary:",
            r"Task finished",
            r"completed successfully",
            r"Cursor turned off",
            r"\(done\)",
            r"\[done\]",
            # More specific markers for actual completion
            r"Task complete\.",
            r"Implementation finished\.",
            r"Migration successful\.",
        ]

        last_chunk = output[-1000:]
        return any(re.search(marker, last_chunk, re.MULTILINE | re.IGNORECASE) for marker in markers)

    def run_cycle(self, force_prune: bool = False, reprompt: bool = True) -> dict[str, Any]:
        """Run one pruning cycle."""
        logger.info(f"THEGENT SMART_PRUNE: Starting cycle (force={force_prune}, reprompt={reprompt})")
        sessions = self.discover_sessions()
        panes = list_tmux_panes()
        results = {"scanned": len(sessions), "pruned": 0, "reprompted": 0, "kept": 0, "details": []}

        now = time.time()

        # Cursor terminal directory detection
        cursor_term_dir = Path(
            "/Users/kooshapari/.cursor/projects/Users-kooshapari-temp-PRODVERCEL-485-kush-thegent/terminals"
        )

        # Filter to only running sessions
        active_sessions = [s for s in sessions if s.get("status") == "running"]

        for sess in active_sessions:
            sid = sess["id"]
            pid = sess.get("pid")

            # NEVER prune the agent itself in this loop
            if sess["agent"] in ("cursor-agent", "claude", "codex", "droid", "roid", "opencode", "thegent"):
                # We only want to prune their CHILDREN (LSPs etc) if they are done
                pass

            logger.debug(f"Processing session {sid} (PID {pid})")

            # Map to tmux pane
            pane = None
            if pid:
                for p in panes:
                    # Best effort match: command name or PID in title/path
                    if sess["agent"] in p.command.lower() or str(pid) in p.title:
                        pane = p
                        break

            output = ""
            if pane:
                output = capture_tmux_pane(pane.pane_id, last_lines=50)
                logger.debug(f"Mapped {sid} to tmux pane {pane.pane_id}")
            elif sess["agent"] == "cursor" and cursor_term_dir.exists():
                # Improved fallback for Cursor: match by PID in terminal file
                for tfile in cursor_term_dir.glob("*.txt"):
                    try:
                        content = tfile.read_text()
                        if f"pid: {pid}" in content:
                            output = content
                            logger.debug(f"Mapped {sid} to terminal file {tfile.name}")
                            # Also extract started_at if we don't have it
                            if not sess.get("started_at_utc"):
                                m = re.search(r"started_at: (.*)", content)
                                if m:
                                    sess["started_at_utc"] = m.group(1).strip()
                            break
                    except:
                        continue

            if not output:
                logger.debug(f"No output found for {sid}, skipping")
                results["kept"] += 1
                continue

            # Get or create snapshot
            snap = self.snapshots.get(sid)
            if not snap:
                snap = SessionSnapshot(session_id=sid, last_output=output, last_check_time=now)
                self.snapshots[sid] = snap

            # 1. Idle Detection
            if output == snap.last_output:
                snap.idle_count += 1
            else:
                snap.idle_count = 0
                snap.last_output = output

            snap.last_check_time = now
            is_idle = snap.idle_count >= IDLE_COUNT_THRESHOLD

            # 2. Completion Detection
            is_complete = self.detect_completion(output)
            snap.complete_signal_detected = is_complete

            # 3. Docs Verification
            # Best effort start time from session data, fallback to 1h ago
            start_time = sess.get("started_at_utc")
            if isinstance(start_time, str):
                try:
                    # Simple parse if ISO, otherwise fallback
                    from datetime import datetime

                    st = datetime.fromisoformat(start_time.replace("Z", "+00:00")).timestamp()
                except:
                    st = now - 3600
            else:
                st = now - 3600

            docs_written = self.check_docs_written(st)
            snap.docs_verified = docs_written

            # Decision Matrix
            if is_idle and is_complete:
                if docs_written or force_prune:
                    # PRUNE
                    self._prune_session(sess, pane=pane)
                    results["pruned"] += 1
                    results["details"].append(
                        f"Pruned {sid} (idle={is_idle}, complete={is_complete}, docs={docs_written})"
                    )
                    if sid in self.snapshots:
                        del self.snapshots[sid]
                elif reprompt:
                    # REPROMPT
                    msg = "Automated Guard: You appear to have finished your task but haven't written a conversation dump to docs/research/. Please write one now before I prune this session to save memory."
                    sent = False
                    if pane:
                        sent = send_to_tmux_pane(pane.pane_id, msg)

                    if not sent and sys.platform == "darwin":
                        # Fallback: macOS Desktop Automation (AppleScript)
                        try:
                            from thegent.automation.macos_desktop import MacOSDesktopAutomation

                            automation = MacOSDesktopAutomation()
                            # This tries to type into the active window if it matches our agent
                            script = f'''
                            tell application "System Events"
                                set activeApp to name of first application process whose frontmost is true
                                if activeApp contains "Cursor" or activeApp contains "Ghostty" then
                                    keystroke "{msg}"
                                    key code 36 -- Enter
                                end if
                            end tell
                            '''
                            automation.run_applescript(script)
                            sent = True
                        except:
                            pass

                    if sent:
                        results["reprompted"] += 1
                        results["details"].append(f"Reprompted {sid}")
                    else:
                        results["kept"] += 1
                else:
                    results["kept"] += 1

        self._save_state()
        return results

    def _prune_session(self, session: dict[str, Any], pane: TmuxPane | None = None):
        """Kill LSPs/MCPs for a session. If interactive, prompt user."""
        pid = session.get("pid")
        if not pid:
            return

        tty = session.get("tty")
        agent = session.get("agent", "unknown")

        # If it's a TTY-attached session, try interactive pause/kill
        if tty and sys.platform == "darwin":
            # Attempt interactive prompt if in tmux
            if pane:
                self._show_interactive_menu(session, pane)
                return

        # Use enhanced mcp_prune to target sub-processes of this specific parent
        from thegent.orchestration.pruning.prune import mcp_prune

        try:
            # We cast to int because ps_impl might return it as string or int
            caller_info = f"smart_prune (session {session['id']}, agent {agent})"
            mcp_prune(force=True, parent_pid=int(pid), interactive=False, caller_info=caller_info)
        except Exception as e:
            logger.error(f"Failed targeted prune for {session['id']} (PID {pid}): {e}", exc_info=True)
            # DO NOT fallback to global orphan prune here, it's too dangerous
            # and could kill legitimate shells or other agents.
            # mcp_prune(force=True)

        # If it's a thegent-managed session, we can stop it properly
        if session.get("source") == "thegent-run":
            try:
                from thegent.cli.commands.impl import stop_impl

                stop_impl(session_id=session["id"])
            except:
                pass

    def _show_interactive_menu(self, session: dict[str, Any], pane: TmuxPane):
        """Show a tmux menu for resource management."""
        import subprocess

        pid = int(session["pid"])
        sid = session["id"]
        agent = session["agent"]
        title_text = session.get("prompt_preview", agent)

        menu_title = f"THEGENT: Resource Guard for {agent}"

        # Capture last 50 lines and title for context message
        last_output = capture_tmux_pane(pane.pane_id, last_lines=50)

        # Build tmux display-menu command
        # Syntax: display-menu [-t target-pane] [-T title] [-x x] [-y y] name key command ...
        cmd = [
            "tmux",
            "display-menu",
            "-t",
            pane.pane_id,
            "-T",
            menu_title,
            "Pause & View Context (P)",
            "p",
            f"run-shell 'kill -STOP {pid}; tmux display-message -t {pane.pane_id} \"PAUSED: {agent} session ({title_text}). Use kill -CONT {pid} to resume. Review cockpit for details.\"'",
            "Kill & Reclaim (K)",
            "k",
            f"run-shell 'thegent mcp prune --force --parent-pid {pid}'",
            "Bypass - Keep Alive (B)",
            "b",
            f"display-message 'Prune bypassed for session {sid}.'",
            "",
            "",
            "",
            "Exit Menu (Esc)",
            "Escape",
            "",
        ]

        try:
            # We also send a clear text banner before showing the menu so it's visible in the pane
            # Include the last 50 lines of context as requested
            context_header = f"\n\n{'=' * 20} THEGENT CONTEXT SNAPSHOT {'=' * 20}\n"
            context_footer = f"\n{'=' * 66}\n"
            banner = f"{context_header}{last_output}{context_footer}\n*** THEGENT: High resources detected for session {sid} ({agent}) ***\nTask: {title_text}\n(Showing menu for Kill/Pause/Bypass)\n"
            send_to_tmux_pane(pane.pane_id, banner, enter=False)

            subprocess.run(cmd, check=False)
            logger.info(f"Showed interactive menu for {sid} in pane {pane.pane_id}")
        except Exception as e:
            logger.warning(f"Failed to show interactive menu: {e}")
            # Fallback: just send keys as a text prompt
            msg = f"\n\n*** THEGENT RESOURCE GUARD ***\nAgent {agent} (PID {pid}) is using high resources.\nUse 'kill -STOP {pid}' to pause, or 'thegent mcp prune --force --parent-pid {pid}' to kill sub-procs.\n******************************\n"
            send_to_tmux_pane(pane.pane_id, msg, enter=False)


def smart_prune_main(force: bool = False, reprompt: bool = True):
    """Entry point for smart pruning."""
    pruner = SmartPruner()
    results = pruner.run_cycle(force_prune=force, reprompt=reprompt)
    return results
