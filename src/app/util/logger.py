import os
from aiologger import Logger
from aiologger.handlers.files import AsyncFileHandler
from aiologger.formatters.base import Formatter

def setup_logging():
    log_dir = "app/components/logs"
    log_format = "[%(asctime)s] [%(levelname)s]: %(message)s"
    formatter = Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    logger = Logger(name="app_logger")

    file_handler = AsyncFileHandler(
        os.path.join(log_dir, "logs.log"), 
        encoding="utf-8"
    )
    file_handler.formatter = formatter
    logger.add_handler(file_handler)

    return logger

logger = setup_logging()