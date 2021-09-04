import pymongo
from src.utility.errors import DuplicateEntry
import time
from src.CONSTANTS import USERNAME, PASSWORD
from random import randint
import pprint


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
        self.members = self.db.Members
        self.prisons = self.db.Prisons
        self.searches = self.db.Searches

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

    def create_prison(self, serverID: int, memberID: int, member_name: str, member_discriminator: int, prisonID: int, roles: list, reason: str):
        """Creates a prison entry in the MongoDB Database (duplicates are impossible)"""
        count = self.prisons.count_documents({"serverID": serverID, "memberID": memberID})
        if count > 0:
            raise DuplicateEntry
        self.prisons.insert_one({
            "serverID": serverID,
            "memberID": memberID,
            "member_name": member_name,
            "member_discriminator": member_discriminator,
            "prisonID": prisonID,
            "roles": roles,
            "reason": reason,
            "creation_date": time.strftime("%d.%m.%Y %H:%M:%S")
        })

    def create_search(self, serverID: int, authorID: int, messageID: int, song_dictionary: dict):
        pprint.pprint(song_dictionary)
        self.searches.insert_one({
            "serverID": serverID,
            "authorID": authorID,
            "messageID": messageID,
            "songs": song_dictionary,
            "cursor": 1
        })

    def update_server_name(self, serverID: int, server_name: str):
        self.servers.update_one(query={"serverID": serverID}, update={"$set": {"server_name": server_name}})

    def increase_search_cursor(self, serverID: int, authorID: int, msgID: int):
        self.searches.update_one({"serverID": serverID, "authorID": authorID, "messageID": msgID}, {"$inc": {"cursor": 1}})

    def decrease_search_cursor(self, serverID: int, authorID: int, msgID: int):
        self.searches.update_one({"serverID": serverID, "authorID": authorID, "messageID": msgID}, {"$inc": {"cursor": -1}})

    def delete_server(self, serverID: int):
        self.servers.delete_one({"serverID": serverID})

    def delete_prison(self, serverID: int, memberID: int):
        self.prisons.delete_one({"serverID": serverID, "memberID": memberID})

    def delete_search(self, serverID: int, authorID: int, messageID: int):
        self.searches.delete_one({"serverID": serverID, "authorID": authorID, "messageID": messageID})

    def find_search_exists(self, serverID: int, memberID: int, messageID: int) -> bool:
        count = self.searches.count_documents({"serverID": serverID, "authorID": memberID, "messageID": messageID})
        if count > 0:
            return True
        return False

    def find_search(self, serverID: int, authorID: int, messageID: int):
        count = self.searches.count_documents({"serverID": serverID, "authorID": authorID, "messageID": messageID})
        if count == 0:
            return {}
        search = self.searches.find_one({"serverID": serverID, "authorID": authorID, "messageID": messageID})
        return search

    def find_prisons(self, serverID: int) -> list:  # For /checkprison
        count = self.prisons.count_documents({"serverID": serverID})
        if count == 0:
            return []
        prisons = self.prisons.find({"serverID": serverID})
        return_list = []
        for prison in prisons:
            try:
                name = prison["member_name"] + "#" + str(prison["member_discriminator"])
                return_list.append("{} | {} | {}".format(name, prison["creation_date"], prison["reason"]))
            except KeyError:
                continue
        return return_list

    def find_prison_ids(self, serverID: int):
        count = self.prisons.count_documents({"serverID": serverID})
        if count == 0:
            return []
        prisons = self.prisons.find({"serverID": serverID})
        return_list = []
        for prison in prisons:
            try:
                return_list.append(prison["prisonID"])
            except KeyError:
                continue
        return return_list

    def find_is_imprisoned(self, serverID: int, memberID: int) -> bool:
        count = self.prisons.count_documents({"serverID": serverID, "memberID": memberID})
        if count == 0:
            return False
        return True

    def find_prison_id(self, serverID: int, memberID: int) -> int:
        count = self.prisons.count_documents({"serverID": serverID})
        if count == 0:
            return 0
        prison = self.prisons.find_one({"serverID": serverID, "memberID": memberID})
        try:
            return prison["prisonID"]
        except KeyError:
            return 0

    def find_prisoner_roles(self, serverID: int, memberID: int) -> list:
        count = self.prisons.count_documents({"serverID": serverID, "memberID": memberID})
        if count == 0:
            return []
        result = self.prisons.find_one({"serverID": serverID, "memberID": memberID})
        try:
            return result["roles"]
        except KeyError:
            return []

    def clear_server(self, serverID: int):
        self.servers.delete_one({"serverID": serverID})
        self.searches.delete_many({"serverID": serverID})
        self.prisons.delete_many({"serverID": serverID})

    def clear_prisons(self, serverID: int):
        self.prisons.delete_many({"serverID": serverID})


if __name__ == "__main__":
    db = Database()
