import pandas as pd
from datetime import datetime, timedelta
import re

def safe_timestamp_format(timestamp) -> str:
    """Safely format a timestamp to ISO8601 string"""
    try:
        if pd.isna(timestamp):
            return "N/A"
        if isinstance(timestamp, (pd.Timestamp, datetime)):
            return timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
        return str(timestamp)
    except Exception as e:
        return str(timestamp)

def parse_time_range(time_range) -> tuple[str, str]:
    """Return (start, end) as ISO8601 strings. If time_range is ISO, use as start and add 1h for end. If relative, convert to ISO."""
    if hasattr(time_range, 'value'):
        time_range = str(time_range)
    if 'T' in time_range and 'Z' in time_range:
        try:
            start_time = datetime.strptime(time_range, '%Y-%m-%dT%H:%M:%SZ')
            end_time = start_time + timedelta(hours=1)
            return (
                start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            )
        except Exception:
            return time_range, ""
    match = re.match(r'-(\d+)([hm])', time_range)
    now = datetime.utcnow()
    if match:
        amount = int(match.group(1))
        unit = match.group(2)
        if unit == 'h':
            delta = timedelta(hours=amount)
        else:
            delta = timedelta(minutes=amount)
        start = (now - delta).strftime('%Y-%m-%dT%H:%M:%SZ')
        end = now.strftime('%Y-%m-%dT%H:%M:%SZ')
        return start, end
    return time_range, "" 