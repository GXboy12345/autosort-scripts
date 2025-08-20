"""
Logging utility for AutoSort

Provides centralized logging configuration with improved formatting,
file rotation, and different log levels for different components.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
import os


def setup_logging(
    log_file: Optional[str] = None,
    log_level: str = "INFO",
    max_bytes: int = 1024 * 1024,  # 1MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up logging configuration for the application.
    
    Args:
        log_file: Path to log file (default: autosort.log)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("autosort")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log_file specified)
    if log_file:
        log_path = Path(log_file)
        
        # Create log directory if it doesn't exist
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"autosort.{name}")


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_colored_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Set up colored logging for console output.
    
    Args:
        log_level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("autosort")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Use colored formatter
    colored_formatter = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(colored_formatter)
    logger.addHandler(console_handler)
    
    # Prevent propagation
    logger.propagate = False
    
    return logger


def log_system_info(logger: logging.Logger) -> None:
    """
    Log system information for debugging.
    
    Args:
        logger: Logger instance
    """
    import platform
    
    logger.info("=== System Information ===")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Python Version: {platform.python_version()}")
    logger.info(f"Architecture: {platform.architecture()}")
    logger.info(f"Processor: {platform.processor()}")
    logger.info(f"Working Directory: {os.getcwd()}")
    logger.info("==========================")


def log_memory_usage(logger: logging.Logger) -> None:
    """
    Log memory usage information.
    
    Args:
        logger: Logger instance
    """
    try:
        import psutil
        
        process = psutil.Process()
        memory_info = process.memory_info()
        
        logger.debug(f"Memory Usage: {memory_info.rss / 1024 / 1024:.2f} MB")
        logger.debug(f"Virtual Memory: {memory_info.vms / 1024 / 1024:.2f} MB")
        
    except ImportError:
        logger.debug("psutil not available for memory monitoring")


class ProgressLogger:
    """
    Logger wrapper for progress tracking.
    
    Provides methods for logging progress updates with consistent formatting.
    """
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize progress logger.
        
        Args:
            logger: Base logger instance
        """
        self.logger = logger
        self.start_time = None
    
    def start_operation(self, operation_name: str) -> None:
        """
        Log the start of an operation.
        
        Args:
            operation_name: Name of the operation
        """
        import time
        self.start_time = time.time()
        self.logger.info(f"Starting {operation_name}")
    
    def log_progress(self, current: int, total: int, message: str = "") -> None:
        """
        Log progress update.
        
        Args:
            current: Current progress value
            total: Total value
            message: Additional message
        """
        percentage = (current / total) * 100 if total > 0 else 0
        progress_msg = f"Progress: {current}/{total} ({percentage:.1f}%)"
        
        if message:
            progress_msg += f" - {message}"
        
        self.logger.info(progress_msg)
    
    def end_operation(self, operation_name: str, success: bool = True) -> None:
        """
        Log the end of an operation.
        
        Args:
            operation_name: Name of the operation
            success: Whether the operation was successful
        """
        import time
        
        if self.start_time:
            duration = time.time() - self.start_time
            status = "completed" if success else "failed"
            self.logger.info(f"{operation_name} {status} in {duration:.2f} seconds")
        else:
            status = "completed" if success else "failed"
            self.logger.info(f"{operation_name} {status}")
        
        self.start_time = None
