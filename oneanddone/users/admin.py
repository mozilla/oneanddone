from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from oneanddone.users import models


class MyUserAdmin(UserAdmin):

    list_display = ('username', 'display_email', 'is_staff', 'is_superuser',
                    'last_login', 'date_joined')

    def get_queryset(self, request):
        """
        Only return users if they have signed the privacy policy.
        """
        qs = super(MyUserAdmin, self).get_queryset(request)
        return qs.filter(profile__privacy_policy_accepted=True)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'username', 'privacy_policy_accepted', 'email', 'bugzilla_email')
    readonly_fields = ('user', 'name', 'username', 'email', 'bugzilla_email')

    def get_queryset(self, request):
        """
        Only return profiles for users if they have signed the privacy policy.
        """
        qs = super(UserProfileAdmin, self).get_queryset(request)
        return qs.filter(privacy_policy_accepted=True)


admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
admin.site.register(models.UserProfile, UserProfileAdmin)
