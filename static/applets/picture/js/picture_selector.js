function resolve_urn(urn) {
    return '/' + urn.split(':').join('/') + '/'
}

$(function () {
    function set_urn(div, urn) {
        div.children("input").val(urn);
        var qs = '?view=image&amp;max_size=100,100';
        div.children("img").attr("src", resolve_urn(urn) + qs);
    }

    $("div.ductus_picture_selector input").hide();
    $("div.ductus_picture_selector").each(function (i) {
        if ($(this).children("input").val()) {
            $(this).children("div").html("Download new");
            $(this).children("img").addClass("ductus_draggable_img")
                                   .draggable({helper: 'clone'});
        } else {
            $(this).children("div").html('<input/><a>fetch</a>');
        }
    });

    $("div.ductus_picture_selector img").droppable({
        accept: '.ductus_draggable_img',
        drop:
            function (ev, ui) {
                var urn = ui.draggable.siblings("input").val();
                var img = set_urn($(this).parent(), urn);
                ui.draggable.effect("transfer", {to: this}, 1000);
            }
        });

    $("div.ductus_picture_selector div a").click(function (event) {
        $(this).siblings("input").hide();
        // fixme: what about error, or somebody pushing twice?
        var div = $(this).parent().parent();
        $.post('/new/picture/',
               {'uri': $(this).siblings("input").val()},
               function (data) { set_urn(div, data.urn); },
               'json');
    });
});

