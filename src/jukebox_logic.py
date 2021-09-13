from src.discord_bot.youtube_api import Api
from googleapiclient.errors import HttpError
from src.discord_bot.errors import *
import discord

COLOUR = 0xC2842F


class Singleton(object):
    """An object that will only exist once, even if you initialize it multiple times"""
    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.__init__(*args, **kwds)
        return it

    def __init__(self, *args, **kwds):
        if args != () and isinstance(args[0], discord.client):
            self.client = args[0]


class ClientLogic(Singleton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def play(self, url):
        #TODO: Do shit here
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


def setup(client_par):
    global client
    client = client_par
