# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from pages.home import HomePage


class TestUserTasks():

    def test_that_user_can_complete_a_task(self, base_url, selenium, new_user, task):
        home_page = HomePage(base_url, selenium).open()
        home_page.login_and_complete_profile(new_user)

        available_tasks_page = home_page.click_pick_a_task_button()
        assert len(available_tasks_page.available_tasks) > 0

        task = available_tasks_page.available_tasks[0]
        task_name = task.name
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

        home_page = task_details.click_save_for_later_button()

        assert home_page.is_task_in_progress
        assert task_name == home_page.task_in_progress
        task_details = home_page.click_task_in_progress()

        feedback = task_details.click_complete_task_button()

        whats_next = feedback.click_no_thanks_button()

        profile_details = whats_next.click_user_profile_details()

        assert 1 == profile_details.completed_tasks_count
        assert 1 == len(profile_details.completed_tasks)
        assert task_name == profile_details.completed_tasks[0].name

    def test_that_user_can_abandon_a_task(self, base_url, selenium, new_user, task):
        home_page = HomePage(base_url, selenium).open()
        home_page.login_and_complete_profile(new_user)

        available_tasks_page = home_page.click_pick_a_task_button()
        task_details = available_tasks_page.available_tasks[0].click()
        task_details.click_get_started_button()
        feedback = task_details.click_abandon_task_button()
        whats_next = feedback.click_no_thanks_button()

        profile_details = whats_next.click_user_profile_details()

        assert 0 == profile_details.completed_tasks_count
