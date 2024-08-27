import json
from typing import Optional

import requests


class DiscordGateway:

    def __init__(self, token):
        self.base_url = "https://discord.com/api/v10/"
        self.token = token
        self.version = "1.0.0"
        self.guild_id = self.get_guild_id()
        self.channels = self.get_channels()

    def connect(self):
        res = self.send_request("get", "/gateway")
        data = res.json()
        wss_url = data["url"]
        print(wss_url)

    def send_request(self, request_type: str, path: str, args: Optional[dict] = None):
        if args is None:
            args = {}

        url = self.base_url + path

        headers = {
            "User-Agent": f"DiscordBot (https://example.com, {self.version})",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": self.token,
        }

        if request_type.lower() == "get":
            response = requests.get(url, params=args, headers=headers)
            if response.status_code == 200:
                return response.json()
        elif request_type.lower() == "post":
            response = requests.post(url, json=args, headers=headers)
            if response.status_code == 200:
                return response.json()
        else:
            raise ValueError("Unsupported request type")

    def get_guild_id(self):
        guilds = self.send_request("get", "/users/@me/guilds")
        guild_id = next(
            (guild["id"] for guild in guilds if guild["name"] == "Igor"), None
        )
        return guild_id

    def get_channels(self):
        channels = self.send_request("get", f"/guilds/{self.guild_id}/channels")
        return channels

    def get_channel_id(self, channel_name):
        channels = self.get_channels()
        channel_id = next(
            (channel["id"] for channel in channels if channel["name"] == channel_name),
            None,
        )
        return channel_id

    def send_message(self, message, channel_name):
        channel_id = self.get_channel_id(channel_name)
        self.send_request(
            "post", f"/channels/{channel_id}/messages", {"content": message}
        )
