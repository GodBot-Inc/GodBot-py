from src.discord_api import messages
from data.custom_lavalink import lavalink
from time import time
from asyncio import sleep
from src.discord_bot.DatabaseCommunication import Database
from utility.get import ActionRows

COLOUR = 12747823
Red = 15158332
Green = 5763719
db = Database()


class Singleton(object):
    """An object that will only exist once, even if you initialize it multiple times"""

    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.__init__(*args, **kwds)
        return it

    def __init__(self, client=None, *args, **kwds):
        if client is not None:
            self.client = client


class ClientLogic(Singleton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def connect_to(self, guild_id: int, channel_id: int):
        ws = self.client._connection._get_websocket(guild_id)
        if channel_id == 0:
            await ws.voice_state(str(guild_id), None)
            return
        await ws.voice_state(str(guild_id), str(channel_id))

    async def play(self, platform: str, url: str, url_type: str, guild_id: int, guild_region: str, channel: int = None):
        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(guild_id)
        if player is None:
            player = self.client.music.player_manager.create(guild_id, endpoint=guild_region)
        if not player.is_connected:
            await self.connect_to(guild_id, channel)
            player.store("channel", channel)

        if platform == "youtube":
            pass
