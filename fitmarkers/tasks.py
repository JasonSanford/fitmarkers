import datetime
import json
import logging
import urllib

from celery import task, chord
from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos.error import GEOSException
from django.contrib.gis.measure import D
from social.apps.django_app.default.models import UserSocialAuth

from exceptions import InvalidWorkoutTypeException
from leaderboards.utils import create_or_update_entry
from models import Workout
from markers.models import Marker, WorkoutMarker
from remote import Providers
from remote.oauth.runkeeper import RunKeeperAPI
from remote.oauth.mapmyfitness import MapMyFitnessAPI
from remote.runkeeper import utils as rk_utils
from remote.mapmyfitness import utils as mmf_utils
from utils import get_first_day_of_month


logger = logging.getLogger(__name__)


@task(name='get_new_workouts_for_all_users')
def get_new_workouts_for_all_users():
    users = User.objects.filter(is_active=True)
    for user in users:
        get_new_workouts_for_user.delay(user)


@task(name='get_new_workouts_for_user')
def get_new_workouts_for_user(user):
    since_datetime = get_first_day_of_month()
    social_auth_users = UserSocialAuth.objects.filter(user=user)
    
    runkeeper_users = [sau for sau in social_auth_users if sau.provider == 'runkeeper']
    mmf_users = [sau for sau in social_auth_users if sau.provider == 'mapmyfitness']

    get_new_runkeeper_workouts.delay(runkeeper_users, since_datetime)
    get_new_mmf_workouts.delay(mmf_users, since_datetime)


@task(name='get_new_runkeeper_workouts')
def get_new_runkeeper_workouts(social_auth_users, since_date):
    for sau in social_auth_users:
        rk_api = RunKeeperAPI(social_auth_user=sau)
        activities_response = rk_api.get('/fitnessActivities?noEarlierThan={0}-{1}-{2}'.format(since_date.year, since_date.month, since_date.day))
        raw_workouts = activities_response.json()['items']
        existing_workout_count = 0
        no_path_workout_count = 0
        workouts_to_create = {}
        for raw_workout in raw_workouts:
            uri_parts = raw_workout['uri'].split('fitnessActivities/')
            workout_id = int(uri_parts[1])
            #
            # We could use get_or_create here, but there's no sense going through
            # process of parsing the workout geometry if we don't have to.
            #
            try:
                existing_workout = Workout.objects.get(provider_id=workout_id, provider=Providers.RUNKEEPER)
                existing_workout_count += 1
                continue
            except Workout.DoesNotExist:
                pass
            if raw_workout['has_path']:
                raw_workout_full = rk_api.get(raw_workout['uri']).json()
                try:
                    workouts_to_create[workout_id] = {
                        'user': sau.user,
                        'provider': Providers.RUNKEEPER,
                        'provider_id': workout_id,
                        'type': rk_utils.type_string_to_int(raw_workout['type']),
                        'start_datetime': rk_utils.date_string_to_datetime(raw_workout['start_time']),
                        'duration': int(raw_workout['duration']),
                        'geom': GEOSGeometry(json.dumps(rk_utils.path_to_geojson(raw_workout_full['path']))),
                    }
                except InvalidWorkoutTypeException as exc:
                    logger.error('Invalid workout type for User: {0}, Provider Id: {1}. - {2}'.format(sau.user, Providers.RUNKEEPER, str(exc)))
                    continue
            else:
                no_path_workout_count += 1
        logger.info('Creating {0} workouts for {1}.'.format(len(workouts_to_create), sau.user))
        logger.info('Ignoring {0} workouts for {1} because they already exist.'.format(existing_workout_count, sau.user))
        logger.info('Ignoring {0} workouts for {1} because there is no path.'.format(no_path_workout_count, sau.user))
        if workouts_to_create:
            create_workouts.delay(sau, workouts_to_create, Providers.RUNKEEPER)


@task(name='create_workouts')
def create_workouts(social_auth_user, raw_workouts, provider):
    created_workouts = []
    for provider_id, raw_workout in raw_workouts.iteritems():
        workout = Workout(**raw_workout)
        workout.save()
        created_workouts.append(workout)
        logger.info('Created {0} for {1}'.format(workout, social_auth_user.user))
    # We want to wait until markers have been checked for each worker before updating
    # leaderboards, so use chord to wait for all subtasks to complete.
    header = [check_workout_for_markers.s(workout) for workout in created_workouts]
    callback = update_leaderboards_for_user.subtask(args=(social_auth_user.user,), immutable=True)
    chord(header)(callback)


