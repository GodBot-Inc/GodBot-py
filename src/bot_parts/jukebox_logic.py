import discord
import src.discord_api
from src.youtube_api import Api
from googleapiclient.errors import HttpError
from src.errors import *
from discord_slash.utils.manage_components import (create_actionrow,
                                                   create_button)
from discord_slash.model import ButtonStyle
from src.DatabaseCommunication import Database

COLOUR = 0xC2842F


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
