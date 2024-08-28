import os
import sys

import toml


class Hub:
    """
    The Hub class is the central coordinator of the application. It manages the
    initialization and lifecycle of channels and reactors. All its methods run
    asynchronously.

    Attributes:
    - config (dict): Config settings loaded from a TOML file
    - channels (list): A list of registered channels
    - reactors (list): A list of registered reactors.

    Methods:
    - __init__(self, config_file: str) -> None:
        Initializes the Hub instance with the specified config file
    - load_config(self, path: str) -> dict:
        Loads the config settings from the specified TOML file
    -  config_path(self) -> str:
        Returns the path to the default configuration file
    - get_class_by_name(self, class_name: str) -> type:
        Retrieves a class by its name from the global scope
    - initialize_channels(self) -> None:
        Initialize the channels based on the config settings
    - initialize_reactors -> None:
        Initialize the reactors based on the config settings
    - start(self) -> None:
        Starts the Hub by initializing channels and reactors and putting
        channels in listening mode
    - event_handler(self, event: Any) -> None:
        Handles incoming events by passing them to the appropriate reactors for
        processing
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
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "config.toml")

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

    def start(self) -> None:
        """
        Kicks off the initialization of the channels and reactors

        Iterates over all the channels registered with the hub and puts them in
        listening mode.
        """

        self.initialize_channels()
        self.initialize_reactors()

        for channel in self.channels:
            channel.start_listening()

    def event_handler(self, event: str) -> None:
        """
        It receives events and iterates through the list of reactors. For each
        reactor, it checks whether the reactor is interested in the event, and
        if so, it calls the reactor's handle_event method to process the event.
        """
        if event == "q":
            sys.exit()

        for reactor in self.reactors:
            if reactor.check_event(event):
                reactor.handle_event(event)
