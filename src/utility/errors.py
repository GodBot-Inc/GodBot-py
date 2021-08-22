class DuplicateEntry(Exception):
    """Gets raised if a duplicate exists in the database"""
    pass


class VideoNotFound(Exception):
    """Gets raised when a video from the play_playlist function is not found (automatically handled)"""
    pass
