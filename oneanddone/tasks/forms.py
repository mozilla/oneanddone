from django import forms

from oneanddone.tasks.models import Feedback


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ('text',)
