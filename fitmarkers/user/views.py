import json

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

from ..models import Workout
from ..markers.models import WorkoutMarker


@login_required
def user(request):
    return redirect('fitmarkers.user.views.dashboard')


@login_required
def dashboard(request):
    return render(request, 'user_dashboard.html')


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
                'description': wm.marker.description
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