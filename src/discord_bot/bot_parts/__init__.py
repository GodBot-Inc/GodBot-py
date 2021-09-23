from __future__ import unicode_literals

from src.discord_bot.CONSTANTS import *
import discord
from discord.ext.commands import Cog
from src.discord_bot.DatabaseCommunication import Database
from data.custom_lavalink import lavalink
from src.Api import jukebox_api_logic
import asyncio
import aiohttp
from discord_slash.cog_ext import cog_slash
from utility.get import ActionRows
from src.discord_bot.errors import *
from typing import Tuple
from typing import Dict
from src.discord_bot.youtube_api import Api
from discord_slash import SlashContext
from math import ceil
from utility.get import Embed
