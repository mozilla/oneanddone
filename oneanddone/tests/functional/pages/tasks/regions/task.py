# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from pypom import Region
from selenium.webdriver.common.by import By

from pages.tasks.task_details import TaskDetailsPage


class Task(Region):

    _name_locator = (By.CSS_SELECTOR, 'a.task-name')

    @property
    def name(self):
        return self.find_element(self._name_locator).text

    def click(self):
        self.find_element(self._name_locator).click()
        return TaskDetailsPage(self.selenium, self.base_url).wait_for_page_to_load()
