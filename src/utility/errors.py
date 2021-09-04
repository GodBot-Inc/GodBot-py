class DuplicateEntry(Exception):
    """Gets raised if a duplicate exists in the database"""
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
