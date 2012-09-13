define([
       'jquery',
       'block/block',
       'block/blockmanager',
   ], function(jQuery, block, BlockManager, vcardTemplate) {

    var DuctusPageListMacroBlock = block.AbstractBlock.extend({
        title: 'PageListMacro',

        init: function(element, postProcessFn) {
            var that = this;
            window.console.log('pagelist macro block init');

            postProcessFn();
        },

        update: function(element, postProcessFn) {
            window.console.log('pagelist macro block update');
            postProcessFn();
        }
    });

    return {
        DuctusPageListMacroBlock: DuctusPageListMacroBlock
    }
});
