# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from selenium.webdriver.common.by import By

from pages.page import PageRegion
from pages.tasks.task_details import TaskDetailsPage


class Task(PageRegion):

    _name_locator = (By.CSS_SELECTOR, 'a.task-name')

    @property
    def name(self):
        return self.root.find_element(*self._name_locator).text

    def click(self):
        self.root.find_element(*self._name_locator).click()
        return TaskDetailsPage(self.base_url, self.selenium).wait_for_page_to_load()
