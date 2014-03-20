# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.conf.urls.defaults import patterns, url

from oneanddone.tasks import views


urlpatterns = patterns('',
    url(r'^tasks/available/$', views.AvailableTasksView.as_view(), name='tasks.available'),
    url(r'^tasks/random/$', views.RandomTasksView.as_view(), name='tasks.random'),
    url(r'^tasks/(?P<pk>\d+)/$', views.TaskDetailView.as_view(), name='tasks.detail'),
    url(r'^tasks/(?P<pk>\d+)/start/$', views.StartTaskView.as_view(), name='tasks.start'),
    url(r'^tasks/(?P<pk>\d+)/finish/$', views.FinishTaskView.as_view(), name='tasks.finish'),
    url(r'^tasks/(?P<pk>\d+)/abandon/$', views.AbandonTaskView.as_view(), name='tasks.abandon'),
    url(r'^tasks/feedback/(?P<pk>\d+)/$', views.CreateFeedbackView.as_view(), name='tasks.feedback'),

    # API for interacting with tasks and task areas
    url(r'^api/v1/task/$', views.TaskListAPI.as_view(), name='api-task'),
    url(r'^api/v1/task/(?P<pk>\d+)/$', views.TaskDetailAPI.as_view(),
        name='api-task-detail'),
    url(r'^api/v1/taskarea/$', views.TaskAreaListAPI.as_view(), name='api-taskarea'),
    url(r'^api/v1/taskarea/(?P<pk>\d+)/$', views.TaskAreaDetailAPI.as_view(),
        name='api-taskarea-detail'),

)
