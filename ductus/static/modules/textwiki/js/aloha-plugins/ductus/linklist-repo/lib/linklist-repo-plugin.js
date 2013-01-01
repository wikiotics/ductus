/* wikilink repository, adapted from aloha's slowlinklist.js
 *
/* Ductus WikiLink List Repository
 * --------------------------
 * A simple repository of ductus internal links
 */
define(
[ 'aloha', 'jquery' ],
function ( Aloha, jQuery ) {
    'use strict'

    new ( Aloha.AbstractRepository.extend( {

        _constructor: function () {
            this._super( 'linklist' );
        },

        // cache ajax results that are actually used
        links_cache: [],

        init: function () {
            this.repositoryName = 'Linklist';
        },

        /**
         * Search the repository for object items matching query
         * This queries the backend index.
         * If none is found it returns null.
         *
         * @param {Object} p
         * @param {Function} callback
         */
        query: function ( p, callback ) {
            var that = this, name = '';

            // make sure we get results if the user typed a relative url
            // or when editing an existing link
            if (p.queryString[0] == '/') {
                name = fqpagename_from_url(p.queryString);
            } else {
                name = p.queryString;
            }

            $.ajax({
                url: '/special/ajax/search-pages',
                data: {
                    pagename: name
                },
                success: function(data) {
                    var i, items = [];

                    for (i = 0; i < data.length; i++) {
                        items.push(new Aloha.RepositoryDocument ({
                            id: data[i].absolute_pagename,
                            name: data[i].path,
                            parentId: document.location.host,
                            repositoryId: that.repositoryId,
                            type: 'website',
                            uri: that.parseUri(data[i].path),
                            url: data[i].path,
                        }));
                    }
                    that.links_cache = items;
                    callback.call(that, items);
                },
                error: function(xhr, textStatus, errorThrown) {
                    console.log(xhr.status + ' error. Could not retrieve urls for link.');
                },
                type: 'GET',
                dataType: 'json'
            });
        },

        //parseUri 1.2.2
        //(c) Steven Levithan <stevenlevithan.com>
        //MIT License
        //http://blog.stevenlevithan.com/archives/parseuri
        parseUri: function(str) {
            var o = {
                    strictMode: false,
                    key: [ "source","protocol","authority","userInfo","user","password","host","port","relative","path","directory","file","query","anchor"],
                    q: {
                        name: "queryKey",
                        parser: /(?:^|&)([^&=]*)=?([^&]*)/g
                    },
                    parser: {
                        strict: /^(?:([^:\/?#]+):)?(?:\/\/((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?))?((((?:[^?#\/]*\/)*)([^?#]*))(?:\?([^#]*))?(?:#(.*))?)/,
                        loose: /^(?:(?![^:@]+:[^:@\/]*@)([^:\/?#.]+):)?(?:\/\/)?((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?)(((\/(?:[^?#](?![^?#\/]*\.[^?#\/.]+(?:[?#]|s)))*\/?)?([^?#\/]*))(?:\?([^#]*))?(?:#(.*))?)/
                    }
                },
                m = o.parser[o.strictMode ? "strict" : "loose"].exec(str),
                uri = {},
                i = 14;

            while (i--) uri[o.key[i]] = m[i] || "";

            uri[o.q.name] = {};
            uri[o.key[12]].replace(o.q.parser, function ($0, $1, $2) {
                if ($1) uri[o.q.name][$1] = $2;
            });

            return uri;
        },

        getObjectById: function ( itemId, callback ) {
            // this is called at several stages by the repository manager
            // aloha documentation is quite vague about it...
            // it returns an array (!) containing the item with id == itemId
            var d, i,
                l = this.links_cache.length;

            // find the cached link from the ajax query results
            for (i = 0; i < l; i++) {
                if (this.links_cache[i]['id'] == itemId) {
                    d = [this.links_cache[i]];
                }
            }
            callback.call( this, d );
        },

    } ) )();

} );
