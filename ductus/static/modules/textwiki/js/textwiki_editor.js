

$(function() {

    function TextWiki(tw) {

        if (!tw) {
            tw = {
                resource: {
                    blob: {
                        markup_language: 'ductus-html5',
                        natural_language: 'en',
                        text: ""
                    }
                }
            };
        }
        ModelWidget.call(this, tw, '<div class="ductus_TextWiki"></div>');

        this.sidebar = $('<div id="ductus_Sidebar"></div>');

        this.content_editor = $('<div class="content-editor"></div>').appendTo(this.elt);
        this.content_editor.append(tw.resource.blob.text);

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

        // get the editor content from aloha
        var text = '';
        if (Aloha.editables && Aloha.editables.length) {
            text = Aloha.editables[0].getContents();
        } else {
            text = this.content_editor.html();
        }

        return this.add_inner_blueprint_constructor({
            blob: {
                text: text,
                markup_language: "ductus-html5"
            },
            tags: {array: tags}
        });
    };

    var page = new TextWiki(resource_json);
    $('#side_toolbar').append(page.sidebar);
    $('#textwiki-editor').append(page.elt);

    Aloha.ready( function() {
        Aloha.jQuery('div.content-editor').aloha();
        Aloha.require(['jquery', 'ui/scopes', 'ui/ui-plugin'],function(jQ, Scopes, UiPlugin){
            var toolbar = jQ('.aloha-toolbar');
            jQ('#toolbar-container').append(toolbar);
            Scopes.setScope('Aloha.continuoustext');
            UiPlugin.showToolbar();
            Aloha.bind('aloha-editable-deactivated', function(){
                UiPlugin.showToolbar();
            });
        });
     });
});
