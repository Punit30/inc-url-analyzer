from datetime import datetime
from pytz import timezone

def get_now_for_timezone(tz: str="UTC") -> datetime:
    """
    Get the current timestamp in a specific timezone.
    
    :param tz: Name of the timezone (e.g., 'America/New_York'). Defaults to 'UTC'.
    :return: Current timestamp as a datetime object.
    """
    return datetime.now(tz=timezone(tz))

def format_timestamp(dt: datetime, fmt: str="%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object into a string.
    
    :param dt: Datetime object to format.
    :param fmt: Format string (default is "%Y-%m-%d %H:%M:%S").
    :return: Formatted date string.
    """
    return dt.strftime(fmt)