# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from pages.home import HomePage


class TestAvailableTasks():

    def test_assigned_task_is_not_available(self, base_url, selenium, assigned_task, new_user):
        home_page = HomePage(selenium, base_url).open()
        home_page.login(new_user)
        available_tasks_page = home_page.click_available_tasks()
        home_page.search_for_task(assigned_task.name)
        assert len(available_tasks_page.available_tasks) == 0

    def test_one_time_task_is_available(self, base_url, selenium, nonrepeatable_task, new_user):
        home_page = HomePage(selenium, base_url).open()
        home_page.login(new_user)
        available_tasks_page = home_page.click_available_tasks()
        home_page.search_for_task(nonrepeatable_task.name)
        assert len(available_tasks_page.available_tasks) == 1

        task = available_tasks_page.available_tasks[0]
        task_details = task.click()
        assert task_details.is_get_started_button_visible
        assert not task_details.is_save_for_later_button_visible
        assert not task_details.is_abandon_task_button_visible
        assert not task_details.is_complete_task_button_visible

        task_details.click_get_started_button()
        assert not task_details.is_get_started_button_visible
        assert task_details.is_save_for_later_button_visible
        assert task_details.is_abandon_task_button_visible
        assert task_details.is_complete_task_button_visible
