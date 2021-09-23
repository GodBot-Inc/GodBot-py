from typing import Tuple
from src.discord_bot.youtube_api import Api
from googleapiclient.errors import HttpError
from src.discord_bot.errors import *
from src.discord_bot.discord_api import messages
import discord
import aiohttp
from data.custom_lavalink import lavalink
from time import time
from asyncio import sleep
from src.discord_bot.DatabaseCommunication import Database
from discord_slash.utils.manage_components import create_button, create_actionrow

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


async def start_timer(msg, type: int) -> None:
    """

    A function that is called when a message with buttons is created.
    After 5 minutes the buttons get disabled.

    Parameters
    ----------
    msg: The message object gained from the async ctx.send method
    type: 1 -> search; 2 -> queue

    Returns
    ---------
    None

    """

    def get_ar(type: int):
        if type == 1:
            return [
                {
                    "type": 1,
                    "components": [
                        {
                            "type": 2,
                            "label": "Url",
                            "style": 5,
                            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                            "disabled": True
                        },
                        {
                            "type": 2,
                            "label": "◀",
                            "style": 2,
                            "custom_id": "closed_search_left",
                            "disabled": True
                        },
                        {
                            "type": 2,
                            "label": "▶",
                            "style": 2,
                            "custom_id": "closed_search_right",
                            "disabled": True
                        }
                    ]
                }
            ]
        elif type == 2:
            return [
                {
                    "type": 1,
                    "components": [
                        {
                            "type": 1,
                            "components": [
                                {
                                    "type": 2,
                                    "label": "◀◀",
                                    "style": 2,
                                    "custom_id": "queue_first",
                                    "disabled": True
                                },
                                {
                                    "type": 2,
                                    "label": "◀",
                                    "style": 2,
                                    "custom_id": "queue_left",
                                    "disabled": True
                                },
                                {
                                    "type": 2,
                                    "label": "▶",
                                    "style": 2,
                                    "custom_id": "queue_right",
                                    "disabled": True
                                },
                                {
                                    "type": 2,
                                    "label": "▶▶",
                                    "style": 2,
                                    "custom_id": "queue_last",
                                    "disabled": True
                                }
                            ]
                        }
                    ]
                }
            ]

    """Here we start a timer that expires after 300 seconds"""
    start = time()
    while time() - start < 300:
        """While 120 have not passed"""
        msg_json = messages.get(msg.channel.id, msg.id)
        if msg_json == {} or msg_json is None:
            db.delete_search(msg.id)
            return

        component_id = msg_json["components"][0]["components"][1]["custom_id"]
        if component_id == "closed_search_left":
            db.delete_search(msg.id)
            return
        elif component_id == "closed_queue_left":
            db.delete_queue(msg.id)
            return
        await sleep(30)  # Cooldown so we don't request the discord_bot API too often
    if type == 1:
        await msg.edit(
            components=[create_actionrow(
                create_button(
                    style=5,
                    label="Url",
                    url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    disabled=True
                ),
                create_button(
                    style=2,
                    label="◀",
                    custom_id="closed_search_left",
                    disabled=True
                ),
                create_button(
                    style=2,
                    label="▶",
                    custom_id="closed_search_right",
                    disabled=True
                )
            )]
        )
        db.delete_search(msg.id)
    elif type == 2:
        await msg.edit(
            components=[create_actionrow(
                create_button(
                    style=2,
                    label="◀◀",
                    custom_id="a",
                    disabled=True
                ),
                create_button(
                    style=2,
                    label="◀",
                    custom_id="closed_queue_left",
                    disabled=True
                ),
                create_button(
                    style=2,
                    label="▶",
                    custom_id="queue_right",
                    disabled=True
                ),
                create_button(
                    style=2,
                    label="▶▶",
                    custom_id="queue_last",
                    disabled=True
                )
            )]
        )
        db.delete_queue(msg.id)
    if type == 1:
        db.delete_search(msg.id)
    elif type == 2:
        db.delete_queue(msg.id)


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


async def search(search: str, results: int = 8, songfilter: str = "True"):
    yt = Api()

    results = max(min(results, 12), 2)

    if songfilter == "True":
        try:
            yt.search(search, results, True)
        except HttpError as e:
            raise YTApiError(e)
    else:
        try:
            yt.search(search, results, False)
        except HttpError as e:
            raise YTApiError(e)

    song_dictionary: dict = {}
    for x in range(yt.found):
        song_dictionary[str(x + 1)] = {"title": yt.title[x], "thumbnail": yt.thumbnail[x], "url": yt.url[x],
                                       "views": yt.views[x]}
    yt.close()
    return song_dictionary
