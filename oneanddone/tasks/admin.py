from django.contrib import admin

from mptt.admin import MPTTModelAdmin

from oneanddone.tasks import models
from oneanddone.tasks.forms import TaskModelForm


class RecordCreatorMixin(object):
    """
    Record the creator when an instance is created via tha admin.
    """
    def save_model(self, request, obj, form, change):
        if obj.pk is None:
            obj.creator = request.user
        super(RecordCreatorMixin, self).save_model(request, obj, form, change)


class TaskAreaAdmin(RecordCreatorMixin, MPTTModelAdmin):
    exclude = ('creator',)


class TaskAdmin(RecordCreatorMixin, admin.ModelAdmin):
    form = TaskModelForm
    list_display = ('name', 'area_full_name', 'execution_time', 'is_available',
                    'start_date', 'end_date', 'is_draft')
    list_filter = ('area', 'is_draft')
    search_fields = ('name', 'area__name', 'short_description')
    fieldsets = (
        (None, {
            'fields': ('name', 'area', 'execution_time')
        }),
        ('Details', {
            'fields': ('short_description', 'instructions')
        }),
        ('Availability', {
            'fields': ('start_date', 'end_date', 'is_draft')
        })
    )

    def is_available(self, task):
        return task.is_available
    is_available.boolean = True

    def area_full_name(self, task):
        return task.area.full_name


class TaskAttemptAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'state', 'modified')
    list_filter = ('state',)
    readonly_fields = ('task', 'user', 'state')


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'state', 'created')
    search_fields = ('text',)
    readonly_fields = ('task', 'user', 'state', 'text')
    exclude = ('attempt',)

    def task(self, feedback):
        return feedback.attempt.task

    def user(self, feedback):
        return feedback.attempt.user

    def state(self, feedback):
        return feedback.attempt.get_state_display()


admin.site.register(models.TaskArea, TaskAreaAdmin)
admin.site.register(models.Task, TaskAdmin)
admin.site.register(models.TaskAttempt, TaskAttemptAdmin)
admin.site.register(models.Feedback, FeedbackAdmin)
