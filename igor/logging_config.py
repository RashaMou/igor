import logging
import logging.config
import os
from datetime import datetime

# determine environment
ENV = os.environ.get("IGOR_ENV", "development")

# base configurations
BASE_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {},
    "loggers": {
        "": {  # root logger
            "handlers": ["default"],
            "level": os.environ.get("LOG_LEVEL", "INFO"),
            "propagate": True,
        },
    },
}

# environment-specific configurations
if ENV == "development":
    BASE_CONFIG["handlers"]["default"] = {
        "level": "DEBUG",
        "class": "logging.StreamHandler",
        "formatter": "standard",
    }
elif ENV == "production":
    BASE_CONFIG["handlers"]["default"] = {
        "level": "INFO",
        "class": "logging.handlers.RotatingFileHandler",
        "filename": f'/var/log/igor/igor_{datetime.now().strftime("%Y%m%d")}.log',
        "maxBytes": 5242880,  # 5MB
        "backupCount": 3,
        "formatter": "standard",
    }
# add handlers for AWS cloudwatch and error emails


def setup_logging():
    logging.config.dictConfig(BASE_CONFIG)
    logger = logging.getLogger(__name__)
    logger.info(f"Logger set up in {ENV} environment")


def get_logger(name):
    return logging.getLogger(name)
