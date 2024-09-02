from abc import ABC, abstractmethod
from igor.event import Event
from igor.response import Response
from igor.hub import Hub


class Channel(ABC):
    """
    Abstract base class for all channels in Igor.

    A channel represents a specific communication platform (e.g., Telegram, Discord, Console).
    It's responsible for receiving input from the platform, converting it to Igor events,
    and sending responses back to the platform.

    Attributes:
        hub (Hub): The central hub that manages all channels and reactors.
    """

    def __init__(self, hub: Hub):
        """
        Initialize a new Channel instance.

        Args:
            hub (Hub): The central hub that manages all channels and reactors.
        """
        self.hub = hub

    @abstractmethod
    async def start_listening(self) -> None:
        """
        Start listening for incoming messages or events from the platform.

        This method should implement the necessary logic to connect to the platform
        and set up any required event listeners or polling mechanisms.

        This method is called by the hub when Igor starts up.
        """
        pass

    @abstractmethod
    async def stop_listening(self) -> None:
        """
        Stop listening for incoming messages or events from the platform.

        This method should implement the necessary logic to disconnect from the platform
        and clean up any resources.

        This method is called by the hub when Igor is shutting down.
        """
        pass

    @abstractmethod
    def channel_event_to_igor_event(self, channel_event: Any) -> Event:
        """
        Convert a channel-specific event to an Igor Event.

        This method should be implemented to convert the channel's native message format
        into an Igor Event that can be processed by reactors.

        Args:
            message (ChannelMessage): The channel-specific message to convert.

        Returns:
            Event: The Igor Event created from the message.
        """
        pass

    @abstractmethod
    async def send_response(self, event: Event, response: Response) -> None:
        """
        Send a response back to the platform.

        This method should implement the necessary logic to send the response
        back to the user through the specific platform this channel represents.

        Args:
            event (Event): The original event that triggered this response.
            response (Response): The response to be sent back to the user.
        """
        pass
