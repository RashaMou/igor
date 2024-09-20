import asyncio
import os
from igor.hub import Hub
from igor.logging_config import setup_logging, get_logger


async def main():
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Igor starting up")

    config_path = os.path.join(os.path.dirname(__file__), "config.toml")

    hub = Hub(config_path)

    try:
        logger.info("Initializing Hub")
        await hub.start()
    except Exception as e:
        logger.error(f"Error starting the hub: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
