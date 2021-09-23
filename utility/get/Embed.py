from discord import Embed
from discord import Colour


def error(msg: str):
    return Embed(
        title=":x: {}".format(msg),
        description="",
        colour=Colour.red()
    )


def success(msg: str):
    return Embed(
        title=":white_check_mark: {}".format(msg),
        description="",
        colour=Colour.green()
    )
