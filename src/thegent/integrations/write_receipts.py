"""Write operation receipt tracking for sync cycles.

Tracks successful and failed write operations with remote IDs and cycle
information for audit and reconciliation.

FR traceability: WL-308 (Remote Write Receipts)
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class WriteReceipt:
    """Receipt for a single write operation.

    Attributes:
        wl_id: Work item or entity ID (local).
        connector: Connector that performed the write.
        operation: Type of operation (create, update, delete).
        remote_id: ID assigned by remote system, or None if failed.
        success: True if write succeeded.
        timestamp: When the write occurred.
        cycle_id: Sync cycle identifier.
    """

    wl_id: str
    connector: str
    operation: str
    remote_id: str | None
    success: bool
    timestamp: datetime
    cycle_id: str

    def to_dict(self) -> dict:
        """Convert to dict for serialization.

        Returns:
            Dict representation with timestamp as ISO string.
        """
        result = asdict(self)
        result["timestamp"] = self.timestamp.isoformat()
        return result


class WriteReceiptLog:
    """Log of write receipts persisted to JSONL.

    Attributes:
        log_path: Path to the JSONL file.
    """

    def __init__(self, log_path: Path | str) -> None:
        """Initialize the receipt log.

        Args:
            log_path: Path to the JSONL log file.
        """
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, receipt: WriteReceipt) -> None:
        """Append a receipt to the log.

        Args:
            receipt: The receipt to log.

        Raises:
            ValueError: If receipt is not a WriteReceipt.
        """
        if not isinstance(receipt, WriteReceipt):
            raise ValueError("receipt must be a WriteReceipt")

        line = json.dumps(receipt.to_dict())
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

        logger.debug(f"Logged write receipt: {receipt.wl_id} -> {receipt.remote_id}")

    def read_all(self) -> list[WriteReceipt]:
        """Read all receipts from the log.

        Returns:
            List of all WriteReceipt objects.

        Raises:
            ValueError: If log file is malformed.
        """
        if not self.log_path.exists():
            return []

        receipts = []
        with self.log_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    receipt = self._dict_to_receipt(data)
                    receipts.append(receipt)
                except (json.JSONDecodeError, ValueError) as e:
                    raise ValueError(f"Malformed receipt log entry: {e}") from e

        return receipts

    def read_by_cycle(self, cycle_id: str) -> list[WriteReceipt]:
        """Read receipts for a specific cycle.

        Args:
            cycle_id: The cycle ID to filter by.

        Returns:
            List of receipts matching the cycle.

        Raises:
            ValueError: If cycle_id is empty.
        """
        if not cycle_id or not isinstance(cycle_id, str):
            raise ValueError("cycle_id must be a non-empty string")

        all_receipts = self.read_all()
        return [r for r in all_receipts if r.cycle_id == cycle_id]

    def read_failures(self) -> list[WriteReceipt]:
        """Read all failed write receipts.

        Returns:
            List of receipts with success=False.
        """
        all_receipts = self.read_all()
        return [r for r in all_receipts if not r.success]

    @staticmethod
    def _dict_to_receipt(data: dict) -> WriteReceipt:
        """Convert a dict to a WriteReceipt.

        Args:
            data: Dictionary with receipt fields.

        Returns:
            A WriteReceipt instance.

        Raises:
            ValueError: If required fields are missing.
        """
        required_fields = {
            "wl_id",
            "connector",
            "operation",
            "remote_id",
            "success",
            "timestamp",
            "cycle_id",
        }
        if not required_fields.issubset(data.keys()):
            missing = required_fields - set(data.keys())
            raise ValueError(f"Missing required fields: {missing}")

        try:
            timestamp_str = data["timestamp"]
            if isinstance(timestamp_str, str):
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            else:
                raise ValueError("timestamp must be a string")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid timestamp: {e}") from e

        return WriteReceipt(
            wl_id=data["wl_id"],
            connector=data["connector"],
            operation=data["operation"],
            remote_id=data["remote_id"],
            success=data["success"],
            timestamp=timestamp,
            cycle_id=data["cycle_id"],
        )
