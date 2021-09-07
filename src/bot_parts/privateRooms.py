from discord.ext.commands import Cog
from utility.DatabaseCommunication import Database


ICON_LINK = r"https://notion-emojis.s3-us-west-2.amazonaws.com/v0/svg-twitter/1f512.svg"


class PrivateRooms(Cog):
    def __init__(self, client):
        self.client = client
        self.db = Database()

    @Cog.listener()
    async def on_ready(self):
        print("private Rooms loaded")


def setup(client):
    client.add_cog(PrivateRooms(client))
