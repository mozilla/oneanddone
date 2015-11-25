# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait as Wait


TIMEOUT = 10


class Page(object):

    _page_title = None
    _url = None

    def __init__(self, base_url, selenium):
        self.base_url = base_url
        self.selenium = selenium
        self.timeout = TIMEOUT

    @property
    def is_the_current_page(self):
        if self._page_title is not None:
            Wait(self.selenium, self.timeout).until(lambda s: s.title)
            assert self._page_title == self.selenium.title
        return True

    @property
    def url(self):
        if self._url is not None:
            return self._url.format(base_url=self.base_url)
        return self.base_url

    def is_element_visible(self, locator):
        try:
            return self.selenium.find_element(*locator).is_displayed()
        except (NoSuchElementException,):
            return False

    def open(self):
        self.selenium.get(self.url)
        return self.wait_for_page_to_load()

    def type_in_element(self, locator, text):
        text_fld = self.selenium.find_element(*locator)
        text_fld.clear()
        text_fld.send_keys(text)

    def wait_for_page_to_load(self):
        assert self.is_the_current_page
        return self


class PageRegion(object):

    _root_locator = None

    def __init__(self, base_url, selenium, root=None):
        self.base_url = base_url
        self.selenium = selenium
        self.timeout = TIMEOUT
        self.root_element = root

    @property
    def root(self):
        if self.root_element is None and self._root_locator is not None:
            self.root_element = self.selenium.find_element(*self._root_locator)
        return self.root_element
