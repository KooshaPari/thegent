"""File-based IPC (inter-process communication) for cross-project agent coordination.

Uses a Maildir-style atomic write protocol so agents in different projects
can exchange messages without any network service.

Directory layout::

    ~/.thegent/ipc/
      <recipient_hash>/      # SHA256 of recipient address, first 16 hex chars
        tmp/                 # staging: write here first
        new/                 # ready to be read
        cur/                 # claimed (in-flight) by receiver
      broadcast/             # well-known inbox for broadcast messages
        tmp/
        new/
        cur/

Message file format (JSON, one message per file)::

    {
        "msg_id":   "<uuid>",
        "sender":   "<project_root>:<agent_id>",
        "recipient": "<project_root>:<agent_id>" | "*",
        "topic":    "<string>",
        "payload":  { ... },
        "timestamp": <unix float>,
        "reply_to": "<msg_id>" | null
    }

Atomicity guarantee: every delivery uses ``os.rename`` from ``tmp/`` to
``new/``, which is atomic on POSIX filesystems.  Concurrent senders writing
to the same inbox are safe because each file name contains a UUID.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

_log = logging.getLogger(__name__)

# Global IPC directory under the user's home folder.
IPC_DIR: Path = Path.home() / ".thegent" / "ipc"

# Special address used for broadcast messages.
BROADCAST_ADDR: str = "*"

# Well-known inbox name for broadcast deliveries.
_BROADCAST_INBOX: str = "broadcast"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class IpcMessage:
    """A single IPC message exchanged between agents.

    Attributes:
        msg_id:    Unique identifier for this message (UUID).
        sender:    Originator address in ``"<project_root>:<agent_id>"`` form.
        recipient: Destination address or ``"*"`` for broadcast.
        topic:     Application-level message category / type.
        payload:   Arbitrary JSON-serialisable data.
        timestamp: Unix epoch float when the message was created.
        reply_to:  ``msg_id`` of the message this is a reply to, or ``None``.
    """

    msg_id: str
    sender: str
    recipient: str
    topic: str
    payload: dict
    timestamp: float
    reply_to: str | None = None

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_json(self) -> str:
        """Serialise to a JSON string."""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, text: str) -> IpcMessage:
        """Deserialise from a JSON string."""
        data = json.loads(text)
        return cls(**data)

    @classmethod
    def from_dict(cls, data: dict) -> IpcMessage:
        """Construct from a plain dictionary."""
        return cls(**data)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _inbox_name(address: str) -> str:
    """Return the inbox directory name for *address*.

    For ordinary addresses we use the first 16 hex characters of the SHA-256
    digest so that project paths with slashes or colons don't create nested
    directories.  The broadcast inbox has a fixed well-known name.
    """
    if address == BROADCAST_ADDR:
        return _BROADCAST_INBOX
    digest = hashlib.sha256(address.encode()).hexdigest()
    return digest[:16]


def _init_inbox(inbox_dir: Path) -> None:
    """Create the three Maildir sub-directories inside *inbox_dir*."""
    for subdir in ("tmp", "new", "cur"):
        (inbox_dir / subdir).mkdir(parents=True, exist_ok=True, mode=0o1777)


def _deliver(inbox_dir: Path, msg: IpcMessage) -> None:
    """Atomically deliver *msg* into *inbox_dir*/new/."""
    _init_inbox(inbox_dir)
    tmp_path = inbox_dir / "tmp" / msg.msg_id
    new_path = inbox_dir / "new" / msg.msg_id
    tmp_path.write_text(msg.to_json(), encoding="utf-8")
    tmp_path.rename(new_path)
    _log.debug("delivered msg=%s to %s", msg.msg_id, inbox_dir)


def _claim_one(inbox_dir: Path) -> IpcMessage | None:
    """Claim the oldest message from *inbox_dir*/new/ (FIFO by mtime).

    Returns ``None`` when there are no messages.
    """
    new_dir = inbox_dir / "new"
    cur_dir = inbox_dir / "cur"
    if not new_dir.exists():
        return None

    entries = [e for e in new_dir.iterdir() if e.is_file()]
    if not entries:
        return None

    # FIFO: sort by modification time (oldest first).
    entries.sort(key=lambda e: e.stat().st_mtime)

    for entry in entries:
        cur_path = cur_dir / entry.name
        try:
            entry.rename(cur_path)
        except FileNotFoundError:
            # Another reader raced us; try the next entry.
            _log.debug("msg %s already claimed, skipping", entry.name)
            continue

        try:
            msg = IpcMessage.from_json(cur_path.read_text(encoding="utf-8"))
            _log.debug("claimed msg=%s", msg.msg_id)
            return msg
        except (json.JSONDecodeError, TypeError) as exc:
            _log.warning("skipping corrupt message %s: %s", cur_path, exc)
            cur_path.unlink(missing_ok=True)

    return None


def _list_inbox(inbox_dir: Path) -> list[IpcMessage]:
    """Return all messages in *inbox_dir*/new/ without claiming them."""
    new_dir = inbox_dir / "new"
    if not new_dir.exists():
        return []
    results: list[IpcMessage] = []
    for entry in new_dir.iterdir():
        if not entry.is_file():
            continue
        try:
            results.append(IpcMessage.from_json(entry.read_text(encoding="utf-8")))
        except (FileNotFoundError, json.JSONDecodeError, TypeError) as exc:
            _log.debug("skipping %s: %s", entry, exc)
    return results


# ---------------------------------------------------------------------------
# Primary API
# ---------------------------------------------------------------------------


class CrossProjectIpc:
    """File-based IPC client for cross-project agent communication.

    Each instance is bound to a single ``(project_root, agent_id)`` pair and
    writes/reads from ``IPC_DIR`` (``~/.thegent/ipc/`` by default).

    Args:
        agent_id:     Identifier for this agent (unique within the project).
        project_root: Filesystem path to the owning project.
        ipc_dir:      Override the global IPC directory (useful in tests).
    """

    def __init__(
        self,
        agent_id: str,
        project_root: Path,
        *,
        ipc_dir: Path | None = None,
    ) -> None:
        self.agent_id = agent_id
        self.project_root = Path(project_root)
        self._ipc_dir = ipc_dir or IPC_DIR

        # My canonical address: "<project_root>:<agent_id>"
        self.address: str = f"{self.project_root}:{self.agent_id}"

        # My personal inbox directory
        self._inbox_dir: Path = self._ipc_dir / _inbox_name(self.address)
        _init_inbox(self._inbox_dir)

    # ------------------------------------------------------------------
    # Sending
    # ------------------------------------------------------------------

    def send(self, recipient: str, topic: str, payload: dict) -> str:
        """Send a message to *recipient*.

        Args:
            recipient: Target address (``"<project_root>:<agent_id>"``).
            topic:     Message topic / type string.
            payload:   Arbitrary JSON-serialisable data.

        Returns:
            The unique ``msg_id`` of the sent message.
        """
        msg = IpcMessage(
            msg_id=str(uuid.uuid4()),
            sender=self.address,
            recipient=recipient,
            topic=topic,
            payload=payload,
            timestamp=time.time(),
            reply_to=None,
        )
        inbox_dir = self._ipc_dir / _inbox_name(recipient)
        _deliver(inbox_dir, msg)
        _log.info("send msg=%s topic=%s to=%s", msg.msg_id, topic, recipient)
        return msg.msg_id

    def broadcast(self, topic: str, payload: dict) -> str:
        """Broadcast a message to all listening agents.

        Delivers to the well-known ``broadcast`` inbox so that any agent
        polling that inbox receives it.

        Args:
            topic:   Message topic.
            payload: Arbitrary JSON-serialisable data.

        Returns:
            The unique ``msg_id``.
        """
        msg = IpcMessage(
            msg_id=str(uuid.uuid4()),
            sender=self.address,
            recipient=BROADCAST_ADDR,
            topic=topic,
            payload=payload,
            timestamp=time.time(),
            reply_to=None,
        )
        broadcast_dir = self._ipc_dir / _BROADCAST_INBOX
        _deliver(broadcast_dir, msg)
        _log.info("broadcast msg=%s topic=%s", msg.msg_id, topic)
        return msg.msg_id

    def reply(self, original: IpcMessage, payload: dict) -> str:
        """Send a reply to the sender of *original*.

        Args:
            original: The message being replied to.
            payload:  Reply payload.

        Returns:
            The unique ``msg_id`` of the reply.
        """
        msg = IpcMessage(
            msg_id=str(uuid.uuid4()),
            sender=self.address,
            recipient=original.sender,
            topic=original.topic,
            payload=payload,
            timestamp=time.time(),
            reply_to=original.msg_id,
        )
        inbox_dir = self._ipc_dir / _inbox_name(original.sender)
        _deliver(inbox_dir, msg)
        _log.info("reply msg=%s reply_to=%s", msg.msg_id, original.msg_id)
        return msg.msg_id

    # ------------------------------------------------------------------
    # Receiving
    # ------------------------------------------------------------------

    def receive(self, timeout: float = 0.0) -> IpcMessage | None:
        """Claim the next message from this agent's inbox.

        When *timeout* is 0 the call is non-blocking; when *timeout* > 0 it
        polls until a message arrives or the timeout elapses.

        Args:
            timeout: Maximum seconds to wait.  0 means non-blocking.

        Returns:
            The claimed :class:`IpcMessage`, or ``None`` if none arrived.
        """
        return self._poll(self._inbox_dir, timeout)

    def receive_broadcast(self, timeout: float = 0.0) -> IpcMessage | None:
        """Claim the next broadcast message.

        Args:
            timeout: Maximum seconds to wait.  0 means non-blocking.

        Returns:
            The claimed :class:`IpcMessage`, or ``None``.
        """
        broadcast_dir = self._ipc_dir / _BROADCAST_INBOX
        return self._poll(broadcast_dir, timeout)

    def receive_topic(self, topic: str, timeout: float = 5.0) -> IpcMessage | None:
        """Claim the next message matching *topic* from this agent's inbox.

        Messages that do not match *topic* are left untouched in the inbox.

        Args:
            topic:   The topic string to filter on.
            timeout: Maximum seconds to wait.

        Returns:
            The first matching :class:`IpcMessage`, or ``None``.
        """
        deadline = time.monotonic() + timeout
        poll_interval = 0.05
        while True:
            # Peek at all available messages without claiming them.
            available = _list_inbox(self._inbox_dir)
            for msg in available:
                if msg.topic == topic:
                    # Attempt to claim it atomically.
                    new_path = self._inbox_dir / "new" / msg.msg_id
                    cur_path = self._inbox_dir / "cur" / msg.msg_id
                    try:
                        new_path.rename(cur_path)
                        _log.debug("receive_topic claimed msg=%s topic=%s", msg.msg_id, topic)
                        return msg
                    except FileNotFoundError:
                        # Another reader claimed it; move on.
                        _log.debug("msg %s raced away", msg.msg_id)
                        continue

            if timeout == 0.0 or time.monotonic() >= deadline:
                return None
            time.sleep(poll_interval)

    def ack(self, msg_id: str) -> None:
        """Acknowledge receipt of *msg_id*, removing it from the inbox.

        Idempotent — safe to call more than once or on an unknown ID.

        Args:
            msg_id: The message ID to acknowledge.
        """
        cur_path = self._inbox_dir / "cur" / msg_id
        try:
            cur_path.unlink()
            _log.debug("ack msg=%s", msg_id)
        except FileNotFoundError:
            _log.debug("ack msg=%s not found (already removed?)", msg_id)

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def list_pending(self) -> list[IpcMessage]:
        """Return all messages waiting in this agent's ``new/`` inbox."""
        return _list_inbox(self._inbox_dir)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _poll(inbox_dir: Path, timeout: float) -> IpcMessage | None:
        """Poll *inbox_dir* for a message, blocking up to *timeout* seconds."""
        if timeout == 0.0:
            return _claim_one(inbox_dir)

        poll_interval = 0.05
        deadline = time.monotonic() + timeout
        while True:
            msg = _claim_one(inbox_dir)
            if msg is not None:
                return msg
            if time.monotonic() >= deadline:
                return None
            time.sleep(poll_interval)


