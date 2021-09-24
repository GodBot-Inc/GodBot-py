import discord
from src.CONSTANTS import *
import sys
# Put the path to your cloned repository here:
sys.path.insert(0, REPOSITORY_PATH)

from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option

from src.discord_bot.InteractionsHandler import EventHandler
from src.discord_bot.DatabaseCommunication import Database
from data.custom_lavalink import lavalink
from src.Api import jukebox_api_logic

# Windows: go into systemvariables and add variable named PYTHONPATH with path to src
# MacOS: `nano ~/.bash_profile` add line `export PYTHONPATH="directory_to_src"`
# Linux: `nano ~/.bashrc` add line `export PYTHONPATH="directory_to_src"`

"""Init variables needed for the bot to work"""
intents = discord.Intents().all()
client = commands.Bot(command_prefix=".", intents=intents)
slash = SlashCommand(client)
client.remove_command("help")
db = Database()


#Lavalink Definition
async def track_hook(event):
    if isinstance(event, lavalink.events.QueueEndEvent):
        print(f"Event in track_hook is being called {event}")
        guild_id: int = int(event.player.guild_id)
        await connect_to(guild_id, 0)


async def connect_to(guild_id: int, channel_id: int):
    ws = client._connection._get_websocket(guild_id)
    if channel_id == 0:
        await ws.voice_state(str(guild_id), None)
        return
    await ws.voice_state(str(guild_id), str(channel_id))


client.music = lavalink.Client(APPLICATION_ID)
client.music.add_node(LAVALINK_IP, LAVALINK_PORT, LAVALINK_PW, "eu", "music-node")
client.add_listener(client.music.voice_update_handler, "on_socket_response")
client.music.add_event_hook(track_hook)
logic = jukebox_api_logic.ClientLogic(client)


@client.check
async def globally_block_dms(ctx):
    return ctx.guild is not None


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


"""Loads all cogs"""
# for file in os.listdir("bot_parts"):
#     if file.endswith(".py") and file != "__init__.py":
#         client.load_extension(f"bot_parts.{file[:-3]}")
# client.load_extension("src.Api.flask_api")
client.load_extension("bot_parts.jukebox")


if __name__ == "__main__":
    try:
        client.run(TOKEN)
    except KeyboardInterrupt:
        client.close()
