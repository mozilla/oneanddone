# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template
from django.utils.translation import ugettext as _, ugettext_lazy as _lazy

from django_ace import AceWidget
from requests.exceptions import RequestException
from urlparse import urlparse, parse_qs

from oneanddone.base.widgets import CalendarInput
from oneanddone.tasks.bugzilla_utils import BugzillaUtils
from oneanddone.tasks.models import (BugzillaBug, Feedback, Task,
                                     TaskAttemptCommunication,
                                     TaskImportBatch,
                                     TaskInvalidationCriterion,
                                     TaskTeam)
from oneanddone.users.models import User


class SendEmail(object):
    """
    Helper to send emails after user and/or admin actions.
    """
    def send_email(self,
                   attempt,
                   base_url,
                   email_type,
                   communication_content=None,
                   feedback=None):
        """
        Send an email to the user or an admin after a verification action.

        :param attempt: The attempt being verified
        :param base_url: The base url for the site
        :param email_type: The type of email to send
        :param communication_content (default None): The content of the communication
        :param feedback (default None): A Feedback object
        """
        type_data_dict = {
            'feedback':
            {'subject': "Feedback on %s from One and Done",
             'template': 'feedback_email.txt',
             'to_email': attempt.task.owner.email},
            'verified':
            {'subject': "One and Done task '%s' verified as complete!",
             'template': 'verification_complete_email.txt',
             'to_email': attempt.user.display_email},
            'verify_from_user':
            {'subject': 'One and Done task verification requested for %s',
             'template': 'verification_email_user.txt',
             'to_email': attempt.task.owner.email},
            'verify_from_admin':
            {'subject': 'One and Done task verification update for %s',
             'template': 'verification_email_admin.txt',
             'to_email': attempt.user.display_email}}
        data = type_data_dict[email_type]
        task_name = attempt.task.name
        subject = data['subject'] % task_name
        template = get_template('tasks/emails/%s' % data['template'])
        message = template.render({
            'attempt_link': '%s/tasks/attempt/%s' % (base_url, attempt.id),
            'content': communication_content,
            'feedback': feedback and feedback.text,
            'feedback_link': feedback and '%s/admin/tasks/feedback/%s' % (
                base_url, feedback.id),
            'task_link': base_url + attempt.task.get_absolute_url(),
            'task_name': task_name,
            'task_state': attempt.get_state_display(),
            'time_spent_on_task': feedback and feedback.time_spent_in_minutes,
            'user': attempt.user})

        # Manually replace quotes and double-quotes as these get
        # escaped by the template and this makes the message look bad.
        filtered_message = message.replace('&#34;', '"').replace('&#39;', "'")
        send_mail(
            subject,
            filtered_message,
            settings.SERVER_EMAIL,
            [data['to_email']])


class BaseTaskInvalidCriteriaFormSet(forms.formsets.BaseFormSet):
    # make it impossible to submit an empty form as part of the formset
    def __init__(self, *args, **kwargs):
        super(BaseTaskInvalidCriteriaFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False


class FeedbackForm(forms.ModelForm, SendEmail):
    time_spent_in_minutes = forms.IntegerField(
        label=_lazy(u'How many minutes did you spend on the task?'))

    class Meta:
        model = Feedback
        fields = ('text', 'time_spent_in_minutes')


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


class SubmitVerifiedTaskForm(forms.ModelForm, SendEmail):

    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': 'fill-width'}))

    class Meta:
        model = TaskAttemptCommunication
        fields = ('content',)


class TaskForm(forms.ModelForm):
    keywords = (forms.CharField(
                help_text=_lazy(u'Please use commas to separate your keywords.'),
                required=False,
                widget=forms.TextInput(attrs={'class': 'medium-field'})))
    owner = forms.ModelChoiceField(
        queryset=User.objects.filter(
            is_staff=True).order_by('profile__name').exclude(profile__name=None))
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
                self.add_error('start_date',
                               forms.ValidationError(_("'End date' must be after "
                                                       "'Start date'")))
        if cleaned_data.get('must_be_verified'):
            if not cleaned_data.get('verification_instructions'):
                self.add_error('verification_instructions',
                               forms.ValidationError(_("If the task is a Verified task "
                                                       "then you must provide some "
                                                       "verification instructions")))
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
                  'is_draft', 'is_invalid', 'owner', 'next_task', 'must_be_verified',
                  'verification_instructions')
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
            'verification_instructions': forms.Textarea(attrs={'rows': 4, 'class': 'fill-width'}),
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


class TeamForm(forms.ModelForm):
    url_code = forms.RegexField(
        label=_lazy(u'Team url suffix:'),
        help_text=_lazy(u'This will be added to the end of https://oneanddone.mozilla.org/'),
        max_length=30, regex=r'^[a-zA-Z0-9]+$',
        error_messages={'invalid': _lazy(u'This value may contain only alphanumeric characters.')})

    def save(self, creator, *args, **kwargs):
        self.instance.creator = creator
        return super(TeamForm, self).save(*args, **kwargs)

    class Media:
        css = {
            'all': ('css/admin_ace.css',)
        }

    class Meta:
        model = TaskTeam
        fields = ('description', 'name', 'url_code')
        widgets = {
            'description': AceWidget(mode='markdown', theme='textmate', width='800px',
                                     height='300px', wordwrap=True,
                                     attrs={'class': 'fill-width'}),
            'name': forms.TextInput(attrs={'size': 100, 'class': 'fill-width'}),
            'url_code': forms.TextInput(attrs={'size': 100, 'class': 'fill-width'}),
        }
