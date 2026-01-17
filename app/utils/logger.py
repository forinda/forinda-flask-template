import logging
import os
from logging.handlers import RotatingFileHandler


class Logger:
    """Reusable logger class for the Flask application."""

    _loggers = {}

    @classmethod
    def get_logger(cls, name: str, log_level: int | None = None) -> logging.Logger:
        """
        Get or create a logger with the specified name.

        Args:
            name: Name of the logger (typically __name__ of the module)
            log_level: Logging level (default: INFO)

        Returns:
            Configured logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)

        # Prevent adding handlers multiple times
        if logger.handlers:
            cls._loggers[name] = logger
            return logger

        log_level = log_level or logging.INFO
        logger.setLevel(log_level)

        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File handler for all logs
        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10,
        )
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s %(levelname)s [%(name)s] [%(pathname)s:%(lineno)d] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Error file handler
        error_handler = RotatingFileHandler(
            'logs/error.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10,
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)

        cls._loggers[name] = logger
        return logger

    @classmethod
    def set_level(cls, name: str, level: int):
        """Set logging level for a specific logger."""
        if name in cls._loggers:
            cls._loggers[name].setLevel(level)

    @classmethod
    def set_all_levels(cls, level: int):
        """Set logging level for all loggers."""
        for logger in cls._loggers.values():
            logger.setLevel(level)


# Convenience function for quick logger creation
def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Usage:
        from app.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info('This is an info message')
    """
    return Logger.get_logger(name)
