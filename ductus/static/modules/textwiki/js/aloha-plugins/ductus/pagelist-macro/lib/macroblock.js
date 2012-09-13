define([
       'jquery',
       'block/block',
       'block/blockmanager',
   ], function(jQuery, block, BlockManager, vcardTemplate) {

    var DuctusPageListMacroBlock = block.AbstractBlock.extend({
        title: 'PageListMacro',

        init: function(element, postProcessFn) {
            var that = this;

            postProcessFn();
        },

        update: function(element, postProcessFn) {
            postProcessFn();
        }
    });

    return {
        DuctusPageListMacroBlock: DuctusPageListMacroBlock
    }
});
