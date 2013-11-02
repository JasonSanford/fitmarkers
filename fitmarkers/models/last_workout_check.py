from django.contrib.auth.models import User
from django.db import models

import behaviors

class LastWorkoutCheck(behaviors.Timestampable):
    RUNKEEPER = 1
    MAPMYFITNESS = 2

    PROVIDER_CHOICES = (
        (RUNKEEPER, 'RunKeeper',),
        (MAPMYFITNESS, 'MapMyFitness',),
    )

    user = models.ForeignKey(User)
    provider = models.IntegerField(choices=PROVIDER_CHOICES)
    last_check = models.DateTimeField()