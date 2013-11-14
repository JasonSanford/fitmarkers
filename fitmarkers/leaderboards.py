import logging

import keyval


logger = logging.getLogger(__name__)


def create_or_update_entry(points, user_id, all_time=False, year=None, month=None):
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

    leaderboard_db = keyval.get_db(keyval.TYPE_LEADERBOARD)
    leaderboard_db.zadd(leaderboard_key, points, user_id)

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