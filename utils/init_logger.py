"""
Initialize the global debug logger.
"""
import os
import logging
from datetime import datetime
from .debug_logger import logger

def init_logger(
    log_level: int = logging.DEBUG,
    log_to_file: bool = True,
    log_dir: str = "logs",
    log_file: str = None,
    show_timestamp: bool = True,
    show_level: bool = True,
    show_file: bool = True,
    show_line: bool = True,
    show_function: bool = True
) -> None:
    """
    Initialize the global debug logger.
    
    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to a file
        log_dir: Directory to store log files
        log_file: Name of the log file (defaults to timestamp-based name)
        show_timestamp: Whether to show timestamps in logs
        show_level: Whether to show log levels in logs
        show_file: Whether to show file names in logs
        show_line: Whether to show line numbers in logs
        show_function: Whether to show function names in logs
    """
    # Create log directory if it doesn't exist
    if log_to_file:
        os.makedirs(log_dir, exist_ok=True)
        
    # Generate log file name if not provided
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"game_{timestamp}.log"
        
    # Configure logger
    logger.configure(
        enabled=True,
        level=log_level,
        show_timestamp=show_timestamp,
        show_level=show_level,
        show_file=show_file,
        show_line=show_line,
        show_function=show_function,
        log_to_file=log_to_file,
        log_file=log_file,
        log_dir=log_dir
    )
    
    # Log initialization
    logger.info("Debug logger initialized")
    logger.debug(f"Log level: {logging.getLevelName(log_level)}")
    logger.debug(f"Log file: {os.path.join(log_dir, log_file)}")
    
def disable_logger() -> None:
    """Disable the global debug logger."""
    logger.disable()
    logger.info("Debug logger disabled")
    
def enable_logger() -> None:
    """Enable the global debug logger."""
    logger.enable()
    logger.info("Debug logger enabled")
    
def set_log_level(level: int) -> None:
    """Set the logging level."""
    logger.set_level(level)
    logger.info(f"Log level set to {logging.getLevelName(level)}")
    
def get_logger():
    """Get the global logger instance."""
    return logger 