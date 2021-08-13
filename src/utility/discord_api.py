import asyncio
from pprint import pprint

from aiohttp import ClientSession

# For authorization, we use the bot token
headers = {
    "Authorization": "Bot ODQyMzg3OTY3NTEwMzE1MDA5.YJ0k7g.twiQk0Y9qCp2ZMae-NEBGwD0K1E"
}

class Api:
    @staticmethod
    async def get_message(channel_id: int, message_id: int):
        url = "https://discord.com/api/v8/channels/{}/messages/{}"
        async with ClientSession() as session:
            async with session.get(url.format(channel_id, message_id), headers=headers) as r:
                await asyncio.sleep(0.5)  # sleeps half a second to reduce the number of calls a second
                return await r.json()


if __name__ == "__main__":
    msg = asyncio.run(Api.get_message(867677864407859240, 869118811670982676))
    print(msg["components"][0]["components"][0]["custom_id"])
