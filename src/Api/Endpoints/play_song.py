from . import *


async def check_url(url: str) -> Tuple[str, str, str]:
    """

    A helper function to determine whether the given url is a video- or playlist-url.
    It also returns the Id to access either the playlist or the video.

    Parameters
    ----------
    url: The given url that's going to be checked

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

    async def yt_url_processing(processed_url: str) -> Tuple[str, str, str]:
        """

        Parameters
        ----------
        processed_url: The url that should be processed

        Returns
        -------
        Tuple[str, str, str]: first is the type of the link ("music"/"normal", "playlist"/"video", ID)

        """
        try:
            playlist_url: str = url.split("list=")[1]
        except IndexError:  # Url is not a playlist
            try:
                videoId: str = url.split("watch?v=")[1]
            except IndexError:
                raise VideoTypeNotFound

            if "music.youtube.com" in url:
                return "music", "video", videoId
            elif "youtube.com" in url:
                return "normal", "video", videoId
            else:
                raise VideoTypeNotFound
        else:
            try:
                playlist_url: str = playlist_url.split("&")[0]
            except IndexError:
                pass

            if "music.youtube.com" in url:
                return "music", "playlist", playlist_url
            elif "youtube.com" in url:
                return "normal", "playlist", playlist_url
            else:
                raise VideoTypeNotFound

    if not await valid_url(url):
        raise InvalidURL

    if "youtube.com" in url:
        return await yt_url_processing(url)
    else:
        raise InvalidURL


class Play(Resource):
    #ARGS:
    play_parser = reqparse.RequestParser()
    play_parser.add_argument("applicationID", type=int, help="The application_id")
    play_parser.add_argument("track", type=str, help="The uri from the song that should be played")
    play_parser.add_argument("guildID", type=int, help="The guild in that the song should be played")
    play_parser.add_argument("voiceID", type=int, help="The Voicechannel in that the song should be played")
    play_parser.add_argument("requesterID", type=int, help="The ID of the member that wants to play the song")

    def post(self):
        """

        Called if a song should be played form a uri

        Returns
        400: Argument not given
        401: Wrong parameter type
        402: Authorization failed

        """
        args = self.play_parser.parse_args()

        if args["requesterID"] is None:
            abort(400, error="applicationID was not specified")
        if args["applicationID"] != APPLICATION_ID:
            abort(402, error="Wrong applicationID")
        if not isinstance(args["applicationID"], int):
            abort(401, error="The applicationID must be of type int")
        if args["track"] is None:
            abort(400, error="The track was not specified")
        if not isinstance(args["track"], str):
            abort(401, error="The track must be a string")
        if args["guildID"] is None:
            abort(400, error="The guildID was not specified")
        if not isinstance(args["guildID"], int):
            abort(401, error="The guildID must be an int")
        if args["voiceID"] is None:
            abort(400, error="The voiceID was not specified")
        if not isinstance(args["voiceID"], int):
            abort(401, error="The voiceID must be of type int")
        if args["requesterID"] is None:
            abort(400, error="The requesterID was not specified")

        return {
            "application_id": args["application_id"],
            "track_uri": args["track_uri"],
            "guild_id": args["guild_id"],
            "voice_id": args["voice_id"],
            "requester_id": args["requester_id"]
        }


def setup(api):
    global jukebox
    jukebox = jukebox_logic.ClientLogic()
    api.add_resource(Play, "/play")
