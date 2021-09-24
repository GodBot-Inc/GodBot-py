from typing import Tuple
from src.errors import *
import aiohttp


async def check_url(checked_url: str) -> Tuple[str, str, str]:
    """

    A helper function to determine whether the given url is a video- or playlist-url.
    It also returns the Id to access either the playlist or the video.

    Parameters
    ----------
    checked_url: The given url that's going to be checked

    Returns
    -------
    Tuple[str, str, str]: first is the type of the link ("music"/"normal", "playlist"/"video", ID)

    """

    async def valid_url(validate_url: str) -> bool:
        """

        A function that sends a get request to the given link so you can test if it is a valid one.


        Parameters
        ----------
        validate_url: The url that should be tested

        Returns
        -------
        bool: Whether the website is callable or not

        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(validate_url) as resp:
                    pass
            except aiohttp.client_exceptions.InvalidURL:
                return False
            else:
                return True

    async def yt_url_processing() -> Tuple[str, str]:
        """

        A function to determine the

        Parameters
        ----------

        Returns
        -------
        Tuple[str, str]: first is the type of the link ("playlist"/"video", ID)

        """
        try:
            playlistId: str = checked_url.split("list=")[1]
        except IndexError:  # Url is not a playlist
            try:
                videoId: str = checked_url.split("watch?v=")[1]
            except IndexError:
                raise VideoTypeNotFound

            if "youtube.com" in checked_url:
                return "video", videoId
            else:
                raise VideoTypeNotFound
        else:
            try:
                playlistId: str = playlistId.split("&")[0]
            except IndexError:
                pass

            if "youtube.com" in checked_url:
                return "playlist", playlistId
            else:
                raise VideoTypeNotFound

    if not await valid_url(checked_url):
        raise InvalidURL

    if "youtube.com" in checked_url:
        return await yt_url_processing()
    else:
        raise InvalidURL
