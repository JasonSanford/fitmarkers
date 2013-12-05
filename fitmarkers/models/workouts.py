from django.contrib.auth.models import User
from django.contrib.gis.db import models as geo_models
from django.db import models

import behaviors
from ..utils import get_last_monday


class Workout(behaviors.Timestampable, geo_models.Model):
    TYPE_RUN = 1
    TYPE_RIDE = 2
    TYPE_WALK = 3

    TYPE_CHOICES = (
        (TYPE_RUN, 'Run'),
        (TYPE_RIDE, 'Ride'),
        (TYPE_WALK, 'Walk'),
    )

    RUNKEEPER = 1
    MAPMYFITNESS = 2

    PROVIDER_CHOICES = (
        (RUNKEEPER, 'RunKeeper'),
        (MAPMYFITNESS, 'MapMyFitness'),
    )

    user = models.ForeignKey(User)
    provider = models.IntegerField(choices=PROVIDER_CHOICES)
    provider_id = models.IntegerField()
    type = models.IntegerField(choices=TYPE_CHOICES)
    start_datetime = models.DateTimeField()
    duration = models.IntegerField()
    processed = models.BooleanField(default=False)
    geom = geo_models.LineStringField()

    objects = geo_models.GeoManager()

    @property
    def is_this_week(self):
        return self.start_datetime > get_last_monday(self.user)

    @property
    def display_date(self):
        #
        # For the current week (since the past Monday) show just the day.
        # Anything before that, show "Feb 28, 2013"
        #
        if self.is_this_week:
            formatter = '%A'
        else:
            formatter = '%b %d, %Y'
        return self.start_datetime.strftime(formatter)

    @property
    def name(self):
        return 'A {0} from {1} on {2}'.format(self.get_type_display(), self.get_provider_display(), self.display_date)

    class Meta:
        app_label = 'fitmarkers'

    def __str__(self):
        return '<Workout {0}>'.format(self.id)
