from . import *


def status_code_check(response):
    if response.status_code in [400, 401, 402, 403, 405]:
        raise InvalidFormBody(response.json())
    elif response.status_code == 404:
        raise NotFound(response.json())
    elif response.status_code in [500, 501, 502, 503]:
        raise ConnectionError(response.json())


def get(guild_id: int) -> dict:
    response = requests.get("https://discord.com/api/v8/guilds/{}".format(guild_id))
    status_code_check(response)
    return response.json()
