import json
import logging
import urllib

from celery import task
from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from social.apps.django_app.default.models import UserSocialAuth

from models import Workout
from markers.models import Marker, WorkoutMarker
from remote import Providers
from remote.oauth.runkeeper import RunKeeperAPI
from remote.oauth.mapmyfitness import MapMyFitnessAPI
from remote.runkeeper import utils as rk_utils
from remote.mapmyfitness import utils as mmf_utils
from utils import get_last_monday


logger = logging.getLogger(__name__)


@task(name='get_new_workouts_for_all_users')
def get_new_workouts_for_all_users():
    users = User.objects.filter(is_active=True)
    for user in users:
        get_new_workouts_for_user(user)


@task(name='get_new_workouts_for_user')
def get_new_workouts_for_user(user):
    last_monday = get_last_monday()
    social_auth_users = UserSocialAuth.objects.filter(user=user)
    
    runkeeper_users = [sau for sau in social_auth_users if sau.provider == 'runkeeper']
    mmf_users = [sau for sau in social_auth_users if sau.provider == 'mapmyfitness']

    get_new_runkeeper_workouts(runkeeper_users, last_monday)
    get_new_mmf_workouts(mmf_users, last_monday)


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
                workouts_to_create[workout_id] = {
                    'user': sau.user,
                    'provider': Providers.RUNKEEPER,
                    'provider_id': workout_id,
                    'start_datetime': rk_utils.date_string_to_datetime(raw_workout['start_time']),
                    'duration': int(raw_workout['duration']),
                    'geom': GEOSGeometry(json.dumps(rk_utils.path_to_geojson(raw_workout_full['path']))),
                }
            else:
                no_path_workout_count += 1
        logger.info('Creating {0} workouts for {1}.'.format(len(workouts_to_create), sau.user))
        logger.info('Ignoring {0} workouts for {1} because they already exist.'.format(existing_workout_count, sau.user))
        logger.info('Ignoring {0} workouts for {1} because there is no path.'.format(no_path_workout_count, sau.user))
        create_workouts(sau, workouts_to_create, Providers.RUNKEEPER)


@task(name='create_workouts')
def create_workouts(social_auth_user, raw_workouts, provider):
    for provider_id, raw_workout in raw_workouts.iteritems():
        workout = Workout(**raw_workout)
        workout.save()
        check_workout_for_markers.apply_async((workout,))
        logger.info('Created {0} for {1}'.format(workout, social_auth_user.user))


@task(name='get_new_mmf_workouts')
def get_new_mmf_workouts(social_auth_users, since_date):
    for sau in social_auth_users:
        mmf_api = MapMyFitnessAPI(social_auth_user=sau)
        url_params = {
            'user': 9118466,
            'created_after': '{0}-{1}-{2}T00:00:00+00:00'.format(since_date.year, since_date.month, since_date.day)
        }
        encoded_params = urllib.urlencode(url_params)
        workouts_response = mmf_api.get('/v7.0/workout/?{0}'.format(encoded_params)).json()
        raw_workouts = workouts_response['_embedded']['workouts']
        existing_workout_count = 0
        no_time_series_workout_count = 0
        workouts_to_create = {}
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
            if raw_workout['has_time_series']:
                workout_route = mmf_api.get('{0}?field_set=detailed'.format(raw_workout['_links']['route'][0]['href'])).json()
                workouts_to_create[workout_id] = {
                    'user': sau.user,
                    'provider': Providers.MAPMYFITNESS,
                    'provider_id': workout_id,
                    'start_datetime': mmf_utils.date_string_to_datetime(raw_workout['start_datetime']),
                    'duration': int(raw_workout['aggregates']['active_time_total']),
                    'geom': GEOSGeometry(json.dumps(mmf_utils.points_to_geojson(workout_route['points']))),
                }
            else:
                no_time_series_workout_count += 1
        logger.info('Creating {0} workouts for {1}.'.format(len(workouts_to_create), sau.user))
        logger.info('Ignoring {0} workouts for {1} because they already exist.'.format(existing_workout_count, sau.user))
        logger.info('Ignoring {0} workouts for {1} because there is no time series.'.format(no_time_series_workout_count, sau.user))
        create_workouts(sau, workouts_to_create, Providers.RUNKEEPER)


@task(name='check_workout_for_markers')
def check_workout_for_markers(workout):
    markers_on_workout = Marker.objects.filter(geom__distance_lte=(workout.geom, D(m=20)))
    for marker_on_workout in markers_on_workout:
        workout_marker = WorkoutMarker(workout=workout, marker=marker_on_workout)
        workout_marker.save()
    workout.processed = True
    workout.save()
    logging.info('Created {0} WorkoutMarkers for {1}'.format(len(markers_on_workout), workout))
