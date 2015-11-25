# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from pages.home import HomePage


class TestLogin():

    def test_that_a_new_user_can_login(self, base_url, selenium, new_user):
        home_page = HomePage(base_url, selenium).open()
        assert not home_page.is_user_logged_in

        edit_profile = home_page.login(new_user)
        assert edit_profile.is_user_logged_in

        edit_profile.type_name(new_user['name'])
        edit_profile.type_username(new_user['name'])
        assert edit_profile.is_privacy_policy_checkbox_checked
        home_page = edit_profile.click_save_button('home_page')

        assert new_user['name'].upper() in home_page.profile_link_text
        assert new_user['name'] in home_page.displayed_profile_name
