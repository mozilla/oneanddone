# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from selenium.webdriver.common.by import By

from pages.base import Base
from pages.tasks.whats_next import WhatsNextPage


class TaskFeedbackPage(Base):

    _name_locator = (By.CSS_SELECTOR, 'main.billboard.content-container.feedback > h1')
    _no_thanks_button_locator = (By.CSS_SELECTOR, 'a.no-feedback')

    @property
    def _page_title(self):
        return '%s | Mozilla One and Done' % self.name

    @property
    def name(self):
        return self.selenium.find_element(*self._name_locator).text

    def click_no_thanks_button(self):
        self.selenium.find_element(*self._no_thanks_button_locator).click()
        return WhatsNextPage(self.base_url, self.selenium).wait_for_page_to_load()
