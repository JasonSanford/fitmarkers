import ast
import datetime
import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from fitmarkers import keyval
from fitmarkers.leaderboards import START_DATE as leaderboards_start_date
from fitmarkers.utils import add_months


logger = logging.getLogger(__name__)


def leaderboards_landing(request):
    now = datetime.datetime.now()

    leaderboard_month_date = leaderboards_start_date
    current_month_date = datetime.date(now.year, now.month, 1)
    past_leaderboard_months = []
    while leaderboard_month_date < current_month_date:
        past_leaderboard_months.append(leaderboard_month_date)
        leaderboard_month_date = add_months(leaderboard_month_date, 1)

    context = {
        'current_year': str(now.year),
        'current_month': str(now.month).zfill(2),
        'past_leaderboard_months': past_leaderboard_months,
    }
    return render(request, 'leaderboards_landing.html', context)


def get_leaderboard(request):
    """
    Get leaderboard entries - Used in ajax view on leaderboards page
    """
    activity = request.GET.get('activity')
    timespan = request.GET.get('timespan')

    leaderboard_key = 'type_{0}:timespan_{1}'.format(activity, timespan)

    leaderboard_meta_key = '{0}:meta'.format(leaderboard_key)
    leaderboard_db = keyval.get_db(keyval.TYPE_LEADERBOARD)

    offset = 0
    limit = 20
    user_ids = leaderboard_db.zrevrange(leaderboard_key, offset, offset + limit)
    entries = leaderboard_db.hmget(leaderboard_meta_key, *user_ids)
    leaderboard_count = leaderboard_db.zcard(leaderboard_key)

    context = {'entries': [], 'total_count': leaderboard_count}
    for stringy_dict_entry in entries:
        entry = ast.literal_eval(stringy_dict_entry)
        entry['is_authd_user'] = entry['user_id'] == request.user.id
        context['entries'].append(entry)

    response = render_to_string('leaderboard.html', context)

    return HttpResponse(response, content_type='text/html')