@task(name='get_new_mmf_workouts')
def get_new_mmf_workouts(social_auth_users, since_date):
    for sau in social_auth_users:
        mmf_api = MapMyFitnessAPI(social_auth_user=sau)
        url_params = {
            'user': sau.uid,
            'created_after': '{0}-{1}-{2}T00:00:00+00:00'.format(since_date.year, since_date.month, since_date.day)
        }
        encoded_params = urllib.urlencode(url_params)

        existing_workout_count = 0
        no_time_series_workout_count = 0
        workouts_to_create = {}
        url = '/v7.0/workout/?{0}'.format(encoded_params)
        there_are_more_workouts = True

        while there_are_more_workouts:

            workouts_response = mmf_api.get(url).json()

            raw_workouts = workouts_response['_embedded']['workouts']
            there_are_more_workouts = '_links' in workouts_response and 'next' in workouts_response['_links'] and workouts_response['_links']['next']

            if there_are_more_workouts:
                url = workouts_response['_links']['next'][0]['href']

            for raw_workout in raw_workouts:

                workout_id = raw_workout['_links']['self'][0]['id']
                #
                # We could use get_or_create here, but there's no sense going through
                # process of parsing the workout geometry if we don't have to.
                #
                try:
                    existing_workout = Workout.objects.get(provider_id=workout_id, provider=Providers.MAPMYFITNESS)
                    existing_workout_count += 1
                    continue
                except Workout.DoesNotExist:
                    pass
                if raw_workout['has_time_series'] and 'route' in raw_workout['_links']:
                    workout_route = mmf_api.get('{0}?field_set=detailed'.format(raw_workout['_links']['route'][0]['href'])).json()
                    if len(workout_route['points']) < 2:
                        logger.info('Workout route for user: {0} only has one point: {1}'.format(sau.user, workout_route))
                        continue
                    try:
                        workouts_to_create[workout_id] = {
                            'user': sau.user,
                            'provider': Providers.MAPMYFITNESS,
                            'provider_id': workout_id,
                            'type': mmf_utils.type_dict_to_int(raw_workout['_links']['activity_type'][0], mmf_api),
                            'start_datetime': mmf_utils.date_string_to_datetime(raw_workout['start_datetime']),
                            'duration': int(raw_workout['aggregates']['active_time_total']),
                            'geom': GEOSGeometry(json.dumps(mmf_utils.points_to_geojson(workout_route['points']))),
                        }
                    except InvalidWorkoutTypeException as exc:
                        logger.error('Invalid workout type for User: {0}, Provider Id: {1}. - {2}'.format(sau.user, Providers.MAPMYFITNESS, str(exc)))
                        continue
                    except GEOSException as exc:
                        logger.error('GEOSException processing User: {0}, workout route: {1}.'.format(sau.user, workout_route))
                        continue
                else:
                    no_time_series_workout_count += 1

        logger.info('Creating {0} workouts for {1}.'.format(len(workouts_to_create), sau.user))
        logger.info('Ignoring {0} workouts for {1} because they already exist.'.format(existing_workout_count, sau.user))
        logger.info('Ignoring {0} workouts for {1} because there is no time series.'.format(no_time_series_workout_count, sau.user))
        if workouts_to_create:
            create_workouts.delay(sau, workouts_to_create, Providers.RUNKEEPER)


@task(name='check_workout_for_markers')
def check_workout_for_markers(workout):
    # First check to see that all current WMs are deleted
    WorkoutMarker.objects.filter(workout=workout).delete()
    markers_on_workout = Marker.objects.filter(geom__distance_lte=(workout.geom, D(m=20)))
    for marker_on_workout in markers_on_workout:
        workout_marker = WorkoutMarker(workout=workout, marker=marker_on_workout)
        workout_marker.save()
    workout.processed = True
    workout.save()
    logger.info('Created {0} WorkoutMarkers for {1}'.format(len(markers_on_workout), workout))


@task(name='update_leaderboards_for_user')
def update_leaderboards_for_user(user):
    """
    Monthly
    """
    today = datetime.date.today()
    first_of_month = get_first_day_of_month()

    monthly_workouts = Workout.objects.filter(user=user, start_datetime__gte=first_of_month)

    timespans = ('all', 'monthly',)
    activity_types = {
        'all': None,
        'run': Workout.TYPE_RUN,
        'ride': Workout.TYPE_RIDE,
        'walk': Workout.TYPE_WALK,
    }

    all_time_workouts = Workout.objects.filter(user=user)
    monthly_workouts = all_time_workouts.filter(user=user, start_datetime__gte=first_of_month)

    for timespan in timespans:
        if timespan == 'all':
            workouts = all_time_workouts
            kwargs = {'all_time': True}
        else:
            workouts = monthly_workouts
            kwargs = {'year': today.year, 'month': today.month}
        for activity_type, activity_enum in activity_types.iteritems():
            if activity_type != 'all':
                these_workouts = workouts.filter(type=activity_enum)
            else:
                these_workouts = workouts
            workouts_ids = these_workouts.values_list('id', flat=True)
            workout_markers = WorkoutMarker.objects.filter(workout__id__in=workouts_ids).distinct('marker')
            points = 0
            for workout_marker in workout_markers:
                points += workout_marker.marker.point_value
            logger.info('Creating/Updating {0} {1} points for {2}: {3}'.format(timespan, activity_type, user, points))
            create_or_update_entry(points, user, activity_type, **kwargs)
