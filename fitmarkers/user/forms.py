from django.forms import ModelForm

from fitmarkers.models import UserProfile


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('timezone',)
