from . import *


def authorize():
    url = "https://discord.com/api/v8/applications/{}/commands".format(APPLICATION_ID)

    json = {
        "name": "remove",
        "description": "Removes a song from the queue with the given index",
        "options": [
            {
                "name": "index",
                "description": "The index of the song that is going to be removed",
                "type": 4,
                "required": True
            }
        ]
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
