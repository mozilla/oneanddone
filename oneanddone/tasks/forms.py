from django import forms

from epiceditor.widgets import AdminEpicEditorWidget

from oneanddone.tasks.models import Feedback, Task


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ('text',)


class TaskModelForm(forms.ModelForm):
    instructions = forms.CharField(widget=AdminEpicEditorWidget())

    class Meta:
        model = Task
