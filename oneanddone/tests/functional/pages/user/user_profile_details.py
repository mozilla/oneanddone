# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from selenium.webdriver.common.by import By

from pages.base import Base
from pages.page import PageRegion
from pages.tasks.task_details import TaskDetailsPage
from pages.user.user_profile_edit import UserProfileEditPage


class UserProfileDetailsPage(Base):

    _bugzilla_email_locator = (By.CSS_SELECTOR, '#bugzilla-email span')
    _completed_tasks_list_locator = (By.CSS_SELECTOR, '.task-status > ul > li')
    _edit_profile_button_locator = (By.ID, 'edit-profile')
    _tasks_completed_locator = (By.CSS_SELECTOR, '#completed-tasks-count span')
    _user_profile_name_locator = (By.CSS_SELECTOR, '#user-profile-name span')
    _user_profile_url_locator = (By.CSS_SELECTOR, '#user-profile-url span')

    @property
    def _page_title(self):
        return 'User profile for %s | Mozilla One and Done' % self.user_profile_name

    @property
    def bugzilla_email(self):
        return self.selenium.find_element(*self._bugzilla_email_locator).text

    @property
    def completed_tasks_count(self):
        return int(self.selenium.find_element(*self._tasks_completed_locator).text)

    @property
    def completed_tasks(self):
        return [self.Task(self.base_url, self.selenium, web_element) for web_element in
                self.selenium.find_elements(*self._completed_tasks_list_locator)]

    @property
    def user_profile_name(self):
        return self.selenium.find_element(*self._user_profile_name_locator).text

    @property
    def user_profile_url(self):
        return self.selenium.find_element(*self._user_profile_url_locator).text

    def click_edit_profile_button(self):
        self.selenium.find_element(*self._edit_profile_button_locator).click()
        return UserProfileEditPage(self.base_url, self.selenium).wait_for_page_to_load()

    class Task(PageRegion):
        _name_locator = (By.CSS_SELECTOR, 'a')

        @property
        def name(self):
            return self.root.find_element(*self._name_locator).text

        def click(self):
            self.root.find_element(*self._name_locator).click()
            return TaskDetailsPage(self.base_url, self.selenium).wait_for_page_to_load()
