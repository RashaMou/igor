class Event:
    def __init__(self, type: str, content: str, channel: str, discord_channel_id: str = None):
        self.channel = channel
        self.content = content
        self.type = type
        self.discord_channel_id = discord_channel_id
