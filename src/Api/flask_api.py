from flask import *
from flask_restful import Resource, abort, reqparse, Api
from Endpoints import play_song


def load_endpoints(api):
    play_song.setup(api)


def start_server():
    app = Flask("GodbotApi")
    api = Api(app)
    load_endpoints(api)
    app.run(debug=True)


if __name__ == "__main__":
    start_server()
