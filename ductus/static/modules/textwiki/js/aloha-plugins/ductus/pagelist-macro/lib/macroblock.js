define([
       'jquery',
       'block/block',
       'block/blockmanager',
   ], function(jQuery, block, BlockManager, vcardTemplate) {

    var DuctusPageListMacroBlock = block.AbstractBlock.extend({
        title: 'PageListMacro',

        init: function(element, postProcessFn) {
            this.update(element, postProcessFn);
        },

        update: function(element, postProcessFn) {
            jQuery(element).attr('macro-marker-text', 'PageList macro: ' + element.attr('data-tags'));
            postProcessFn();
        }
    });

    return {
        DuctusPageListMacroBlock: DuctusPageListMacroBlock
    }
});
