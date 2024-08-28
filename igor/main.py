import asyncio
import os
from igor.hub import Hub

async def main():
    config_path = os.path.join(os.path.dirname(__file__), 'config.toml')
 
    hub = Hub(config_path)

    try:
        await hub.start()
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("Shutting down Igor...")

if __name__ == "__main__":
    asyncio.run(main())
