#!/usr/bin/env python3
"""
Policy Gate CLI: Agent Policy Change Approval System

Agents submit policy change requests, humans approve/deny, agents check status.
Stores requests in SQLite at ~/.phenotype/policy-requests.db

Usage:
  policy-gate request --policy <name> --change "<desc>" --requester "<agent>"
  policy-gate list [--status {pending|approved|denied}]
  policy-gate approve <id>
  policy-gate deny <id> [--reason "<reason>"]
  policy-gate check <id>
  policy-gate history <policy-name>
"""

import sqlite3
import json
import typer
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from enum import Enum
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Policy change approval system for agents")
console = Console()

# Constants
DB_DIR = Path.home() / ".phenotype"
DB_PATH = DB_DIR / "policy-requests.db"


class Status(str, Enum):
    """Request status enum."""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"


def ensure_db():
    """Create database and schema if not exists."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    conn.execute("""
        CREATE TABLE IF NOT EXISTS policy_requests (
            id TEXT PRIMARY KEY,
            policy_name TEXT NOT NULL,
            change_description TEXT NOT NULL,
            requester TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            requested_at TEXT NOT NULL,
            reviewed_by TEXT,
            reviewed_at TEXT,
            review_reason TEXT,
            metadata TEXT
        )
    """)

    conn.commit()
    conn.close()


def get_db():
    """Get database connection."""
    ensure_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def generate_request_id(policy_name: str, timestamp: str) -> str:
    """Generate a unique request ID."""
    # Format: POL-{POLICY}-{TIMESTAMP_HASH}
    import hashlib
    ts_hash = hashlib.md5(timestamp.encode()).hexdigest()[:8].upper()
    policy_short = policy_name[:8].upper()
    return f"POL-{policy_short}-{ts_hash}"


@app.command()
def request(
    policy: str = typer.Option(..., help="Policy name (e.g., 'agent-escalation', 'data-retention')"),
    change: str = typer.Option(..., help="Description of the change"),
    requester: str = typer.Option(..., help="Agent ID or name requesting the change"),
    metadata: Optional[str] = typer.Option(None, help="Optional JSON metadata"),
) -> None:
    """Submit a policy change request.

    Returns the request ID on success.
    Exit code: 0 on success, 1 on error.
    """
    try:
        conn = get_db()
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        request_id = generate_request_id(policy, now)

        # Validate metadata if provided
        if metadata:
            try:
                json.loads(metadata)
            except json.JSONDecodeError:
                console.print(f"[red]Error: invalid JSON metadata[/red]")
                raise typer.Exit(code=1)

        conn.execute("""
            INSERT INTO policy_requests
            (id, policy_name, change_description, requester, status, requested_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (request_id, policy, change, requester, "pending", now, metadata))

        conn.commit()
        conn.close()

        console.print(f"[green]✓ Request submitted[/green]")
        console.print(f"  ID: [cyan]{request_id}[/cyan]")
        console.print(f"  Policy: {policy}")
        console.print(f"  Status: pending")

    except Exception as e:
        console.print(f"[red]Error submitting request: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def list(
    status: Optional[Status] = typer.Option(None, help="Filter by status (pending, approved, denied)"),
    policy: Optional[str] = typer.Option(None, help="Filter by policy name"),
    limit: int = typer.Option(50, help="Maximum results to show"),
) -> None:
    """List policy change requests.

    Shows pending requests by default.
    """
    try:
        conn = get_db()

        query = "SELECT * FROM policy_requests WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status.value)
        else:
            # Default to pending if no status specified
            query += " AND status = ?"
            params.append("pending")

        if policy:
            query += " AND policy_name = ?"
            params.append(policy)

        query += " ORDER BY requested_at DESC LIMIT ?"
        params.append(limit)

        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            console.print("[yellow]No requests found[/yellow]")
            return

        table = Table(title=f"Policy Requests ({len(rows)})")
        table.add_column("ID", style="cyan")
        table.add_column("Policy", style="blue")
        table.add_column("Requester", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Requested", style="dim")

        for row in rows:
            status_style = {
                "pending": "yellow",
                "approved": "green",
                "denied": "red",
            }.get(row["status"], "white")

            table.add_row(
                row["id"],
                row["policy_name"],
                row["requester"],
                f"[{status_style}]{row['status']}[/{status_style}]",
                row["requested_at"][:10],
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing requests: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def approve(
    request_id: str = typer.Argument(..., help="Request ID to approve"),
    reviewer: Optional[str] = typer.Option(None, help="Reviewer name (default: $USER)"),
) -> None:
    """Approve a policy change request.

    Exit code: 0 on success, 1 on error.
    """
    try:
        import os
        reviewer_name = reviewer or os.getenv("USER", "unknown")

        conn = get_db()

        # Check request exists
        cursor = conn.execute(
            "SELECT * FROM policy_requests WHERE id = ?",
            (request_id,)
        )
        req = cursor.fetchone()

        if not req:
            console.print(f"[red]Error: Request {request_id} not found[/red]")
            raise typer.Exit(code=1)

        if req["status"] != "pending":
            console.print(f"[red]Error: Request is already {req['status']}[/red]")
            raise typer.Exit(code=1)

        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        conn.execute("""
            UPDATE policy_requests
            SET status = ?, reviewed_by = ?, reviewed_at = ?
            WHERE id = ?
        """, ("approved", reviewer_name, now, request_id))

        conn.commit()
        conn.close()

        console.print(f"[green]✓ Request approved[/green]")
        console.print(f"  ID: {request_id}")
        console.print(f"  Policy: {req['policy_name']}")
        console.print(f"  Reviewer: {reviewer_name}")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error approving request: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def deny(
    request_id: str = typer.Argument(..., help="Request ID to deny"),
    reason: Optional[str] = typer.Option(None, help="Reason for denial"),
    reviewer: Optional[str] = typer.Option(None, help="Reviewer name (default: $USER)"),
) -> None:
    """Deny a policy change request.

    Exit code: 0 on success, 1 on error.
    """
    try:
        import os
        reviewer_name = reviewer or os.getenv("USER", "unknown")

        conn = get_db()

        # Check request exists
        cursor = conn.execute(
            "SELECT * FROM policy_requests WHERE id = ?",
            (request_id,)
        )
        req = cursor.fetchone()

        if not req:
            console.print(f"[red]Error: Request {request_id} not found[/red]")
            raise typer.Exit(code=1)

        if req["status"] != "pending":
            console.print(f"[red]Error: Request is already {req['status']}[/red]")
            raise typer.Exit(code=1)

        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        conn.execute("""
            UPDATE policy_requests
            SET status = ?, reviewed_by = ?, reviewed_at = ?, review_reason = ?
            WHERE id = ?
        """, ("denied", reviewer_name, now, reason or "", request_id))

        conn.commit()
        conn.close()

        console.print(f"[red]✓ Request denied[/red]")
        console.print(f"  ID: {request_id}")
        console.print(f"  Policy: {req['policy_name']}")
        console.print(f"  Reviewer: {reviewer_name}")
        if reason:
            console.print(f"  Reason: {reason}")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error denying request: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def check(
    request_id: str = typer.Argument(..., help="Request ID to check"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output, use exit code only"),
) -> None:
    """Check the status of a policy change request.

    Exit codes:
      0 = approved (change may proceed)
      1 = pending or error (change must not proceed)
      2 = denied (change is explicitly blocked)
    """
    try:
        conn = get_db()

        cursor = conn.execute(
            "SELECT * FROM policy_requests WHERE id = ?",
            (request_id,)
        )
        req = cursor.fetchone()
        conn.close()

        if not req:
            if not quiet:
                console.print(f"[red]Error: Request {request_id} not found[/red]")
            raise typer.Exit(code=1)

        status = req["status"]

        if not quiet:
            status_emoji = {
                "pending": "⏳",
                "approved": "✓",
                "denied": "✗",
            }.get(status, "?")

            status_style = {
                "pending": "yellow",
                "approved": "green",
                "denied": "red",
            }.get(status, "white")

            console.print(f"[{status_style}]{status_emoji} {request_id}: {status}[/{status_style}]")
            console.print(f"  Policy: {req['policy_name']}")
            console.print(f"  Requester: {req['requester']}")
            console.print(f"  Requested: {req['requested_at']}")

            if req["reviewed_by"]:
                console.print(f"  Reviewed by: {req['reviewed_by']} at {req['reviewed_at']}")
            if req["review_reason"]:
                console.print(f"  Reason: {req['review_reason']}")

        # Exit codes match status
        if status == "approved":
            raise typer.Exit(code=0)
        elif status == "denied":
            raise typer.Exit(code=2)
        else:  # pending or unknown
            raise typer.Exit(code=1)

    except typer.Exit:
        raise
    except Exception as e:
        if not quiet:
            console.print(f"[red]Error checking request: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def history(
    policy_name: str = typer.Argument(..., help="Policy name to show history for"),
    limit: int = typer.Option(20, help="Maximum records to show"),
) -> None:
    """Show history of requests for a specific policy.

    Includes all statuses (pending, approved, denied).
    """
    try:
        conn = get_db()

        cursor = conn.execute("""
            SELECT * FROM policy_requests
            WHERE policy_name = ?
            ORDER BY requested_at DESC
            LIMIT ?
        """, (policy_name, limit))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            console.print(f"[yellow]No history found for policy '{policy_name}'[/yellow]")
            return

        table = Table(title=f"Policy History: {policy_name}")
        table.add_column("ID", style="cyan")
        table.add_column("Requester", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Requested", style="dim")
        table.add_column("Reviewed", style="dim")

        for row in rows:
            status_style = {
                "pending": "yellow",
                "approved": "green",
                "denied": "red",
            }.get(row["status"], "white")

            reviewed = row["reviewed_at"][:10] if row["reviewed_at"] else "-"

            table.add_row(
                row["id"],
                row["requester"],
                f"[{status_style}]{row['status']}[/{status_style}]",
                row["requested_at"][:10],
                reviewed,
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error retrieving history: {e}[/red]")
        raise typer.Exit(code=1)


@app.callback()
def callback():
    """Policy Gate: Agent-driven policy change approval system."""
    pass


if __name__ == "__main__":
    app()
