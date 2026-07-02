def valid_date(year:int, month: int|None = None, day: int|None = None) -> bool:
    if year < 0 or year > 3000:
        return False
    if month is not None and (month <= 0 or month > 12):
        return False
    if day is not None and (day <= 0 or day > 31):
        return False

    return True

def str_to_date(date: str) -> int|tuple[int, int]|tuple[int, int, int]:
    filter_date = ""
    for c in date:
        if c.isdigit():
            filter_date += c
    date = filter_date
    if len(date) == 4:
        year = int(date)
        if not valid_date(year):
            raise ValueError("Invalid date format")
        return year
    if len(date) == 6:
        month = int(date[0:2])
        year = int(date[2:])
        if not valid_date(year, month):
            raise ValueError("Invalid date format")
        return month, year
    if len(date) == 8:
        day = int(date[0:2])
        month = int(date[2:4])
        year = int(date[4:])
        if not valid_date(year, month, day):
            raise ValueError("Invalid date format")
        return day, month, year
    else:
        raise ValueError("Invalid date format")

def date_to_str(day: int|None, month: int|None, year: int) -> str:
    date = str(year)
    if month is not None:
        date = f"{month}_" + date
        if month < 10:
            date = '0' + date
    if day is not None:
        date = f"{day}_" + date
        if day < 10:
            date = '0' + date

    return date