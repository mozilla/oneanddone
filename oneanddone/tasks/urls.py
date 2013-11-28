# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.conf.urls.defaults import patterns, url

from oneanddone.tasks import views


urlpatterns = patterns('',
    url(r'^tasks/available/$', views.AvailableTasksView.as_view(), name='tasks.available'),
    url(r'^tasks/(?P<pk>\d+)/$', views.TaskDetailView.as_view(), name='tasks.detail'),
    url(r'^tasks/(?P<pk>\d+)/start/$', views.StartTaskView.as_view(), name='tasks.start'),
    url(r'^tasks/(?P<pk>\d+)/finish/$', views.FinishTaskView.as_view(), name='tasks.finish'),
    url(r'^tasks/(?P<pk>\d+)/abandon/$', views.AbandonTaskView.as_view(), name='tasks.abandon'),
    url(r'^tasks/(?P<pk>\d+)/feedback/completed/$', views.CreateFeedbackView.as_view(), {'aborted':False}, name='tasks.feedback.completed'),
    url(r'^tasks/(?P<pk>\d+)/feedback/aborted/$', views.CreateFeedbackView.as_view(), {'aborted':True}, name='tasks.feedback.aborted'),
)
