"""Smart pruning logic for agent resource reclamation.

Implements the strategy defined in docs/research/SMART_PRUNING_STRATEGY.md.
"""

import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from thegent.cli_impl import ps_impl
from thegent.config import ThegentSettings
from thegent.execution import RunRegistry
from thegent.tools.terminal import capture_tmux_pane, list_tmux_panes, send_to_tmux_pane

logger = logging.getLogger(__name__)

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

    def __init__(self, project_root: Optional[Path] = None):
        self.settings = ThegentSettings()
        self.project_root = project_root or Path.cwd()
        self.state_file = Path.home() / ".thegent" / "smart_prune_state.json"
        self.snapshots: Dict[str, SessionSnapshot] = {}
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
                        complete_signal_detected=snap.get("complete_signal_detected", False)
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
                    "complete_signal_detected": snap.complete_signal_detected
                }
                for sid, snap in self.snapshots.items()
            }
            self.state_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.warning(f"Failed to save smart prune state: {e}")

    def discover_sessions(self) -> List[Dict[str, Any]]:
        """Find all active managed and IDE sessions."""
        return ps_impl(scan_ide=True, all=True)

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
            r"Done!",
            r"Task finished",
            r"completed successfully",
            r"Cursor turned off",
            r"\(done\)",
            r"\[done\]",
            r"exit code: 0",
            r"^>$", # Claude Code prompt return
        ]
        
        last_chunk = output[-1000:]
        for marker in markers:
            if re.search(marker, last_chunk, re.MULTILINE | re.IGNORECASE):
                return True
        return False

    def run_cycle(self, force_prune: bool = False, reprompt: bool = True) -> Dict[str, Any]:
        """Run one pruning cycle."""
        sessions = self.discover_sessions()
        panes = list_tmux_panes()
        results = {
            "scanned": len(sessions),
            "pruned": 0,
            "reprompted": 0,
            "kept": 0,
            "details": []
        }

        now = time.time()
        
        # Cursor terminal directory detection
        cursor_term_dir = Path("/Users/kooshapari/.cursor/projects/Users-kooshapari-temp-PRODVERCEL-485-kush-thegent/terminals")
        
        # Filter to only running sessions
        active_sessions = [s for s in sessions if s.get("status") == "running"]
        
        for sess in active_sessions:
            sid = sess["id"]
            pid = sess.get("pid")
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
            is_idle = snap.idle_count >= 2 # 2 consecutive unchanged outputs (assuming 30s interval)
            
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
                    st = datetime.fromisoformat(start_time.replace('Z', '+00:00')).timestamp()
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
                    self._prune_session(sess)
                    results["pruned"] += 1
                    results["details"].append(f"Pruned {sid} (idle={is_idle}, complete={is_complete}, docs={docs_written})")
                    if sid in self.snapshots:
                        del self.snapshots[sid]
                elif reprompt:
                    # REPROMPT
                    msg = "Automated Guard: You appear to have finished your task but haven't written a conversation dump to docs/research/. Please write one now before I prune this session to save memory."
                    sent = False
                    if pane:
                        sent = send_to_tmux_pane(pane.pane_id, msg)
                    
                    if not sent and self.settings.platform == "darwin":
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

    def _prune_session(self, session: Dict[str, Any]):
        """Kill LSPs/MCPs for a session."""
        pid = session.get("pid")
        if not pid:
            return

        # Use enhanced mcp_prune to target sub-processes of this specific parent
        from thegent.main import mcp_prune
        try:
            # We cast to int because ps_impl might return it as string or int
            mcp_prune(force=True, parent_pid=int(pid))
        except Exception as e:
            logger.warning(f"Failed targeted prune for {session['id']} (PID {pid}): {e}")
            # Fallback to global orphan prune
            mcp_prune(force=True)
        
        # If it's a thegent-managed session, we can stop it properly
        if session.get("source") == "thegent-run":
            try:
                from thegent.cli_impl import stop_impl
                stop_impl(run_id=session["id"])
            except:
                pass

def smart_prune_main(force: bool = False, reprompt: bool = True):
    """Entry point for smart pruning."""
    pruner = SmartPruner()
    results = pruner.run_cycle(force_prune=force, reprompt=reprompt)
    return results
