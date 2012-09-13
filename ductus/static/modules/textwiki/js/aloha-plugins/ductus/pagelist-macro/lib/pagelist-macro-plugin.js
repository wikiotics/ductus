define([
    'jquery',
    'aloha/plugin',
    'block/blockmanager',
    'pagelist-macro/macroblock',
    'ui/ui',
    'ui/button',
    'ui/scopes',
    'ui/port-helper-attribute-field',
], function(
    jQuery,
    Plugin,
    BlockManager,
    ductusmacroblock,
    Ui,
    Button,
    Scopes,
    AttributeField
) {

    return Plugin.create('ductus-pagelist-macro', {

        init: function() {
            var that = this;
            this._currentBlock = {};    // a reference to the currently selected block, as we only seem to be able to figure that from an activate event

            // init the pagelist plugin using an aloha block mechanism
            BlockManager.registerBlockType('DuctusPageListMacroBlock', ductusmacroblock.DuctusPageListMacroBlock);

            // make sure the BlockManager is aware of pre-existing macro marker when opening the editor
            Aloha.ready(function() {
                Aloha.jQuery('div.ductus-macro').alohaBlock({
                    'aloha-block-type': 'DuctusPageListMacroBlock',
                    'block-skip-scope':'true'
                });
                BlockManager.bind('block-activate', function (blocks) {
                    that._currentBlock = blocks[0];
                    that._tagField.setValue(that._currentBlock.attr('tags'));
                    that._tagField.foreground();
                });
            });
            this.initButtons();
        },

        initButtons: function() {
            // create aloha toolbar buttons
            var that = this;

            this._insertTocButton = Ui.adopt("insertToc", Button, {
                tooltip: 'insert pagelist macro',
                icon: 'aloha-icon aloha-icon-orderedlist',
                scope: 'Aloha.continuoustext',
                click: function () { that.insertMacroBlock(); }
            });
            this._tagField = AttributeField({
                width: 250,
                label: 'Tags',
                name: 'PageListTags',
                scope: 'pagelisttags'
            });

            this._tagField.addListener( 'keyup', function ( event ) {

                if ( event.keyCode == 13 ) {
                    // the user hit 'enter': remove the macro marker if the input field is empty
                    var val = that._tagField.getValue();
                    if (val == '') {
                        window.console.log('remove macro');
                    } else {
                        that._currentBlock.attr('tags', val);
                    }
                }
            });
        },

        insertMacroBlock: function() {
            // this is class when the user clicks the macro button in the aloha toolbar

            var marker = Aloha.jQuery('<div class="ductus-macro" data-macro-name="pagelist" data-tags="sometag"></div>');
            marker.attr('data-block-skip-scope', 'true');   // prevent aloha from switching scope upon activation of a marker
            var range = Aloha.Selection.getRangeObject();
            var Editable = Aloha.activeEditable;
            var Container = Aloha.jQuery(document.getElementById(Editable.getId()));
            GENTICS.Utils.Dom.insertIntoDOM(marker, range, Container);
            marker.alohaBlock({
                'aloha-block-type': 'DuctusPageListMacroBlock'
            });
            this._tagField.setValue(BlockManager.getBlock(marker).attr('tags'));
            this._tagField.foreground();
            this._tagField.focus();
        },

    });
});
