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


async def start_timer(channel_id: int, msg_id: int):
    def get_ar(type: str):
        if type == "search":
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

    """Here we start a timer that expires after 300 seconds"""
    #TODO: Differentiate between different things (queue, search)
    start = time()
    while time() - start < 300:
        """While 120 have not passed"""
        msg_json = messages.get(channel_id, msg_id)
        if msg_json == {} or msg_json is None:
            db.delete_search(msg_id)
            return

        component_id = msg_json["components"][0]["components"][1]["custom_id"]
        if component_id == "closed_search_left":
            db.delete_search(msg_id)
            return
        elif component_id == "closed_queue_left":
            db.delete_queue(msg_id)
            return
        await sleep(30)  # Cooldown so we don't request the discord_bot API too often
    messages.edit(channel_id, msg_id, components=get_ar("search"))
    db.delete_search(msg_id)


class ClientLogic(Singleton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def connect_to(self, guild_id: int, channel_id: int):
        ws = self.client._connection._get_websocket(guild_id)
        if channel_id == 0:
            await ws.voice_state(str(guild_id), None)
            return
        await ws.voice_state(str(guild_id), str(channel_id))

    async def play(self, url: str, guild_id: int, guild_region: str, channel: int = None, from_api: bool = False):
        async def check_url(checked_url: str) -> Tuple[str, str, str]:
            """

            A helper function to determine whether the given url is a video- or playlist-url.
            It also returns the Id to access either the playlist or the video.

            Parameters
            ----------
            checked_url: The given url that's going to be checked

            Returns
            -------
            Tuple[str, str, str]: first is the type of the link ("music"/"normal", "playlist"/"video", ID)

            """

            async def valid_url(validate_url: str) -> bool:
                """

                A function that sends a get request to the given link so you can test if it is a valid one.

                Parameters
                ----------
                validate_url: The url that should be tested

                Returns
                -------
                bool: Whether the website is callable or not

                """
                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.get(validate_url) as resp:
                            pass
                    except aiohttp.client_exceptions.InvalidURL:
                        return False
                    else:
                        return True

            async def yt_url_processing(processed_url: str) -> Tuple[str, str, str]:
                """

                Parameters
                ----------
                processed_url: The url that should be processed

                Returns
                -------
                Tuple[str, str, str]: first is the type of the link ("music"/"normal", "playlist"/"video", ID)

                """
                try:
                    playlist_url: str = checked_url.split("list=")[1]
                except IndexError:  # Url is not a playlist
                    try:
                        videoId: str = checked_url.split("watch?v=")[1]
                    except IndexError:
                        raise VideoTypeNotFound

                    if "music.youtube.com" in url:
                        return "music", "video", videoId
                    elif "youtube.com" in url:
                        return "normal", "video", videoId
                    else:
                        raise VideoTypeNotFound
                else:
                    try:
                        playlist_url: str = playlist_url.split("&")[0]
                    except IndexError:
                        pass

                    if "music.youtube.com" in url:
                        return "music", "playlist", playlist_url
                    elif "youtube.com" in url:
                        return "normal", "playlist", playlist_url
                    else:
                        raise VideoTypeNotFound

            if not await valid_url(url):
                raise InvalidURL

            if "youtube.com" in url:
                return await yt_url_processing(url)
            else:
                raise InvalidURL

        if not from_api:
            try:
                url_type: tuple = await check_url(url)
            except (InvalidURL, VideoTypeNotFound):
                if channel is not None:
                    messages.send(channel,
                                  content="",
                                  embed={
                                      "title": ":x: Invalid Url.\n:white_ckeck_mark: Supported:\n-Youtube Music playlist/video\n-Youtube playlist/video",
                                      "description": "",
                                      "color": Red
                                  })
                    return

        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(guild_id)
        if player is None:
            player = self.client.music.player_manager.create(guild_id, endpoint=guild_region)
        if not player.is_connected:
            await self.connect_to(guild_id, channel)
            player.store("channel", channel)

        player_channel: int = player.fetch("channel")
        if player_channel is None:
            if player_channel is not None:
                messages.send(channel,
                              embed={
                                  "title": ":x: I could not get the channel I'm in",
                                  "description": "",
                                  "color": Red
                              })
                return
            raise PlayerChannelNotFound
        if player_channel != channel:
            pass
        #TODO: Rewrite src.jukebox.py play so it fit's the bot and the api


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
