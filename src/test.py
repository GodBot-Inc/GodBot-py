import aiohttp
from aiohttp.client_exceptions import InvalidURL
import asyncio
from pprint import pprint


async def run():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("https://music.youtube.com/playlist?list=PLKfD8K0QKDy_wOV6s5JcW-uSlCbBAx7ZK&feature=share") as resp:
                pprint(await resp.text())
                for x in range(3):
                    print()
                pprint(await resp.json())
        except InvalidURL:
            print("Invalid Url")


asyncio.run(run())
