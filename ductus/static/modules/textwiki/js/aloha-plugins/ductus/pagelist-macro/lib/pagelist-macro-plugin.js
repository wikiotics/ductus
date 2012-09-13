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
            // init the pagelist plugin using an aloha block mechanism
            BlockManager.registerBlockType('DuctusPageListMacroBlock', ductusmacroblock.DuctusPageListMacroBlock);

            // make sure the BlockManager is aware of pre-existing macro marker when opening the editor
            Aloha.ready(function() {
                Aloha.jQuery('div.ductus-macro').alohaBlock({
                    'aloha-block-type': 'DuctusPageListMacroBlock'
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
        },

        insertMacroBlock: function() {
            // this is class when the user clicks the macro button in the aloha toolbar

            var marker = Aloha.jQuery('<div class="ductus-macro" data-macro-name="pagelist" data-tags="sometag"></div>');
            var range = Aloha.Selection.getRangeObject();
            var Editable = Aloha.activeEditable;
            var Container = Aloha.jQuery(document.getElementById(Editable.getId()));
            GENTICS.Utils.Dom.insertIntoDOM(marker, range, Container);
            marker.alohaBlock({
                'aloha-block-type': 'DuctusPageListMacroBlock'
            });
        },

    });
});
