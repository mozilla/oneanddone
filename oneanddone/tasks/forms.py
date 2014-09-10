# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django import forms

from django_ace import AceWidget
from tower import ugettext as _

from oneanddone.tasks.models import Feedback, Task
from oneanddone.tasks.widgets import CalendarInput, HorizRadioSelect


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ('text',)


class TaskForm(forms.ModelForm):
    keywords = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': 50}))

    def __init__(self, *args, **kwargs):
        if kwargs['instance']:
            initial = kwargs.get('initial', {})
            initial['keywords'] = kwargs['instance'].keywords_list
            kwargs['initial'] = initial
        super(TaskForm, self).__init__(*args, **kwargs)
        # self.fields['keywords'].value = self.instance.keywords_list

    def save(self, creator, *args, **kwargs):
        self.instance.creator = creator
        super(TaskForm, self).save(*args, **kwargs)
        self._process_keywords(creator)

    def _process_keywords(self, creator):
        if 'keywords' in self.changed_data:
            for taskkeyword in self.instance.keyword_set.all():
                taskkeyword.delete()
            for keyword in self.cleaned_data['keywords'].split(','):
                if len(keyword.strip()):
                    self.instance.keyword_set.create(name=keyword.strip(), creator=creator)

    def clean(self):
        cleaned_data = super(TaskForm, self).clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date:
            if start_date >= end_date:
                raise forms.ValidationError(_("'End date' must be after 'Start date'"))
        return cleaned_data

    class Meta:
        model = Task
        fields = ('name', 'short_description', 'execution_time', 'difficulty',
                  'priority', 'repeatable', 'team', 'project', 'type', 'start_date',
                  'end_date', 'why_this_matters', 'prerequisites', 'instructions',
                  'is_draft')
        widgets = {
            'name': forms.TextInput(attrs={'size': 100}),
            'short_description': forms.TextInput(attrs={'size': 100}),
            'execution_time': HorizRadioSelect,
            'instructions': AceWidget(mode='markdown', theme='textmate', width='800px',
                                      height='300px', wordwrap=True),
            'start_date': CalendarInput,
            'end_date': CalendarInput,
            'why_this_matters': forms.Textarea(attrs={'cols': 100, 'rows': 2}),
            'prerequisites': forms.Textarea(attrs={'cols': 100, 'rows': 4}),
        }

    class Media:
        css = {
            'all': ('css/admin_ace.css',)
        }


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
