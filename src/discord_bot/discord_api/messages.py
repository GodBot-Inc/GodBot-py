from . import *
from src.discord.CONSTANTS import TOKEN


def status_code_check(response):
    if response.status_code in [400, 401, 402, 403, 405]:
        raise InvalidFormBody(response.json())
    elif response.status_code == 404:
        raise NotFound(response.json())
    elif response.status_code in [500, 501, 502, 503]:
        raise ConnectionError(response.json())
    else:
        print("Else status_code" + str(response.status_code))


def get(channel_id: int, message_id: int):
    response = requests.get(f"https://discord.com/api/v8/channels/{channel_id}/messages/{message_id}",
                            headers={"Authorization": f"Bot {TOKEN}"})
    status_code_check(response)
    return response.json()


def send(channel_id: int, content: str = None, embed: dict = None, components: dict = None):
    response = requests.post(
        f"https://discord.com/api/v8/channels/{channel_id}/messages",
        headers={"Authorization": f"Bot {TOKEN}"},
        json={"content": content, "embed": embed, "components": components}
    )
    status_code_check(response)
    return response.json()


def edit(channel_id: int, message_id: int, content: dict = None, embed: dict = None, components: dict = None):
    response = requests.patch(
        f"https://discord.com/api/v8/channels/{channel_id}/messages/{message_id}",
        headers={"Authorization": f"Bot {TOKEN}"},
        json={"content": content, "embed": embed, "components": components}
    )
    status_code_check(response)
    return response.json()


def delete(channel_id: int, message_id: int):
    response = requests.delete(
        f"https://discord.com/api/v8/channels/{channel_id}/messages/{message_id}",
        headers={"Authorization": f"Bot {TOKEN}"},
    )
    status_code_check(response)
    return response.json()
