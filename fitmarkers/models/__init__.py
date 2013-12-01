from django.contrib.auth.models import User
from django.db import models

from workout import Workout


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    timezone = models.CharField(max_length=100, default='America/Denver')


User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


__all__ = (Workout, UserProfile,)
