from . import *
from discord.ext.commands import Cog


ICON_LINK = r"https://w7.pngwing.com/pngs/773/218/png-transparent-computer-icons-help-miscellaneous-text-hand-thumbnail.png"
COLOUR_CODE = 0x0C4FEB


class Help(Cog):
    """This is the help part so users can get an introduction to the bot in discord_bot"""
    def __init__(self, client):
        self.client = client

    @Cog.listener()
    async def on_ready(self):
        print("Help Extension loaded")

    @cog_slash(name="help")
    async def help(self, ctx: SlashContext):
        embed = discord.Embed(
            title="Jukebox Help Menu",
            description="**In Development**",
            colour=COLOUR_CODE
        )
        embed.set_thumbnail(url="https://overview-ow.com/rasberryKai/Icons/music.png")
        embed.add_field(name="`/play [youtube-link]`",
                        value="Plays the requested song from the youtube/youtube-music url. If a song is already playing it will be added to the queue",
                        inline=False)
        embed.add_field(name="`/search [search-term] (optional: results) (optional: songfilter)`",
                        value="Performs a yt-search for the term", inline=False)
        embed.add_field(name="`/pause`", value="Pauses the audio playing", inline=False)
        embed.add_field(name="`/resume`", value="Resumes the paused audio", inline=False)
        embed.add_field(name="`/loop [mode]`", value="Loops the current song if on and plays songs in order if off",
                        inline=False)
        embed.add_field(name="`/skip`", value="Skips the current song. **NOTE:** Stops the loop mode if on",
                        inline=False)
        embed.add_field(name="`/skipto [index]`", value="Skips to the given song", inline=False)
        embed.add_field(name="`/stop`", value="Stops playing the audio and clears the queue", inline=False)
        embed.add_field(name="`/volume [level]`", value="Adjusts the volume of a song immediately", inline=False)
        embed.add_field(name="`/current`", value="Shows Information about the current song", inline=False)
        embed.add_field(name="`/queue`", value="Shows you the songs in the queue with it's indices", inline=False)
        embed.add_field(name="`/remove [index]`", value="Removes the song with the given index from the queue",
                        inline=False)
        embed.add_field(name="`/removedupes`", value="Removes all duplicates from the queue", inline=False)
        embed.add_field(name="`/leave`", value="Leaves the Voicechannel and removes the player", inline=False)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Help(client))
