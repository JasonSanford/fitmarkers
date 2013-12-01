import datetime

from pytz import timezone


def get_last_monday(user):
    str_user_timezone = user.profile.timezone
    user_timezone = timezone(str_user_timezone)
    now = datetime.datetime.now(user_timezone)
    last_monday = now - datetime.timedelta(days=now.weekday())
    last_monday_datetime = datetime.datetime(last_monday.year, last_monday.month, last_monday.day, tzinfo=user_timezone)
    return last_monday_datetime


def get_first_day_of_month(user):
    str_user_timezone = user.profile.timezone
    user_timezone = timezone(str_user_timezone)
    now = datetime.datetime.now(user_timezone)
    first_of_month = datetime.datetime(now.year, now.month, 1, tzinfo=user_timezone)
    return first_of_month
