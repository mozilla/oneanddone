# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from selenium.webdriver.common.by import By

from pages.base import Base
from pages.tasks.regions.task import Task


class TeamDetailsPage(Base):

    _page_heading = (By.CSS_SELECTOR, '.content-container > h2')

    _task_list_header_locator = (By.CSS_SELECTOR, 'div.task-list-container > h3')
    _available_task_list_locator = (By.CSS_SELECTOR, '.task-list > li')

    @property
    def page_heading(self):
        return self.selenium.find_element(*self._page_heading).text

    @property
    def task_list_header(self):
        return self.selenium.find_element(*self._task_list_header_locator).text

    @property
    def available_tasks(self):
        return [Task(self.base_url, self.selenium, web_element)
                for web_element in self.selenium.find_elements(*self._available_task_list_locator)]
