from django.contrib import admin

from oneanddone.tasks import models


class TaskAreaAdmin(admin.ModelAdmin):
    pass


class TaskAdmin(admin.ModelAdmin):
    pass


class TaskAttemptAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.TaskArea, TaskAreaAdmin)
admin.site.register(models.Task, TaskAdmin)
admin.site.register(models.TaskAttempt, TaskAttemptAdmin)
