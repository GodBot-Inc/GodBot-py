from discord_api import messages

print(messages.send(867677864407859240,
                    content="I'm content",
                    embed={
                        "title": "I'm a title",
                        "description": "I'm a description",
                        "colour": 0x11111
                    },
                    components=[
                        {
                            "type": 1,
                            "components": [
                                {
                                    "type": 2,
                                    "label": "Click me and nothing will happen",
                                    "style": 1,
                                    "custom_id": "click_one"
                                }
                            ]
                        }
                    ]))
