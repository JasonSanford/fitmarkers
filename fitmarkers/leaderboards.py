import keyval


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
