import pymongo

from src.discord_bot.errors import *
import time
from src.discord_bot.CONSTANTS import USERNAME, PASSWORD


class Singleton(object):
    """An object that will only exist once, even if you initialize it multiple times"""
    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.__init__(*args, **kwds)
        return it


class Database(Singleton):
    def __init__(self, *args, **kwds):
        self.client = pymongo.MongoClient("mongodb+srv://{}:{}@cluster0.z4ax5.mongodb.net/MyFirstDatabase?retryWrites=true&w=majority".format(USERNAME, PASSWORD))
        self.db = self.client.discord
        self.servers = self.db.Servers
        self.searches = self.db.Searches
        self.queues = self.db.Queues

    def create_server(self, serverID: int, server_name: str):
        """Creates a server entry in the MongoDB Database (duplicates are impossible)"""
        count = self.servers.count_documents({"serverID": serverID})
        if count > 0:
            raise DuplicateEntry
        self.servers.insert_one({
            "serverID": serverID,
            "server_name": server_name,
            "join_date": time.strftime("%Y-%m-%d %H:%M:%S")
        })

    def create_search(self, serverID: int, authorID: int, messageID: int, song_dictionary: dict):
        self.searches.insert_one({
            "serverID": serverID,
            "authorID": authorID,
            "messageID": messageID,
            "songs": song_dictionary,
            "cursor": 1
        })

    def create_queue(self, serverID: int, messageID: int, descriptions: dict, current_page: int, max_pages: int):
        self.queues.insert_one({
            "serverID": serverID,
            "messageID": messageID,
            "descriptions": descriptions,
            "current_page": current_page,
            "max_pages": max_pages
        })

    def update_server_name(self, serverID: int, server_name: str):
        self.servers.update_one(query={"serverID": serverID}, update={"$set": {"server_name": server_name}})

    def increase_search_cursor(self, serverID: int, authorID: int, msgID: int):
        self.searches.update_one({"serverID": serverID, "authorID": authorID, "messageID": msgID}, {"$inc": {"cursor": 1}})

    def decrease_search_cursor(self, serverID: int, authorID: int, msgID: int):
        self.searches.update_one({"serverID": serverID, "authorID": authorID, "messageID": msgID}, {"$inc": {"cursor": -1}})

    def update_queue_page(self, msgID: int, page: int):
        self.queues.update_one({"messageID": msgID}, {"$set": {"current_page": page}})

    def increase_queue_page(self, msgID: int):
        self.queues.update_one({"messageID": msgID}, {"$inc": {"current_page": 1}})

    def decrease_queue_page(self, msgID: int):
        self.queues.update_one({"messageID": msgID}, {"$inc": {"current_page": -1}})

    def delete_server(self, serverID: int):
        self.servers.delete_one({"serverID": serverID})

    def delete_search(self, messageID: int):
        self.searches.delete_one({"messageID": messageID})

    def delete_queue(self, messageID: int):
        self.queues.delete_one({"messageID": messageID})

    def find_search_exists(self, serverID: int, memberID: int, messageID: int) -> bool:
        count = self.searches.count_documents({"serverID": serverID, "authorID": memberID, "messageID": messageID})
        if count > 0:
            return True
        return False

    def find_search(self, serverID: int, authorID: int, messageID: int) -> dict:
        count = self.searches.count_documents({"serverID": serverID, "authorID": authorID, "messageID": messageID})
        if count == 0:
            raise NoEntriesFound
        search = self.searches.find_one({"serverID": serverID, "authorID": authorID, "messageID": messageID})
        return search

    def find_queue(self, msgID: int) -> int:
        count = self.queues.count_documents({"messageID": msgID})
        if count == 0:
            raise NoEntriesFound
        return self.queues.find_one({"messageID": msgID})

    def clear_server(self, serverID: int):
        self.servers.delete_one({"serverID": serverID})
        self.searches.delete_many({"serverID": serverID})
        self.queues.delete_many({"serverID": serverID})


if __name__ == "__main__":
    db = Database()
