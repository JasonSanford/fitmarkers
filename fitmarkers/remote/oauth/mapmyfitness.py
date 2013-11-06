from django.conf import settings
from requests_oauthlib import OAuth1Session
from social.apps.django_app.default.models import UserSocialAuth


class MapMyFitnessAPI(object):
    _base_uri = 'https://api.mapmyapi.com'
    _provider = 'mapmyfitness'

    def __init__(self, user=None, social_auth_user=None):
        if not (user or social_auth_user):
            raise IndexError('Either user or social_auth_user must be passed')
        if not social_auth_user:
            social_auth_user = UserSocialAuth.objects.get(user=user, provider=self._provider)
        social_extra = social_auth_user.extra_data
        self.session = OAuth1Session(settings.SOCIAL_AUTH_MAPMYFITNESS_KEY,
                                     client_secret=settings.SOCIAL_AUTH_MAPMYFITNESS_SECRET,
                                     resource_owner_key=social_extra['access_token']['oauth_token'],
                                     resource_owner_secret=social_extra['access_token']['oauth_token_secret'])

    def get(self, method):
        return self.session.get(self._base_uri + method)
