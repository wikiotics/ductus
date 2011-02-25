function resolve_urn(urn) {
    return '/' + urn.split(':').join('/');
}

$(function () {

    // AJAX status indicator
    $("body").append($('<div id="ductus_ajax_status">Working...</div>').hide().ajaxStart(function () {
        $(this).show();
    }).ajaxStop(function () {
        $(this).hide();
    }));

});
