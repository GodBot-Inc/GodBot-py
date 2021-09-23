from __future__ import unicode_literals

from src.discord_bot.DatabaseCommunication import Database
from src.discord_bot.CONSTANTS import *
from data.custom_lavalink import lavalink
import discord
import asyncio
from discord_slash.utils.manage_components import (create_button,
                                                   create_actionrow)
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash import SlashContext
from src.discord_bot.errors import *
from src.discord_bot.InteractionsHandler import EventHandler
from typing import Tuple
import aiohttp
from math import ceil
from pprint import pprint
from src.discord_bot.discord_api import messages
from src.discord_bot.youtube_api import Api
from src import jukebox_api_logic
from discord.ext.commands import Cog
from discord_slash.cog_ext import cog_slash
from discord_slash.utils.manage_components import ButtonStyle
from utility.get import ActionRows
