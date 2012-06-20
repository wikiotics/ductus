

$(function() {

    function TextWiki(tw) {

        if (!tw) {
            tw = {
                resource: {
                    blob: {
                        markup_language: 'creole-1.0',
                        natural_language: 'en',
                        text: "",
                    }
                }
           }
        }
        ModelWidget.call(this, tw, '<div class="ductus_TextWiki"></div>');

        this.sidebar = $('<div id="ductus_Sidebar"></div>');

        this.textarea = this.elt.append($('<textarea />')).find('textarea');
        this.textarea.val(tw.resource.blob.text);

        this.tagging_widget = new TaggingWidget(tw.resource.tags);
        this.tagging_widget.elt.make_sidebar_widget(gettext('Tags'), this.sidebar);

        this.save_widget = new SaveWidget(this, 'the page');
        this.save_widget.elt.make_sidebar_widget(gettext('Save...'), this.sidebar);

        this.record_initial_inner_blueprint();
    }
    TextWiki.prototype = chain_clone(ModelWidget.prototype);
    TextWiki.prototype.fqn = '{http://wikiotics.org/ns/2009/wikitext}wikitext';
    TextWiki.prototype.inner_blueprint_repr = function () {
        var tags = [];
        $.each(this.tagging_widget.get_tag_list(), function (i, tag) {
            if (tag != '') {
                tags.push({value: tag});
            }
        });
        return this.add_inner_blueprint_constructor({
            blob: {
                text: this.textarea.val(),
                markup_language: "creole-1.0"
            },
            tags: {array: tags}
        });
    };
    TextWiki.prototype.preview = function() {
        // get the rendered markup from an AJAX call and insert it above the editor
        $.ajax({
            url: '/special/preview_textwiki',
            type: 'POST',
            dataType: 'json',
            data: {text: this.textarea.val()},
            success: function(data) {
                if (data['html']) {
                    $('#textwiki-preview').empty().append(data['html']);
                } else {
                    $('#textwiki-preview').empty().append(data['error']);
                }
            },
            error: function() {
                alert(gettext('Error previewing your changes'));
            }
        });
    }

    var page = new TextWiki(resource_json);
    $('#textwiki-save-widget').append(page.sidebar);
    $('#textwiki-editor').append(page.elt);

});
