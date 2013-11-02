import requests
from social.apps.django_app.default.models import UserSocialAuth


class OAuthAPI(object):
    def __init__(self, user=None, social_auth_user=None):
        if not (user or social_auth_user):
            raise IndexError('Either user or social_auth_user must be passed')
        if not social_auth_user:
            social_auth_user = UserSocialAuth.objects.get(user=user, provider=self._provider)
        social_extra = social_auth_user.extra_data
        access_token = social_extra['access_token']
        self._headers = {'Authorization': 'Bearer {0}'.format(access_token)}

    def get(self, method):
        return requests.get(self._base_uri + method, headers=self._headers)
