from . import OAuthAPI

class MapMyFitnessAPI(OAuthAPI):
    _base_uri = 'https://api.mapmyapi.com'
    _provider = 'mapmyfitness'
