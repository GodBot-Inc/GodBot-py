import discord
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import (create_actionrow,
                                                   create_button)

from src.discord_bot.DatabaseCommunication import Database
from src.discord_bot.discord_api import messages
from src import jukebox_logic

db = Database()

COLOUR = 0xC2842F


def define_logic():
    global logic
    logic = jukebox_logic.ClientLogic()


define_logic()


class EventHandler:
    @staticmethod
    async def handle(ctx):
        """This function is called if an Event (Button Press) should be handled"""
        # Search
        if ctx.custom_id == "search_right":
            await EventHandler._on_right(ctx)
        elif ctx.custom_id == "search_left":
            await EventHandler._on_left(ctx)

        # Queue
        elif ctx.custom_id == "queue_first":
            await EventHandler._on_queue_first(ctx)
        elif ctx.custom_id == "queue_left":
            await EventHandler._on_queue_left(ctx)
        elif ctx.custom_id == "queue_right":
            await EventHandler._on_queue_right(ctx)
        elif ctx.custom_id == "queue_last":
            await EventHandler._on_queue_last(ctx)

    @staticmethod
    async def __get_actionrow(tag: str, url: str = None):
        # Search
        if tag == "normal":
            buttons = [
                create_button(
                    style=5,
                    label="Url",
                    url=url
                ),
                create_button(
                    style=2,
                    label="◀",
                    custom_id="search_left"
                ),
                create_button(
                    style=2,
                    label="▶",
                    custom_id="search_right"
                )
            ]
            return create_actionrow(*buttons)

        elif tag == "expired":
            buttons = [
                create_button(
                    style=5,
                    label="Expired after 5 minutes",
                    disabled=True,
                    url="https://www.youtube.com/watch?v=d1YBv2mWll0"
                ),
                create_button(
                    style=2,
                    label="◀",
                    disabled=True
                ),
                create_button(
                    style=2,
                    label="▶",
                    disabled=True
                )
            ]
            return create_actionrow(*buttons)

        elif tag == "disable":
            buttons = [
                create_button(
                    style=5,
                    label="Url",
                    disabled=True,
                ),
                create_button(
                    style=ButtonStyle.grey,
                    label="◀",
                    disabled=True,
                    custom_id="closed_search_left"
                ),
                create_button(
                    style=ButtonStyle.grey,
                    label="▶",
                    disabled=True,
                    custom_id="closed_search_right"
                )
            ]
            return create_actionrow(*buttons)

        # Queue
        elif tag == "queue_no_left":
            return [create_actionrow(
                create_button(
                    style=2,
                    label="◀◀",
                    custom_id="queue_first",
                    disabled=True
                ),
                create_button(
                    style=2,
                    label="◀",
                    custom_id="queue_left",
                    disabled=True
                ),
                create_button(
                    style=2,
                    label="▶",
                    custom_id="queue_right"
                ),
                create_button(
                    style=2,
                    label="▶▶",
                    custom_id="queue_last"
                )
            )]

        elif tag == "queue":
            return [create_actionrow(
                create_button(
                    style=2,
                    label="◀◀",
                    custom_id="queue_first"
                ),
                create_button(
                    style=2,
                    label="◀",
                    custom_id="queue_left"
                ),
                create_button(
                    style=2,
                    label="▶",
                    custom_id="queue_right"
                ),
                create_button(
                    style=2,
                    label="▶▶",
                    custom_id="queue_last"
                )
            )]

        elif tag == "queue_no_right":
            return [create_actionrow(
                create_button(
                    style=2,
                    label="◀◀",
                    custom_id="queue_first"
                ),
                create_button(
                    style=2,
                    label="◀",
                    custom_id="queue_left"
                ),
                create_button(
                    style=2,
                    label="▶",
                    custom_id="queue_right",
                    disabled=True
                ),
                create_button(
                    style=2,
                    label="▶▶",
                    custom_id="queue_last",
                    disabled=True
                )
            )]

    @staticmethod
    async def __get_embed(ctx, song_dictionary: dict, cursor: int, tag: str = None):
        """This is an exclusive function to the EventHandler"""
        if tag == "search" or tag is None:
            mbed = discord.Embed(
                title="`{}`".format(song_dictionary[str(cursor)]["title"]),
                description="",
                colour=0xC2842F
            )
            mbed.add_field(name=":eye:", value="{}".format(song_dictionary[str(cursor)]["views"]))
            mbed.add_field(name="Page:", value="{}/{}".format(cursor, len(song_dictionary)))
            mbed.set_thumbnail(url=song_dictionary[str(cursor)]["thumbnail"])
            mbed.set_footer(icon_url=ctx.author.avatar_url,
                            text=f"Searched by {ctx.author.display_name}#{ctx.author.discriminator}")
            return mbed

    @staticmethod
    async def _on_left(ctx):
        """This function should normally be called from handle, but can be called normally if you pass ctx"""
        search = db.find_search_exists(ctx.guild.id, ctx.author.id, ctx.origin_message_id)
        if not search:
            await ctx.send(":x: You pressed a button of someone elses search!")
            return
        search = db.find_search(ctx.guild.id, ctx.author.id, ctx.origin_message_id)
        if search["cursor"] == 1:
            """Here we update nothing for the user. The message stays the same. We do this so there is not Interaction failed message"""
            mbed = await EventHandler.__get_embed(ctx, search["songs"], search["cursor"])
            await ctx.edit_origin(embed=mbed)
            return
        mbed = await EventHandler.__get_embed(ctx, search["songs"], search["cursor"] - 1)
        ar = await EventHandler.__get_actionrow("normal", search["songs"][str(search["cursor"] - 1)]["url"])
        await ctx.edit_origin(embed=mbed, components=[ar])
        db.decrease_search_cursor(ctx.guild.id, ctx.author.id, ctx.origin_message_id)

    @staticmethod
    async def _on_right(ctx):
        """This function should normally be called from handle, but can be called normally if you pass ctx"""
        search = db.find_search_exists(ctx.guild.id, ctx.author.id, ctx.origin_message_id)
        if not search:
            await ctx.send(":x: You pressed a button from an other search!")
            return
        search = db.find_search(ctx.guild.id, ctx.author.id, ctx.origin_message_id)
        if list(search["songs"].keys())[-1] == str(search["cursor"]):
            """Here we update nothing for the user. The message stays the same. We do this so there is not Interaction failed message"""
            mbed = await EventHandler.__get_embed(ctx, search["songs"], search["cursor"])
            await ctx.edit_origin(embed=mbed)
            return
        mbed = await EventHandler.__get_embed(ctx, search["songs"], search["cursor"] + 1)
        ar = await EventHandler.__get_actionrow("normal", search["songs"][str(search["cursor"] + 1)]["url"])
        await ctx.edit_origin(embed=mbed, components=[ar])
        db.increase_search_cursor(ctx.guild.id, ctx.author.id, ctx.origin_message_id)

    @staticmethod
    async def _on_queue_first(ctx):
        """

        This functions skips to the first page of the queue

        Parameters
        ----------
        ctx: just a parameter

        Returns
        -------

        """
        queue: dict = db.find_queue(ctx.origin_message_id)
        embed = discord.Embed(
            title="Queue",
            description=queue.get("descriptions").get("1"),
            colour=COLOUR
        )
        embed.set_footer(text="Page 1/{}".format(queue.get("max_pages")))
        await ctx.edit_origin(
            embed=embed,
            components=await EventHandler.__get_actionrow("queue_no_left")
        )

        db.update_queue_page(ctx.origin_message_id, 1)

    @staticmethod
    async def _on_queue_left(ctx):
        """

        This function refreshes the original queue message to get one page to the left

        Parameters
        ----------
        ctx: just a parameter (again)

        Returns
        -------

        """
        queue: dict = db.find_queue(ctx.origin_message_id)

        embed = discord.Embed(
            title="Queue",
            description=queue.get("descriptions").get(str(queue.get("current_page") - 1)),
            colour=COLOUR
        )
        embed.set_footer(text="Page {}/{}".format(queue.get("current_page") - 1, queue.get("max_pages")))

        if queue.get("current_page") - 1 == 1:
            components = await EventHandler.__get_actionrow("queue_no_left")
        else:
            components = await EventHandler.__get_actionrow("queue")

        await ctx.edit_origin(
            embed=embed,
            components=components
        )

        db.update_queue_page(ctx.origin_message_id, queue.get("current_page") - 1)

    @staticmethod
    async def _on_queue_right(ctx):
        """

        This function refreshes the original queue message to get one page to the right

        Parameters
        ----------
        ctx: just a parameter (again)(again)

        Returns
        -------

        """
        queue: dict = db.find_queue(ctx.origin_message_id)

        embed = discord.Embed(
            title="Queue",
            description=queue.get("descriptions").get(str(queue.get("current_page") + 1)),
            colour=COLOUR
        )
        embed.set_footer(text="Page {}/{}".format(queue.get("current_page") + 1, queue.get("max_pages")))

        if queue.get("current_page") + 1 == queue.get("max_pages"):
            components = await EventHandler.__get_actionrow("queue_no_right")
        else:
            components = await EventHandler.__get_actionrow("queue")

        await ctx.edit_origin(
            embed=embed,
            components=components
        )

        db.update_queue_page(ctx.origin_message_id, queue.get("current_page") + 1)

    @staticmethod
    async def _on_queue_last(ctx):
        """

        This function refreshes the original queue message to get to the last page

        Parameters
        ----------
        ctx: just a parameter (again)(again)(again)

        Returns
        -------

        """
        queue: dict = db.find_queue(ctx.origin_message_id)

        embed = discord.Embed(
            title="Queue",
            description=queue.get("descriptions").get(str(queue.get("max_pages"))),
            colour=COLOUR
        )
        embed.set_footer(text="Page {}/{}".format(queue.get("max_pages"), queue.get("max_pages")))

        await ctx.edit_origin(
            embed=embed,
            components=await EventHandler.__get_actionrow("queue_no_right")
        )

        db.update_queue_page(ctx.origin_message_id, queue.get("max_pages"))
