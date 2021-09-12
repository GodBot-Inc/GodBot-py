from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pprint import pprint
from src.discord.CONSTANTS import YT_API_KEY

"""
TODO: Choose a different structure for the YT-Api wrapper.
1. In the search_url you can pass a list. But you still send a single reqeust for
every url (You have to). But then the list makes no sense because you can just loop
it in the function it makes absolutely NO DIFFERENCE and it would be better readable.
2. The variables title etc. should be strings. But we need a replacement for search
in search the lists make sense, because you have a list of different results.
"""


class Api:
    def __init__(self):
        self.yt = build("youtube", "v3", developerKey=YT_API_KEY)
        self.title = []
        self.thumbnail = []
        self.url = []
        self.videoId = []
        self.likes = []
        self.dislikes = []
        self.comments = []
        self.views = []
        self.found = 0
        self._watch_url = "https://www.youtube.com/watch?v={}"

    def __del__(self):
        pass

    def reset_vars(self):
        self.title = []
        self.thumbnail = []
        self.url = []
        self.videoId = []
        self.likes = []
        self.dislikes = []
        self.comments = []
        self.views = []
        self.found = 0

    def search_statistics(self, videoId: int):
        request = self.yt.videos().list(
            part="statistics",
            id=videoId
        )
        try:
            response = request.execute()
        except HttpError as e:
            print(f"Could not get statistics for {videoId} Error Details {e}")
            return
        pprint(response)
        pprint(response["items"][0]["statistics"])
        raw_views = "".join(list(response["items"][0]["statistics"]["viewCount"])[::-1])
        try:
            raw_likes = "".join(list(response["items"][0]["statistics"]["likeCount"])[::-1])
            raw_dislikes = "".join(list(response["items"][0]["statistics"]["dislikeCount"])[::-1])
        except KeyError:
            pass
        else:
            self.likes.append(" ".join([raw_likes[i:i + 3][::-1] for i in range(0, len(raw_likes), 3)][::-1]))
            self.dislikes.append(" ".join([raw_dislikes[i:i + 3][::-1] for i in range(0, len(raw_dislikes), 3)][::-1]))
        try:
            raw_comments = "".join(list(response["items"][0]["statistics"]["commentCount"])[::-1])
        except KeyError:
            pass
        else:
            self.comments.append(" ".join([raw_comments[i:i + 3][::-1] for i in range(0, len(raw_comments), 3)][::-1]))
        self.views.append(" ".join([raw_views[i:i + 3][::-1] for i in range(0, len(raw_views), 3)][::-1]))

    def search(self, keyword: str, maxResults: int, only_songs: bool):
        self.reset_vars()
        self.title = []
        self.thumbnail = []
        self.url = []
        self.videoId = []
        self.views = []
        if only_songs:
            r = self.yt.search().list(
                part="snippet",
                maxResults=maxResults,
                q=keyword,
                type="video",
                videoCategoryId=10
            )
        else:
            r = self.yt.search().list(
                part="snippet",
                maxResults=maxResults,
                q=keyword,
                type="video"
            )
        response: dict = r.execute()
        self.found = len(response["items"])
        for x in range(0, len(response["items"])):
            self.title.append(response["items"][x]["snippet"]["title"])
            self.thumbnail.append(response["items"][x]["snippet"]["thumbnails"]["high"]["url"])
            self.url.append(self._watch_url.format(response["items"][x]["id"]["videoId"]))
            self.videoId.append(response["items"][x]["id"]["videoId"])
            self.search_statistics(self.videoId[x])

    def search_video_url(self, urls: list):
        self.reset_vars()
        for url in urls:
            if len(url.split("&list=")) > 1:
                print(f"The given link is a playlist {url}")
            try:
                Id = url.split("?v=")[1]
            except IndexError:
                continue
            request = self.yt.videos().list(
                part="snippet",
                maxResults=1,
                id=Id
            )
            try:
                response = request.execute()
            except HttpError as e:
                print(f"Could not proccess {url} Error Details {e}")
                return
            if not response["items"]:
                print(f"Nothing found to {url}")
                continue
            if response["items"][0]["snippet"]["liveBroadcastContent"] == "live":
                print(f"The given link {url} is a livestream")
                continue
            pprint(response)
            self.title.append(response["items"][0]["snippet"]["title"])
            self.thumbnail.append(response["items"][0]["snippet"]["thumbnails"]["high"]["url"])
            self.search_statistics(Id)

    def search_playlist_items(self, Id: str):
        self.reset_vars()
        request = self.yt.playlistItems().list(
            part="snippet",
            maxResults=25,
            playlistId=Id,
            fields="items/snippet/resourceId(videoId),items/snippet(thumbnails(high),title)"
        )

        try:
            response = request.execute()
        except HttpError as e:
            print(e)
            return

        self.found = len(response["items"])
        if self.found == 0:
            return

        for x in range(0, len(response["items"])):
            self.url.append(self._watch_url.format(response["items"][x]["snippet"]["resourceId"]["videoId"]))
            self.videoId.append(response["items"][x]["snippet"]["resourceId"]["videoId"])
            self.thumbnail.append(response["items"][x]["snippet"]["thumbnails"]["high"]["url"])
            self.title.append(response["items"][x]["snippet"]["title"])

    def close(self):
        self.yt.close()
        self.__del__()


if __name__ == "__main__":
    yt = Api()
    yt.search_playlist_items("PLKfD8K0QKDy_wOV6s5JcW-uSlCbBAx7ZK")
