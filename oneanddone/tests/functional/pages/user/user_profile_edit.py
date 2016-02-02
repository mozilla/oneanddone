# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from selenium.webdriver.common.by import By

from pages.base import Base
from pages.user.user_profile_delete import UserProfileDeletePage


class UserProfileEditPage(Base):

    _bugzilla_email_input_locator = (By.ID, 'id_bugzilla_email')
    _delete_profile_button_locator = (By.ID, 'delete-profile')
    _name_input_locator = (By.ID, 'id_name')
    _privacy_policy_checkbox_locator = (By.ID, 'id_pp_checkbox')
    _save_button_locator = (By.ID, 'save-profile')
    _user_profile_url_input_locator = (By.ID, 'id_personal_url')
    _username_input_locator = (By.ID, 'id_username')

    @property
    def bugzilla_email(self):
        return self.find_element(
            self._bugzilla_email_input_locator).get_attribute('value')

    @bugzilla_email.setter
    def bugzilla_email(self, value):
        self.set_field(self._bugzilla_email_input_locator, value)

    @property
    def display_name(self):
        return self.find_element(self._name_input_locator).get_attribute('value')

    @display_name.setter
    def display_name(self, fullname):
        self.set_field(self._name_input_locator, fullname)

    @property
    def is_privacy_policy_checkbox_checked(self):
        return self.find_element(self._privacy_policy_checkbox_locator).is_selected()

    @property
    def user_profile_url(self):
        return self.find_element(
            self._user_profile_url_input_locator).get_attribute('value')

    @user_profile_url.setter
    def user_profile_url(self, url):
        self.set_field(self._user_profile_url_input_locator, url)

    @property
    def username(self):
        return self.find_element(self._username_input_locator).get_attribute('value')

    @username.setter
    def username(self, username):
        self.set_field(self._username_input_locator, username)

    def click_delete_profile_button(self):
        self.find_element(self._delete_profile_button_locator).click()
        return UserProfileDeletePage(self.selenium, self.base_url).wait_for_page_to_load()

    def click_save_button(self, expectation):
        self.find_element(self._save_button_locator).click()
        return self.expected_page(expectation)

    def toggle_privacy_policy_checkbox(self):
        self.find_element(self._privacy_policy_checkbox_locator).click()
