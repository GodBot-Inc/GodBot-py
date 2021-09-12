import os

import discord
from discord.ext import commands
from discord.utils import get
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option

from CONSTANTS import TOKEN
from src.discord.ButtonHandler import EventHandler
from src.discord.DatabaseCommunication import Database

# Windows: go into systemvariables and add variable named PYTHONPATH with path to src
# MacOS: `nano ~/.bash_profile` add line `export PYTHONPATH="directory_to_src"`
# Linux: `nano ~/.bashrc` add line `export PYTHONPATH="directory_to_src"`

"""Init variables needed for the bot to work"""
intents = discord.Intents().all()
client = commands.Bot(command_prefix=".", intents=intents)
slash = SlashCommand(client)
client.remove_command("help")
db = Database()


@client.check
async def globally_block_dms(ctx):
    return ctx.guild is not None


async def check_muted():
    while True:
        pass


@client.event
async def on_ready():
    """This gets triggered when the bot is started"""
    print("main is ready")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="/help"),
                                 status=discord.Status.online)


@client.event
async def on_component(ctx):
    """
    This gets triggered whenever an interaction is triggered (mostly button presses).
    Then it passes the ctx parameter to the methos handle from EventHandler which handles the interaction.
    """
    await EventHandler.handle(ctx)


@client.event
async def on_guild_join(guild):
    """Here we save everything related to a server into the database"""
    db.create_server(guild.id, guild.name)


@client.event
async def on_guild_remove(server):
    """Here we remove everything related to the server from the database"""
    db.clear_server(server.id)


@client.event
async def on_guild_update(before, after):
    """
    This method is called when the afk channel, the afk duration changes or the server name changes
    But the server name is the only thing we care about
    """
    if before.name != after.name:
        db.update_server_name(after.id, after.name)


@client.event
async def on_member_join(member):
    """If a new user joins we check if he was imprisoned. If so, we imprison him again but nicely :D"""
    imprisoned: bool = db.find_is_imprisoned(member.guild.id, member.id)
    if imprisoned:  # if user left to escape the prison (what a noob)
        for role in member.guild.roles:
            if role.name == "Prisoner":
                member.add_roles(role)
                break
        overwrites = {
            member.guild.default_role: discord.PermissionOverwrite(connect=False, manage_channels=False),
            member.guild.me: discord.PermissionOverwrite(manage_channels=True, connect=True),
            member: discord.PermissionOverwrite(
                connect=True,
                speak=True,
                stream=True
            )
        }
        prison_exists = False
        for category in member.guild.categories:
            if category.name == "Prisons":
                prison_exists = True
        if not prison_exists:
            category = member.guild.create_category(name="Prisons")
        else:
            category = get(member.guild.categories, name="Prisons")
            if category is None:
                return
        await member.guild.create_voice_channel(f"{member.display_name}'s Cell", category=category,
                                                overwrites=overwrites)
    try:
        channel = await member.create_dm()
        if imprisoned:
            mbed = discord.Embed(
                title="Welcome!",
                description="Welcome to {}. You are still imprisoned btw".format(member.guild.name),
                colour=discord.Colour.blue()
            )
        else:
            mbed = discord.Embed(
                title="Welcome!",
                description="Welcome to {}.".format(member.guild.name),
                colour=discord.Colour.blue()
            )
        await channel.send(embed=mbed)
    except discord.HTTPException:
        pass


@client.event
async def on_member_remove(member):
    """idk"""
    pass


@client.command()
async def ping(ctx):
    await ctx.send(f"{round(client.latency, 1)}")


@slash.slash(
    name="invitelink",
    description="get an invitelink to the server",
    options=[
        create_option(
            name="duration",
            description="This defines the duration of the invitelink (in minutes)",
            required=True,
            option_type=4
        )
    ]
)
async def invitelink(ctx, duration: int):
    """Sends an invitelink with the given duration to the server"""
    if duration > 120:
        mbed = discord.Embed(
            title="Failed",
            description="The duration cannot be longer than 120 minutes",
            colour=discord.Colour.red()
        )
        await ctx.send(embed=mbed)
        return
    try:
        link = await ctx.channel.create_invite(max_age=300)
    except discord.NotFound:
        mbed = discord.Embed(
            title="Failed",
            description="Please chose an other channel for the invite",
            colour=discord.Colour.red()
        )
        await ctx.send(embed=mbed)
        return
    except discord.HTTPException:
        mbed = discord.Embed(
            title="Failed",
            description="I could not create an instant invite link to the server",
            colour=discord.Colour.red()
        )
        await ctx.send(embed=mbed)
        return
    mbed = discord.Embed(
        title="Success",
        description=f"Here is your invite link: {link}",
        colour=discord.Colour.green()
    )
    await ctx.send(embed=mbed)


