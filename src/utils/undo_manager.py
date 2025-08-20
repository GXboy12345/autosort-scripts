"""
Undo Manager for AutoSort

Provides undo functionality for file operations with persistent storage
and transaction support.
"""

import json
import logging
import shutil
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import time

from core.file_organizer import FileOperation, OperationType

logger = logging.getLogger(__name__)


@dataclass
class UndoTransaction:
    """Undo transaction record."""
    id: str
    timestamp: float
    description: str
    operations: List[FileOperation]
    completed: bool = False
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class UndoManager:
    """
    Manages undo functionality for file operations.
    
    This class provides the ability to undo file organization operations,
    with persistent storage and transaction support.
    """
    
    def __init__(self, undo_file: Optional[Path] = None):
        """
        Initialize the undo manager.
        
        Args:
            undo_file: Path to undo history file
        """
        self.undo_file = undo_file or Path("autosort_undo.json")
        self.transactions: List[UndoTransaction] = []
        self.max_transactions = 50  # Keep last 50 transactions
        self._load_transactions()
    
    def start_transaction(self, description: str) -> str:
        """
        Start a new undo transaction.
        
        Args:
            description: Description of the transaction
            
        Returns:
            Transaction ID
        """
        import uuid
        
        transaction_id = str(uuid.uuid4())
        transaction = UndoTransaction(
            id=transaction_id,
            timestamp=time.time(),
            description=description,
            operations=[]
        )
        
        self.transactions.append(transaction)
        logger.debug(f"Started transaction: {transaction_id} - {description}")
        
        return transaction_id
    
    def add_operation(self, transaction_id: str, operation: FileOperation) -> bool:
        """
        Add an operation to a transaction.
        
        Args:
            transaction_id: Transaction ID
            operation: File operation to add
            
        Returns:
            True if added successfully, False otherwise
        """
        transaction = self._find_transaction(transaction_id)
        if not transaction:
            logger.error(f"Transaction not found: {transaction_id}")
            return False
        
        transaction.operations.append(operation)
        logger.debug(f"Added operation to transaction {transaction_id}: {operation.operation_type}")
        return True
    
    def commit_transaction(self, transaction_id: str) -> bool:
        """
        Commit a transaction.
        
        Args:
            transaction_id: Transaction ID to commit
            
        Returns:
            True if committed successfully, False otherwise
        """
        transaction = self._find_transaction(transaction_id)
        if not transaction:
            logger.error(f"Transaction not found: {transaction_id}")
            return False
        
        transaction.completed = True
        self._save_transactions()
        logger.info(f"Committed transaction: {transaction_id}")
        return True
    
    def rollback_transaction(self, transaction_id: str) -> bool:
        """
        Rollback a transaction (undo all operations).
        
        Args:
            transaction_id: Transaction ID to rollback
            
        Returns:
            True if rollback successful, False otherwise
        """
        transaction = self._find_transaction(transaction_id)
        if not transaction:
            logger.error(f"Transaction not found: {transaction_id}")
            return False
        
        if not transaction.completed:
            logger.error(f"Cannot rollback incomplete transaction: {transaction_id}")
            return False
        
        logger.info(f"Rolling back transaction: {transaction_id}")
        
        # Undo operations in reverse order
        success_count = 0
        error_count = 0
        
        for operation in reversed(transaction.operations):
            if self._undo_operation(operation):
                success_count += 1
            else:
                error_count += 1
        
        # Remove transaction from history
        self.transactions.remove(transaction)
        self._save_transactions()
        
        logger.info(f"Rollback completed: {success_count} successful, {error_count} errors")
        return error_count == 0
    
    def undo_last_transaction(self) -> bool:
        """
        Undo the last completed transaction.
        
        Returns:
            True if undo successful, False otherwise
        """
        # Find the last completed transaction
        completed_transactions = [t for t in self.transactions if t.completed]
        
        if not completed_transactions:
            logger.info("No completed transactions to undo")
            return False
        
        last_transaction = completed_transactions[-1]
        return self.rollback_transaction(last_transaction.id)
    
    def get_transaction_history(self) -> List[Dict[str, Any]]:
        """
        Get transaction history.
        
        Returns:
            List of transaction information dictionaries
        """
        history = []
        
        for transaction in self.transactions:
            history.append({
                'id': transaction.id,
                'timestamp': transaction.timestamp,
                'description': transaction.description,
                'operation_count': len(transaction.operations),
                'completed': transaction.completed,
                'date': datetime.fromtimestamp(transaction.timestamp).isoformat()
            })
        
        return history
    
    def clear_history(self) -> bool:
        """
        Clear all transaction history.
        
        Returns:
            True if cleared successfully, False otherwise
        """
        try:
            self.transactions.clear()
            self._save_transactions()
            logger.info("Transaction history cleared")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing transaction history: {e}")
            return False
    
    def get_undo_info(self) -> Dict[str, Any]:
        """
        Get information about undo capabilities.
        
        Returns:
            Dictionary with undo information
        """
        completed_transactions = [t for t in self.transactions if t.completed]
        
        return {
            'can_undo': len(completed_transactions) > 0,
            'transaction_count': len(self.transactions),
            'completed_count': len(completed_transactions),
            'last_transaction': completed_transactions[-1].description if completed_transactions else None
        }
    
    def _find_transaction(self, transaction_id: str) -> Optional[UndoTransaction]:
        """
        Find a transaction by ID.
        
        Args:
            transaction_id: Transaction ID to find
            
        Returns:
            Transaction object or None if not found
        """
        for transaction in self.transactions:
            if transaction.id == transaction_id:
                return transaction
        return None
    
    def _undo_operation(self, operation: FileOperation) -> bool:
        """
        Undo a single file operation.
        
        Args:
            operation: File operation to undo
            
        Returns:
            True if undone successfully, False otherwise
        """
        try:
            if operation.operation_type == OperationType.MOVE:
                return self._undo_move_operation(operation)
            elif operation.operation_type == OperationType.CREATE_DIR:
                return self._undo_create_dir_operation(operation)
            elif operation.operation_type == OperationType.DELETE:
                return self._undo_delete_operation(operation)
            else:
                logger.warning(f"Unknown operation type: {operation.operation_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error undoing operation: {e}")
            return False
    
    def _undo_move_operation(self, operation: FileOperation) -> bool:
        """
        Undo a move operation.
        
        Args:
            operation: Move operation to undo
            
        Returns:
            True if undone successfully, False otherwise
        """
        try:
            # Check if destination still exists
            if not operation.destination or not operation.destination.exists():
                logger.warning(f"Destination file no longer exists: {operation.destination}")
                return False
            
            # Check if source location is available
            if operation.source.exists():
                # Check if it's the same file (same size and modification time)
                dest_stat = operation.destination.stat()
                source_stat = operation.source.stat()
                
                if (dest_stat.st_size == source_stat.st_size and 
                    abs(dest_stat.st_mtime - source_stat.st_mtime) < 1):
                    # Same file, just remove the destination
                    operation.destination.unlink()
                    logger.info(f"Removed duplicate file: {operation.destination}")
                    return True
                else:
                    # Different file, generate unique name
                    unique_source = self._get_unique_source_path(operation.source)
                    shutil.move(str(operation.destination), str(unique_source))
                    logger.info(f"Undid move with unique name: {operation.destination} → {unique_source}")
                    return True
            
            # Source doesn't exist, safe to move back
            shutil.move(str(operation.destination), str(operation.source))
            logger.info(f"Undid move: {operation.destination} → {operation.source}")
            return True
            
        except Exception as e:
            logger.error(f"Error undoing move operation: {e}")
            return False
    
    def _get_unique_source_path(self, original_path: Path) -> Path:
        """
        Generate a unique path for the source file when undoing.
        
        Args:
            original_path: Original source path
            
        Returns:
            Unique source path
        """
        if not original_path.exists():
            return original_path
        
        stem = original_path.stem
        suffix = original_path.suffix
        parent = original_path.parent
        
        counter = 1
        while counter <= 1000:
            candidate = parent / f"{stem}_restored_{counter}{suffix}"
            if not candidate.exists():
                return candidate
            counter += 1
        
        # Fallback with timestamp
        import time
        timestamp = int(time.time())
        return parent / f"{stem}_restored_{timestamp}{suffix}"
    
    def _undo_create_dir_operation(self, operation: FileOperation) -> bool:
        """
        Undo a create directory operation.
        
        Args:
            operation: Create directory operation to undo
            
        Returns:
            True if undone successfully, False otherwise
        """
        try:
            # Check if directory exists and is empty
            if not operation.source.exists():
                logger.warning(f"Directory no longer exists: {operation.source}")
                return False
            
            if not operation.source.is_dir():
                logger.warning(f"Path is not a directory: {operation.source}")
                return False
            
            # Check if directory is empty
            if any(operation.source.iterdir()):
                logger.warning(f"Directory is not empty: {operation.source}")
                return False
            
            # Remove directory
            operation.source.rmdir()
            logger.info(f"Undid create directory: {operation.source}")
            return True
            
        except Exception as e:
            logger.error(f"Error undoing create directory operation: {e}")
            return False
    
    def _undo_delete_operation(self, operation: FileOperation) -> bool:
        """
        Undo a delete operation (if we have backup information).
        
        Args:
            operation: Delete operation to undo
            
        Returns:
            True if undone successfully, False otherwise
        """
        # This would require backup information that we don't currently store
        logger.warning("Delete operations cannot be undone without backup information")
        return False
    
    def _load_transactions(self) -> None:
        """Load transactions from file."""
        try:
            if self.undo_file.exists():
                with open(self.undo_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.transactions = []
                for transaction_data in data.get('transactions', []):
                    # Convert operation data back to FileOperation objects
                    operations = []
                    for op_data in transaction_data.get('operations', []):
                        operation = FileOperation(
                            operation_type=OperationType(op_data['operation_type']),
                            source=Path(op_data['source']),
                            destination=Path(op_data['destination']) if op_data.get('destination') else None,
                            timestamp=op_data.get('timestamp', 0.0),
                            metadata=op_data.get('metadata', {})
                        )
                        operations.append(operation)
                    
                    transaction = UndoTransaction(
                        id=transaction_data['id'],
                        timestamp=transaction_data['timestamp'],
                        description=transaction_data['description'],
                        operations=operations,
                        completed=transaction_data.get('completed', False),
                        metadata=transaction_data.get('metadata', {})
                    )
                    self.transactions.append(transaction)
                
                logger.debug(f"Loaded {len(self.transactions)} transactions from {self.undo_file}")
                
        except Exception as e:
            logger.error(f"Error loading transactions: {e}")
            self.transactions = []
    
    def _save_transactions(self) -> None:
        """Save transactions to file."""
        try:
            # Limit number of transactions
            if len(self.transactions) > self.max_transactions:
                self.transactions = self.transactions[-self.max_transactions:]
            
            # Convert to serializable format
            data = {
                'version': '1.0',
                'timestamp': time.time(),
                'transactions': []
            }
            
            for transaction in self.transactions:
                transaction_data = {
                    'id': transaction.id,
                    'timestamp': transaction.timestamp,
                    'description': transaction.description,
                    'completed': transaction.completed,
                    'metadata': transaction.metadata,
                    'operations': []
                }
                
                for operation in transaction.operations:
                    operation_data = {
                        'operation_type': operation.operation_type.value,
                        'source': str(operation.source),
                        'timestamp': operation.timestamp,
                        'metadata': operation.metadata
                    }
                    
                    if operation.destination:
                        operation_data['destination'] = str(operation.destination)
                    
                    transaction_data['operations'].append(operation_data)
                
                data['transactions'].append(transaction_data)
            
            # Save to file
            with open(self.undo_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved {len(self.transactions)} transactions to {self.undo_file}")
            
        except Exception as e:
            logger.error(f"Error saving transactions: {e}")
