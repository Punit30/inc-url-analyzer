from enum import Enum


class PlatformEnum(str, Enum):
    """
    Enum for platform.
    """
    FACEBOOK = "FACEBOOK"
    INSTAGRAM = "INSTAGRAM"
    WEBSITE = "WEBSITE"
    YOUTUBE = "YOUTUBE"

    def __str__(self):
        return self.value
