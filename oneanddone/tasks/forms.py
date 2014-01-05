# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
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
