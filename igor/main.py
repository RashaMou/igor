import asyncio
import os
from igor.hub import Hub


async def main():
    config_path = os.path.join(os.path.dirname(__file__), "config.toml")

    hub = Hub(config_path)

    try:
        await hub.start()
    except Exception as e:
        print(f"Error starting the hub: {e}")


if __name__ == "__main__":
    asyncio.run(main())
