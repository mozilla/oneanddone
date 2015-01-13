# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django import forms

from django_ace import AceWidget
from requests.exceptions import RequestException
from tower import ugettext as _
from urlparse import urlparse, parse_qs

from oneanddone.base.widgets import CalendarInput
from oneanddone.tasks.bugzilla_utils import BugzillaUtils
from oneanddone.tasks.models import (BugzillaBug, Feedback, Task,
                                     TaskImportBatch,
                                     TaskInvalidationCriterion)
from oneanddone.users.models import User


class BaseTaskInvalidCriteriaFormSet(forms.formsets.BaseFormSet):
    # make it impossible to submit an empty form as part of the formset
    def __init__(self, *args, **kwargs):
        super(BaseTaskInvalidCriteriaFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ('text',)


class PreviewConfirmationForm(forms.Form):
    """ Used to create a multi-step object-creation/update process, with a
        chance to preview and cancel changes before committing them.
    """
    submission_stages = ('fill', 'preview', 'confirm')
    stage = forms.CharField(widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super(PreviewConfirmationForm, self).clean()
        if cleaned_data.get('stage') not in self.submission_stages:
            raise forms.ValidationError(_('Form data is missing or has been '
                                          'tampered.'))
        return cleaned_data


class TaskForm(forms.ModelForm):
    keywords = (forms.CharField(
                help_text=_('Please use commas to separate your keywords.'),
                required=False,
                widget=forms.TextInput(attrs={'class': 'medium-field'})))
    owner = forms.ModelChoiceField(queryset=User.objects.filter(is_staff=True).order_by('profile__name'))
    next_task = forms.ModelChoiceField(
        queryset=Task.objects.filter(Task.is_available_filter()).order_by('name'),
        required=False)

    def __init__(self, *args, **kwargs):
        if kwargs['instance']:
            initial = kwargs.get('initial', {})
            initial['keywords'] = kwargs['instance'].keywords_list
            kwargs['initial'] = initial
        super(TaskForm, self).__init__(*args, **kwargs)

    def _process_keywords(self, creator):
        form_keywords = self.cleaned_data['keywords'].split(',')
        # When cloning a task we need to process/add the keywords even
        # they weren't changed in the form.
        if ('keywords' in self.changed_data or
                self.instance.keyword_set.count() != len(form_keywords)):
            kw = [k.strip() for k in form_keywords]
            self.instance.replace_keywords(kw, creator)

    def clean(self):
        cleaned_data = super(TaskForm, self).clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date:
            if start_date >= end_date:
                raise forms.ValidationError(_("'End date' must be after 'Start date'"))
        return cleaned_data

    def save(self, creator, *args, **kwargs):
        self.instance.creator = creator
        super(TaskForm, self).save(*args, **kwargs)
        if kwargs.get('commit', True):
            self._process_keywords(creator)
        return self.instance

    class Media:
        css = {
            'all': ('css/admin_ace.css',)
        }

    class Meta:
        model = Task
        fields = ('name', 'short_description', 'execution_time', 'difficulty',
                  'priority', 'repeatable', 'team', 'project', 'type', 'start_date',
                  'end_date', 'why_this_matters', 'prerequisites', 'instructions',
                  'is_draft', 'is_invalid', 'owner', 'next_task')
        widgets = {
            'name': forms.TextInput(attrs={'size': 100, 'class': 'fill-width'}),
            'short_description': forms.TextInput(attrs={'size': 100, 'class': 'fill-width'}),
            'instructions': AceWidget(mode='markdown', theme='textmate', width='800px',
                                      height='300px', wordwrap=True,
                                      attrs={'class': 'fill-width'}),
            'start_date': CalendarInput,
            'end_date': CalendarInput,
            'why_this_matters': forms.Textarea(attrs={'rows': 2, 'class': 'fill-width'}),
            'prerequisites': forms.Textarea(attrs={'rows': 4, 'class': 'fill-width'}),
        }


class TaskImportBatchForm(forms.ModelForm):
    def clean(self):
        max_results = 100
        max_batch_size = 20
        cleaned_data = super(TaskImportBatchForm, self).clean()
        query_url = cleaned_data.get('query', '')
        query = parse_qs(urlparse(query_url).query)
        if not query:
            raise forms.ValidationError(_('For the query URL, please provide '
                                          'a full URL that includes search '
                                          'parameters.'))

        try:
            bugcount = BugzillaUtils().request_bugcount(query)
        except ValueError as e:
            raise forms.ValidationError(_(' '.join(['External error:', str(e)])))
        except (RuntimeError, RequestException):
            raise forms.ValidationError(_('Sorry. we cannot retrieve any '
                                          'data from Bugzilla at this time. '
                                          'Please report this to the One and '
                                          'Done team.'))

        if not bugcount:
            raise forms.ValidationError(_('Your query does not return any results.'))
        elif bugcount > max_results:
            message = _('Your query returns more than '
                        '{num} items.').format(num=str(max_results))
            raise forms.ValidationError(message)

        fresh_bugs = self._get_fresh_bugs(query_url, query, bugcount, max_batch_size)

        if not fresh_bugs:
            message = _('The results of this query have all been imported '
                        'before. To import these results again as different '
                        'tasks, please use a different query.')
            raise forms.ValidationError(message)

        cleaned_data['_fresh_bugs'] = fresh_bugs

        return cleaned_data

    def save(self, creator, *args, **kwargs):
        self.instance.creator = creator
        super(TaskImportBatchForm, self).save(*args, **kwargs)
        return self.instance

    @staticmethod
    def _get_fresh_bugs(query_url, query, max_results, max_batch_size):
        ''' Returns at most first `max_batch_size` bugs (ordered by bug id)
            that have not already been imported via `query`.
        '''
        existing_bug_ids = BugzillaBug.objects.filter(
            tasks__batch__query__exact=query_url).values_list('bugzilla_id',
                                                              flat=True)

        def fetch(query, limit, offset):
            new_bugs = BugzillaUtils().request_bugs(query, limit=limit, offset=offset)
            return [bug for bug in new_bugs if bug['id'] not in existing_bug_ids]

        fresh_bugs = []
        for offset in range(0, max_results, max_batch_size):
            fresh_bugs.extend(fetch(query, max_batch_size, offset))
            if len(fresh_bugs) >= max_batch_size:
                return fresh_bugs[:max_batch_size]
        return fresh_bugs

    class Meta:
        model = TaskImportBatch
        fields = ('description', 'query')
        widgets = {
            'query': forms.TextInput(attrs={'size': 100, 'class': 'fill-width'}),
            'description': forms.TextInput(attrs={'size': 100, 'class': 'fill-width'})}


class TaskInvalidationCriterionForm(forms.Form):
    criterion = forms.ModelChoiceField(
        queryset=TaskInvalidationCriterion.objects.all())


TaskInvalidCriteriaFormSet = forms.formsets.formset_factory(
    TaskInvalidationCriterionForm,
    formset=BaseTaskInvalidCriteriaFormSet)
