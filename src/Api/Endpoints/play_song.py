from . import *


class Play(Resource):
    #ARGS:
    play_parser = reqparse.RequestParser()
    play_parser.add_argument("applicationID", type=int, help="The application_id")
    play_parser.add_argument("track_url", type=str, help="The url from the song that should be played")
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

        if args.get("requesterID") is None:
            abort(400, error="requesterID was not specified: The DiscordID from the account that send the request")
        if not isinstance(args.get("requesterID"), int):
            abort(401, error="requesterID must be of type int")
        if args.get("applicationID") != APPLICATION_ID:
            abort(400, error="Wrong applicationID")
        if not isinstance(args.get("applicationID"), int):
            abort(401, error="The applicationID must be of type int. That is the id of the GodBot application NOT THE BOT TOKEN!")
        if args.get("track_url") is None:
            abort(400, error="The track_url was not specified: The url from the song that should be played")
        if not isinstance(args.get("track_url"), str):
            abort(401, error="The track must be a string and look similar to this: 'https://youtube.com/'")
        if args.get("guildID") is None:
            abort(400, error="The guildID was not specified: The ServerID")
        if not isinstance(args.get("guildID"), int):
            abort(401, error="The guildID must be an int not a str")
        if args.get("voiceID") is None:
            abort(400, error="The voiceID was not specified: The discordID of the Voicechannel that the song should be played in")
        if not isinstance(args.get("voiceID"), int):
            abort(401, error="The voiceID must be of type int not str")

        try:
            url_result: tuple = check_url(args.get("track_url"))
        except InvalidURL:
            abort(404, error="The given track_url is not callable from aiohttp (it is not valid)")
            return
        except VideoTypeNotFound:
            abort(404, error="The youtubeID of the given track could not be found: 'https://youtube.com/watch?v=[ID]?'")
            return

        try:
            discord_api.guild.get(args.get("guildID"))
        except NotFound:
            abort(404, error="Invalid GuildID: Discord Api could not match any guild with the ID {}".format(args.get("guildID")))
        except ConnectionError:
            abort(500, error="Discord didn't respond try to send the request later")

        if url_result[0] == "youtube":
            jukebox.play(
                "youtube",
                "https://youtube.com/watch?v={}".format()
            )


def setup(api):
    global jukebox
    jukebox = jukebox_api_logic.ClientLogic()
    api.add_resource(Play, "/play")
