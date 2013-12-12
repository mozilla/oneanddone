/*
* This Source Code Form is subject to the terms of the Mozilla Public
* License, v. 2.0. If a copy of the MPL was not distributed with this
* file, You can obtain one at http://mozilla.org/MPL/2.0/.
*/
$(function() {
    $('.range-row input')
        .on('input', showSliderValue)
        .on('change', showSliderValue)
        .change();

    function showSliderValue() {
        var $input = $(this);
        var $label = $input.siblings('.range-label');
        $label.text($input.val());
    }
});
