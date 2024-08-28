import os
import sys
import asyncio
from igor.response import Response
from igor.event import Event

import toml


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
            await channel.start_listening()

    def get_class_by_name(self, type, class_name: str):
        module = __import__(f"{type}.{class_name.lower()}", fromlist=[class_name])
        try:
            return getattr(module, class_name)
        except AttributeError as e:
            print(f"Error getting class by name: {e}")

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
            print(f"initialized following channels: {self.channels}")

    def initialize_reactors(self) -> None:
        if "reactors" in self.config:
            for _, reactor_config in self.config["reactors"].items():
                ReactorClass = self.get_class_by_name(
                    "reactors", reactor_config["class"]
                )
                if ReactorClass:
                    reactor = ReactorClass(self)
                    self.reactors.append(reactor)
            print(f"initialized following reactors: {self.reactors}")


    async def process_event(self, event: Event):
        """
        Processes events sent from channels. It checks if any reactors should
        react to the event, and if so, kicks off sending the event and response
        to the appropriate channel
        """
        for reactor in self.reactors:
            if reactor.can_handle(event):
                response = await reactor.handle(event)
                if response:
                    await self.send_response(event, response)
                    return  # Stop after first matching reactor

    async def send_response(self, event: Event, response: Response):
        """
        Sends incoming events and their responses to the appropriate channel
        """
        channel_name = event.channel
        if channel_name in self.channels:
            channel = self.channels[channel_name]
            await channel.send_response(event, response.content)
        else:
            print(f"Channel {channel_name} not found")

