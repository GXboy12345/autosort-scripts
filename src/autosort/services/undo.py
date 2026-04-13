"""Undo system with transaction-based persistence."""

from __future__ import annotations

import json
import logging
import shutil
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from autosort.core.organizer import FileOperation, OperationType

logger = logging.getLogger(__name__)

UNDO_DIR = Path.home() / ".config" / "autosort"
DEFAULT_UNDO_PATH = UNDO_DIR / "undo.json"


@dataclass
class UndoTransaction:
    id: str
    timestamp: float
    description: str
    operations: List[FileOperation]
    completed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class UndoManager:
    """Manages undo transactions with JSON persistence."""

    def __init__(self, undo_file: Optional[Path] = None, max_transactions: int = 50):
        self.undo_file = undo_file or DEFAULT_UNDO_PATH
        self.max_transactions = max_transactions
        self.transactions: List[UndoTransaction] = []
        self._load()

    def start_transaction(self, description: str) -> str:
        tid = str(uuid.uuid4())
        self.transactions.append(
            UndoTransaction(id=tid, timestamp=time.time(), description=description, operations=[])
        )
        return tid

    def add_operation(self, transaction_id: str, operation: FileOperation) -> bool:
        tx = self._find(transaction_id)
        if tx is None:
            return False
        tx.operations.append(operation)
        return True

    def commit_transaction(self, transaction_id: str) -> bool:
        tx = self._find(transaction_id)
        if tx is None:
            return False
        tx.completed = True
        self._save()
        return True

    def rollback_transaction(self, transaction_id: str) -> bool:
        tx = self._find(transaction_id)
        if tx is None or not tx.completed:
            return False
        errors = sum(0 if self._undo_op(op) else 1 for op in reversed(tx.operations))
        self.transactions.remove(tx)
        self._save()
        return errors == 0

    def undo_last_transaction(self) -> bool:
        completed = [t for t in self.transactions if t.completed]
        if not completed:
            return False
        return self.rollback_transaction(completed[-1].id)

    def get_transaction_history(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": t.id,
                "timestamp": t.timestamp,
                "description": t.description,
                "operation_count": len(t.operations),
                "completed": t.completed,
                "date": datetime.fromtimestamp(t.timestamp).strftime("%Y-%m-%d %H:%M"),
            }
            for t in self.transactions
        ]

    def get_undo_info(self) -> Dict[str, Any]:
        completed = [t for t in self.transactions if t.completed]
        return {
            "can_undo": len(completed) > 0,
            "transaction_count": len(self.transactions),
            "completed_count": len(completed),
            "last_transaction": completed[-1].description if completed else None,
            "last_file_count": len(completed[-1].operations) if completed else 0,
        }

    def clear_history(self) -> bool:
        self.transactions.clear()
        self._save()
        return True

    # -- internals --

    def _find(self, tid: str) -> Optional[UndoTransaction]:
        return next((t for t in self.transactions if t.id == tid), None)

    def _undo_op(self, op: FileOperation) -> bool:
        try:
            if op.operation_type == OperationType.MOVE:
                return self._undo_move(op)
            if op.operation_type == OperationType.CREATE_DIR:
                return self._undo_mkdir(op)
            return False
        except Exception as e:
            logger.error(f"Undo failed: {e}")
            return False

    def _undo_move(self, op: FileOperation) -> bool:
        if not op.destination or not op.destination.exists():
            return False
        if op.source.exists():
            target = self._unique(op.source)
            shutil.move(str(op.destination), str(target))
        else:
            shutil.move(str(op.destination), str(op.source))
        return True

    def _undo_mkdir(self, op: FileOperation) -> bool:
        if op.source.is_dir() and not any(op.source.iterdir()):
            op.source.rmdir()
            return True
        return False

    def _unique(self, p: Path) -> Path:
        if not p.exists():
            return p
        stem, sfx, parent = p.stem, p.suffix, p.parent
        for i in range(1, 1001):
            c = parent / f"{stem}_restored_{i}{sfx}"
            if not c.exists():
                return c
        return parent / f"{stem}_restored_{int(time.time())}{sfx}"

    def _load(self):
        try:
            if not self.undo_file.exists():
                return
            with open(self.undo_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.transactions = []
            for td in data.get("transactions", []):
                ops = [
                    FileOperation(
                        operation_type=OperationType(od["operation_type"]),
                        source=Path(od["source"]),
                        destination=Path(od["destination"]) if od.get("destination") else None,
                        timestamp=od.get("timestamp", 0.0),
                        metadata=od.get("metadata", {}),
                    )
                    for od in td.get("operations", [])
                ]
                self.transactions.append(
                    UndoTransaction(
                        id=td["id"],
                        timestamp=td["timestamp"],
                        description=td["description"],
                        operations=ops,
                        completed=td.get("completed", False),
                        metadata=td.get("metadata", {}),
                    )
                )
        except Exception as e:
            logger.error(f"Error loading undo history: {e}")
            self.transactions = []

    def _save(self):
        try:
            if len(self.transactions) > self.max_transactions:
                self.transactions = self.transactions[-self.max_transactions :]
            data = {
                "version": "2.0",
                "timestamp": time.time(),
                "transactions": [
                    {
                        "id": t.id,
                        "timestamp": t.timestamp,
                        "description": t.description,
                        "completed": t.completed,
                        "metadata": t.metadata,
                        "operations": [
                            {
                                "operation_type": o.operation_type.value,
                                "source": str(o.source),
                                "destination": str(o.destination) if o.destination else None,
                                "timestamp": o.timestamp,
                                "metadata": o.metadata,
                            }
                            for o in t.operations
                        ],
                    }
                    for t in self.transactions
                ],
            }
            self.undo_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.undo_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving undo history: {e}")
