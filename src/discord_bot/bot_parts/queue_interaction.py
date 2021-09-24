from . import *
from discord.ext.commands import Cog


class QueueInteraction(Cog):
    def __init__(self, client):
        self.client = client
        self.db = Database()

    @Cog.listener()
    async def on_ready(self):
        print("Queue Interactions are loaded")

    @cog_slash(name="loopqueue")
    async def _loopqueue(self, ctx: SlashContext, mode: str, smart_modifying: str = "True"):
        # TODO: Write loopqueue (save snapshot to database)
        pass

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
            await ctx.send(embed=Embed.error("You are not connected to a Voicechannel"))

        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        if player is None:
            await ctx.send(embed=Embed.error("Could not find a player on your server"))
            return
        if not player.is_playing and not player.paused:
            await ctx.send(embed=Embed.error("I'm not playing audio or being paused"))
            return

        channel: int = player.fetch("channel")
        if channel is None:
            await ctx.send(embed=Embed.error("Could not get teh channel I'm currently in"))
            return
        if channel != ctx.author.voice.channel.id:
            await ctx.send(embed=Embed.error("You are not in the same Voicechannel as I am"))
            return

        if not player.queue:
            await ctx.send(
                embed=Embed.error("Queue is empty so I can't remove anything from it"))
            return

        if index == 0:
            await player.skip()
            await ctx.send(embed=discord.Embed(title="",
                                               description=f":next_track: **Skipped** [{player.current.title}]({player.current.uri})",
                                               colour=discord.Colour.blue()))

        elif index - 1 > len(player.queue):
            await ctx.send(embed=Embed.error("There is no track with this index"))

        else:
            track: lavalink.AudioTrack = player.queue.pop(index - 1)
            mbed = discord.Embed(
                title="",
                description=f":white_check_mark: **Removed [{track.title}]({track.uri}) from the queue.**",
                colour=discord.Colour.green()
            )
            await ctx.send(embed=mbed)

    # TODO: Move command that lets you switch songs

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

            Returns
            ----------
            Tuple[list, int]

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
            await ctx.send(embed=Embed.error("You are not connected to a Voicechannel"))
            return

        player: lavalink.models.DefaultPlayer = self.client.music.player_manager.get(ctx.guild.id)
        if player is None:
            await ctx.send(embed=Embed.error("Could not find a player on your server"))
            return
        if not player.is_playing and not player.paused:
            await ctx.send(embed=Embed.error("I'm not playing audio or being paused"))
            return

        channel: int = player.fetch("channel")
        if channel is None:
            await ctx.send(embed=Embed.error("Could not find the channel I'm in"))
            return
        if channel != ctx.author.voice.channel.id:
            await ctx.send(embed=Embed.error("You are not in the same channel as I am"))
            return

        entduped_tuple: tuple = entdupe(player.queue)
        player.queue = entduped_tuple[0]
        await ctx.send(embed=Embed.success(f":white_check_mark: Removed {entduped_tuple[1]}"))


def setup(client):
    client.add_cog(QueueInteraction(client))
