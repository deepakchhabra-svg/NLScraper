"""
Utility functions for the scraper
"""
import os
import json
import logging
import re
from typing import Dict, Optional
import coloredlogs

import config


def setup_logging() -> logging.Logger:
    """
    Setup logging configuration
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger('NLScraper')
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Create logs directory if it doesn't exist
    os.makedirs(config.LOGS_DIR, exist_ok=True)
    
    # File handler
    file_handler = logging.FileHandler(config.LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler with colors
    coloredlogs.install(
        level=config.LOG_LEVEL,
        logger=logger,
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    return logger


def save_checkpoint(data: Dict, checkpoint_file: str) -> bool:
    """
    Save checkpoint data to file
    
    Args:
        data: Dictionary containing checkpoint data
        checkpoint_file: Path to checkpoint file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(checkpoint_file), exist_ok=True)
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logging.error(f"Failed to save checkpoint: {e}")
        return False


def load_checkpoint(checkpoint_file: str) -> Optional[Dict]:
    """
    Load checkpoint data from file
    
    Args:
        checkpoint_file: Path to checkpoint file
        
    Returns:
        Dictionary with checkpoint data or None if not found
    """
    try:
        if not os.path.exists(checkpoint_file):
            return None
        
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data
    except Exception as e:
        logging.error(f"Failed to load checkpoint: {e}")
        return None


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize a string to be used as a filename
    
    Args:
        filename: Original filename
        max_length: Maximum length of the filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    
    # Truncate to max length
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length - len(ext)] + ext
    
    return filename


def format_price(price_string: str) -> str:
    """
    Format price string to standard format
    
    Args:
        price_string: Raw price string
        
    Returns:
        Formatted price string
    """
    if not price_string or price_string == 'N/A':
        return price_string
    
    # Remove currency symbols, spaces, and commas
    price_cleaned = price_string.replace('$', '').replace(',', '').replace(' ', '').strip()
    
    # Extract numeric value with single decimal point using regex
    price_match = re.search(r'\d+\.?\d*', price_cleaned)
    
    if not price_match:
        return price_string
    
    try:
        # Convert to float and format
        price_float = float(price_match.group())
        return f"${price_float:.2f}"
    except (ValueError, AttributeError):
        return price_string


def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Raw text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ''
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters that might cause issues in CSV
    text = text.replace('\n', ' ').replace('\r', ' ')
    
    return text.strip()
