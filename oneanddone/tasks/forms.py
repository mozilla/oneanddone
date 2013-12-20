from django import forms

from django_ace import AceWidget

from oneanddone.tasks.models import Feedback, Task


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ('text',)


class TaskModelForm(forms.ModelForm):
    instructions = forms.CharField(widget=AceWidget(mode='markdown', theme='textmate', width='800px',
                                                    height='600px', wordwrap=True))

    class Meta:
        model = Task

    class Media:
        css = {
            'all': ('css/admin_ace.css',)
        }

    instructions.help_text = ('Instructions are written in <a href="http://markdowntutorial.com/" target="_blank">Markdown</a>.')
