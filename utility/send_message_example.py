button_example = {
    "components": [  # Components of the message (Action Row, Dropwdown menu)
        {
            "type": 1,  # Action Row can contain up to 5 Buttons
            "components": [
                {
                    "type": 2,  # Button
                    "style": 2,  # secondary button
                    "label": "Hello",  # Message that is shown on the button
                    "custom_id": "Moin",  # Custom id to recognize the button
                    "disabled": False  # Whether the button is disabled or not
                }
            ]
        }
    ]
}

msg_embed_example = {
    "embed": {
        "title": "Hello I'm a title",  # Shows up at the top of the embed (bigger than description)
        "description": "I'm describing things :D",  # Description shows up in the embed (smaller than title)
        "colour": 0x111111  # Hash Colour
    }
}

from src.discord_api import messages

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