# @slash.slash(
#     name="enable",
#     description="Enable a part of the bot",
#     options=[
#         create_option(
#             name="part_name",
#             description="Give the part you want to enable",
#             required=True,
#             option_type=3,
#             choices=[
#                 create_choice(
#                     name="Jukebox",
#                     value="jukebox"
#                 ),
#                 create_choice(
#                     name="Moderation",
#                     value="moderation"
#                 ),
#                 create_choice(
#                     name="prison",
#                     value="prison"
#                 ),
#                 create_choice(
#                     name="Private Rooms",
#                     value="privaterooms"
#                 )
#             ]
#         )
#     ]
# )
# async def enable(ctx, part_name: str):
#     """
#     Enables a part of the bot.
#     The bot is split up in parts. You can see them in the bot_parts folder.
#     You can enable and disable specific parts of the bot so you can basically configure it at your own will which is pretty sick.
#     """
#     if not ctx.author.guild_permissions.administrator:
#         mbed = discord.Embed(
#             title="Failed",
#             description="You do not have administrator privileges",
#             colour=discord.Colour.red()
#         )
#         await ctx.send(embed=mbed)
#         return
#     try:
#         client.load_extension(f"bot_parts.{part_name}")
#         mbed = discord.Embed(
#             title="Success",
#             description=f"{part_name} was successfully activated",
#             colour=discord.Colour.green()
#         )
#         await ctx.send(embed=mbed)
#     except:
#         mbed = discord.Embed(
#             title="Failed",
#             description=f"{part_name} could not be activated. It might already be",
#             colour=discord.Colour.red()
#         )
#         await ctx.send(embed=mbed)
#
#
# async def _remove_all_prisons(ctx):
#     """
#     This is a help_method for the disable command.
#     If the prison part is unloaded/disabled every prison entry gets deleted from the database.
#     """
#     prison_ids: list = db.find_prison_ids(ctx.guild.id)
#     if prison_ids == []:
#         return
#     error_list = []
#     for prison in prison_ids:
#         prison_channel = get(ctx.guild.channels, id=prison)
#         if prison_channel is None:
#             continue
#         try:
#             prison_channel.delete()
#         except discord.Forbidden:
#             error_list.append(f":x: I have not the permission to delete the channel {prison_channel.mention}")
#         except discord.NotFound:
#             error_list.append(f":x: I could not find the channel {prison_channel.mention} so I could not delete it")
#         except discord.HTTPException:
#             error_list.append(f":x: I could not delete the channel {prison_channel.mention}")
#     if error_list == []:
#         return
#     await ctx.send("{}".format("\n".join(error_list)))
#
#
# async def remove_all_privaterooms(ctx):
#     pass
#
#
# @slash.slash(
#     name="disable",
#     description="Disables a part of the bot",
#     options=[
#         create_option(
#             name="part_name",
#             description="Give the part you want to disable",
#             required=True,
#             option_type=3,
#             choices=[
#                 create_choice(
#                     name="Jukebox",
#                     value="jukebox"
#                 ),
#                 create_choice(
#                     name="Moderation",
#                     value="moderation"
#                 ),
#                 create_choice(
#                     name="prison",
#                     value="prison"
#                 ),
#                 create_choice(
#                     name="Private Rooms",
#                     value="privaterooms"
#                 )
#             ]
#         )
#     ]
# )
# async def disable(ctx, part_name: str):
#     """
#     Disables a part of the bot.
#     For an explanation look at enable.
#     """
#     if not ctx.author.guild_permissions.administrator:
#         mbed = discord.Embed(
#             title="Failed",
#             description="You do not have administrator privileges",
#             colour=discord.Colour.red()
#         )
#         await ctx.send(embed=mbed)
#         return
#     try:
#         client.unload_extension(f"bot_parts.{part_name}")
#     except:
#         mbed = discord.Embed(
#             title="Failed",
#             description=f"{part_name} could not be deactivated. It might already be",
#             colour=discord.Colour.red()
#         )
#         await ctx.send(embed=mbed)
#         return
#     mbed = discord.Embed(
#         title="Success",
#         description=f"{part_name} was successfully deactivated",
#         colour=discord.Colour.green()
#     )
#     await ctx.send(embed=mbed)
#     if part_name == "prison":
#         asyncio.gather(_remove_all_prisons(ctx))
#         db.clear_prisons(ctx.guild.id)


"""Loads all cogs"""
for file in os.listdir("bot_parts"):
    if file.endswith(".py"):
        client.load_extension(f"bot_parts.{file[:-3]}")

if __name__ == "__main__":
    try:
        client.run(TOKEN)
    except KeyboardInterrupt:
        client.close()
