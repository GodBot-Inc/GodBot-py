import discord
from discord.ext.commands import Cog
from discord.utils import get
from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.cog_ext import cog_slash
from utility.DatabaseCommunication import Database


class Stats(Cog):
    def __init__(self, client):
        self.client = client
        self.db = Database()
        


def setup(client):
    client.add_cog(Stats(client))
