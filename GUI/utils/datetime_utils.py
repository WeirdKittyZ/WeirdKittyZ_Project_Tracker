from datetime import datetime, date

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"


def now_str() -> str:
    return datetime.now().strftime(DATETIME_FORMAT)


def today_str() -> str:
    return date.today().strftime(DATE_FORMAT)


def normalize_date(value: str) -> str:
    if not value:
        return today_str()
    return datetime.strptime(value.strip(), DATE_FORMAT).strftime(DATE_FORMAT)
