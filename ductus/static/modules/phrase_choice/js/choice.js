var phrase_choice_correct_callbacks = [];
var phrase_choice_incorrect_callbacks = [];
var phrase_choice_actions_enabled = false;

var pc_connect_click_actions = function () {
    phrase_choice_actions_enabled = true;
    $(".phrase_choice_phrase div").click(function () {
        if (!phrase_choice_actions_enabled)
            return;

        var already_called = false;
        if ($(this).parent().hasClass("correct")) {
            phrase_choice_actions_enabled = false;
            $('.ductus_phrase_choice table tr td').not('.correct').hide(500, function () {
                if (!already_called) {
                    $.each(phrase_choice_correct_callbacks, function(i, cb) { cb(); });
                }
                already_called = true;
            });
        } else {
            $(this).parent().fadeTo(200, .25, function () {
                if (!already_called) {
                    $.each(phrase_choice_incorrect_callbacks, function(i, cb) { cb(); });
                }
                already_called = true;
            });
        }
    });
};

$(function () {
    pc_connect_click_actions();
});
