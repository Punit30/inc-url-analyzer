from enum import Enum

class URLListSortingEnum(Enum):
    engagement_rate_asc = "engagement_rate_asc"
    engagement_rate_desc = "engagement_rate_desc"

    def __str__(self):
        return self.value