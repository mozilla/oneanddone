from django.contrib import admin

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


class TaskTeamAdmin(RecordCreatorMixin, admin.ModelAdmin):
    list_display = ('name', 'creator', 'modified')
    readonly_fields = ('creator', 'modified')


class TaskProjectAdmin(RecordCreatorMixin, admin.ModelAdmin):
    list_display = ('name', 'creator', 'modified')
    readonly_fields = ('creator', 'modified')


class TaskTypeAdmin(RecordCreatorMixin, admin.ModelAdmin):
    list_display = ('name', 'creator', 'modified')
    readonly_fields = ('creator', 'modified')


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


admin.site.register(models.TaskTeam, TaskTeamAdmin)
admin.site.register(models.TaskProject, TaskProjectAdmin)
admin.site.register(models.TaskType, TaskTeamAdmin)
admin.site.register(models.TaskAttempt, TaskAttemptAdmin)
admin.site.register(models.Feedback, FeedbackAdmin)
