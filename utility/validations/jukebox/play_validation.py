from . import *


def authorize():
    url = "https://discord.com/api/v8/applications/{}/commands".format(APPLICATION_ID)

    json = {
        "name": "play",
        "description": "Plays the song given with the url",
        "options": [
            {
                "name": "url",
                "description": "Url of a song (Playlists are not supported yet)",
                "type": 3,
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
