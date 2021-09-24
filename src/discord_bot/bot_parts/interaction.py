from . import *
from discord.ext.commands import Cog


class Interaction(Cog):
    def __init__(self, client):
        self.client = client
        self.db = Database()

    @Cog.listener()
    async def on_ready(self):
        print("Interactions are loaded")

    @cog_slash(name="search")
    async def _search(self, ctx: SlashContext, search: str, results: int = 8, songfilter: str = "True"):
        """A search function with that you can search for Youtube Videos withing discord_bot

        Args:
            ctx (SlashContext): Object passed to communicate with discord_bot
            search (str): The search Key (Can be one or more words)
            results (int, optional): How many results should be shown. Defaults to 8.
            songfilter (str, optional): Whether to only show songs. Defaults to "True".
        """

        def get_dict():
            yt = Api()

            if songfilter == "True":
                yt.search(search, results, True)
            else:
                yt.search(search, results, False)

            song_dictionary: dict = {}
            for x in range(yt.found):
                song_dictionary[str(x + 1)] = {"title": yt.title[x], "thumbnail": yt.thumbnail[x], "url": yt.url[x],
                                               "views": yt.views[x]}
            yt.close()
            return song_dictionary

        await ctx.defer()

        results = max(min(results, 12), 2)

        try:
            song_dictionary: dict = get_dict()
        except HttpError:
            await ctx.send(embed=Embed.error("The YouTube Api didn't respond"))
            return

        mbed = discord.Embed(
            title="`{}`".format(song_dictionary.get("1")["title"]),
            description="",
            colour=COLOUR
        )
        mbed.add_field(name=":eye:", value="{}".format(song_dictionary["1"]["views"]))
        mbed.add_field(name="Page:", value="{}/{}".format(1, len(song_dictionary)))
        mbed.set_thumbnail(url=song_dictionary.get("1").get("thumbnail"))
        mbed.set_footer(icon_url=ctx.author.avatar_url,
                        text=f"Searched by {ctx.author.display_name}#{ctx.author.discriminator}")

        msg: discord.Message = await ctx.send(
            embed=mbed,
            components=ActionRows.search(song_dictionary.get("1").get("url"))
        )

        self.db.create_search(ctx.guild.id, ctx.author.id, msg.id, song_dictionary)
        await utils.start_timer(msg, 1)

    @cog_slash(name="queue")
    async def _queue(self, ctx):
        """

        Command to display the songs that are staged in the queue.

        Parameters
        ----------
        ctx: Object passed to communicate with discord

        """
        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        if player is None:
            await ctx.send(embed=Embed.error("There is no active player on your server"))
            return
        if not player.is_playing and not player.paused:
            await ctx.send(embed=Embed.error("I'm not playing audio or being paused"))
            return

        if player.current is None:
            await ctx.send(
                embed=discord.Embed(
                    title=":x: I'm currently not playing audio",
                    description="",
                    colour=discord.Colour.red()
                )
            )
            return

        if not player.queue:
            await ctx.send(
                embed=discord.Embed(
                    title="Queue",
                    description="**Now playing** __[{}]({})__ | :mag_right: <@{}>".format(player.current.title,
                                                                                          player.current.uri,
                                                                                          player.current.requester),
                    colour=COLOUR
                )
            )
            return

        pages = ceil(len(player.queue) / 10)
        descriptions: dict = {
            "1": "**Now playing** __[{}]({})__ | :mag_right: <@{}>".format(player.current.title, player.current.uri,
                                                                           player.current.requester)
        }

        for x in range(len(player.queue)):
            # TODO: Make Q compatible with more than 100 songs
            if x > 9:
                current_page: int = int(list(str(x))[
                                            0]) + 1  # We take the first number 10 -> 1 and increment it by one to get the current page
            else:
                current_page: int = 1
            if x % 10 == 0 and x != 0:
                descriptions[str(current_page)] = "**{}** [{}]({}) | :mag_right: <@{}>".format(x + 1,
                                                                                               player.queue[x].title,
                                                                                               player.queue[x].uri,
                                                                                               player.queue[
                                                                                                   x].requester)
                continue
            descriptions[str(current_page)] += "\n\n**{}** [{}]({}) | :mag_right: <@{}>".format(x + 1,
                                                                                                player.queue[x].title,
                                                                                                player.queue[x].uri,
                                                                                                player.queue[
                                                                                                    x].requester)

        if pages != 1:
            embed = discord.Embed(
                title="Queue",
                description=descriptions.get("1"),
                colour=COLOUR
            )
            embed.set_footer(text="Page 1/{}".format(pages))

            msg = await ctx.send(
                embed=embed,
                components=ActionRows.queue("left_disabled")
            )

            self.db.create_queue(ctx.guild.id, msg.id, descriptions, 1, pages)
            await utils.start_timer(msg, 2)
        else:
            await ctx.send(
                embed=discord.Embed(
                    title="Queue",
                    description=descriptions.get("1"),
                    colour=COLOUR
                )
            )

    @cog_slash(name="current")
    async def _current(self, ctx: SlashContext):
        """

        Shows Information about the current song that is playing

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
            await ctx.send(embed=Embed.error("I'm not playing audio or being paused"))
            return

        channel: int = player.fetch("channel")
        if channel is None:
            await ctx.send(embed=Embed.error("I could nto get the channel I'm in"))
            return
        if channel != ctx.author.voice.channel.id:
            await ctx.send(embed=Embed.error("You are not in the same channel as I am"))
            return

        yt = Api()
        try:
            yt.search_video_url([player.current.uri])
        except KeyError:
            await ctx.send(embed=Embed.error("Could not process the current song"))
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
        yt.close()
        await ctx.send(embed=mbed)


def setup(client):
    client.add_cog(Interaction(client))
