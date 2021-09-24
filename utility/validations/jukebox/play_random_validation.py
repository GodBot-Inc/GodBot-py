from . import *


def authorize():
    url = "https://discord.com/api/v8/applications/{}/commands".format(APPLICATION_ID)

    json = {
        "name": "playrandom",
        "description": "Plays a random song that matches your keyword",
        "options": [
            {
                "name": "search",
                "description": "Here you give a search term I will search for",
                "type": 3,
                "required": True
            },
            {
                "name": "queuelength",
                "description": "Max songs I will randomly put in the queue",
                "type": 4,
                "required": False
            },
            {
                "name": "songfilter",
                "description": "Whether only songs should be played",
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
            },
            {
                "name": "priority_level",
                "description": "The priority level determines how strict to search (High -> most public, Low -> random)",
                "type": 3,
                "required": False,
                "choices": [
                    {
                        "name": "High",
                        "value": "high"
                    },
                    {
                        "name": "Medium",
                        "value": "medium"
                    },
                    {
                        "name": "Low",
                        "value": "low"
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
