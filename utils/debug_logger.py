"""
Global debug logging utility.
"""
import logging
import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

@dataclass
class LogConfig:
    """Configuration for debug logging."""
    enabled: bool = True
    level: int = logging.DEBUG
    show_timestamp: bool = True
    show_level: bool = True
    show_file: bool = True
    show_line: bool = True
    show_function: bool = True
    log_to_file: bool = True
    log_file: str = "debug.log"
    log_dir: str = "logs"
    max_file_size: int = 5 * 1024 * 1024  # 5MB
    backup_count: int = 3

class DebugLogger:
    """Global debug logging utility."""
    
    _instance: Optional['DebugLogger'] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._config = LogConfig()
            self._logger = logging.getLogger("debug")
            self._setup_logger()
            
    def _setup_logger(self) -> None:
        """Set up the logger with the current configuration."""
        # Clear any existing handlers
        self._logger.handlers.clear()
        
        # Set log level
        self._logger.setLevel(self._config.level)
        
        # Create formatter
        format_parts = []
        if self._config.show_timestamp:
            format_parts.append("%(asctime)s")
        if self._config.show_level:
            format_parts.append("%(levelname)s")
        if self._config.show_file:
            format_parts.append("%(filename)s")
        if self._config.show_line:
            format_parts.append(":%(lineno)d")
        if self._config.show_function:
            format_parts.append(":%(funcName)s")
        format_parts.append(" - %(message)s")
        
        formatter = logging.Formatter(" ".join(format_parts))
        
        # Add console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        
        # Add file handler if enabled
        if self._config.log_to_file:
            # Create log directory if it doesn't exist
            os.makedirs(self._config.log_dir, exist_ok=True)
            
            # Set up rotating file handler
            from logging.handlers import RotatingFileHandler
            log_path = os.path.join(self._config.log_dir, self._config.log_file)
            file_handler = RotatingFileHandler(
                log_path,
                maxBytes=self._config.max_file_size,
                backupCount=self._config.backup_count
            )
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
            
    def configure(self, **kwargs) -> None:
        """Configure the logger."""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        self._setup_logger()
        
    def enable(self) -> None:
        """Enable logging."""
        self._config.enabled = True
        self._logger.setLevel(self._config.level)
        
    def disable(self) -> None:
        """Disable logging."""
        self._config.enabled = False
        self._logger.setLevel(logging.CRITICAL)
        
    def set_level(self, level: int) -> None:
        """Set the logging level."""
        self._config.level = level
        self._logger.setLevel(level)
        
    def debug(self, message: str, **kwargs) -> None:
        """Log a debug message."""
        if self._config.enabled:
            self._logger.debug(message, **kwargs)
            
    def info(self, message: str, **kwargs) -> None:
        """Log an info message."""
        if self._config.enabled:
            self._logger.info(message, **kwargs)
            
    def warning(self, message: str, **kwargs) -> None:
        """Log a warning message."""
        if self._config.enabled:
            self._logger.warning(message, **kwargs)
            
    def error(self, message: str, **kwargs) -> None:
        """Log an error message."""
        if self._config.enabled:
            self._logger.error(message, **kwargs)
            
    def critical(self, message: str, **kwargs) -> None:
        """Log a critical message."""
        if self._config.enabled:
            self._logger.critical(message, **kwargs)
            
    def exception(self, message: str, **kwargs) -> None:
        """Log an exception message."""
        if self._config.enabled:
            self._logger.exception(message, **kwargs)
            
    def get_logger(self) -> logging.Logger:
        """Get the underlying logger instance."""
        return self._logger
        
    def get_config(self) -> LogConfig:
        """Get the current configuration."""
        return self._config

# Create global instance
logger = DebugLogger()

# Example usage:
if __name__ == "__main__":
    # Configure logger
    logger.configure(
        enabled=True,
        level=logging.DEBUG,
        show_timestamp=True,
        show_level=True,
        show_file=True,
        show_line=True,
        show_function=True,
        log_to_file=True
    )
    
    # Log some messages
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    try:
        1/0
    except Exception as e:
        logger.exception("An error occurred") 