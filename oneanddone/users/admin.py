from django.contrib import admin

from oneanddone.users import models


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'username', 'privacy_policy_accepted')
    readonly_fields = ('name', 'username')


admin.site.register(models.UserProfile, UserProfileAdmin)
