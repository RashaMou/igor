import os
import asyncio
from igor.response import Response
from igor.event import Event
from igor.logging_config import get_logger

import toml

logger = get_logger(__name__)


class Hub:
    """
    The Hub class is the central coordinator of the application. It manages the
    initialization and lifecycle of channels and reactors. All its methods run
    asynchronously.
    """

    def __init__(self, config_file: str) -> None:
        self.config = self.load_config(config_file)
        self.channels = {}
        self.reactors = []
        self.shutdown_event = asyncio.Event()
        self.tasks = []

    def load_config(self, path: str) -> dict:
        with open(path, "r", encoding="utf-8") as config_file:
            config = toml.load(config_file)
        return config

    def config_path(self) -> str:
        """
        Loads the config settings from the specified TOML file
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "config.toml")

    async def start(self) -> None:
        """
        Kicks off the initialization of the channels and reactors

        Iterates over all the channels registered with the hub and puts them in
        listening mode.
        """
        self.initialize_channels()
        self.initialize_reactors()

        for channel in self.channels.values():
            self.tasks.append(asyncio.create_task(channel.start_listening()))

        await self.shutdown_event.wait()

        await asyncio.gather(*self.tasks, return_exceptions=True)

    def signal_shutdown(self):
        """
        Signal the shutdown event to stop all channels.
        """
        self.shutdown_event.set()

        for task in self.tasks:
            task.cancel()

    def get_class_by_name(self, type, class_name: str):
        module = __import__(f"{type}.{class_name.lower()}", fromlist=[class_name])
        try:
            return getattr(module, class_name)
        except AttributeError as e:
            logger.error(f"Error getting class by name: {e}")

    def initialize_channels(self) -> None:
        if "channels" in self.config:
            for channel_name, channel_config in self.config["channels"].items():
                ChannelClass = self.get_class_by_name(
                    "channels", channel_config["class"]
                )
                if ChannelClass:
                    del channel_config["class"]
                    channel = ChannelClass(self, **channel_config)
                    self.channels[channel_name] = channel
                logger.info(f"initialized {channel_name.capitalize()} channel")

    def initialize_reactors(self) -> None:
        if "reactors" in self.config:
            for _, reactor_config in self.config["reactors"].items():
                ReactorClass = self.get_class_by_name(
                    "reactors", reactor_config["class"]
                )
                if ReactorClass:
                    reactor = ReactorClass(self)
                    self.reactors.append(reactor)
                logger.info(f"initialized {reactor_config["class"]} reactor")

    async def process_event(self, event: Event):
        """
        Processes events sent from channels. It checks if any reactors should
        react to the event, and if so, kicks off sending the event and response
        to the appropriate channel
        """
        logger.debug(f"Processing event: {event}")
        for reactor in self.reactors:
            if reactor.can_handle(event):
                logger.info(f"Reactor {reactor.__class__.__name__} handling event")
                response = reactor.handle(event)
                if response:
                    await self.send_channel_response(event, response)
                    return  # Stop after first matching reactor
        logger.warning(f"No reactor found to handle event: {event}")

    async def send_channel_response(self, event: Event, response: Response):
        """
        Sends incoming events and their responses to the appropriate channel
        """
        channel_name = event.channel
        if channel_name in self.channels:
            channel = self.channels[channel_name]
            await channel.send_response(event, response)
        else:
            logger.warning(f"Channel {channel_name} not found")
