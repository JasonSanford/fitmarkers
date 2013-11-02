import datetime

from django.utils.timezone import utc


def path_to_geojson(path):
    linestring = {
        'type': 'LineString',
        'coordinates': [
            (coord['longitude'], coord['latitude'])
            for coord in path
        ]
    }
    return linestring


def date_string_to_datetime(date_string):
    #
    # Given a date string from the RunKeeper API that looks
    # like 'Wed, 30 Oct 2013 15:51:13', return a datetime.datetime
    #
    valuable_string = date_string.split(', ')[1]
    
    # now at '30 Oct 2013 15:51:13'
    day_string, month_string, year_string, time_string = valuable_string.split(' ')
    
    day = int(day_string)
    month = datetime.datetime.strptime(month_string, '%b').month
    year = int(year_string)
    hours, minutes, seconds = map(int, time_string.split(':'))

    dt = datetime.datetime(year, month, day, hours, minutes, seconds, tzinfo=utc)
    return dt