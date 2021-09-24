from . import *
from discord.ext.commands import Cog


class PlayerInteraction(Cog):
    def __init__(self, client):
        self.client = client

    @Cog.listener()
    async def on_ready(self):
        print("Player Interactions are loaded")

    async def connect_to(self, guild_id: int, channel_id: int):
        ws = self.client._connection._get_websocket(guild_id)
        if channel_id == 0:
            await ws.voice_state(str(guild_id), None)
            return
        await ws.voice_state(str(guild_id), str(channel_id))

    @cog_slash(name="pause")
    async def _pause(self, ctx):
        """

        Pauses the audio playing on a server

        Parameters
        ----------
        ctx: Object passed to communicate with discord_bot

        """
        if ctx.author.voice is None:
            await ctx.send(embed=Embed.error("You are not connected to a Voicechannel"))
            return

        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        if player is None:
            await ctx.send(embed=Embed.error("there is no player active on your server"))
            return
        if player.paused:
            await ctx.send(embed=Embed.error("I'm already on pause"))
            return

        channel: int = player.fetch("channel")
        if channel is None:
            await ctx.send(embed=Embed.error("Could not get the channel I'm currently in"))
            return
        if channel != ctx.author.voice.channel.id:
            await ctx.send(embed=Embed.error("We are not in the same channel"))
            return

        await player.set_pause(True)
        await ctx.send(
            embed=discord.Embed(title=":pause_button: Paused Audio", description="", colour=discord.Colour.blue()))

    @cog_slash(name="resume")
    async def _resume(self, ctx):
        """

        Resumes the paused audio

        Parameters
        ----------
        ctx: Object passed to communicate with discord_bot

        """
        if ctx.author.voice is None:
            await ctx.send(embed=Embed.error("You are not connected to a Voicechannel"))
            return

        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        if player is None:
            await ctx.send(embed=Embed.error("There is no palyer active on your server"))
            return
        if not player.paused:
            await ctx.send(embed=Embed.error("I'm not on pause"))
            return

        channel: int = player.fetch("channel")
        if channel is None:
            await ctx.send(embed=Embed.error("Could not get the channel I'm currently in"))
            return
        if channel != ctx.author.voice.channel.id:
            await ctx.send(embed=Embed.error("We are not in the same channel"))
            return

        await player.set_pause(False)
        mbed = discord.Embed(title=":play_pause: Resumed Audio", description="", colour=discord.Colour.blue())
        await ctx.send(embed=mbed)

    @cog_slash(name="stop")
    async def _stop(self, ctx):
        """

        This command stops the audio playing. It clears the queue too.

        Parameters
        ----------
        ctx: Object passed to communicate with discord_bot

        """
        if ctx.author.voice is None:
            await ctx.send(embed=Embed.error("You are not connected to a Voicechannel"))
            return

        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        if player is None:
            await ctx.send(embed=Embed.error("There is no player active on your server"))
            return
        if not player.paused and not player.is_playing:
            await ctx.send(embed=Embed.error("I'm not paused and I'm not playing any songs"))
            return

        channel: int = player.fetch("channel")
        if channel is None:
            await ctx.send(embed=Embed.error("I could not get the channel I'm currently in"))
            return
        if channel != ctx.author.voice.channel.id:
            await ctx.send(embed=Embed.error("We are not in the same channel"))
            return

        await player.stop()
        mbed = discord.Embed(title=":stop_button: Stopped Audio", description="", colour=discord.Colour.blue())
        await ctx.send(embed=mbed)

    @cog_slash(name="skip")
    async def _skip(self, ctx: SlashContext):
        """

        Skips a song in the queue.

        Parameters
        ----------
        ctx: Object passed to communicate with discord_bot

        """
        if ctx.author.voice is None:
            await ctx.send(embed=Embed.error("You are not connected to a Voicechannel"))
            return

        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        if player is None:
            await ctx.send(embed=Embed.error("There is no player active on your server"))
            return
        if not player.is_playing and not player.paused:
            await ctx.send(embed=Embed.error("No music is playing or being paused"))
            return

        channel: int = player.fetch("channel")
        if channel is None:
            await ctx.send(embed=Embed.error("Could not get the channel I'm currently in"))
            return
        if channel != ctx.author.voice.channel.id:
            await ctx.send(embed=Embed.error("You are not in the same channel as I am"))
            return

        mbed = discord.Embed(title="",
                             description=f":next_track: **Skipped** [{player.current.title}]({player.current.uri})",
                             colour=discord.Colour.blue())

        await player.skip()
        await ctx.send(embed=mbed)

    @cog_slash(name="skipto")
    async def _skipto(self, ctx: SlashContext, index: int):
        """

        Skips to a song in the queue (you can skip multiple songs at once)

        Parameters
        ----------
        ctx: Object passed to communicate with discord_bot
        index: The index that the method should skip into

        """
        if ctx.author.voice.channel is None:
            await ctx.send(embed=Embed.error("You are not connected to a Voicechannel"))
            return

        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        if player is None:
            await ctx.send(embed=Embed.error("There is no player active on your server"))
            return
        if not player.is_playing and not player.paused:
            await ctx.send(embed=Embed.error("No music is playing or being paused"))
            return

        channel: int = player.fetch("channel")
        if channel is None:
            await ctx.send(embed=Embed.error("Could not get the channel I'm currently in"))
            return
        if channel != ctx.author.voice.channel.id:
            await ctx.send(embed=Embed.error("You are not in the same channel as I am"))
            return

        index = max(index, 0)
        if index > len(player.queue):
            await ctx.send(embed=Embed.error("This song does not exist in the queue"))
            return

        song: lavalink.models.AudioTrack = player.queue[index - 1]
        await player.skip(index - 1)
        await ctx.send(
            embed=discord.Embed(
                title="",
                description=":next_track: **Skipped** to song [{}]({})".format(song.title, song.uri),
                colour=discord.Colour.blue()
            )
        )

    @cog_slash(name="loop")
    async def _loop(self, ctx: SlashContext, mode: str):
        """

        Loops the current song. If ti ends the same song will be appended to the queue at the second position.

        Parameters
        ----------
        ctx: Object passed to communicate with discord_bot
        mode: Whether to turn loop on or off

        """
        if ctx.author.voice is None:
            await ctx.send(embed=Embed.error("You are not connected to a Voicechannel"))
            return

        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        if player is None:
            await ctx.send(embed=Embed.error("There is no player active on your server"))
            return
        if not player.is_playing and not player.paused:
            await ctx.send(embed=Embed.error("No music is playing or being paused"))
            return

        channel: int = player.fetch("channel")
        if channel is None:
            await ctx.send(embed=Embed.error("Could not get the channel I'm currently in"))
            return
        if channel != ctx.author.voice.channel.id:
            await ctx.send(embed=Embed.error("You are not in the same channel as me"))
            return

        if player.repeat and mode == "True":
            await ctx.send(embed=Embed.error("Already looping the current song"))
            return
        if not player.repeat and mode == "False":
            await ctx.send(embed=Embed.error("Not looping the current song"))
            return

        if mode == "True":
            mbed = discord.Embed(title=":repeat: Looping the current song", description="",
                                 colour=discord.Colour.blue())
            player.set_repeat(True)
            await ctx.send(embed=mbed)
        else:
            mbed = discord.Embed(title=":arrow_right: Playing songs in order", description="",
                                 colour=discord.Colour.blue())
            player.set_repeat(False)
            await ctx.send(embed=mbed)

    @cog_slash(name="volume")
    async def _volume(self, ctx: SlashContext, level: int):
        """

        Changes the volume that the bot is playing the audio with. This applies to everyone on the server.

        Parameters
        ----------
        ctx: Object passed to communicate with discord_bot
        level: The volume level the bot will be playing at. 1-10

        Returns
        -------

        """
        level: int = max(min(level, 10), 0)

        if ctx.author.voice is None:
            await ctx.send(embed=Embed.error("You are not connected to a Voicechannel"))
            return

        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        if player is None:
            await ctx.send(embed=Embed.error("There is no player active on your server"))
            return

        channel: int = player.fetch("channel")
        if channel is None:
            await ctx.send(embed=Embed.error("I could not get the channel I'm in"))
            return
        if channel != ctx.author.voice.channel.id:
            await ctx.send(embed=Embed.error("You are not in the same Voicechannel as I am"))
            return

        volume: int = player.volume
        await player.set_volume(level * 10)
        if level > volume / 10:
            mbed = discord.Embed(title=f":arrow_up: Volume is now set to `{level}`", description="",
                                 colour=discord.Colour.blue())
            await ctx.send(embed=mbed)
        elif level < volume / 10:
            mbed = discord.Embed(title=f":arrow_down: Volume is now set to `{level}`", description="",
                                 colour=discord.Colour.blue())
            await ctx.send(embed=mbed)
        elif level == volume / 10:
            mbed = discord.Embed(title=f"Volume is now set to `{level}`", description="", colour=discord.Colour.blue())
            await ctx.send(embed=mbed)

    @cog_slash(name="leave")
    async def _leave(self, ctx: SlashContext):
        """

        The bot leaves the Voicechannel on the server. It also cleans up the queue and player.

        Parameters
        ----------
        ctx: Object passed to communicate with discord_bot

        """
        if ctx.author.voice is None:
            await ctx.send(embed=Embed.error("You are not connected to a Voicechannel"))
            return

        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        channel: int = player.fetch("channel")
        if channel is None:
            await ctx.send(embed=Embed.error("Could nto find the channel I'm in"))
            return
        if channel != ctx.author.voice.channel.id:
            await ctx.send(embed=Embed.error("You are not in the same channel as I am"))
            return

        if player is not None:
            await player.stop()
        await self.connect_to(ctx.guild.id, 0)
        await ctx.send(
            embed=Embed.success(":white_check_mark: Left the Voicechannel and cleaned up")
        )


def setup(client):
    client.add_cog(PlayerInteraction(client))
