class DatabaseError(Exception):
    """Gets raised if an error occurs in the database"""
    pass


class DuplicateEntry(DatabaseError):
    """Gets raised if a duplicate exists in the database"""
    pass


class NoEntriesFound(DatabaseError):
    """Gets raised if a find request can't find any entries"""
    pass


class DiscordApiError(Exception):
    """Get's raised in src.discord_api if something goes wrong"""
    pass


class InvalidFormBody(DiscordApiError):
    """Get's raised if a request could not be send and it's the programmers fault"""
    pass


class ConnectionError(DiscordApiError):
    """Get's raised if the discord_bot Api has problems"""
    pass


class NotFound(DiscordApiError):
    """Get's raised if the requests library didn't find anything"""
    pass


class GodBotError(Exception):
    """Any Error raised from the GodBot Program will inherit from this class. You could call it the God Error :D"""
    pass


class VideoTypeNotFound(GodBotError):
    """Gets raised when a video type could not be gotten"""
    pass


class InvalidURL(GodBotError):
    """Gets raised if the godbot finds an invalid url was passed"""
    pass


class PlayerChannelNotFound(GodBotError):
    """Get's raised if the player could not fetch it's channel"""
    pass


class YTApiError(Exception):
    """Raised if something went wrong with the youtube API"""
    pass


class VideoNotFound(YTApiError):
    """Gets raised when a video from the play_playlist function is not found (automatically handled)"""
    pass


class PlaylistNotFound(YTApiError):
    """Raised when a requested playlist is not found"""
    pass


class ApiError(Exception):
    """An error that the Api 'receivs'"""
    pass


class InvalidApiUrl(ApiError):
    """Get's raised when a url passed from the api is not valid"""
    pass