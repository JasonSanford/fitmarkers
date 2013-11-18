import redis


TYPE_LEADERBOARD = 0
TYPE_CELERY = 1  # Don't ever use this from Django, only here to show this db is used already.
TYPE_CACHE = 2  # Don't ever use this from Django, only here to show this db is used already by the Django cache


def get_db(db_index):
    r = redis.StrictRedis(host='localhost', port=6379, db=db_index)
    return r