from . import *


def authorize():
    url = "https://discord.com/api/v8/applications/{}/commands".format(APPLICATION_ID)

    json = {
        "name": "loop",
        "description": "Turns the loop function on or off",
        "options": [
            {
                "name": "mode",
                "description": "Specify if the loop should be on or off",
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
