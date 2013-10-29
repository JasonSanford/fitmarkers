from . import OAuthAPI

class RunKeeperAPI(OAuthAPI):
    _base_uri = 'https://api.runkeeper.com'
    _provider = 'runkeeper'
