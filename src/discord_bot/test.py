# from discord_api import messages
# from pprint import pprint
#
# description_string: str = "**Now playing** - __[ACDC - Thunderstruck](https://music.youtube.com/)__ | `3:40` | :mag_right: <@430764134519275531>"
#
# for x in range(10):
#     description_string += f"\n\n**{x + 1}** - [ACDC - Thunderstruck](https://music.youtube.com/) | `3:40` | :mag_right: <@430764134519275531>"
#
# pprint(messages.send(867677864407859240,
#                      embed={
#                          "title": "Queue",
#                          "description": description_string,
#                          "colour": 12747823,
#                          "footer": {
#                              "text": ":clock12:`37:40`"
#                          }
#                      },
#                      components=[
#                          {
#                              "type": 1,
#                              "components": [
#                                  {
#                                      "type": 2,
#                                      "label": "◀◀",
#                                      "style": 2,
#                                      "custom_id": "queue_first",
#                                      "disabled": False
#                                  },
#                                  {
#                                      "type": 2,
#                                      "label": "◀",
#                                      "style": 2,
#                                      "custom_id": "queue_skip_left",
#                                      "disabled": False
#                                  },
#                                  {
#                                      "type": 2,
#                                      "label": "▶",
#                                      "style": 2,
#                                      "custom_id": "queue_skip_right",
#                                      "disabled": False
#                                  },
#                                  {
#                                      "type": 2,
#                                      "label": "▶▶",
#                                      "style": 2,
#                                      "custom_id": "queue_last",
#                                      "disabled": False
#                                  }
#                              ]
#                          }
#                      ])
#        )
