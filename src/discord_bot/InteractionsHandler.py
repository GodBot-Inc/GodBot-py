from asyncio import sleep
from time import time

import discord
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import (create_actionrow,
                                                   create_button)

from src.discord.DatabaseCommunication import Database
from src.discord.discord_api import messages

db = Database()

COLOUR = 0xC2842F


class EventHandler:
    @staticmethod
    async def start_timer(ctx, msg: discord.Message, msg_id: int):
        """Here we start a timer that expires after 120 seconds"""
        start = time()
        while time() - start < 300:
            """While 120 have not passed"""
            msg_json = messages.get(ctx.channel.id, msg_id)
            if msg_json == {} or msg_json is None:
                db.delete_search(msg_id)
                return
            component_id = msg_json["components"][0]["components"][1]["custom_id"]
            if component_id == "closed_search_left":
                return
            await sleep(30)  # Cooldown so we don't request the discord_bot API too often
        ar = await EventHandler.__get_actionrow("expired")
        await msg.edit(components=[ar])
        db.delete_search(msg_id)

    @staticmethod
    async def handle(ctx):
        """This function is called if an Event (Button Press) should be handled"""
        if ctx.custom_id == "search_right":
            await EventHandler._on_right(ctx)
        elif ctx.custom_id == "search_left":
            await EventHandler._on_left(ctx)

    @staticmethod
    async def __get_actionrow(tag: str, url: str=None):
        if tag == "normal":
            buttons = [
                create_button(
                    style=5,
                    label="Url",
                    url=url
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
                    style=ButtonStyle.grey,
                    label="◀",
                    disabled=True
                ),
                create_button(
                    style=ButtonStyle.grey,
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

    @staticmethod
    async def __get_embed(ctx, song_dictionary: dict, cursor: int, tag: str=None):
        """This is an exclusive function to the EventHandler"""
        if tag == "search" or tag is None:
            mbed = discord.Embed(
                title="`{}`".format(song_dictionary[str(cursor)]["title"]),
                description=":eye_in_speech_bubble: {}\n{}/{}".format(
                    song_dictionary[str(cursor)]["views"],
                    cursor,
                    len(song_dictionary)
                ),
                colour=0xC2842F
            )
            mbed.set_thumbnail(url=song_dictionary[str(cursor)]["thumbnail"])
            mbed.set_footer(icon_url=ctx.author.avatar_url, text=f"Searched by {ctx.author.display_name}#{ctx.author.discriminator}")
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
            await ctx.send(":x: You pressed a button of someone elses search!")
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
