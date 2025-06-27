from pytz import timezone
from typing import Optional
from datetime import datetime, timedelta, date


def get_utc_range_from_ist_date(ist_date: date):
    # Start and end of IST day
    start_ist = datetime.combine(ist_date, datetime.min.time())
    end_ist = datetime.combine(ist_date, datetime.max.time())
    # Convert IST to UTC (IST = UTC+5:30)
    ist_offset = timedelta(hours=5, minutes=30)
    start_utc = (start_ist - ist_offset).replace(tzinfo=timezone("UTC"))
    end_utc = (end_ist - ist_offset).replace(tzinfo=timezone("UTC"))
    return start_utc, end_utc

def get_now_for_timezone(tz: str="UTC") -> str:
    """
    Get the current timestamp in a specific timezone.
    
    :param tz: Name of the timezone (e.g., 'America/New_York'). Defaults to 'UTC'.
    :return: Current timestamp as a datetime object.
    """
    return datetime.now(tz=timezone(tz)).isoformat()

def format_timestamp(dt: datetime, fmt: Optional[str]="%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object into a string.
    
    :param dt: Datetime object to format.
    :param fmt: Format string (default is "%Y-%m-%d %H:%M:%S").
    :return: Formatted date string.
    """
    return dt.strftime(fmt)

def format_date_str(dt_str: str, fmt: Optional[str]="%Y-%m-%d %H:%M:%S") -> str:
    """
        Convert a date string into a formatted date string.

        Parameters:
            dt_str (str): Input date string in ISO or common formats.
            fmt (str): Desired output format (default is "%Y-%m-%d %H:%M:%S").

        Returns:
            str: Formatted date string.
        """
    try:
        dt = datetime.fromisoformat(dt_str)
    except ValueError:
        dt = datetime.strptime(dt_str, fmt)

    return dt.strftime(fmt)