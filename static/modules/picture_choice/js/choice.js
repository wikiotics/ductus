var picture_choice_correct_callbacks = [];
var picture_choice_incorrect_callbacks = [];
var picture_choice_actions_enabled = false;

var pc_connect_click_actions = function () {
    picture_choice_actions_enabled = true;
    $(".picture_choice_picture * img").click(function () {
        if (!picture_choice_actions_enabled)
            return;
        picture_choice_actions_enabled = false;

        var already_called = false;
        if ($(this).parent().parent().hasClass("correct")) {
            $('.ductus_picture_choice table tr td').not('.correct').hide(500, function () {
                if (!already_called) {
                    $.each(picture_choice_correct_callbacks, function(i, cb) { cb(); });
                }
                already_called = true;
            });
        } else {
            $(this).parent().fadeTo(200, .25, function () {
                if (!already_called) {
                    $.each(picture_choice_incorrect_callbacks, function(i, cb) { cb(); });
                }
                already_called = true;
            });
        }
    });
};

$(function () {
    pc_connect_click_actions();
});
