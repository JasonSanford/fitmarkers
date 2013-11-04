from django.conf.urls import patterns, include, url

urlpatterns = patterns('fitmarkers.markers.views',
    url(r'^$', 'search', name='search'),
)
