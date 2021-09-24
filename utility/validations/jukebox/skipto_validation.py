from . import *


def authorize():
    url = "https://discord.com/api/v8/applications/{}/commands".format(APPLICATION_ID)

    json = {
        "name": "skipto",
        "description": "Skips to a specific song in the queue",
        "options": [
            {
                "name": "index",
                "description": "The index of a song that you want to skip to",
                "type": 4,
                "required": True
            }
        ]
    }

    # For authorization, you can use either your bot token
    headers = {
        "Authorization": "Bot {}".format(TOKEN)
    }

    r = requests.post(url, headers=headers, json=json)
    try:
        print(r.json())
    except JSONDecodeError:
        print(r)
