import logging
import sys
from config import LOGGING_CONFIG

def setup_logger(name='DiscordBot'):
    """Setup and configure logger for the bot"""
    
    # Create logger
    logger = logging.getLogger(name)
    
    # Set logging level
    level = getattr(logging, LOGGING_CONFIG['level'].upper(), logging.INFO)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(
        fmt=LOGGING_CONFIG['format'],
        datefmt=LOGGING_CONFIG['date_format']
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    
    # Disable discord.py debug logging unless explicitly enabled
    if level != logging.DEBUG:
        logging.getLogger('discord').setLevel(logging.WARNING)
        logging.getLogger('discord.http').setLevel(logging.WARNING)
    
    return logger

# Create default logger instance
default_logger = setup_logger()
