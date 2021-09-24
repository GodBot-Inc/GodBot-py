from . import *


def authorize():
    url = "https://discord.com/api/v8/applications/{}/commands".format(APPLICATION_ID)

    json = {
        "name": "search",
        "description": "Searches the web for songs that fit your search-key",
        "options": [
            {
                "name": "search",
                "description": "Here you give a key that I will search for",
                "type": 3,
                "required": True
            },
            {
                "name": "results",
                "description": "How many videos should be shown (max. 12 min. 2)? Default is 8",
                "type": 4,
                "required": False
            },
            {
                "name": "songfilter",
                "description": "Whether only songs should be searched",
                "type": 3,
                "required": False,
                "choices": [
                    {
                        "name": "Only Songs",
                        "value": "True"
                    },
                    {
                        "name": "Everything",
                        "value": "False"
                    }
                ]
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
