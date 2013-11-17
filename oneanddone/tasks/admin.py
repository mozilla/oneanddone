from django.contrib import admin

from oneanddone.tasks import models


class TaskAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')


class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'area', 'execution_time', 'allow_multiple_finishes', 'start_date',
                    'end_date')
    list_filter = ('area', 'allow_multiple_finishes')
    search_fields = ('name', 'area__name', 'short_description')
    fieldsets = (
        (None, {
            'fields': ('name', 'area', 'execution_time')
        }),
        ('Details', {
            'fields': ('short_description', 'instructions')
        }),
        ('Availability', {
            'fields': ('allow_multiple_finishes', 'start_date', 'end_date')
        })
    )


class TaskAttemptAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'state')
    list_filter = ('state',)


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('task', 'user')
    search_fields = ('text',)


admin.site.register(models.TaskArea, TaskAreaAdmin)
admin.site.register(models.Task, TaskAdmin)
admin.site.register(models.TaskAttempt, TaskAttemptAdmin)
admin.site.register(models.Feedback, FeedbackAdmin)
