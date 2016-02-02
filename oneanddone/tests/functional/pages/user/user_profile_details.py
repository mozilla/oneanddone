# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from selenium.webdriver.common.by import By

from pages.base import Base
from pages.tasks.regions.task import Task
from pages.user.user_profile_edit import UserProfileEditPage


class UserProfileDetailsPage(Base):

    URL_TEMPLATE = '/profile'

    _bugzilla_email_locator = (By.CSS_SELECTOR, '#bugzilla-email span')
    _completed_tasks_list_locator = (By.CSS_SELECTOR, '.task-status > ul > li')
    _edit_profile_button_locator = (By.ID, 'edit-profile')
    _tasks_completed_locator = (By.CSS_SELECTOR, '#completed-tasks-count span')
    _user_profile_name_locator = (By.CSS_SELECTOR, '#user-profile-name span')
    _user_profile_url_locator = (By.CSS_SELECTOR, '#user-profile-url span')

    @property
    def bugzilla_email(self):
        return self.find_element(self._bugzilla_email_locator).text

    @property
    def completed_tasks_count(self):
        return int(self.find_element(self._tasks_completed_locator).text)

    @property
    def completed_tasks(self):
        return [Task(self, web_element) for web_element in
                self.find_elements(self._completed_tasks_list_locator)]

    @property
    def user_profile_name(self):
        return self.find_element(self._user_profile_name_locator).text

    @property
    def user_profile_url(self):
        return self.find_element(self._user_profile_url_locator).text

    def click_edit_profile_button(self):
        self.find_element(self._edit_profile_button_locator).click()
        return UserProfileEditPage(self.selenium, self.base_url).wait_for_page_to_load()
