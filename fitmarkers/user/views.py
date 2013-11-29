import datetime
import json

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import Http404, HttpResponse
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
    timespans = ('all_time', 'monthly',)
    activity_types = ('all', 'run', 'ride', 'walk',)

    context = {
        'all_time_leaderboards': {},
        'monthly_leaderboards': {},
    }

    now = datetime.datetime.now()

    for timespan in timespans:
        for activity_type in activity_types:
            kwargs = {'activity_type': activity_type}
            if timespan == 'all_time':
                kwargs['all_time'] = True
            else:
                kwargs['month'] = now.month
                kwargs['year'] = now.year

            rank = get_user_rank(request.user.id, **kwargs)
            score = get_user_score(request.user.id, **kwargs)
            if rank is not None:
                rank += 1  # 0-based index
            count = get_leaderboard_count(**kwargs)

            context['{0}_leaderboards'.format(timespan)][activity_type] = {
                'rank': rank,
                'score': score,
                'count': count,
            }

    return render(request, 'user_dashboard.html', context)


@login_required
def monthly_workouts(request):
    activity_type = request.GET.get('activity_type')
    first_day_of_month = get_first_day_of_month()
    filter_kwargs = {
        'user': request.user,
        'start_datetime__gte': first_day_of_month,
    }
    if activity_type:
        attr = 'type_{0}'.format(activity_type)
        filter_kwargs['type'] = getattr(Workout, attr.upper())
    monthly_workouts = Workout.objects.filter(**filter_kwargs).order_by('-start_datetime').select_related('WorkoutMarker').annotate(workout_marker_count=Count('workoutmarker'))
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

    workouts = [
        {
            'id': w.id,
            'date': w.start_datetime.strftime('%b %d, %Y'),
            'type': w.get_type_display(),
            'marker_count': w.workout_marker_count,
            'url': reverse('user_workout', args=[w.id])
        } for w in monthly_workouts
    ]

    content = {
        'workouts': workouts,
        'markers_geojson': monthly_markers_geojson,
    }

    return HttpResponse(json.dumps(content), content_type='application/json')


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
