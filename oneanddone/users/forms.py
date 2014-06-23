from django import forms

from tower import ugettext as _

from oneanddone.users.models import UserProfile


class SignUpForm(forms.ModelForm):
    privacy_policy_accepted = forms.BooleanField(
        label = _("You are creating a profile that will include a public username and work history. You will begin to receive email communications from Mozilla once you have completed tasks. You may unsubscribe at anytime by clicking the line at the bottom of these emails."),
        required = True,)
    username = forms.RegexField(
        label= _("Username:"),
        max_length=30, regex=r'^[a-zA-Z0-9]+$',
        error_messages = {'invalid': _("This value may contain only alphanumeric characters.")})

    class Meta:
        model = UserProfile
        fields = ('name', 'username', 'privacy_policy_accepted')


class UserProfileForm(forms.ModelForm):
    username = forms.RegexField(
        label= _("Username:"),
        max_length=30, regex=r'^[a-zA-Z0-9]+$',
        error_messages = {'invalid': _("This value may contain only alphanumeric characters.")})

    class Meta:
        model = UserProfile
        fields = ('name', 'username')
