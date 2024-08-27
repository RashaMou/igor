import asyncio
import os

from igor.hub import Hub


async def main():
    # initialize the hub
    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "config.toml"
    )
    hub = Hub(config_path)

    hub.start()


if __name__ == "__main__":
    # initialize the loop
    asyncio.run(main())
