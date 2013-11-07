import datetime

from django.utils.timezone import utc

from fitmarkers.models import Workout
from fitmarkers.exceptions import InvalidWorkoutTypeException


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


def type_dict_to_int(type_dict, mmf_api):
    #
    # Given a dict from the MapMyFitness API that looks like
    # {'href': '/v7.0/activity_type/16/', 'id': '618'}
    # get the root activity type name and return corresponding
    # Workout.TYPE_CHOICES choice
    #
    # TODO: Get some memcache up in here, what a waste to do all this HTTP.
    input_id = type_dict['id']
    activity_type_response = mmf_api.get(type_dict['href']).json()
    if activity_type_response['_links']['root'][0]['id'] == input_id:
        mmf_name = activity_type_response['name']
    else:
        root_activity_type_response = mmf_api.get(activity_type_response['_links']['root'][0]['href']).json()
        mmf_name = root_activity_type_response['name']

    mmf_types = (
        ('Run / Jog', Workout.TYPE_RUN),
        ('Walk', Workout.TYPE_WALK),
        ('Bike Ride', Workout.TYPE_RIDE),
    )

    for name, workout_type in mmf_types:
        if mmf_name == name:
            return workout_type

    raise InvalidWorkoutTypeException('{0} is not a valid workout type.'.format(mmf_name))
