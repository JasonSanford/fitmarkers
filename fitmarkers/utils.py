import datetime


def get_last_monday():
    today = datetime.date.today()
    last_monday = today - datetime.timedelta(days=today.weekday())
    last_monday_datetime = datetime.datetime(last_monday.year, last_monday.month, last_monday.day)
    return last_monday_datetime