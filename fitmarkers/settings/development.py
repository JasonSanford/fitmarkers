from defaults import *

STATIC_URL = '/static/'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['fitmarkers']['level'] = 'DEBUG'

CELERYBEAT_SCHEDULE['get_new_workouts_for_all_users']['schedule'] = timedelta(minutes=1)
