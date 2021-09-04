import aiohttp
from aiohttp.client_exceptions import InvalidURL
import asyncio


async def nope():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                pass
        except InvalidURL:
            print("Invalid Url")


asyncio.run(run())
