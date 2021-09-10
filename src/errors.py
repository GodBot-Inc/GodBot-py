class DuplicateEntry(Exception):
    """Gets raised if a duplicate exists in the database"""
    pass


class DiscordApiError(Exception):
    """Get's raised in src.discord_api if something goes wrong"""
    pass


class InvalidFormBody(DiscordApiError):
    """Get's raised if a request could not be send and it's the programmers fault"""
    pass


class ConnectionError(DiscordApiError):
    """Get's raised if the discord Api has problems"""
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


class YTApiError(Exception):
    """Raised if something went wrong with the youtube API"""
    pass


class VideoNotFound(YTApiError):
    """Gets raised when a video from the play_playlist function is not found (automatically handled)"""
    pass


class PlaylistNotFound(YTApiError):
    """Raised when a requested playlist is not found"""
    pass
