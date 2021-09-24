from . import *
from discord.ext.commands import Cog

COLOUR = 0xC2842F


class Player(Cog):
    def __init__(self, client):
        self.client = client
        self.db = Database()

    @Cog.listener()
    async def on_ready(self):
        print("Player is loaded")

    async def connect_to(self, guild_id: int, channel_id: int):
        ws = self.client._connection._get_websocket(guild_id)
        if channel_id == 0:
            await ws.voice_state(str(guild_id), None)
            return
        await ws.voice_state(str(guild_id), str(channel_id))

    @Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState):
        print("voice state update")
        if not member.bot and after.channel is None:
            if not [m for m in before.channel.members if not m.bot]:
                player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(member.guild.id)
                if player is not None:
                    await player.stop()
                await self.connect_to(member.guild.id, 0)

        if member == self.client.user and after.channel is not None and before.channel is not None:
            player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(member.guild.id)
            if player is not None:
                player.delete("channel")
                player.store("channel", after.channel.id)
                print(player.fetch("channel"))
                if player.is_playing and not player.paused:
                    await asyncio.sleep(1)
                    await player.set_pause(True)
                    await asyncio.sleep(0.5)
                    await player.set_pause(False)

    async def play_video(self, ctx: SlashContext, player: lavalink.models.DefaultPlayer, videoId: str,
                         playlist: bool = False, platform: str = "youtube") -> bool:
        """

        This function plays a single video in discord_bot.
        It either plays it immediately or appends it to the queue. Whether something is played or not.
        This is a helper function because in a lot of functions songs are played.

        Parameters
        ----------
        ctx: Object passed to communicate with discord_bot
        player: The player that plays the audio
        videoId: The YoutubeID of the video that's going to be played
        playlist: Whether to send a play message or not
        platform: From which platform the video should be taken

        """
        if platform == "youtube":
            results: dict = await player.node.get_tracks(f"https://www.youtube.com/watch?v={videoId}")
        else:
            raise GodBotError

        if not results["tracks"]:
            raise VideoNotFound

        track = results["tracks"][0]
        print(track)

        player.add(requester=ctx.author.id, track=track)

        if not playlist:
            no_thumbnail: bool = False
            no_title: bool = False

            yt = Api()
            yt.search_video_url(["https://www.youtube.com/watch?v={}".format(videoId)])
            if not yt.thumbnail:
                no_thumbnail = True
            if not yt.title:
                no_title = True

            if not player.is_playing and not player.paused:
                await player.play()
                if no_title:
                    mbed = discord.Embed(
                        title="Now playing",
                        description=f"https://www.youtube.com/watch?v={videoId}",
                        colour=COLOUR
                    )
                else:
                    mbed = discord.Embed(
                        title="Now playing",
                        description=f"[{yt.title[0]}](https://www.youtube.com/watch?v={videoId})",
                        colour=COLOUR
                    )

            else:
                if no_title:
                    mbed = discord.Embed(
                        title="Now playing",
                        description=f"https://www.youtube.com/watch?v={videoId}",
                        colour=COLOUR
                    )
                else:
                    mbed = discord.Embed(
                        title="Added to Queue",
                        description=f"[{yt.title[0]}](https://www.youtube.com/watch?v={videoId})",
                        colour=COLOUR
                    )

            if not no_thumbnail:
                mbed.set_thumbnail(url=yt.thumbnail[0])
            else:
                mbed.set_thumbnail(url="https://overview-ow.com/rasberryKai/Icons/music.png")
            mbed.set_footer(icon_url=ctx.author.avatar_url,
                            text=f"Added by {ctx.author.display_name}#{ctx.author.discriminator}")
            await ctx.send(embed=mbed)
            yt.close()

        if not player.is_playing and not player.paused:
            await player.play()

    async def play_playlist(self, ctx: SlashContext, player: lavalink.models.DefaultPlayer, playlistId: str = None,
                            videoIds: tuple = None, platform: str = "youtube"):
        """

        This method plays a playlist either from a playlistId or from several videoIds.
        More than one video is played from a lot of functions so this method exists.

        Parameters
        ----------
        ctx: Object passed to interact with discord_bot
        player: The player that plays audio
        playlistId: The ID that youtube have that playlist as an identifier. Here used to get the videos from it. Defaults to None
        videoIds: If you want to play with this method and you don't have a playlistId put some videoIds in a tuple and pass it. Defaults to None
        platform: From which platform the playlist should be played

        """
        yt = Api()

        videos_found: int = 0

        player_state: bool = False
        if player.is_playing or player.paused:
            player_state = True

        if playlistId is None and videoIds is None:
            raise PlaylistNotFound

        msg = await ctx.send(embed=discord.Embed(title="Processing Playlist", description="", colour=COLOUR))

        if playlistId is not None:
            yt.search_playlist_items(playlistId)
            if yt.found == 0:
                await msg.delete()
                raise PlaylistNotFound

            for x in range(0, yt.found):
                try:
                    await self.play_video(ctx, player, yt.videoId[x], True)
                except VideoNotFound:
                    pass
                else:
                    videos_found += 1
                    try:
                        await msg.edit(embed=discord.Embed(title=f"Processing Playlist Songs added: `{videos_found}`",
                                                           description="",
                                                           colour=COLOUR))
                    except NotFound as e:
                        print("Request Failure {}".format(e))
                        pass

        if videoIds is not None:
            for x in range(0, videoIds):
                try:
                    await self.play_video(ctx, player, videoIds[x], True)
                except VideoNotFound:
                    pass
                else:
                    videos_found += 1
                    try:
                        await msg.edit(
                            embed=discord.Embed(title=f"Processing Playlist `{videos_found}`", description="",
                                                colour=COLOUR))
                    except NotFound as e:
                        print("Request Failure {}".format(e))
                        pass

        if player_state:
            mbed = discord.Embed(
                title="Added playlist",
                description="",
                colour=COLOUR
            )
        else:
            mbed = discord.Embed(
                title="Playing playlist",
                description="",
                colour=COLOUR
            )
        mbed.add_field(name="Songs added", value=f"`{videos_found}`")
        mbed.set_thumbnail(url=yt.thumbnail[0])
        mbed.set_footer(icon_url=ctx.author.avatar_url,
                        text=f"Added by {ctx.author.display_name}#{ctx.author.discriminator}")

        try:
            await msg.edit(embed=mbed)
        except NotFound:
            await ctx.send(embed=mbed)
        yt.close()

    @cog_slash(name="play")
    async def _play(self, ctx: SlashContext, url: str):
        """

        A play command with that you can play a song from a youtube url.

        Parameters
        ----------
        ctx: Object passed to interact with discord_bot
        url: URL of a song. Not allowed: Livestreams

        """
        await ctx.defer()

        if ctx.author.voice is None:
            await ctx.send(embed=Embed.error("You are not connected to a Voicechannel"))
            return

        try:
            url_type: tuple = await check_url(url)
        except (InvalidURL, VideoTypeNotFound):
            await ctx.send(embed=Embed.error(":x: Invalid Url. :white_check_mark: Supported:\n*Youtube Music playlist/video\n*Youtube playlist/video"))
            return

        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        if player is None:
            player = self.client.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        if not player.is_connected:
            await self.connect_to(ctx.guild.id, ctx.author.voice.channel.id)
            player.store("channel", ctx.author.voice.channel.id)

        channel: int = player.fetch("channel")
        if channel is None:
            await ctx.send(embed=Embed.error(":x: I could not get the channel I'm in"))
        if channel != ctx.author.voice.channel.id:
            await ctx.send(embed=Embed.error(":x: We are not in the same channel"))

        if url_type[1] == "video":
            try:
                await self.play_video(ctx, player, url_type[2], platform=url_type[0])
            except VideoNotFound:
                await ctx.send(embed=Embed.error("Could not find the video"))

        elif url_type[1] == "playlist":
            try:
                await self.play_playlist(ctx, player, url_type[2], platform=url_type[0])
            except PlaylistNotFound:
                await ctx.send(embed=Embed.error("Could not find the playlist"))

        else:
            await ctx.send(embed=Embed.error(":x: I could not determine the link-type"))

    @cog_slash(name="searchplay")
    async def _searchplay(self, ctx: SlashContext, search: str, queue_length: int = 1, priority_level: str = "high"):
        """

        Searches for relevant songs according to the search key and plays it

        Parameters
        ----------
        ctx: An object used to communicate with discord
        search: The search-key that the bot is going to search for
        queue_length: How many songs the bot should play
        priority_level: How strict the bot should filter the results (There are 3 levels -> low, middle, high)

        Returns
        -------

        """
        await ctx.send(embed=Embed.error("In Development"))

    #TODO: Playnow command


def setup(client):
    client.add_cog(Player(client))
