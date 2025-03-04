# Logger setup utility

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

def setup_logging(log_level: str = "INFO", log_to_file: bool = True, log_dir: Optional[str] = None) -> logging.Logger:
    """Set up logging configuration for the AI Co-Scientist system.
    
    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to a file in addition to console
        log_dir: Optional directory for log files. If None, logs are stored in 'logs'
            directory in the project root
    
    Returns:
        The configured logger instance
    """
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    # Clear any existing handlers
    for handler in logger.handlers[:]:  
        logger.removeHandler(handler)
    
    # Create console handler with formatter
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add console handler to logger
    logger.addHandler(console_handler)
    
    # Add file handler if requested
    if log_to_file:
        if log_dir is None:
            # Get the project root directory (assuming this file is in src/utils)
            project_root = Path(__file__).parents[2]  # Go up two levels from this file
            log_dir = project_root / "logs"
        else:
            log_dir = Path(log_dir)
        
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Create a timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"ai_coscientist_{timestamp}.log"
        
        # Create file handler with formatter
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        
        # Add file handler to logger
        logger.addHandler(file_handler)
        logger.info(f"Logging to file: {log_file}")
    
    logger.info(f"Logging initialized at level {log_level}")
    return logger
