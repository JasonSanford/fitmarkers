from django.conf.urls import patterns, include, url

urlpatterns = patterns('fitmarkers.user.views',
    url(r'^$', 'user', name='user'),
    url(r'^dashboard/', 'dashboard', name='user_dashboard'),
    url(r'^monthly_workouts/', 'monthly_workouts', name='user_monthly_workouts'),
    url(r'^workout/(?P<workout_id>\d+)', 'workout', name='user_workout'),
)
