# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.conf.urls import url

from oneanddone.tasks import views


urlpatterns = [
    url(r'^tasks/(?P<pk>\d+)/$', views.TaskDetailView.as_view(), name='tasks.detail'),
    url(r'^tasks/(?P<pk>\d+)/abandon/$', views.AbandonTaskView.as_view(), name='tasks.abandon'),
    url(r'^tasks/(?P<pk>\d+)/finish/$', views.FinishTaskView.as_view(), name='tasks.finish'),
    url(r'^tasks/(?P<pk>\d+)/start/$', views.StartTaskView.as_view(), name='tasks.start'),
    url(r'^tasks/(?P<pk>\d+)/submit/$', views.SubmitTaskForVerificationView.as_view(),
        name='tasks.submit'),
    url(r'^tasks/(?P<pk>\d+)/verify/$', views.VerifyTaskView.as_view(), name='tasks.verify'),
    url(r'^tasks/(?P<pk>\d+)/whatsnext/$', views.WhatsNextView.as_view(), name='tasks.whats_next'),
    url(r'^tasks/activity/$', views.ActivityView.as_view(), name='tasks.activity'),
    url(r'^tasks/attempt/(?P<pk>\d+)/$', views.TaskAttemptDetailView.as_view(),
        name='tasks.attempt'),
    url(r'^tasks/verification_list/$', views.TaskVerificationListView.as_view(),
        name='tasks.verification_list'),
    url(r'^tasks/available/$', views.AvailableTasksView.as_view(), name='tasks.available'),
    url(r'^tasks/clone/(?P<clone>\d+)/$', views.CreateTaskView.as_view(), name='tasks.clone'),
    url(r'^tasks/create/$', views.CreateTaskView.as_view(), name='tasks.create'),
    url(r'^tasks/edit/(?P<pk>\d+)/$', views.UpdateTaskView.as_view(), name='tasks.edit'),
    url(r'^tasks/edit_team/(?P<pk>\d+)/$', views.UpdateTeamView.as_view(), name='tasks.edit_team'),
    url(r'^tasks/feedback/(?P<pk>\d+)/$', views.CreateFeedbackView.as_view(),
        name='tasks.feedback'),
    url(r'^tasks/import/$', views.ImportTasksView.as_view(), name='tasks.import'),
    url(r'^tasks/list/$', views.ListTasksView.as_view(), name='tasks.list'),
    url(r'^tasks/metrics/$', views.MetricsView.as_view(), name='tasks.metrics'),
    url(r'^tasks/random/$', views.RandomTasksView.as_view(), name='tasks.random'),
    url(r'^tasks/too_short/$', views.ListTooShortTasksView.as_view(), name='tasks.too_short'),
    url(r'^team/(?P<pk>\d+)/$', views.TeamView.as_view(), name='tasks.team'),
    # the next line allows for arbitraty team names to act as urls
    # e.g., oneanddone.mozilla.org/myteam/
    url(r'^(?P<url_code>[^/\\]+)/$', views.TeamView.as_view(), name='tasks.team_short'),

    # API for interacting with tasks and task areas
    url(r'^api/v1/task/$', views.TaskListAPI.as_view(), name='api-task'),
    url(r'^api/v1/task/(?P<pk>\d+)/$', views.TaskDetailAPI.as_view(),
        name='api-task-detail'),
]
