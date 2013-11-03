from django.contrib.auth.models import User
from django.contrib.gis.db import models as geo_models
from django.db import models

import behaviors


class Workout(behaviors.Timestampable, geo_models.Model):
    class Meta:
        app_label = 'fitmarkers'

    user = models.ForeignKey(User)
    provider = models.IntegerField()
    provider_id = models.IntegerField()
    start_datetime = models.DateTimeField()
    duration = models.IntegerField()
    processed = models.BooleanField(default=False)
    geom = geo_models.LineStringField()

    objects = geo_models.GeoManager()

    def __str__(self):
        return '<Workout {0}>'.format(self.id)
