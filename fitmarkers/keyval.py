import redis


TYPE_LEADERBOARD = 0


def get_db(db_index):
    r = redis.StrictRedis(host='localhost', port=6379, db=db_index)
    return r