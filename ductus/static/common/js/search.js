/* Ductus
 * Copyright (C) 2012  Jim Garrison <garrison@wikiotics.org>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

$(function () {

    var taglist = [];   // list of all tags included in the search results, used for refining the search

    $.fn.clear_search_results = function() {
        $(this).empty();
        return this;
    };

    $.fn.append_search_results = function(results) {
        // append search results returned by ajax to the selector
        // results: a list of search results as returned by the ajax query
        var i,
            item,
            res_length = results.length;
        taglist = [];
        for (i = 0; i < res_length; i++) {
            item = $('<div class="result-item"><a href="' + results[i].path + '">' + results[i].absolute_pagename + '</a></div>');
            $.each(results[i].tags, function(i, tag) {
                item.append('<span class="tag">' + tag + '</span>').addClass('tag-' + tag.replace(':', '_'));
                // collect all tags used by the results
                if ($.inArray(tag, taglist) < 0) {
                    taglist.push(tag);
                }
            });
            this.append(item);
        }
        taglist.sort();
        return this;
    };

    function get_search_params() {
        // get the list of search parameters

        var params = {},
            text,
            tags = [];
        text = $('input.search-text').val();
        if (text != '') {
            params['pagename'] = text;
        }
        $('.tag-list > .selected').each(function(i, tag_elt) {
            tags.push($(tag_elt).attr('data-tag-name'));
        });
        if (tags.length) {
            tags = tags.join('&tag=');
            params['tag'] = tags;
        }
        return params;
    }

    function do_search(params) {
        // actually perform the search with given parameters

        // TODO: validate params
        if (!$.isEmptyObject(params)) {
            $.ajax({
                url: 'ajax/search-pages',
                data: params,
                success: function(data, textStatus, jqXHR) {
                    // display new search results and update the clickable list of tags
                    if (data.length > 0) {
                        $('div.search-results').clear_search_results().append_search_results(data);
                        update_search_toolbar(params);
                    }
                }
            });
        }
    }

    function update_search_toolbar(params) {
        // create a list of clickable tag buttons from the list of tags returned by AJAX query
        // params: the parameters used for the latest AJAX query
        var stat = '';
        $('.refine-by-tag').children().remove();
        $.each(taglist, function(i, tag) {
            toggle = $('<span>' + tag + '</span>').make_tag_toggle(true).appendTo('.refine-by-tag');
        });
        // update search status text
        stat = gettext('Showing results for: ');
        if (params['pagename']) {
            stat += gettext('page name containing "') + params['pagename'] + '" ';
            if (params['tag']) {
                stat += 'and ';
            }
        }
        if (params['tag']) {
            stat += gettext('tagged with: ') + params['tag'];
        }
        $('.search-status').text(stat);
    }

    $.fn.make_tag_toggle = function(selected) {
        if (typeof selected == 'undefined') {
            selected = false;
        }
        $(this).addClass('tag-toggle').click(function() {
            $(this).toggleClass('selected');
            var selected = $('.tag-toggle.selected');
            // show all results...
            $('.result-item').css('display', 'block');
            // ...except the ones not matching the selected tags
            selected.each(function(i, tag_elt) {
                $('.result-item:not(.tag-' + $(tag_elt).text().replace(':', '_') + ')').css('display', 'none');
            });
        });
        return this;
    };

    function setup_search_interface() {
        // attach event handlers where needed
        $('.tag-list > li').make_tag_toggle();
        $('.search-button').click(function() {
            do_search(get_search_params());
        });
        // run the search when user hits "enter" (if input not empty)
        $('.search-text').bind('keyup', function(e) {
            if (e.keyCode == 13 && $(this).val() != '') {
                do_search(get_search_params());
            }
        });
    }

    // TODO: load params from url
    setup_search_interface();
    if (urlParams) {
        do_search(urlParams);
    }
});
