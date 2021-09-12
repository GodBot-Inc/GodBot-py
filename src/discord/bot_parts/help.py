import discord
from discord.ext.commands import Cog
from discord_slash import SlashContext
from discord_slash.cog_ext import cog_slash
from discord_slash.utils.manage_commands import create_choice, create_option


ICON_LINK = r"https://w7.pngwing.com/pngs/773/218/png-transparent-computer-icons-help-miscellaneous-text-hand-thumbnail.png"
COLOUR_CODE=0x0C4FEB


class HelpCog(Cog):
    """This is the help part so users can get an introduction to the bot in discord"""
    def __init__(self, client):
        self.client = client

    @Cog.listener()
    async def on_ready(self):
        print("Help Extension loaded")

    @staticmethod
    def normal() -> discord.Embed:
        embed = discord.Embed(
            title="Help Menu",
            description="All the slashes can be replaced with a .",
            colour=COLOUR_CODE
        )
        embed.set_thumbnail(url="https://overview-ow.com/rasberryKai/Icons/gott.png")
        embed.add_field(name="`/enable [name]`", value="Disables part of the bot", inline=False)
        embed.add_field(name="`/disable [name]`", value="Disables part of the bot", inline=False)
        embed.add_field(name="`/invitelink`", value="Sends an invite link to you", inline=False)
        embed.add_field(name="`/help moderation`", value="shows help menu for moderation commands", inline=False)
        embed.add_field(name="`/help prison`", value="shows help menu for prisons", inline=False)
        embed.add_field(name="`/help privateroom`", value="shows help menu for privaterooms", inline=False)
        embed.add_field(name="`/help jukebox`", value="shows help menu for the jukebox part", inline=False)
        embed.add_field(name="`/help config`", value="shows help menu for the config part", inline=False)
        return embed

    @staticmethod
    def moderation() -> discord.Embed:
        embed = discord.Embed(
            title="Moderation Help Menu",
            colour=COLOUR_CODE
        )
        embed.set_thumbnail(url="https://overview-ow.com/rasberryKai/Icons/analytics.png")
        embed.add_field(name="`/clear (amount) (member)`", value="Clears messages in particular channel", inline=False)
        embed.add_field(name="`/banlist`", value="Shows all banned members", inline=False)
        return embed

    @staticmethod
    def prison() -> discord.Embed:
        embed = discord.Embed(
            title="Prison Help Menu",
            colour=COLOUR_CODE
        )
        embed.set_thumbnail(url="https://overview-ow.com/rasberryKai/Icons/prison.png")
        embed.add_field(name="`/arrest [member]`", value="Arrests a member", inline=False)
        embed.add_field(name="`/release [member]`", value="Releases an imprisoned member", inline=False)
        embed.add_field(name="`/checkprison`", value="Shows you imprisoned members and why they are imprisoned", inline=False)
        return embed

    @staticmethod
    def privateroom() -> discord.Embed:
        embed = discord.Embed(
            title="Private Room Help Menu",
            description="**In Development**",
            colour=COLOUR_CODE
        )
        embed.set_thumbnail(url="https://overview-ow.com/rasberryKai/Icons/private-chat.png")
        embed.add_field(name="`/name [name]`", value="Renames a private channel", inline=False)
        embed.add_field(name="`/open`", value="Opens a private channel which makes it a normal channel", inline=False)
        embed.add_field(name="`/close`", value="Closes a privateroom so it's private again", inline=False)
        embed.add_field(name="`/add [member/role]`", value="Adds all mentioned member and or roles to the privaterom", inline=False)
        embed.add_field(name="`/remove [member/role]`", value="Removes all mentioned memever and or roles from the privateroom", inline=False)
        embed.add_field(name="`/hold`", value="Keeps the privateroom open even if no one is inside", inline=False)
        embed.add_field(name="`/claim`", value="Grants you owner privileges on the channel if the owner left", inline=False)
        return embed

    @staticmethod
    def jukebox() -> discord.Embed:
        embed = discord.Embed(
            title="Jukebox Help Menu",
            description="**In Development**",
            colour=COLOUR_CODE
        )
        embed.set_thumbnail(url="https://overview-ow.com/rasberryKai/Icons/music.png")
        embed.add_field(name="`/play [youtube-link]`", value="Plays the requested song from the youtube/youtube-music url. If a song is already playing it will be added to the queue", inline=False)
        embed.add_field(name="`/search [search-term] (optional: results) (optional: songfilter)`", value="Performs a yt-search for the term", inline=False)
        embed.add_field(name="`/pause`", value="Pauses the audio playing", inline=False)
        embed.add_field(name="`/resume`", value="Resumes the paused audio", inline=False)
        embed.add_field(name="`/loop [mode]`", value="Loops the current song if on and plays songs in order if off", inline=False)
        embed.add_field(name="`/skip`", value="Skips the current song. **NOTE:** Stops the loop mode if on", inline=False)
        embed.add_field(name="`/skipto [index]`", value="Skips to the given song", inline=False)
        embed.add_field(name="`/stop`", value="Stops playing the audio and clears the queue", inline=False)
        embed.add_field(name="`/volume [level]`", value="Adjusts the volume of a song immediately", inline=False)
        embed.add_field(name="`/current`", value="Shows Information about the current song", inline=False)
        embed.add_field(name="`/queue`", value="Shows you the songs in the queue with it's indices", inline=False)
        embed.add_field(name="`/remove [index]`", value="Removes the song with the given index from the queue", inline=False)
        embed.add_field(name="`/removedupes`", value="Removes all duplicates from the queue", inline=False)
        embed.add_field(name="`/leave`", value="Leaves the Voicechannel and removes the player", inline=False)
        return embed

    @staticmethod
    def config() -> discord.Embed:
        embed = discord.Embed(
            title="Config Help Menu",
            description="",
            colour=COLOUR_CODE
        )
        embed.set_thumbnail(url="https://overview-ow.com/rasberryKai/Icons/configuration.png")
        embed.add_field(name="`/setup`", value="Sets up the bot so it works", inline=False)
        embed.add_field(name="`/prereqs`", value="Shows you the prerequirements that the bot needs", inline=False)
        return embed

    @cog_slash(
        name="help",
        description="Shows all commands you can run",
        options=[
            create_option(
                name="part_name",
                description="Choose a plugin!",
                required=False,
                option_type=3,
                choices=[
                    create_choice(
                        name="Moderation",
                        value="moderation"
                    ),
                    create_choice(
                        name="Prison",
                        value="prison"
                    ),
                    create_choice(
                        name="Private Room",
                        value="privateroom"
                    ),
                    create_choice(
                        name="Jukebox",
                        value="jukebox"
                    ),
                    create_choice(
                        name="Config",
                        value="config"
                    )
                ]
            )
        ]
    )
    async def help(self, ctx: SlashContext, part_name: str = None):
        if part_name is None:
            await ctx.send(embed=self.normal())
        elif part_name == "moderation":
            await ctx.send(embed=self.moderation())
        elif part_name == "prison":
            await ctx.send(embed=self.prison())
        elif part_name == "privateroom":
            await ctx.send(embed=self.privateroom())
        elif part_name == "jukebox":
            await ctx.send(embed=self.jukebox())
        elif part_name == "config":
            await ctx.send(embed=self.config())


def setup(client):
    client.add_cog(HelpCog(client))
