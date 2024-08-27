import asyncio
import json
from typing import Optional

import aiohttp
import websockets

from igor.utils import op


# this should be the gateway. This seems like a test, heh
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

    async def send(self, opcode, payload=None):
        if payload == None:
            payload = {}

        data = self.opcode(opcode, payload)
        print(f"> {data}\n")
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

                print("heartbeating")
                await asyncio.sleep(self.heartbeat_interval / 1000)

                await self.send(op.HEARTBEAT, self.sequence_number)

            except Exception as e:
                print(f"Error sending heartbeat: {e}")
                return

    async def receive(self):
        while True:
            try:
                message = await self.websocket.recv()
                data = json.loads(message)
                opcode = data["op"]

                if opcode == op.HEARTBEAT:
                    # self.heartbeat_interval = data["d"]["heartbeat_interval"]
                    print(f"Heartbeat: {data}\n")
                elif opcode == op.HEARTBEAT_ACK:
                    print(f"Heartbeat ACK: {data}\n")
                elif opcode == op.DISPATCH:
                    event_type = data.get("t")
                    if event_type == "READY":
                        self.resume_gateway_url = data["d"].get("resume_gateway_url")
                        self.session_id = data["d"].get("session_id")
                    if event_type == "MESSAGE_CREATE":
                        await self.event_queue.put(data)
                        print(f"DISPATCH event: {data}\n")
                elif opcode == op.RECONNECT:
                    print("Received RECONNECT opcode, initiating reconnection...")
                    await self.reconnect()

                self.sequence_number = data.get("s") or self.sequence_number

            except Exception as e:
                print(f"Error in receive: {e}")

    async def get_next_event(self):
        print("waiting for next event")
        event = await self.event_queue.get()
        print("Event received")
        return event

    async def identify(self):
        print("IDENTIFY")
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
                async with websockets.connect(self.resume_gateway_url) as self.websocket:
                    await self.resume()
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
                "seq": self.sequence_number
            }
        }
        await self.send(resume_payload)

    async def connect(self):
        """
        Opens websocket connection. Once connected, the client receives a Hello
        event that contains the heartbeat_interval. The heartbeat_interval is
        the length of time in ms that determines how often to send a heartbeat
        event in order to maintain the connection.
        """

        while True:
            try:
                data = await self.send_request("get", "/gateway")
                if data is None:
                    return None
                wss_url = data["url"]

                async with websockets.connect(wss_url) as self.websocket:
                    hello_event = await self.websocket.recv()
                    hello_data = json.loads(hello_event)
                    print(f"Received Hello event: {hello_data}\n")

                    self.heartbeat_interval = hello_data["d"]["heartbeat_interval"]
                    """
                    The s field represents the sequence number of the event, which is the relative order in which it occurred. You need to cache the most recent non-null s value for heartbeats, and to pass when Resuming a connection.
                    """
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

    async def send_request(
        self, request_type: str, path: str, args: Optional[dict] = None
    ):
        if args is None:
            args = {}

        url = self.base_url + path

        headers = {
            "User-Agent": f"DiscordBot (https://example.com, {self.version})",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": self.token,
        }

        # create an async session with context manager
        async with aiohttp.ClientSession() as session:
            if request_type.lower() == "get":
                async with session.get(url, params=args, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
            elif request_type.lower() == "post":
                async with session.post(url, json=args, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
            else:
                raise ValueError("Unsupported request type")

    async def get_guild_id(self):
        guilds = await self.send_request("get", "/users/@me/guilds")
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
        channels = await self.send_request("get", f"/guilds/{guild_id}/channels")
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
        res = await self.send_request(
            "post", f"/channels/{channel_id}/messages", {"content": message}
        )
        return res
