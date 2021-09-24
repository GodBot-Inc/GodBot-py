from . import *


def authorize():
    url = "https://discord.com/api/v8/applications/{}/commands".format(APPLICATION_ID)

    json = {
        "name": "loopqueue",
        "description": "It takes a snapshot of the queue and loops it",
        "options": [
            {
                "name": "mode",
                "description": "Whether to loop the queue or not",
                "required": True,
                "type": 3,
                "choices": [
                    {
                        "name": "On",
                        "value": "True"
                    },
                    {
                        "name": "Off",
                        "value": "False"
                    }
                ]
            },
            {
                "name": "smart_modifying",
                "description": "Whether to modify the taken snapshot with function-calls like remove, play etc.",
                "required": False,
                "type": 3,
                "choices": [
                    {
                        "name": "On",
                        "value": "True"
                    },
                    {
                        "name": "Off",
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
