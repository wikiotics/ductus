var picture_choice_correct_callbacks = [];

var pc_connect_click_actions = function () {
    $(".picture_choice_picture * img").click(function () {
        if ($(this).parent().parent().hasClass("correct")) {
            $('.ductus_picture_choice table tr td').not('.correct').hide(500);
            $.each(picture_choice_correct_callbacks, function(i, cb) { cb(); });
        } else {
            $(this).parent().fadeTo(200, .25);
        }
    });
};

$(function () {
    pc_connect_click_actions();
});