# ---------------------------------------------------------------------------
# Long-running server
# ---------------------------------------------------------------------------


class CrossProjectIpcServer:
    """Long-running server that dispatches incoming IPC messages to handlers.

    Handlers are registered per topic.  An optional ``default_handler`` is
    called for messages whose topic has no specific handler.

    Example::

        server = CrossProjectIpcServer(ipc)
        server.register("ping", lambda msg: ipc.reply(msg, {"pong": True}))
        server.run(poll_interval=0.1)

    Args:
        ipc:             A :class:`CrossProjectIpc` instance whose inbox is
                         polled.
        poll_interval:   Seconds between inbox polls when idle.
        include_broadcast: When ``True``, also polls the broadcast inbox.
    """

    def __init__(
        self,
        ipc: CrossProjectIpc,
        *,
        poll_interval: float = 0.1,
        include_broadcast: bool = True,
    ) -> None:
        self._ipc = ipc
        self._poll_interval = poll_interval
        self._include_broadcast = include_broadcast
        self._handlers: dict[str, Callable[[IpcMessage], None]] = {}
        self._default_handler: Callable[[IpcMessage], None] | None = None
        self._running = False

    def register(self, topic: str, handler: Callable[[IpcMessage], None]) -> None:
        """Register a *handler* for messages with the given *topic*.

        Args:
            topic:   The topic string to match.
            handler: Callable that receives an :class:`IpcMessage`.
        """
        self._handlers[topic] = handler

    def set_default_handler(self, handler: Callable[[IpcMessage], None]) -> None:
        """Set a catch-all *handler* for unregistered topics."""
        self._default_handler = handler

    def stop(self) -> None:
        """Signal the server loop to stop after the current iteration."""
        self._running = False

    def run(self, max_iterations: int | None = None) -> None:
        """Start the dispatch loop.

        Args:
            max_iterations: Stop after processing this many iterations
                            (useful for testing).  ``None`` means run forever.
        """
        self._running = True
        iteration = 0
        _log.info("CrossProjectIpcServer starting for %s", self._ipc.address)

        while self._running:
            if max_iterations is not None and iteration >= max_iterations:
                break

            processed = False

            # Check personal inbox.
            msg = self._ipc.receive()
            if msg is not None:
                self._dispatch(msg)
                self._ipc.ack(msg.msg_id)
                processed = True

            # Optionally check broadcast inbox.
            if self._include_broadcast:
                bcast = self._ipc.receive_broadcast()
                if bcast is not None:
                    self._dispatch(bcast)
                    processed = True

            if not processed:
                time.sleep(self._poll_interval)

            iteration += 1

        _log.info("CrossProjectIpcServer stopped after %d iterations", iteration)

    def _dispatch(self, msg: IpcMessage) -> None:
        """Route *msg* to the appropriate handler."""
        handler = self._handlers.get(msg.topic, self._default_handler)
        if handler is None:
            _log.debug("no handler for topic=%s msg=%s", msg.topic, msg.msg_id)
            return
        try:
            handler(msg)
        except Exception:
            _log.exception("handler for topic=%s raised", msg.topic)
