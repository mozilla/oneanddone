from django.contrib import admin

from mptt.admin import MPTTModelAdmin

from oneanddone.tasks import models


class TaskAreaAdmin(MPTTModelAdmin):
    pass


class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'area_full_name', 'execution_time', 'is_available',
                    'start_date', 'end_date')
    list_filter = ['area']
    search_fields = ('name', 'area__name', 'short_description')
    fieldsets = (
        (None, {
            'fields': ('name', 'area', 'execution_time')
        }),
        ('Details', {
            'fields': ('short_description', 'instructions')
        }),
        ('Availability', {
            'fields': ('start_date', 'end_date')
        })
    )

    def is_available(self, task):
        return task.is_available
    is_available.boolean = True

    def area_full_name(self, task):
        return task.area.full_name


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
