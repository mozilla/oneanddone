# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from selenium.webdriver.common.by import By

from pages.base import Base
from pages.home import HomePage


class UserProfileDeletePage(Base):

    _page_title = 'Delete profile | Mozilla One and Done'

    _cancel_button_locator = (By.ID, 'cancel-button')
    _confirm_button_locator = (By.ID, 'confirm-button')

    def click_cancel_button(self):
        self.selenium.find_element(*self._cancel_button_locator).click()
        return HomePage(self.base_url, self.selenium).wait_for_page_to_load()

    def click_confirm_button(self):
        self.selenium.find_element(*self._confirm_button_locator).click()
        return HomePage(self.base_url, self.selenium).wait_for_page_to_load()
