import logging
import sys
from pythonjsonlogger import jsonlogger
from datetime import datetime

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(f'game_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

    # Create formatters
    json_formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Set formatters
    console_handler.setFormatter(json_formatter)
    file_handler.setFormatter(json_formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# Create a logger instance
logger = setup_logging() 