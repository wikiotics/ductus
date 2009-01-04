function resolve_urn(urn) {
    return '/' + urn.split(':').join('/') + '/'
}

// fixme: make it so thumbnail is displayed if the form has a urn in it on page
// load.

$(function () {
    function show_thumbnail(div, urn) {
        div.html('<img src="' + resolve_urn(urn)
                 + '?view=image&amp;max_size=100,100">');
    }

    $("div.ductus_picture_selector input").hide();
    $("div.ductus_picture_selector div").html('<input/><a>fetch</a>');
    $("div.ductus_picture_selector div a").click(function (event) {
        $(this).siblings("input").hide();
        // fixme: what about error, or somebody pushing twice?
        var div = $(this).parent();
        var target_input = div.siblings("input");
        $.post('/new/picture/?view=json',
               {'uri': $(this).siblings("input").val()},
               function (data) {
                   target_input.val(data.urn);
                   show_thumbnail(div, data.urn);
               },
               'json');
    });
});

