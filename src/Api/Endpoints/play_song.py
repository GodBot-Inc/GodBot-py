from . import *


class Play(Resource):
    #ARGS:
    play_parser = reqparse.RequestParser()
    play_parser.add_argument("bot_token", type=int, help="The token of the bot for authorization")
    play_parser.add_argument("track_uri", type=str, help="The uri from the song that should be played")
    play_parser.add_argument("guild_id", type=int, help="The guild in that the song should be played")
    play_parser.add_argument("voice_id", type=int, help="The Voicechannel in that the song should be played")
    play_parser.add_argument("reqeuster_id", type=int, help="The ID of the member that wants to play the song")

    def post(self):
        """

        Called if a song should be played form a uri

        Returns
        400: Not Authorized
        401: No track_uri given

        """
        args = self.play_parser.parse_args()
        if args["bot_token"] != TOKEN:
            return {
                "status_code": 400,
                "Error_details": "Not Authorized"
            }
        if args["track_uri"] is None:
            return {
                "status_code": 401,
                "Error_details": "No track_uri given"
            }
        jukebox.play(args["track_uri"])


def setup(api):
    global jukebox
    jukebox = jukebox_logic.ClientLogic()
    api.add_resource(Play, "/play")
