# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from pages.home import HomePage


class TestTaskDetails():

    @pytest.mark.nondestructive
    def test_that_person_can_view_task_details(self, base_url, selenium, task):
        home_page = HomePage(base_url, selenium).open()
        assert not home_page.is_user_logged_in

        task = home_page.suggested_first_tasks[0]
        task_name = task.name
        task_details = task.click()
        assert task_name == task_details.name

        assert task_details.is_get_started_button_visible
        assert not task_details.is_abandon_task_button_visible
        assert not task_details.is_complete_task_button_visible
        assert not task_details.is_save_for_later_button_visible

        team_name = task_details.team
        assert team_name
        team_details = task_details.click_team()
        assert team_name in team_details.page_heading
