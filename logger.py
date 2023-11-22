import logging
from logging.handlers import TimedRotatingFileHandler
import os

# Настройка логгера с ротацией по времени
handler = TimedRotatingFileHandler("logs/my_log.log", when="midnight", interval=1, backupCount=7)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

class Logger:
# Настройка логгера с ротацией по времени
    def __init__(self):
        log_dir = "logs\\"
        
        # Create the logs directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Настройка логгера с ротацией по времени
        self.handler = TimedRotatingFileHandler(os.path.join(log_dir, "my_log.log"), when="midnight", interval=1, backupCount=7)
        self.handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        # Ensure that you have no other handlers attached to the logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # Remove existing handlers if any
        for h in self.logger.handlers:
            self.logger.removeHandler(h)

        # Add the handler
        self.logger.addHandler(self.handler)
        
    def info(self, mes):
        print(f"Logger: {mes}")
        self.logger.info(mes)
        
    def error(self, mes):
        self.logger.error(mes)
        