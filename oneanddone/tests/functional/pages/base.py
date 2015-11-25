# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from bidpom import BIDPOM
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait

from pages.page import Page


class Base(Page):

    _login_locator = (By.CSS_SELECTOR, 'a.browserid-login')
    _logout_menu_item_locator = (By.CSS_SELECTOR, 'a.browserid-logout')
    _profile_link_locator = (By.ID, 'view-profile')

    @property
    def is_user_logged_in(self):
        return not self.is_element_visible(self._login_locator)

    @property
    def is_login_button_visible(self):
        return self.is_element_visible(self._login_locator)

    @property
    def profile_link_text(self):
        return self.selenium.find_element(*self._profile_link_locator).text

    def click_login(self):
        self.selenium.find_element(*self._login_locator).click()

    def click_user_profile_details(self):
        self.selenium.find_element(*self._profile_link_locator).click()
        from pages.user.user_profile_details import UserProfileDetailsPage
        return UserProfileDetailsPage(self.base_url, self.selenium).wait_for_page_to_load()

    def expected_page(self, expectation):
        if expectation == 'user_profile_details':
            from pages.user.user_profile_details import UserProfileDetailsPage
            return UserProfileDetailsPage(self.base_url, self.selenium).wait_for_page_to_load()
        elif expectation == 'home_page':
            from pages.home import HomePage
            return HomePage(self.base_url, self.selenium).wait_for_page_to_load()

    def login(self, user):
        self.click_login()
        browser_id = BIDPOM(self.selenium, self.timeout)
        browser_id.sign_in(user['email'], user['password'])
        Wait(self.selenium, self.timeout).until(
            EC.visibility_of_element_located(self._logout_menu_item_locator))
        from pages.user.user_profile_edit import UserProfileEditPage
        return UserProfileEditPage(self.base_url, self.selenium).wait_for_page_to_load()

    def login_and_complete_profile(self, user):
        edit_profile = self.login(user)
        edit_profile.type_name(user['name'])
        edit_profile.type_username(user['name'])
        return edit_profile.click_save_button('home_page')
