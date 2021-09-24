from time import time
from src.discord_api import messages
from utility.get import ActionRows
from src.discord_bot.DatabaseCommunication import Database
from asyncio import sleep


db = Database()


async def start_timer(msg, msg_type: int) -> None:
    """

    A function that is called when a message with buttons is created.
    After 5 minutes the buttons get disabled.

    Parameters
    ----------
    msg: The message object gained from the async ctx.send method
    msg_type: 1 -> search; 2 -> queue

    Returns
    ---------
    None

    """
    start = time()
    while time() - start < 600:
        """While 10 minutes have not passed"""
        msg_json = messages.get(msg.channel.id, msg.id)
        if msg_json == {} or msg_json is None:  # If message was deleted
            db.delete_search(msg.id)
            return
        await sleep(60)  # cooldown so we don't request the discord_bot API too often

    if msg_type == 1:
        await msg.edit(
            components=ActionRows.search("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "disabled")
        )
        db.delete_search(msg.id)
    elif msg_type == 2:
        await msg.edit(
            components=ActionRows.queue("disabled")
        )
        db.delete_queue(msg.id)
