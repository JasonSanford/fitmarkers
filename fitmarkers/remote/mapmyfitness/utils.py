import datetime

from django.utils.timezone import utc


def points_to_geojson(points):
    linestring = {
        'type': 'LineString',
        'coordinates': [
            (point['lng'], point['lat'])
            for point in points
        ]
    }
    return linestring


def date_string_to_datetime(date_string):
    #
    # Given a date string from the MapMyFitness API that looks
    # like '2013-11-04T23:45:50+00:00', return a datetime.datetime
    #
    _date_string, time_string = date_string.split('T')
    year, month, day = map(int, _date_string.split('-'))

    valuable_time_string = time_string.split('+')[0]
    hours, minutes, seconds = map(int, valuable_time_string.split(':'))

    dt = datetime.datetime(year, month, day, hours, minutes, seconds, tzinfo=utc)
    return dt
