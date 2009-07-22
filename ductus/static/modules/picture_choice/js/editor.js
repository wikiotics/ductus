$(function () {
    $("ul#picture_choice_lesson").sortable({});
});
$(function () {
    function pcl_object() {
        var groups = [];
        $(".picture_choice_group_item").each(function (i) {
            groups.push($(this).metadata().urn);
        });
        // fixme: assert that the length of our array is equal to the number
        // of list items in #picture_choice_lesson
        return {"groups": groups};
    }
    function pcl_json() { return JSON.stringify(pcl_object()); }
    $("#save_button").click(function () {
        $.post(document.URL, {"pcl": pcl_json()}, function (data) {
            alert("saved");
        });
    });
});
$(function () {
    function load_blank_pcg_form () {
        // fixme look up static urls
        $("#builder_form").load("/new/picture_choice_group", function () {
            connect_picture_widgets();
        });
    }
    load_blank_pcg_form();
    $("#builder_form_submit").click(function () {
        $.post("/new/picture_choice_group", $("#builder form").serialize(), function (data, textStatus) {
            try {
                var new_urn = JSON.parse(data)['urn'];
                // append them to the ul
                $.get(resolve_urn(new_urn), {"view": "_edit_lesson_li"}, function (data) {
                    $("#picture_choice_lesson").append(data);
                });
                // show the form again
                load_blank_pcg_form();
            } catch (e) {
                $("#builder_form").html(data);
            }
        });
    });
});
