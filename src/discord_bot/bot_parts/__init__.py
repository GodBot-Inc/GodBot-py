from __future__ import unicode_literals

import discord
from src.discord_bot.DatabaseCommunication import Database
from discord.ext.commands import Cog
from data.custom_lavalink import lavalink
import asyncio
from discord_slash import SlashContext
from src.discord_bot.youtube_api import Api
from googleapiclient.errors import HttpError
from utility.get import Embed, ActionRows
from src.errors import *
from discord_slash.cog_ext import cog_slash
from typing import Dict, Tuple
import aiohttp
from math import ceil
from src.discord_bot import utils
from utility.check import check_url
COLOUR = 0xC2842F
