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

    all_time_all_types_rank = get_user_rank(request.user.id, all_time=True)
    all_time_all_types_score = get_user_score(request.user.id, all_time=True)
    if all_time_all_types_rank is not None:
        all_time_all_types_rank += 1  # 0-based index
    all_time_all_types_lb_count = get_leaderboard_count(all_time=True)

    now = datetime.datetime.now()

    monthly_all_types_rank = get_user_rank(request.user.id, month=now.month, year=now.year)
    monthly_all_types_score = get_user_score(request.user.id, month=now.month, year=now.year)
    if monthly_all_types_rank is not None:
        monthly_all_types_rank += 1  # 0-based index
    monthly_all_types_lb_count = get_leaderboard_count(month=now.month, year=now.year)

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
        'all_time_all_types_rank': all_time_all_types_rank,
        'all_time_all_types_lb_count': all_time_all_types_lb_count,
        'all_time_all_types_score': all_time_all_types_score,
        'monthly_all_types_rank': monthly_all_types_rank,
        'monthly_all_types_lb_count': monthly_all_types_lb_count,
        'monthly_all_types_score': monthly_all_types_score,
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
