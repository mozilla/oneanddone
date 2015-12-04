# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from pages.home import HomePage


class TestHomePage():

    @pytest.mark.nondestructive
    def test_home_page(self, base_url, selenium, task):
        home_page = HomePage(base_url, selenium).open()
        assert home_page.is_login_button_visible
        assert home_page.is_suggested_first_tasks_heading_visible
        assert len(home_page.suggested_first_tasks) > 0
