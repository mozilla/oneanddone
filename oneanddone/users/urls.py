# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.conf.urls import patterns, url

from oneanddone.users import views


urlpatterns = patterns('',
    url(r'^login/$', views.LoginView.as_view(), name='users.login'),
    url(r'^profile/new/$', views.CreateProfileView.as_view(), name='users.profile.create'),
    url(r'^profile/edit/$', views.UpdateProfileView.as_view(), name='users.profile.update'),
    url(r'^profile/delete/$', views.DeleteProfileView.as_view(), name='users.profile.delete'),
    url(r'^profile/$', views.MyProfileDetailsView.as_view(), name='users.profile.mydetails'),
    url(r'^profile/(?P<id>\d+)/$', views.ProfileDetailsView.as_view(), name='users.profile.details'),
    url(r'^profile/(?P<username>[^/\\]+)/$', views.ProfileDetailsView.as_view(), name='users.profile.details'),

    # API URL's for interacting with User objects
    url(r'^api/v1/user/$', views.UserListAPI.as_view(), name='api-user'),
    url(r'^api/v1/user/(?P<email>[^/\\]+)/$', views.UserDetailAPI.as_view(), name='api-user-detail'),
)
