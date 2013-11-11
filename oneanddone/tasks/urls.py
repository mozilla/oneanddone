# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.conf.urls.defaults import patterns, url

from oneanddone.tasks import views


urlpatterns = patterns('',
    url(r'^tasks/available/$', views.AvailableTasksView.as_view(), name='tasks.available'),
    url(r'^tasks/(?P<pk>\d+)/$', views.TaskDetailView.as_view(), name='tasks.detail'),
)
