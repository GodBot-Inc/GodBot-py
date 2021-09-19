from . import *
from src.Api import flask_api

COLOUR = 0xC2842F


async def _get_embed(mbed_type: str, content: str) -> discord.Embed:
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


class Jukebox(Cog):
    def __init__(self, client):
        self.client = client
        self.db = Database()
        self.client.music = lavalink.Client(APPLICATION_ID)
        self.client.music.add_node(LAVALINK_IP, LAVALINK_PORT, LAVALINK_PW, "eu", "music-node")
        self.client.add_listener(self.client.music.voice_update_handler, "on_socket_response")
        self.client.music.add_event_hook(self.track_hook)
        self.logic = jukebox_logic.ClientLogic(client)
        print("Jukebox extension loaded")
        # flask_api.start_server()

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            print(f"Event in track_hook is being called {event}")
            guild_id: int = int(event.player.guild_id)
            await self.connect_to(guild_id, 0)

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

    @cog_slash(name="search")
    async def _search(self, ctx: SlashContext, search: str, results: int = 8, songfilter: str = "True"):
        """A search function with that you can search for Youtube Videos withing discord_bot

        Args:
            ctx (SlashContext): Object passed to communicate with discord_bot
            search (str): The search Key (Can be one or more words)
            results (int, optional): How many results should be shown. Defaults to 8.
            songfilter (str, optional): Whether to only show songs. Defaults to "True".
        """
        await ctx.defer()

        results = max(min(results, 12), 2)

        song_dictionary: dict = await jukebox_logic.search(search, results, songfilter)

        page = 1
        buttons = [
            create_button(
                style=5,
                label="Url",
                url=song_dictionary["1"]["url"]
            ),
            create_button(
                style=ButtonStyle.grey,
                label="◀",
                custom_id="search_left"
            ),
            create_button(
                style=ButtonStyle.grey,
                label="▶",
                custom_id="search_right"
            )
        ]
        ar = create_actionrow(*buttons)
        current = song_dictionary[str(page)]
        mbed = discord.Embed(
            title="`{}`".format(current["title"]),
            description="",
            colour=COLOUR
        )
        mbed.add_field(name=":eye:", value="{}".format(song_dictionary["1"]["views"]))
        mbed.add_field(name="Page:", value="{}/{}".format(page, len(song_dictionary)))
        mbed.set_thumbnail(url=song_dictionary[str(page)]["thumbnail"])
        mbed.set_footer(icon_url=ctx.author.avatar_url,
                        text=f"Searched by {ctx.author.display_name}#{ctx.author.discriminator}")
        msg: discord.Message = await ctx.send(embed=mbed, components=[ar])
        self.db.create_search(ctx.guild.id, ctx.author.id, msg.id, song_dictionary)
        await jukebox_logic.start_timer(ctx.channel.id, msg.id, 1)

    async def play_video(self, ctx: SlashContext, player: lavalink.models.DefaultPlayer, videoId: str,
                         playlist: bool = False, ytMusic: bool = False) -> bool:
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
        ytMusic: Whether to search in YtMusic or not

        """
        if ytMusic:
            results: dict = await player.node.get_tracks(f"https://music.www.youtube.com/watch?v={videoId}")
        else:
            results: dict = await player.node.get_tracks(f"https://www.youtube.com/watch?v={videoId}")

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
                            videoIds: tuple = None, ytMusic: bool = False):
        """

        This method plays a playlist either from a playlistId or from several videoIds.
        More than one video is played from a lot of functions so this method exists.

        Parameters
        ----------
        ctx: Object passed to interact with discord_bot
        player: The player that plays audio
        playlistId: The ID that youtube have that playlist as an identifier. Here used to get the videos from it. Defaults to None
        videoIds: If you want to play with this method and you don't have a playlistId put some videoIds in a tuple and pass it. Defaults to None
        ytMusic: Whether to search the videos on ytMusic or not

        """
        yt = Api()

        videos_found: int = 0

        player_state: bool = False
        if player.is_playing or player.paused:
            player_state = True

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

        async def check_url(checked_url: str) -> Tuple[str, str, str]:
            """

            A helper function to determine whether the given url is a video- or playlist-url.
            It also returns the Id to access either the playlist or the video.

            Parameters
            ----------
            checked_url: The given url that's going to be checked

            Returns
            -------
            Tuple[str, str, str]: first is the type of the link ("music"/"normal", "playlist"/"video", ID)

            """

            async def valid_url(validate_url: str) -> bool:
                """

                A function that sends a get request to the given link so you can test if it is a valid one.

                Parameters
                ----------
                validate_url: The url that should be tested

                Returns
                -------
                bool: Whether the website is callable or not

                """
                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.get(validate_url) as resp:
                            pass
                    except aiohttp.client_exceptions.InvalidURL:
                        return False
                    else:
                        return True

            async def yt_url_processing(processed_url: str) -> Tuple[str, str, str]:
                """

                Parameters
                ----------
                processed_url: The url that should be processed

                Returns
                -------
                Tuple[str, str, str]: first is the type of the link ("music"/"normal", "playlist"/"video", ID)

                """
                try:
                    playlist_url: str = checked_url.split("list=")[1]
                except IndexError:  # Url is not a playlist
                    try:
                        videoId: str = checked_url.split("watch?v=")[1]
                    except IndexError:
                        raise VideoTypeNotFound

                    if "music.youtube.com" in url:
                        return "music", "video", videoId
                    elif "youtube.com" in url:
                        return "normal", "video", videoId
                    else:
                        raise VideoTypeNotFound
                else:
                    try:
                        playlist_url: str = playlist_url.split("&")[0]
                    except IndexError:
                        pass

                    if "music.youtube.com" in url:
                        return "music", "playlist", playlist_url
                    elif "youtube.com" in url:
                        return "normal", "playlist", playlist_url
                    else:
                        raise VideoTypeNotFound

            if not await valid_url(url):
                raise InvalidURL

            if "youtube.com" in url:
                return await yt_url_processing(url)
            else:
                raise InvalidURL

        await ctx.defer()
        if ctx.author.voice is None:
            await ctx.send(
                embed=await _get_embed(mbed_type="error", content=":x: You are not connected to a Voicechannel"))
            return

        try:
            url_type: tuple = await check_url(url)
        except (InvalidURL, VideoTypeNotFound):
            await ctx.send(embed=await _get_embed("error",
                                                  ":x: Invalid Url. :white_check_mark: Supported:\n*Youtube Music playlist/video\n*Youtube playlist/video"))
            return
        print(url_type)

        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        if player is None:
            player = self.client.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        if not player.is_connected:
            await self.connect_to(ctx.guild.id, ctx.author.voice.channel.id)
            player.store("channel", ctx.author.voice.channel.id)

        channel: int = player.fetch("channel")
        if channel is None:
            await ctx.send(embed=await _get_embed("error", ":x: I could not get the channel I'm in"))
        if channel != ctx.author.voice.channel.id:
            await ctx.send(embed=await _get_embed("error", ":x: We are not in the same channel"))

        if url_type[0] == "normal" and url_type[1] == "video":
            try:
                await self.play_video(ctx, player, url_type[2])
            except VideoNotFound:
                await ctx.send(embed=await _get_embed("error", ":x: Player could not get the track"))

        elif url_type[0] == "music" and url_type[1] == "video":
            try:
                await self.play_video(ctx, player, url_type[2], ytMusic=True)
            except VideoNotFound:
                await ctx.send(embed=await _get_embed("error", ":x: Player could not get the track"))

        elif url_type[0] == "normal" and url_type[1] == "playlist":
            try:
                await self.play_playlist(ctx, player, url_type[2])
            except PlaylistNotFound:
                await ctx.send(
                    embed=await _get_embed("error", ":x: Playlist could not be processed. It might be private"))

        elif url_type[0] == "music" and url_type[1] == "playlist":
            try:
                await self.play_playlist(ctx, player, url_type[2], ytMusic=True)
            except PlaylistNotFound:
                await ctx.send(
                    embed=await _get_embed("error", ":x: Playlist could not be processed. It might be private"))

        else:
            await ctx.send(embed=await _get_embed("error", ":x: I could not determine the link-type"))

    @cog_slash(
        name="playrandom",
        description="Plays random songs ranked by relevance",
        options=[
            create_option(
                name="search",
                description="Here you give a search Term I will search for",
                option_type=3,
                required=True
            ),
            create_option(
                name="queuelength",
                description="Max songs I will randomly put in the queue",
                option_type=4,
                required=False
            ),
            create_option(
                name="songfilter",
                description="Whether only songs should be searched",
                option_type=3,
                required=False,
                choices=[
                    create_choice(
                        name="Only Songs",
                        value="True"
                    ),
                    create_choice(
                        name="Everything",
                        value="False"
                    )
                ]
            ),
            create_option(
                name="priority_level",
                description="The priority level determines how strict to search (High -> public, Low -> random)",
                option_type=3,
                required=False,
                choices=[
                    create_choice(
                        name="High",
                        value="high"
                    ),
                    create_choice(
                        name="Medium",
                        value="medium"
                    ),
                    create_choice(
                        name="Low",
                        value="low"
                    )
                ]
            )
        ]
    )
    async def _playrandom(self, ctx: SlashContext, search: str, queuelength: int = 1, songfilter: str = "True",
                          priority_level: str = "high"):
        """

        Parameters
        ----------
        ctx: Object passed to communicate with discord_bot
        search: The search Key that the bot searches for. Can be one or more words.
        queuelength: How many songs max. will be put into the queue. Defaults to 1
        songfilter: Whether to only search for songs. Defaults to "True"

        """
        await ctx.send(embed=await _get_embed("error", ":x: In Development"))
        return

        if queuelength != 1:
            queuelength = max(min(queuelength, 25), 1)

        if ctx.author.voice is None:
            await ctx.send(":x: You are not in a Voicechannel")

        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        if player is None:
            player = self.client.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        if not player.is_connected:
            await self.connect_to(ctx.guild.id, ctx.author.voice.channel.id)
            player.store("channel", ctx.author.voice.channel.id)

        channel: int = player.fetch("channel")
        if ctx.author.voice.channel.id is None:
            await ctx.send(embed=_get_embed("error", ":x: I could not get the channel I'm in"))
            return
        if channel != ctx.author.voice.channel.id:
            await ctx.send(embed=await _get_embed("error", ":x: We are not in the same channel"))
            return

        yt = Api()
        if songfilter == "True":
            yt.search(search, 1, True)
        else:
            yt.search(search, 1, False)
        if yt.thumbnail == [] or yt.title == [] or yt.url == []:
            if songfilter == "True":
                await ctx.send(
                    embed=await _get_embed("error", f":x: No songs found that are matching the keyword {search}"))
            else:
                await ctx.send(
                    embed=await _get_embed("error", f":x: No videos found that are matching the keyword {search}"))
            return

        results: dict = await player.node.get_tracks(f"ytsearch: {yt.url[0]}")
        if not results["tracks"]:
            await ctx.send(embed=await _get_embed("error",
                                                  ":x: Could not get the song you want to play. Maybe it's and old url or the video is not public"))
            return
        track = results["tracks"][0]

        player.add(requester=ctx.author.id, track=track)

        if not player.is_playing and not player.paused:
            await player.play()

            mbed = discord.Embed(
                title="Now playing",
                description=f"({yt.title[0]})[{yt.url[0]}]",
                colour=COLOUR
            )

        else:
            mbed = discord.Embed(
                title="Added to Queue",
                description=f"({yt.title[0]})[{yt.url[0]}]",
                colour=COLOUR
            )
        mbed.set_thumbnail(url=yt.thumbnail[0])
        mbed.set_footer(icon_url=ctx.author.avatar_url,
                        text=f"Requested by {ctx.author.display_name}#{ctx.author.discriminator}")
        await ctx.send(embed=mbed)
        yt.close()

    @cog_slash(name="pause")
    async def _pause(self, ctx):
        """

        Pauses the audio playing on a server

        Parameters
        ----------
        ctx: Object passed to communicate with discord_bot

        """
        if ctx.author.voice is None:
            await ctx.send(embed=await _get_embed("error", ":x: You are not connected to a Voicechannel"))
            return

        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        if player is None:
            await ctx.send(embed=await _get_embed("error", ":x: there is no player active on your server"))
            return
        if player.paused:
            await ctx.send(embed=await _get_embed("error", ":x: I'm already on pause"))
            return

        channel: int = player.fetch("channel")
        if channel is None:
            await ctx.send(embed=await _get_embed("error", ":x: Could not get the channel I'm currently in"))
            return
        if channel != ctx.author.voice.channel.id:
            await ctx.send(embed=await _get_embed("error", ":x: We are not in the same channel"))
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
            await ctx.send(embed=await _get_embed("error", ":x: You are not connected to a Voicechannel"))
            return

        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        if player is None:
            await ctx.send(embed=await _get_embed("error", ":x: There is no palyer active on your server"))
            return
        if not player.paused:
            await ctx.send(embed=await _get_embed("error", ":x: I'm not on pause"))
            return

        channel: int = player.fetch("channel")
        if channel is None:
            await ctx.send(embed=await _get_embed("error", ":x: Could not get the channel I'm currently in"))
            return
        if channel != ctx.author.voice.channel.id:
            await ctx.send(embed=await _get_embed("error", ":x: We are not in the same channel"))
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
            await ctx.send(embed=await _get_embed("error", ":x: You are not connected to a Voicechannel"))
            return

        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        if player is None:
            await ctx.send(embed=await _get_embed("error", ":x: There is no player active on your server"))
            return
        if not player.paused and not player.is_playing:
            await ctx.send(embed=await _get_embed("error", ":x: I'm not paused and I'm not playing any songs"))
            return

        channel: int = player.fetch("channel")
        if channel is None:
            await ctx.send(embed=await _get_embed("error", ":x: I could not get the channel I'm currently in"))
            return
        if channel != ctx.author.voice.channel.id:
            await ctx.send(embed=await _get_embed("error", ":x: We are not in the same channel"))
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
            await ctx.send(embed=await _get_embed("error", ":x: You are not connected to a Voicechannel"))
            return

        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        if player is None:
            await ctx.send(embed=await _get_embed("error", ":x: There is no player active on your server"))
            return
        if not player.is_playing and not player.paused:
            await ctx.send(embed=await _get_embed("error", ":x: No music is playing or being paused"))
            return

        channel: int = player.fetch("channel")
        if channel is None:
            await ctx.send(embed=await _get_embed("error", ":x: Could not get the channel I'm currently in"))
            return
        if channel != ctx.author.voice.channel.id:
            await ctx.send(embed=await _get_embed("error", ":x: You are not in the same channel as I am"))
            return

        loop_state = player.repeat
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
            await ctx.send(embed=await _get_embed("error", ":x: You are not connected to a Voicechannel"))
            return

        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        if player is None:
            await ctx.send(embed=await _get_embed("error", ":x: There is no player active on your server"))
            return
        if not player.is_playing and not player.paused:
            await ctx.send(embed=await _get_embed("error", ":x: No music is playing or being paused"))
            return

        channel: int = player.fetch("channel")
        if channel is None:
            await ctx.send(embed=await _get_embed("error", ":x: Could not get the channel I'm currently in"))
            return
        if channel != ctx.author.voice.channel.id:
            await ctx.send(embed=await _get_embed("error", ":x: You are not in the same channel as I am"))
            return

        index = max(index, 0)
        if index > len(player.queue):
            await ctx.send(embed=await _get_embed("error", ":x: This song does not exist in the queue"))
            return

        song: lavalink.models.AudioTrack = player.queue[index - 1]
        await player.skip(index - 1)
        await ctx.send(
            embed=discord.Embed(
                title=f":next_track: **Skipped** to song number `[{song.title}]({song.uri})`"
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
            await ctx.send(embed=await _get_embed("error", ":x: You are not connected to a Voicechannel"))
            return

        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        if player is None:
            await ctx.send(embed=await _get_embed("error", ":x: There is no player active on your server"))
            return
        if not player.is_playing and not player.paused:
            await ctx.send(embed=await _get_embed("error", ":x: No music is playing or being paused"))
            return

        channel: int = player.fetch("channel")
        if channel is None:
            await ctx.send(embed=await _get_embed("error", ":x: Could not get the channel I'm currently in"))
            return
        if channel != ctx.author.voice.channel.id:
            await ctx.send(embed=await _get_embed("error", ":x: You are not in the same channel as me"))
            return

        if player.repeat and mode == "True":
            await ctx.send(embed=await _get_embed("error", ":x: Already looping the current song"))
            return
        if not player.repeat and mode == "False":
            await ctx.send(embed=await _get_embed("error", ":x: Not looping the current song"))
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
            await ctx.send(embed=await _get_embed("error", ":x: You are not connected to a Voicechannel"))
            return

        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        if player is None:
            await ctx.send(embed=await _get_embed("error", ":x: There is no player active on your server"))
            return

        channel: int = player.fetch("channel")
        if channel is None:
            await ctx.send(embed=await _get_embed("error", ":x: I could not get the channel I'm in"))
            return
        if channel != ctx.author.voice.channel.id:
            await ctx.send(embed=await _get_embed("error", ":x: You are not in the same Voicechannel as I am"))
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

    @cog_slash(name="queue")
    async def _queue(self, ctx):
        def get_queue_components(component_type: int) -> list:
            """

            Help method to quickly get components for a queue object.

            Parameters
            ----------
            component_type: 1 -> left disabled; 2 -> right disabled; 3 -> nothing disabled

            Returns
            -------
            list: list of action rows that fit the queue schema

            """
            if component_type == 1:
                create_actionrow(
                    create_button(
                        style=2,
                        label="◀◀",
                        custom_id="queue_first",
                        disabled=True
                    )
                )
                return [
                    {
                        "type": 1,
                        "components": [
                            {
                                "type": 2,
                                "label": "◀◀",
                                "style": 2,
                                "custom_id": "queue_first",
                                "disabled": True
                            },
                            {
                                "type": 2,
                                "label": "◀",
                                "style": 2,
                                "custom_id": "queue_left",
                                "disabled": True
                            },
                            {
                                "type": 2,
                                "label": "▶",
                                "style": 2,
                                "custom_id": "queue_right"
                            },
                            {
                                "type": 2,
                                "label": "▶▶",
                                "style": 2,
                                "custom_id": "queue_last"
                            }
                        ]
                    }
                ]
            elif component_type == 2:
                return [
                    {
                        "type": 1,
                        "components": [
                            {
                                "type": 2,
                                "label": "◀◀",
                                "style": 2,
                                "custom_id": "queue_first"
                            },
                            {
                                "type": 2,
                                "label": "◀",
                                "style": 2,
                                "custom_id": "queue_left"
                            },
                            {
                                "type": 2,
                                "label": "▶",
                                "style": 2,
                                "custom_id": "queue_right",
                                "disabled": True
                            },
                            {
                                "type": 2,
                                "label": "▶▶",
                                "style": 2,
                                "custom_id": "queue_last",
                                "disabled": True
                            }
                        ]
                    }
                ]
            elif component_type == 3:
                return [
                    {
                        "type": 1,
                        "components": [
                            {
                                "type": 2,
                                "label": "◀◀",
                                "style": 2,
                                "custom_id": "queue_first"
                            },
                            {
                                "type": 2,
                                "label": "◀",
                                "style": 2,
                                "custom_id": "queue_left"
                            },
                            {
                                "type": 2,
                                "label": "▶",
                                "style": 2,
                                "custom_id": "queue_right"
                            },
                            {
                                "type": 2,
                                "label": "▶▶",
                                "style": 2,
                                "custom_id": "queue_last"
                            }
                        ]
                    }
                ]

        """

        Command to display the songs that are staged in the queue.

        Parameters
        ----------
        ctx: Object passed to communicate with discord

        """
        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        if player is None:
            await ctx.send(embed=await _get_embed("error", ":x: There is no active player on your server"))
            return
        if not player.is_playing and not player.paused:
            await ctx.send(embed=await _get_embed("error", ":x: I'm not playing audio or being paused"))
            return

        if not player.queue:
            # TODO: Program jukebox_logic and invoke current
            messages.send(ctx.channel.id, embed={
                "title": ":x: Only one song is playing",
                "description": "",
                "colour": Red
            })
            return

        pages = ceil(len(player.queue) / 10)
        embed = discord.Embed(
            title="Queue",
            description="",
            colour=COLOUR
        )
        if pages == 1:
            big_dict: dict = {"1": {
                "embed": {
                    "title": "Queue",
                    "description": f"__[{player.current.title}]({player.current.uri})__ | :mag_right: <@{player.current.requester}>",
                    "colour": COLOUR
                },
                "components": []
            }}
        else:
            big_dict: dict = {"1": {
                "embed": {
                    "title": "Queue",
                    "description": f"__[{player.current.title}]({player.current.uri})__ | :mag_right: <@{player.current.requester}>",
                    "colour": COLOUR,
                    "footer": {
                        "text": f"Page 1/{pages}"
                    }
                },
                "components": get_queue_components(1)
            }}

        for x in range(len(player.queue)):
            # TODO: Make Q compatible with more than 100 songs
            if x > 9:
                current_page: int = int(list(str(x))[0]) + 1  # We take the first number 10 -> 1 and increment it by one to get the current page
            else:
                current_page: int = 1
            if x % 10 == 0 and x != 0:
                if current_page == pages:
                    big_dict[str(current_page)] = {
                        "embed": {
                            "title": "Queue",
                            "description": "",
                            "colour": COLOUR,
                            "footer": {
                                "text": f"Page {current_page}/{pages}"
                            }
                        },
                        "components": get_queue_components(2)
                    }
                    continue
                else:
                    big_dict[str(current_page)] = {
                        "embed": {
                            "title": "Queue",
                            "description": "",
                            "colour": COLOUR,
                            "footer": {
                                "text": f"Page {current_page}/{pages}"
                            }
                        },
                        "components": get_queue_components(3)
                    }
                    continue
            big_dict[str(current_page)]["embed"]["description"] += f"\n\n**{x + 1}** [{player.queue[x].title}]({player.queue[x].uri}) | :mag_right: <@{player.current.requester}>"

        msg = await ctx.send("Wait a second")
        await msg.delete()
        msg_id = messages.send(ctx.channel.id, embed=big_dict["1"]["embed"], components=big_dict["1"]["components"])["id"]
        if pages != 1:
            self.db.create_queue(ctx.guild.id, int(msg_id), big_dict, 1, pages)
            await jukebox_logic.start_timer(ctx.channel.id, msg_id, 2)

    @cog_slash(name="current")
    async def _current(self, ctx: SlashContext):
        """

        Shows Information about the current song that is playing

        Parameters
        ----------
        ctx: Object passed to communicate with discord_bot

        """
        if ctx.author.voice is None:
            await ctx.send(embed=await _get_embed("error", ":x: You are not connected to a Voicechannel"))
            return

        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        if player is None:
            await ctx.send(embed=await _get_embed("error", ":x: There is no player active on your server"))
            return
        if not player.is_playing and not player.paused:
            await ctx.send(embed=await _get_embed("error", ":x: I'm not playing audio or being paused"))
            return

        channel: int = player.fetch("channel")
        if channel is None:
            await ctx.send(embed=await _get_embed("error", ":x: I could nto get the channel I'm in"))
            return
        if channel != ctx.author.voice.channel.id:
            await ctx.send(embed=await _get_embed("error", ":x: You are not in the same channel as I am"))
            return

        yt = Api()
        try:
            yt.search_video_url([player.current.uri])
        except KeyError:
            await ctx.send(embed=await _get_embed("error", ":x: Could not process the current song"))
            return

        requester: discord.Member = discord.utils.get(ctx.guild.members, id=player.current.requester)

        mbed = discord.Embed(
            title=f"`{player.current.title}`",
            description="",
            colour=COLOUR
        )
        mbed.set_thumbnail(url=yt.thumbnail[0])
        mbed.add_field(name=":eye:", value=f"`{yt.views[0]}`")

        if not yt.likes[0]:
            mbed.add_field(name=":thumbsup:", value="`-`")
            mbed.add_field(name=":thumbsdown", value="`-`")
        else:
            mbed.add_field(name=":thumbsup:", value=f"`{yt.likes[0]}`")
            mbed.add_field(name=":thumbsdown:", value=f"`{yt.dislikes[0]}`")

        if not yt.comments[0]:
            mbed.add_field(name=":speech_balloon:", value="`-`")
        else:
            mbed.add_field(name=":speech_balloon:", value=f"`{yt.comments[0]}`")

        mbed.add_field(name=":writing_hand:", value=f"`{player.current.author}`")

        if requester is None:
            mbed.add_field(name=":mag_right:", value=f"@{player.current.requester}")
        else:
            mbed.add_field(name=":mag_right:", value=f"{requester.mention}")

        mbed.add_field(name=":link:", value=f"{player.current.uri}", inline=False)
        mbed.set_footer(icon_url=ctx.author.avatar_url,
                        text=f"Searched by {ctx.author.display_name}#{ctx.author.discriminator}")
        await ctx.send(embed=mbed)
        yt.close()

    @cog_slash(name="remove")
    async def _remove(self, ctx: SlashContext, index: int):
        """

        Removes a certain track from the playlist

        Parameters
        ----------
        ctx: Object passed to communicate with discord_bot
        index: This argument determines the song that is going to be removed

        """
        await ctx.defer()

        if ctx.author.voice is None:
            await ctx.send(embed=await _get_embed("error", ":x: You are not connected to a Voicechannel"))

        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        if player is None:
            await ctx.send(embed=await _get_embed("error", ":x: Could not find a player on your server"))
            return
        if not player.is_playing and not player.paused:
            await ctx.send(embed=await _get_embed("error", ":x: I'm not playing audio or being paused"))
            return

        channel: int = player.fetch("channel")
        if channel is None:
            await ctx.send(embed=await _get_embed("error", ":x: Could not get teh channel I'm currently in"))
            return
        if channel != ctx.author.voice.channel.id:
            await ctx.send(embed=await _get_embed("error", ":x: You are not in the same Voicechannel as I am"))
            return

        if not player.queue:
            await ctx.send(
                embed=await _get_embed("error", ":x: Queue is empty so I can't remove anything from it"))
            return

        if index == 0:
            await player.skip()
            await ctx.send(embed=discord.Embed(title="",
                                               description=f":next_track: **Skipped** [{player.current.title}]({player.current.uri})",
                                               colour=discord.Colour.blue()))

        elif index - 1 > len(player.queue):
            await ctx.send(embed=await _get_embed("error", ":x: There is no track with this index"))

        else:
            track: lavalink.AudioTrack = player.queue.pop(index - 1)
            mbed = discord.Embed(
                title="",
                description=f":white_check_mark: **Removed [{track.title}]({track.uri}) from the queue.**",
                colour=discord.Colour.green()
            )
            await ctx.send(embed=mbed)

    @cog_slash(name="removedupes")
    async def _removedupes(self, ctx: SlashContext):
        """

        Removes all duplicates from the queue list

        Parameters
        ----------
        ctx: Object passed to communicate with discord_bot

        """

        def entdupe(seq: list) -> Tuple[list, int]:
            """

            A function that removes all duplicates from a list.

            Parameters
            ----------
            seq: The original list that the function should remove all duplicates from

            """
            result_tracks: list = []
            result_titles: list = []

            removed: int = 0

            for item in seq:
                if item.title not in result_titles:
                    result_tracks.append(item)
                    result_titles.append(item.title)
                else:
                    removed += 1

            return result_tracks, removed

        if ctx.author.voice is None:
            await ctx.send(embed=await _get_embed("error", ":x: You are not connected to a Voicechannel"))
            return

        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        if player is None:
            await ctx.send(embed=await _get_embed("error", ":x: Could not find a player on your server"))
            return
        if not player.is_playing and not player.paused:
            await ctx.send(embed=await _get_embed("error", ":x: I'm not playing audio or being paused"))
            return

        channel: int = player.fetch("channel")
        if channel is None:
            await ctx.send(embed=await _get_embed("error", ":x: Could not find the channel I'm in"))
            return
        if channel != ctx.author.voice.channel.id:
            await ctx.send(embed=await _get_embed("error", ":x: You are not in the same channel as I am"))
            return

        entduped_tuple: tuple = entdupe(player.queue)
        player.queue = entduped_tuple[0]
        await ctx.send(embed=await _get_embed("success", f":white_check_mark: Removed {entduped_tuple[1]}"))

    @cog_slash(name="leave")
    async def _leave(self, ctx: SlashContext):
        """

        The bot leaves the Voicechannel on the server. It also cleans up the queue and player.

        Parameters
        ----------
        ctx: Object passed to communicate with discord_bot

        """
        if ctx.author.voice is None:
            await ctx.send(embed=await _get_embed("error", ":x: You are not connected to a Voicechannel"))
            return

        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        channel: int = player.fetch("channel")
        if channel is None:
            await ctx.send(embed=await _get_embed("error", ":x: Could nto find the channel I'm in"))
            return
        if channel != ctx.author.voice.channel.id:
            await ctx.send(embed=await _get_embed("error", ":x: You are not in the same channel as I am"))
            return

        if player is not None:
            await player.stop()
        await self.connect_to(ctx.guild.id, 0)
        await ctx.send(
            embed=await _get_embed("success", ":white_check_mark: Left the Voicechannel and cleaned up"))


def setup(client):
    client.add_cog(Jukebox(client))
