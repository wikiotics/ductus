function resolve_urn(urn) {
    return '/' + urn.split(':').join('/') + '/'
}

$(function () {
    $("input.ductus_picture_selector").hide();
    $("div.ductus_picture_selector").html('<input/><a>fetch</a>');
    $("div.ductus_picture_selector a").click(function (event) {
        $(this).siblings("input").hide();
        // fixme: what about error, or somebody pushing twice?
        var div = $(this).parent();
        var target_input = div.siblings("input"); // this could be unreliable in a non-table setting
        $.post('/new/picture/?view=json',
               {'uri': $(this).siblings("input").val()},
               function (data) {
                   target_input.val(data.urn);
                   div.html('<img src="' + resolve_urn(data.urn)
                            + '?view=image&amp;max_size=50,50">');
               },
               'json');
    });
});
