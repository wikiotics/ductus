function resolve_urn(urn) {
    return '/' + urn.split(':').join('/');
}

$(function () {

    // CSRF handling for AJAX requests
    // (see http://www.djangoproject.com/weblog/2011/feb/08/security/)
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken",
                                     $("#csrfmiddlewaretoken").val());
            }
        }
    });

    // AJAX status indicator
    $("body").append($('<div id="ductus_ajax_status">Working...</div>').hide().ajaxStart(function () {
        $(this).show();
    }).ajaxStop(function () {
        $(this).hide();
    }));

});
