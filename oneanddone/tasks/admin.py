from django.contrib import admin

from oneanddone.tasks import models


class RecordCreatorMixin(object):
    """
    Record the creator when an instance is created via tha admin.
    """
    def save_model(self, request, obj, form, change):
        if obj.pk is None:
            obj.creator = request.user
        super(RecordCreatorMixin, self).save_model(request, obj, form, change)


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'state', 'created', 'time_spent_in_minutes')
    search_fields = ('text',)
    readonly_fields = ('task', 'user', 'state', 'text')
    exclude = ('attempt',)

    def task(self, feedback):
        return feedback.attempt.task

    def user(self, feedback):
        return feedback.attempt.user

    def state(self, feedback):
        return feedback.attempt.get_state_display()


class TaskAttemptAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'state', 'modified')
    list_filter = ('state',)
    readonly_fields = ('task', 'user', 'state')


class TaskInvalidationCriterionAdmin(RecordCreatorMixin, admin.ModelAdmin):
    list_display = ('field_name', 'relation', 'field_value',
                    'creator', 'modified')
    readonly_fields = ('creator', 'modified')
    exclude = ('batches',)


class TaskProjectAdmin(RecordCreatorMixin, admin.ModelAdmin):
    list_display = ('name', 'creator', 'modified')
    readonly_fields = ('creator', 'modified')


class TaskTeamAdmin(RecordCreatorMixin, admin.ModelAdmin):
    list_display = ('name', 'creator', 'modified')
    readonly_fields = ('creator', 'modified')


class TaskTypeAdmin(RecordCreatorMixin, admin.ModelAdmin):
    list_display = ('name', 'creator', 'modified')
    readonly_fields = ('creator', 'modified')


admin.site.register(models.Feedback, FeedbackAdmin)
admin.site.register(models.TaskAttempt, TaskAttemptAdmin)
admin.site.register(models.TaskInvalidationCriterion,
                    TaskInvalidationCriterionAdmin)
admin.site.register(models.TaskProject, TaskProjectAdmin)
admin.site.register(models.TaskTeam, TaskTeamAdmin)
admin.site.register(models.TaskType, TaskTeamAdmin)
