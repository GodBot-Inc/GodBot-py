import discord
from discord.ext.commands import Cog
from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.cog_ext import cog_slash
from src.discord.DatabaseCommunication import Database


ICON_LINK = r"https://notion-emojis.s3-us-west-2.amazonaws.com/v0/svg-twitter/1f574-fe0f.svg"


class Manager(Cog):
    """This is the manager part of the bot """
    def __init__(self, client):
        self.client = client
        self.db = Database()


    @Cog.listener()
    async def on_ready(self):
        print("Manage extension loaded")


    async def _get_embed(self, mbed_type: str, content: str) -> discord.Embed:
        """A helper function that returns either a short success embed or a short error embed.

        Args:
            mbed_type (str): Whether the message should be a success or an error message.
            content (str): The content of the message.

        Returns:
            discord.Embed: The requested message.
        """
        if mbed_type == "success":
            mbed = discord.Embed(
                title=f"{content}",
                description="",
                colour=discord.Colour.green()
            )
            return mbed
        elif mbed_type == "error":
            mbed = discord.Embed(
                title=f"{content}",
                description="",
                colour=discord.Colour.red()
            )
            return mbed


    @cog_slash(
        name="clear",
        description="Clears specific amount of messages",
        options=[
            create_option(
                name="amount",
                description="Number of messages to be cleared. Note: If nothing is given 100 messages are cleared",
                option_type=4,
                required=False
            )
        ]
    )
    async def clear(self, ctx: SlashContext, amount: int=0):
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send(embed=await self._get_embed("error", ":x: You have not the right to manage messages"))
            return
        await ctx.defer()
        amount = min(max(amount, 0), 100)
        if amount == 0:
            await ctx.channel.purge(limit=100)
            await ctx.send(embed=await self._get_embed("success", ":white_check_mark: 100 Messages cleared"), delete_after=1.5)
            return
        await ctx.channel.purge(limit=amount)
        await ctx.send(embed=await self._get_embed("success", f":white_check_mark: {amount} Messages cleared"), delete_after=1.5)


    @cog_slash(
        name="banlist",
        description="shows you all banned users in a list"
    )
    async def _banlist(self, ctx: SlashContext):
        print("banlist")
        if not ctx.author.guild_permissions.view_guild_insights:
            await ctx.send(embed=await self._get_embed("error", ":x: You have not the right to view guild insights"))
            return
        bans = await ctx.guild.bans()
        if len(bans) == 0:
            mbed = discord.Embed(
                title="**Ban List**",
                description="Empty",
                colour=0x1a1a1a
            )
            await ctx.send(embed=mbed)
        else:
            pretty_list = ["• {0.name}#{0.discriminator}".format(entry.user) for entry in bans]
            mbed = discord.Embed(
                title="**Ban List**",
                description="{}".format("\n".join(pretty_list)),
                colour=0x1a1a1a
            )
            await ctx.send(embed=mbed)


def setup(client):
    client.add_cog(Manager(client))
