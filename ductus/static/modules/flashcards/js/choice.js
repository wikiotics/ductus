var dividers = []; // indices represent cards where dividers should be placed immediately before
dividers.unshift(0);
dividers.push(resource_json.resource.cards.array.length);
// fixme: one day when we use bisect search below, we should at this point assert that the dividers are given in order

function shuffle (a) {
    for (var j, x, i = a.length; i; j = parseInt(Math.random() * i), x = a[--i], a[i] = a[j], a[j] = x);
}

// like python's range() function
function array_range (a, b, c) {
    var start, finish, step = c || 1;
    if (b === undefined) {
        start = 0;
        finish = a;
    } else {
        start = a;
        finish = b;
    }

    var rv = [];
    for (var i = start; i < finish; i += step) {
        rv.push(i);
    }
    return rv;
}

function min_gt(n, array) {
    // fixme: use bisect algorithm
    var rv;
    for (var i = 0; i < array.length; ++i) {
        if (array[i] > n && (array[i] < rv || rv === undefined))
            rv = array[i];
    }
    return rv;
}

function max_lte(n, array) {
    // fixme: use bisect algorithm
    var rv;
    for (var i = 0; i < array.length; ++i) {
        if (array[i] <= n && (array[i] > rv || rv === undefined))
            rv = array[i];
    }
    return rv;
}

var resource_displayer = {
    '{http://wikiotics.org/ns/2009/picture}picture': function (resource) {
        var src = resolve_urn(resource.href) + '?view=image&max_size=250,250';
        return $('<div class="picture"></div>').append($('<img alt=""/>').attr('src', src));
    },
    '{http://wikiotics.org/ns/2011/phrase}phrase': function (resource) {
        return $('<span class="phrase"></span>').text(resource.resource.phrase.text);
    }
};

function display_resource (resource) {
    return resource.resource ? resource_displayer[resource.resource.fqn](resource) : $('<div></div>');
}

$(function () {

    // this is meant to be a generic interface, with `length` and `get_next` properties.
    // If there is no known length, it should return -1.  `get_next()` should be a function
    // that returns -1 after the final frame.
    var lesson_iterator = (function () {
        var index = 0;
        var length = resource_json.resource.cards.array.length;

        // each frame will be shown once
        var a = array_range(length);

        // shuffle everything all together, for now
        shuffle(a);

        return {
            length: length,
            get_next: function () {
                var ind = index++;
                return (ind < a.length) ? a[ind] : -1;
            }
        };
    })();

    function get_wrong_indices (correct_index) {
        var rv = array_range(max_lte(correct_index, dividers), min_gt(correct_index, dividers));
        rv.splice($.inArray(correct_index, rv), 1);
        shuffle(rv);
        return rv;
    }

    var prepared_frame;

    function prepare_frame () {
        var index = lesson_iterator.get_next();
        if (index == -1) {
            prepared_frame = null;
            return;
        }

        var display_indices = get_wrong_indices(index).slice(0, 3);
        display_indices.push(index);
        shuffle(display_indices);

        prepared_frame = $('<div class="ductus_choice"></div>');
        var cards_array = resource_json.resource.cards.array;
        // prompt
        var prompt_sides_array = cards_array[index].resource.sides.array;
        for (var k = 0; k < prompt_columns.length; ++k) {
            var header_number = Math.min(k + 2, 6);
            var header_element = $('<h' + header_number +' class="prompt" lang=""></h' + header_number + '>').appendTo(prepared_frame);
            header_element.append(display_resource(prompt_sides_array[prompt_columns[k]]));
        }
        // answer choices
        var table = $('<table></table>').appendTo(prepared_frame);
        for (var i = 0; i < 2; ++i) {
            var tr = $('<tr></tr>').appendTo(table);
            for (var j = 0; j < 2; ++j) {
                var td = $('<td></td>').appendTo(tr);
                var display_index = display_indices[i * 2 + j];
                if (display_index !== undefined) {
                    var res = cards_array[display_index].resource.sides.array[answer_column];
                    var div = $('<div></div>').append(display_resource(res));
                    td.addClass("choice_item").append(div);
                    if (display_index == index)
                        td.addClass("correct");
                }
            }
        }
    }

    var choice_actions_enabled = false;

    var pc_connect_click_actions = function () {
        choice_actions_enabled = true;
        $(".choice_item").click(function () {
            if (!choice_actions_enabled)
                return;

            var already_called = false;
            if ($(this).hasClass("correct")) {
                choice_actions_enabled = false;
                $('.ductus_choice table tr td').not('.correct').hide(500, function () {
                    if (!already_called) {
                        choice_correct_callback();
                    }
                    already_called = true;
                });
            } else {
                $(this).fadeTo(200, .25, function () {
                    if (!already_called) {
                        choice_incorrect_callback();
                    }
                    already_called = true;
                });
            }
        });
    };

    var frame = -1;
    var correct = 0;
    var incorrect = 0;
    var current_frame_incorrect_guess = false;

    function advance_frame () {
        if (prepared_frame) {
            frame = frame + 1;
            $("#choice_frame_container").empty().append(prepared_frame);
            pc_connect_click_actions();
            $("#frame_number").html(frame + 1 + '');
            current_frame_incorrect_guess = false;
            prepare_frame();
        }
    }

    var choice_correct_callback = function () {
        if (!current_frame_incorrect_guess) {
            correct = correct + 1;
            $("#choice_correct_count").html(correct + '');
        }
        setTimeout(advance_frame, 2500);
    };
    var choice_incorrect_callback = function () {
        if (!current_frame_incorrect_guess) {
            incorrect = incorrect + 1;
            $("#choice_incorrect_count").html(incorrect + '');
            current_frame_incorrect_guess = true;
        }
    };

    if (lesson_iterator.length != -1) {
        $("#number_of_frames").text('' + lesson_iterator.length);
    }
    $("#total_frames_text").toggle(lesson_iterator.length != -1);

    prepare_frame();
    advance_frame();

});

