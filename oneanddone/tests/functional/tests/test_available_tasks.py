# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from pages.home import HomePage


class TestAvailableTasks():

    @pytest.mark.nondestructive
    def test_available_tasks(self, base_url, selenium, task):
        home_page = HomePage(base_url, selenium).open()
        assert not home_page.is_user_logged_in

        available_tasks_page = home_page.click_available_tasks()
        assert available_tasks_page.is_available_tasks_list_visible
        assert len(available_tasks_page.available_tasks) > 0

        task = available_tasks_page.available_tasks[0]
        task_name = task.name
        task_details = task.click()
        assert task_name == task_details.name
