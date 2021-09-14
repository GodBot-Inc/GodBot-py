from . import *


def status_code_check(response):
    if response.status_code in [400, 401, 402, 403, 405]:
        raise InvalidFormBody(response.json())
    elif response.status_code == 404:
        raise NotFound(response.json())
    elif response.status_code in [500, 501, 502, 503]:
        raise ConnectionError(response.json())


def get(channel_id: int, message_id: int):
    response = requests.get(f"https://discord.com/api/v8/channels/{channel_id}/messages/{message_id}",
                            headers={"Authorization": f"Bot {TOKEN}"})
    status_code_check(response)
    try:
        return response.json()
    except TypeError:
        return response


def send(channel_id: int, content: str = None, embed: dict = None, components: dict = None):
    response = requests.post(
        f"https://discord.com/api/v8/channels/{channel_id}/messages",
        headers={"Authorization": f"Bot {TOKEN}"},
        json={"content": content, "embed": embed, "components": components}
    )
    status_code_check(response)
    try:
        return response.json()
    except TypeError:
        return response


def edit(channel_id: int, message_id: int, content: dict = None, embed: dict = None, components: dict = None):
    json_dict: dict = {}
    if content is None and embed is None and components is None:
        return
    elif content is None and embed is None and components is not None:
        json_dict = {
            "content": "",
            "components": components
        }
    elif content is not None and embed is None and components is not None:
        json_dict = {
            "embed"
        }
    elif content is None and embed is not None and components is not None:
        json_dict = {
            "embed": embed,
            "components": components
        }
    elif content is not None and embed is None and components is None:
        json_dict = {
            "content": content
        }
    elif content is None and embed is not None and components is None:
        json_dict = {
            "embed": embed
        }
    elif content is not None and embed is not None and components is None:
        json_dict = {
            "content": content,
            "embed": embed
        }
    elif content is not None and embed is not None and components is not None:
        json_dict = {
            "content": content,
            "embed": embed,
            "components": components
        }

    response = requests.patch(
        f"https://discord.com/api/v8/channels/{channel_id}/messages/{message_id}",
        headers={"Authorization": f"Bot {TOKEN}"},
        json=json_dict
    )
    status_code_check(response)
    try:
        return response.json()
    except TypeError:
        return response


def delete(channel_id: int, message_id: int):
    response = requests.delete(
        f"https://discord.com/api/v8/channels/{channel_id}/messages/{message_id}",
        headers={"Authorization": f"Bot {TOKEN}"},
    )
    status_code_check(response)
    try:
        return response.json()
    except TypeError:
        return response
