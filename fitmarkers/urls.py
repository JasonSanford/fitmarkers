from django.conf import settings
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'fitmarkers.views.home', name='home'),
    url(r'^about$', 'fitmarkers.views.about', name='about'),
    url(r'^login$', 'fitmarkers.views.login', name='login'),
    url(r'^logout$', 'fitmarkers.views.logout', name='logout'),
    url(r'^user/', include('fitmarkers.user.urls')),
    url(r'^markers/', include('fitmarkers.markers.urls')),
    url(r'^leaderboards/', include('fitmarkers.leaderboards.urls')),
    # Examples:
    # url(r'^$', 'fitmarkers.views.home', name='home'),
    # url(r'^fitmarkers/', include('fitmarkers.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url('', include('social.apps.django_app.urls', namespace='social')),
)

if settings.DEBUG:
    urlpatterns += patterns('django.contrib.staticfiles.views',
        url(r'^static/(?P<path>.*)$', 'serve'),
    )