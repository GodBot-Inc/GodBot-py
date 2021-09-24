from . import *


def authorize():
    url = "https://discord.com/api/v8/applications/{}/commands".format(APPLICATION_ID)

    json = {
        "name": "removedupes",
        "description": "Removes all duplicates from the queue"
    }

    # For authorization, you can use either your bot token
    headers = {
        "Authorization": "Bot {}".format(TOKEN)
    }

    r = requests.post(url=url, headers=headers, json=json)
    try:
        print(r.json())
    except JSONDecodeError:
        print(r)
