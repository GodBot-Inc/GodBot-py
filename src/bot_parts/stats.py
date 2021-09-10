from discord.ext.commands import Cog
from src.DatabaseCommunication import Database


class Stats(Cog):
    def __init__(self, client):
        self.client = client
        self.db = Database()
        


def setup(client):
    client.add_cog(Stats(client))
