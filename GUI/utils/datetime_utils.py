from datetime import datetime, date

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DISPLAY_FORMAT  = "%Y-%m-%d %H:%M"       # no seconds — for display only
DATE_FORMAT = "%Y-%m-%d"


def now_str() -> str:
    """Current timestamp stored in Excel (with seconds for precision)."""
    return datetime.now().strftime(DATETIME_FORMAT)


def today_str() -> str:
    return date.today().strftime(DATE_FORMAT)


def normalize_date(value: str) -> str:
    if not value:
        return today_str()
    return datetime.strptime(value.strip(), DATE_FORMAT).strftime(DATE_FORMAT)


def to_display(value) -> str:
    """Convert a stored timestamp (or datetime object) to the short display format."""
    if not value:
        return ""
    if isinstance(value, datetime):
        return value.strftime(DISPLAY_FORMAT)
    s = str(value).strip()
    for fmt in (DATETIME_FORMAT, DISPLAY_FORMAT, DATE_FORMAT):
        try:
            return datetime.strptime(s, fmt).strftime(DISPLAY_FORMAT)
        except ValueError:
            continue
    return s   # fallback: show as-is


def parse_display(value: str) -> str:
    """Parse a user-entered display string back to the stored format."""
    s = (value or "").strip()
    for fmt in (DATETIME_FORMAT, DISPLAY_FORMAT, "%Y-%m-%d %H:%M", DATE_FORMAT):
        try:
            return datetime.strptime(s, fmt).strftime(DATETIME_FORMAT)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date/time: '{value}'. Use format YYYY-MM-DD HH:MM")
