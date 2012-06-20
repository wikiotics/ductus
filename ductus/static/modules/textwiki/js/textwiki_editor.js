

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

        this.save_widget = new SaveWidget(this, 'the page');
        this.save_widget.elt.make_sidebar_widget(gettext('Save...'), this.sidebar);

        this.record_initial_inner_blueprint();
    }
    TextWiki.prototype = chain_clone(ModelWidget.prototype);
    TextWiki.prototype.fqn = '{http://wikiotics.org/ns/2009/wikitext}wikitext';
    TextWiki.prototype.inner_blueprint_repr = function () {
        return this.add_inner_blueprint_constructor({
            blob: {
                text: this.textarea.val(),
                markup_language: "creole-1.0"
            }
        });
    };

    var page = new TextWiki(resource_json);
    $('#textwiki-save-widget').append(page.sidebar);
    $('#textwiki-editor').append(page.elt);

});
