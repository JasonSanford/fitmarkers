import json
import logging

from django.contrib.gis.geos import GEOSGeometry
from django.test import TestCase

from fitmarkers.markers.tests.factories import MarkerFactory
from fitmarkers.tasks import check_workout_for_markers
from fitmarkers.tests.factories import WorkoutFactory
from fitmarkers.tests.test_data import workout_geom, marker_geoms
from fitmarkers.user.tests.factories import UserFactory

tasks_logger = logging.getLogger('fitmarkers.tasks')
tasks_logger.setLevel(logging.ERROR)


class WorkoutTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.user.save()
        #self.workout = WorkoutFactory(user=self.user)
        #self.workout.save()

    def test_workout_details(self):
        #print self.workout
        pass

    def test_workout_markers(self):
        geom = GEOSGeometry(json.dumps(workout_geom))
        workout = WorkoutFactory(geom=geom)
        workout.save()

        for marker_geom in marker_geoms:
            geom = GEOSGeometry(json.dumps(marker_geom))
            marker = MarkerFactory(geom=geom)
            marker.save()

        marker_count = check_workout_for_markers(workout)
        self.assertEqual(marker_count, 8)