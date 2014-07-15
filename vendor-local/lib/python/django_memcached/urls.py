from django.conf.urls import *

urlpatterns = patterns('',
    (r'^$', 'django_memcached.views.server_list'),
    (r'^(\d+)/$', 'django_memcached.views.server_status'),
)
