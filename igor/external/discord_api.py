import asyncio
import json
from igor.client import send_request
from igor.logging_config import get_logger


import websockets

from igor.utils import op

logger = get_logger(__name__)


class DiscordAPI:
    """
    This is the client. We should be able to use this client for any purpose. So
    write it as if I want to interact with my discord from the command line.


    we should be able to:
    - initiate the client class
    - send message
    - get guilds

    """

    def __init__(self, token):
        self.base_url = "https://discord.com/api/v10/"
        self.token = token
        self.version = "1.0.0"
        self.sequence_number = None
        self.heartbeat_interval = None
        self.session_id = None
        self.resume_gateway_url = None
        self.reconnect_codes = [4000, 4001, 4002, 4003, 4005, 4007, 4008, 4009, 7]
        self.event_queue = asyncio.Queue()
        self.headers = {
            "User-Agent": f"DiscordBot (https://example.com, {self.version})",
            "Authorization": self.token,
        }
        logger.debug(f"token is: {self.token}")
        logger.debug(f"DiscordAPI initialized with headers: {self.headers}")

    async def connect(self):
        """
        Opens websocket connection. Once connected, the client receives a Hello
        event that contains the heartbeat_interval. The heartbeat_interval is
        the length of time in ms that determines how often to send a heartbeat
        event in order to maintain the connection.
        """
        url = self.base_url + "/gateway"
        while True:
            try:
                data = await send_request("get", url, optional_headers=self.headers)
                if data is None:
                    return None
                wss_url = data["url"]

                async with websockets.connect(wss_url) as self.websocket:
                    hello_event = await self.websocket.recv()
                    hello_data = json.loads(hello_event)

                    self.heartbeat_interval = hello_data["d"]["heartbeat_interval"]
                    self.sequence_number = hello_data.get("s")

                    await self.identify()

                    # asyncio.gather is used to run these two methods concurrently. If
                    # either of these tasks fail, gather will also fail and the
                    # exception will propagate to the connect method.
                    await asyncio.gather(
                        self.heartbeat(),
                        self.receive(),
                    )

            except Exception as e:
                print(f"Connection error: {e}, reconnecting...")
                await asyncio.sleep(5)

    async def receive(self):
        while True:
            try:
                message = await self.websocket.recv()
                data = json.loads(message)
                opcode = data["op"]

                if opcode == op.HEARTBEAT:
                    self.heartbeat_interval = data["d"]["heartbeat_interval"]
                elif opcode == op.HEARTBEAT_ACK:
                    # TODO: if we don't get a heartbeat_ack then it probably means the
                    # connection is zombified and we should reconnect/resume
                    print(f"Heartbeat ACK: {data}\n")
                elif opcode == op.DISPATCH:
                    event_type = data.get("t")
                    if event_type == "READY":
                        self.resume_gateway_url = data["d"].get("resume_gateway_url")
                        self.session_id = data["d"].get("session_id")
                    if event_type == "MESSAGE_CREATE":
                        await self.event_queue.put(data)
                elif opcode == op.RECONNECT:
                    print("Received RECONNECT opcode, initiating reconnection...")
                    await self.reconnect()

                self.sequence_number = data.get("s") or self.sequence_number

            except Exception as e:
                print(f"Error in receive: {e}")

    async def send(self, opcode, payload=None):
        """
        Utility function to send data via websocket
        """
        if payload is None:
            payload = {}

        data = self.opcode(opcode, payload)
        await self.websocket.send(data)

    def opcode(self, opcode, payload):
        data = {"op": opcode, "d": payload}
        return json.dumps(data)

    async def heartbeat(self):
        """
        Sends heartbeat event at intervals determined by heartbeat_interval.
        The heartbeat event consists of opcode 1 and the last sequence number
        recieved in the "d" field.
        """
        while True:
            try:
                if self.heartbeat_interval is None:
                    print("Heartbeat interval not set")
                    return None

                await asyncio.sleep(self.heartbeat_interval / 1000)

                await self.send(op.HEARTBEAT, self.sequence_number)

            except Exception as e:
                print(f"Error sending heartbeat: {e}")
                return

    async def get_next_event(self):
        event = await self.event_queue.get()
        return event

    async def identify(self):
        event = {
            "token": self.token,
            "intents": (1 << 0 | 1 << 9),
            "properties": {
                "os": "macos",
                "browser": "safari",
                "device": "my_library",
            },
        }

        await self.send(op.IDENTIFY, event)

    async def reconnect(self):
        if self.resume_gateway_url and self.session_id:
            try:
                async with websockets.connect(
                    self.resume_gateway_url
                ) as self.websocket:
                    await self.resume()
            # TODO: if we don't reconnect in time to resume, we should receive an
            # INVALID_SESSION, so we should create a new connection. The
            # reconnect method shouldn't be called in the exception, but
            # rather when we see this opcode. See https://discord.com/developers/docs/topics/gateway#resuming
            except Exception as e:
                print(f"Failed to resume: {e}")
                self.resume_gateway_url = None
                self.session_id = None
                await self.connect()
        else:
            await self.connect()

    async def resume(self):
        resume_payload = {
            "op": op.RESUME,
            "d": {
                "token": self.token,
                "session_id": self.session_id,
                "seq": self.sequence_number,
            },
        }
        await self.send(resume_payload)

    async def get_guild_id(self):
        url = f"{self.base_url}/users/@me/guilds"
        guilds = await send_request("get", url, optional_headers=self.headers)
        if guilds is None:
            return None
        guild_id = next(
            (guild["id"] for guild in guilds if guild["name"] == "Igor"), None
        )
        return guild_id

    async def get_channels(self):
        guild_id = await self.get_guild_id()
        if guild_id is None:
            return None
        url = f"{self.base_url}/guilds/{guild_id}/channels"
        channels = await send_request("get", url, optional_headers=self.headers)
        return channels

    async def get_channel_id(self, channel_name):
        channels = await self.get_channels()
        if channels is None:
            return None
        channel_id = next(
            (channel["id"] for channel in channels if channel["name"] == channel_name),
            None,
        )
        return channel_id

    async def send_message(self, channel_id, message):
        url = f"{self.base_url}/channels/{channel_id}/messages"
        res = await send_request(
            "post", url, {"content": message}, optional_headers=self.headers
        )
        return res
