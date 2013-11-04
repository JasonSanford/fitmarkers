from django.contrib.gis.db import models as geo_models
from django.db import models

from ..models import Workout, behaviors


class Marker(behaviors.Timestampable, geo_models.Model):
    class Meta:
        app_label = 'fitmarkers'

    geom = geo_models.PointField()
    point_value = models.IntegerField(default=1)
    name = models.CharField(max_length=200, null=True)
    description = models.TextField(null=True)

    objects = geo_models.GeoManager()

    def __str__(self):
        return '<Marker {0}>'.format(self.id)


class WorkoutMarker(models.Model):
    class Meta:
        app_label = 'fitmarkers'

    workout = models.ForeignKey(Workout)
    marker = models.ForeignKey(Marker)

    def __str__(self):
        return '<WorkoutMarker {0}>'.format(self.id)