import logging

from fitmarkers import keyval


logger = logging.getLogger(__name__)


def create_or_update_entry(points, user, all_time=False, year=None, month=None):
    """
    Create or Update a leaderboard entry in Redis
    """
    if all_time:
        leaderboard_key = 'type_all:timespan_all'
    elif year and month:
        month_string = str(month).zfill(2)
        leaderboard_key = 'type_all:timespan_{0}{1}'.format(year, month_string)
    else:
        raise NameError('Either all_time=True or year and month must be passed.')

    leaderboard_meta_key = '{0}:meta'.format(leaderboard_key)
    leaderboard_db = keyval.get_db(keyval.TYPE_LEADERBOARD)

    name = '{0} {1}'.format(user.first_name, user.last_name).strip()
    meta = {
        'name': name,
        'user_id': user.id,
        'points': points,
    }

    leaderboard_db.hset(leaderboard_meta_key, user.id, meta)
    leaderboard_db.zadd(leaderboard_key, points, user.id)


def get_user_rank(user_id, all_time=False, year=None, month=None):
    """
    Get a user's rank on a leaderboard
    """
    if all_time:
        leaderboard_key = 'type_all:timespan_all'
    elif year and month:
        month_string = str(month).zfill(2)
        leaderboard_key = 'type_all:timespan_{0}{1}'.format(year, month_string)
    else:
        raise NameError('Either all_time=True or year and month must be passed.')

    leaderboard_db = keyval.get_db(keyval.TYPE_LEADERBOARD)
    rank = leaderboard_db.zrevrank(leaderboard_key, user_id)
    return rank


def get_user_score(user_id, all_time=False, year=None, month=None):
    """
    Get a user's score on a leaderboard
    """
    if all_time:
        leaderboard_key = 'type_all:timespan_all'
    elif year and month:
        month_string = str(month).zfill(2)
        leaderboard_key = 'type_all:timespan_{0}{1}'.format(year, month_string)
    else:
        raise NameError('Either all_time=True or year and month must be passed.')

    leaderboard_db = keyval.get_db(keyval.TYPE_LEADERBOARD)
    score = leaderboard_db.zscore(leaderboard_key, user_id)
    if score is not None:
        score = int(score)
    return score


def get_leaderboard_count(all_time=False, year=None, month=None):
    """
    Get the number of users on a leaderboard
    """
    if all_time:
        leaderboard_key = 'type_all:timespan_all'
    elif year and month:
        month_string = str(month).zfill(2)
        leaderboard_key = 'type_all:timespan_{0}{1}'.format(year, month_string)
    else:
        raise NameError('Either all_time=True or year and month must be passed.')

    leaderboard_db = keyval.get_db(keyval.TYPE_LEADERBOARD)
    count = leaderboard_db.zcard(leaderboard_key)
    return count
