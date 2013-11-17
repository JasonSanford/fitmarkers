from django.conf.urls import patterns, include, url

urlpatterns = patterns('fitmarkers.leaderboards.views',
    url(r'^$', 'leaderboards_landing', name='leaderboards_landing'),
    url(r'^get_leaderboard$', 'get_leaderboard', name='get_leaderboard'),
)
