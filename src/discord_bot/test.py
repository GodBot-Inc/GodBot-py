from discord_api import messages
from pprint import pprint

messages.send(
    channel_id=867677864407859240,
    content="test",
    components=[
        {
            "type": 1,
            "components": [
                {
                    "type": 2,
                    "style": 5,
                    "label": "Url",
                    "url": None
                }
            ]
        }
    ]
)
