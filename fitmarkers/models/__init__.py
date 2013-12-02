from django.contrib.auth.models import User
from django.db import models

from workout import Workout
from behaviors import Timestampable


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    timezone = models.CharField(max_length=100, default='America/Denver')


User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


class Achievement(Timestampable):
    """
    An award for being in the top spot of a monthly
    leaderboard at month's end
    """
    TYPE_RUN = Workout.TYPE_RUN
    TYPE_RIDE = Workout.TYPE_RIDE
    TYPE_WALK = Workout.TYPE_WALK
    TYPE_ALL = 99

    user = models.ForeignKey(User)
    month = models.DateField()  # The first day of the month for award
    activity_type = models.IntegerField()

    class Meta:
        unique_together = ('month', 'activity_type')


__all__ = (Workout, UserProfile, Achievement,)
