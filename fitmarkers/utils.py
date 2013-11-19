import datetime

from django.utils.timezone import utc


def get_last_monday():
    today = datetime.date.today()
    last_monday = today - datetime.timedelta(days=today.weekday())
    last_monday_datetime = datetime.datetime(last_monday.year, last_monday.month, last_monday.day, tzinfo=utc)
    return last_monday_datetime


def get_first_day_of_month():
    today = datetime.date.today()
    # TODO - revert this back to beginning of this month. This was set to 2 months to do some backfill.
    first_of_month = datetime.datetime(today.year, today.month-2, 1, tzinfo=utc)
    return first_of_month
