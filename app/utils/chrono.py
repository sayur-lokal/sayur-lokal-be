from datetime import datetime, timezone, timedelta

# Zona waktu Indonesia (WIB = UTC+7)
INDONESIA_TIMEZONE = timezone(timedelta(hours=7))

def now():
    """
    Mendapatkan waktu saat ini dalam zona waktu Indonesia (WIB)
    """
    return datetime.now(INDONESIA_TIMEZONE)

def format_datetime(dt, format_str="%Y-%m-%d %H:%M:%S"):
    """
    Memformat objek datetime ke string dengan format tertentu
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=INDONESIA_TIMEZONE)
    return dt.strftime(format_str)

def parse_datetime(datetime_str, format_str="%Y-%m-%d %H:%M:%S"):
    """
    Mengubah string datetime menjadi objek datetime dengan zona waktu Indonesia
    """
    dt = datetime.strptime(datetime_str, format_str)
    return dt.replace(tzinfo=INDONESIA_TIMEZONE)

