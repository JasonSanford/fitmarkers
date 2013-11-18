import datetime
import json

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

from ..leaderboards.utils import get_user_rank, get_leaderboard_count, get_user_score
from ..markers.models import WorkoutMarker
from ..models import Workout
from ..utils import get_first_day_of_month


@login_required
def user(request):
    return redirect('fitmarkers.user.views.dashboard')


@login_required
def dashboard(request):
    first_day_of_month = get_first_day_of_month()
    monthly_workouts = Workout.objects.filter(user=request.user, start_datetime__gte=first_day_of_month).order_by('-start_datetime').select_related('WorkoutMarker').annotate(workout_marker_count=Count('workoutmarker'))

    activity_types = ('all', 'run', 'ride', 'walk',)

    monthly_workouts_ids = monthly_workouts.values_list('id', flat=True)

    monthly_workouts_markers = WorkoutMarker.objects.filter(workout__id__in=monthly_workouts_ids).distinct('marker')
    monthly_markers_geojson = {'type': 'FeatureCollection', 'features': []}
    for wm in monthly_workouts_markers:
        wm_feature = {
            'type': 'Feature',
            'properties': {
                'name': wm.marker.name,
                'point_value': wm.marker.point_value,
                'description': wm.marker.description,
                'marker_id': wm.marker.id,
            },
            'geometry': {'type': 'Point', 'coordinates': [wm.marker.geom.x, wm.marker.geom.y]}
        }
        monthly_markers_geojson['features'].append(wm_feature)

    context = {
        'monthly_workouts': monthly_workouts,
        'monthly_markers_geojson': json.dumps(monthly_markers_geojson),
        'activity_types': activity_types,
        'all_time_leaderboards': {},
        'monthly_leaderboards': {},
    }

    now = datetime.datetime.now()

    for activity_type in activity_types:
        all_time_rank = get_user_rank(request.user.id, activity_type, all_time=True)
        all_time_score = get_user_score(request.user.id, activity_type, all_time=True)
        if all_time_rank is not None:
            all_time_rank += 1  # 0-based index
        all_time_count = get_leaderboard_count(activity_type, all_time=True)

        context['all_time_leaderboards'][activity_type] = {
            'rank': all_time_rank,
            'score': all_time_score,
            'count': all_time_count,
        }

        monthly_rank = get_user_rank(request.user.id, activity_type, month=now.month, year=now.year)
        monthly_score = get_user_score(request.user.id, activity_type, month=now.month, year=now.year)
        if monthly_rank is not None:
            monthly_rank += 1  # 0-based index
        monthly_count = get_leaderboard_count(activity_type, month=now.month, year=now.year)

        context['monthly_leaderboards'][activity_type] = {
            'rank': monthly_rank,
            'score': monthly_score,
            'count': monthly_count,
        }

    return render(request, 'user_dashboard.html', context)


@login_required
def workout(request, workout_id):
    #
    # Yes, I should be excepting DoesNotExist or doing
    # a get_object_or_404 here, but I need a QuerySet
    # to get GeoJSON out, so IndexError it is.
    #
    try:
        workout = Workout.objects.filter(id=workout_id).geojson()[0]
    except IndexError:
        raise Http404
    workout_markers = WorkoutMarker.objects.filter(workout=workout)

    workout_markers_geojson = {'type': 'FeatureCollection', 'features': []}
    for wm in workout_markers:
        wm_feature = {
            'type': 'Feature',
            'properties': {
                'name': wm.marker.name,
                'point_value': wm.marker.point_value,
                'description': wm.marker.description,
                'marker_id': wm.marker.id,
            },
            'geometry': {'type': 'Point', 'coordinates': [wm.marker.geom.x, wm.marker.geom.y]}
        }
        workout_markers_geojson['features'].append(wm_feature)

    context = {
        'workout': workout,
        'workout_geojson': workout.geojson,
        'workout_markers_geojson': json.dumps(workout_markers_geojson)
    }
    return render(request, 'user_workout.html', context)
