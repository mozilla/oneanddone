from django import forms

from tower import ugettext as _

from oneanddone.base.widgets import MyURLField
from oneanddone.users.models import UserProfile


class SignUpForm(forms.ModelForm):
    pp_checkbox = forms.BooleanField(
        label=_("You are creating a profile that will include a public username"
                " and work history."
                " You will begin to receive email communications from Mozilla"
                " once you have completed tasks."
                " You may configure email preferences when editing your profile."),
        required=True,
        initial=True)
    username = forms.RegexField(
        label=_("Username:"),
        max_length=30, regex=r'^[a-zA-Z0-9]+$',
        error_messages={'invalid': _("This value may contain only alphanumeric characters.")})
    personal_url = MyURLField(label=_('Personal URL:'))

    class Meta:
        model = UserProfile
        fields = ('name', 'username', 'pp_checkbox', 'personal_url')

    def save(self, *args, **kwargs):
        # We will only reach the save() method if the pp_checkbox was checked
        self.instance.privacy_policy_accepted = True
        return super(SignUpForm, self).save(*args, **kwargs)


class UserProfileForm(forms.ModelForm):
    username = forms.RegexField(
        label=_("Username:"),
        max_length=30, regex=r'^[a-zA-Z0-9]+$',
        error_messages={'invalid': _("This value may contain only alphanumeric characters.")})
    consent_to_email = forms.BooleanField(required=False)
    personal_url = MyURLField(label=_('Personal URL:'))

    class Meta:
        model = UserProfile
        fields = ('name', 'username', 'consent_to_email', 'personal_url')
