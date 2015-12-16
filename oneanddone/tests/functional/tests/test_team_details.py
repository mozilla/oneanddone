# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from pages.home import HomePage


class TestTeamDetails():

    @pytest.mark.nondestructive
    def test_that_person_can_view_team_details(self, base_url, selenium, task):
        home_page = HomePage(base_url, selenium).open()
        assert not home_page.is_user_logged_in

        task = home_page.suggested_first_tasks[0]
        task_name = task.name
        task_details = task.click()
        assert task_name == task_details.name

        team_name = task_details.team
        team_details = task_details.click_team()

        assert team_name in team_details.page_heading
        assert team_details.task_list_header
        assert team_name in team_details.task_list_header
        assert len(team_details.available_tasks) > 0
