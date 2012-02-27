/* Ductus
 * Copyright (C) 2011  Jim Garrison <garrison@wikiotics.org>
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
    $.fn.verticaltabs = function () {
        // for some reason tabs() fails if the element hasn't been inserted into the DOM yet, so we wait until it has been to call it
        var this_ = this;
        setTimeout(function () {
            this_.tabs().addClass('ui-tabs-vertical ui-helper-clearfix');
            this_.find("li").removeClass('ui-corner-top').addClass('ui-corner-left');
        }, 0);
        return this;
    };

    var selected = null;
    var selected_wrapped_set;
    function _unselect() {
        // unmarked the previously selected widget
        if (!selected) return;
        selected_wrapped_set.removeClass("ductus-selected");
    }
    function _select(elt, wrapped_set_func) {
        // mark the clicked widget as selected (color its background)
        _unselect();
        selected = $(elt);
        selected_wrapped_set = wrapped_set_func ? wrapped_set_func() : $(elt);
        selected_wrapped_set.addClass("ductus-selected");
    }

    $.fn.ductus_selectable = function (ui_widget_func, wrapped_set_func, dblclick_handler) {
        // set click/dblclick handlers for a selectable element
        // ui_widget_func: the "click handler" for the widget (also sets the editing widget)
        // wrapped_set_func: a function returning the elements to show as selected when clicked
        // dblclick_handler: (optional) the handler to call when the widget is double clicked
        if (dblclick_handler) {
            this.dblclick(dblclick_handler);
        }
        return this.each(function () {
            $(this).click(function () {
                $('#ductus_PopupWidget').hide();
                _select($(this), wrapped_set_func);
                if (ui_widget_func)
                    ui_widget_func();
            });
        });
    };

    $.fn.make_sidebar_widget = function (title, sidebar) {
        // setup and insert the widget in the editor sidebar
        // (add a title header and collapse/expand handler)
        this.appendTo(sidebar);
        var header = $('<div class="ductus_SidebarWidgetHeader">' + title + '</div>');
        this.before(header);
        this.addClass('ductus_SidebarWidget');
        header.bind('click', function() {
            $(this).next().toggle();
            return false;
        }).next().hide();
    }

    function PhraseWidget(phrase) {
        ModelWidget.call(this, phrase, '<div class="ductus_PhraseWidget"></div>');

        this.input = $('<input/>');
        if (phrase)
            this.input.val(phrase.resource.phrase.text);
        this.elt.append(this.input);

        this.record_initial_inner_blueprint();
    }
    PhraseWidget.prototype = chain_clone(ModelWidget.prototype);
    PhraseWidget.prototype.inner_blueprint_repr = function () {
        return {
	    '@create': PhraseWidget.prototype.fqn,
	    'phrase': {text: this.input.val()}
	};
    };
    PhraseWidget.prototype.fqn = '{http://wikiotics.org/ns/2011/phrase}phrase';
    // define popup menu content and callbacks
    PhraseWidget.prototype.popup_html = {
        'bottom': gettext('delete')
    };
    PhraseWidget.prototype.popup_callback = {
        // target is the phrase widget that generated the popup
        'bottom': function(target) {
            target.elt.parent().data('widget_object').reset();
        }
    };

    function PhraseCreator() {
        Widget.call(this, '<div class="ductus_PhraseCreator"><form><input/></form></div>');

        var this_ = this;
        this.input = this.elt.find('input');
        this.elt.find('form').submit(function (event) {
            event.preventDefault();
            this_.elt.trigger("ductus_element_selected", [{
                resource: {
                    phrase: { text: this_.input.val() },
                    fqn: PhraseWidget.prototype.fqn
                }
            }]);
            this_.input.val('');
        });
    }
    PhraseCreator.prototype = chain_clone(Widget.prototype);
    PhraseCreator.prototype.do_focus = function () {
        this.input.focus();
    };

    function FlashcardSideEditor(fcsw) {
        // the editor shown at the right side, allowing to add elements to a flashcard side, edit or remove them.
        // fcsw is the calling FlashcardSide widget (the one that was clicked on the flashcard deck)
        Widget.call(this, '<div class="ductus_FlashcardSideEditor"><ul></ul></div>');

        var this_ = this;
        var ul = this.elt.find("ul");

        ul.append('<li class="display-only-if-editable">&nbsp;</li>');

        var edit_tab_body = $('<div id="fcs-edit"></div>');
        ul.append('<li><a href="#fcs-edit" id="fcs-edit-tab" class="display-only-if-editable">edit</a></li>');
        this.elt.append(edit_tab_body);
        this.edit_tab_body = edit_tab_body;

        this.elt.verticaltabs();

        // auto-focus on important element when tab is selected
        this.elt.bind("tabsselect", function (event, ui) {
            var widget_object = $(ui.panel).children().first().data("widget_object");
            if (!widget_object)
                return;
            if (widget_object.do_focus) {
                setTimeout(function () {
                    widget_object.do_focus();
                }, 0);
            }
        });
    }
    FlashcardSideEditor.prototype = chain_clone(Widget.prototype);
    FlashcardSideEditor.prototype.set_fcsw = function (fcsw) {
        if (this.fcsw === fcsw)
            return;
        this.fcsw = fcsw;
        // show or hide edit/delete buttons as appropriate
        this.elt.find('.display-only-if-editable').toggle(!!this.fcsw.wrapped);

        // if no existing element, try to select a sensible "new" tab
        if (!fcsw.wrapped) {
            var display_index = fcsw.column.th.index() + 1;
            // fixme: this next row assumes there is only one deck...
            var first_td_in_column = $(".ductus_FlashcardDeck").find("td:nth-child(" + display_index + ")").first();
            var first_fcsw_in_column = first_td_in_column.children().first().data("widget_object");
            if (first_fcsw_in_column && first_fcsw_in_column.wrapped) {
                for (var j = 0; j < FlashcardSide.widgets.length; ++j) {
                    if (FlashcardSide.widgets[j][1].prototype.fqn == first_fcsw_in_column.wrapped.fqn)
                        this.elt.tabs("select", "fcs-new-" + j);
                }
            }
        }
    };
    FlashcardSideEditor.prototype.go_to_main_editor_tab = function () {
        if (this.editor_widget) {
            this.elt.tabs("select", "fcs-edit");
            if (this.editor_widget.focus_on_editor)
                this.editor_widget.focus_on_editor();
        }
    };

    function FlashcardEditor(fcw) {
        Widget.call(this, '<div class="ductus_FlashcardEditor">flashcard editor; coming soon</div>');
        // may allow moving a flashcard up and down
        // allow deleting a flashcard
        // allow putting a divider above or below?
        this.fcw = fcw;
        var this_ = this;
    }
    FlashcardEditor.prototype = chain_clone(Widget.prototype);
    FlashcardEditor.prototype.set_fcw = function (fcw) {
        this.fcw = fcw;
    };

    function FlashcardColumnEditor(fcdw, column) {
        // an in-place editor for flashcard column headers
        Widget.call(this, '<div class="ductus_FlashcardColumnEditor"><span></span><input/></div>');

        this.non_unique_warning = $('<div class="ductus_non_uniq_col_header">' + gettext('Warning: each column name must be unique.') + '</div>').appendTo(this.elt).hide();

        var this_ = this;
        this.column = column;
        this.fcdw = fcdw;
        this.last_valid_heading = '';

        this.input = this.elt.find('input').hide();
        this.span = this.elt.find('span').show();
        this.input.bind('focusout', function (event) {
            this_.input.hide();
            this_.span.show();
            this_.fcdw._set_column_heading(this_.column, this_.last_valid_heading);
        });
        this.input.bind("change keyup keypress drop", function (event) {
            var heading = $.trim($(this).val());
            this_.span.text(heading);

            // do a linear search through all other columns to make sure the heading is unique
            var show_non_unique_warning = false;
            if (heading) {
                for (var i = 0; i < fcdw.columns.length; ++i) {
                    if (heading == fcdw.columns[i].heading && fcdw.columns[i] !== this_.column) {
                        heading = this_.last_valid_heading;
                        show_non_unique_warning = true;
                        break;
                    }
                }
            }

            this_.non_unique_warning.toggle(show_non_unique_warning);
            if (show_non_unique_warning) {
                this_.input.addClass('ductus_input_value_incorrect');
            } else {
                this_.input.removeClass('ductus_input_value_incorrect');
                this_.last_valid_heading = heading;
                if (event.keyCode == 13) {  // user hit enter key
                    $(this_.input).focusout();
                }
            }
        });
        this.input.bind('click', function (event) {
            // prevent popup from showing while editing
            event.stopPropagation();
        });
        this.span.bind('click', function (event) {
            // replace the text with an input
            event.stopPropagation();
            this_.span.hide();
            this_.input.show().focus();
        });
    }
    FlashcardColumnEditor.prototype = chain_clone(Widget.prototype);
    FlashcardColumnEditor.prototype.set = function (fcdw, column) {
        // update the widget when user clicks a different column
        this.column = column;
        this.fcdw = fcdw;
    };
    FlashcardColumnEditor.prototype.set_heading = function (heading) {
        // change the text of the column header
        this.span.text(heading);
        this.input.val(heading);
        this.last_valid_heading = heading;
    }

    function FlashcardDeckEditor(fcdw) {
        // this will edit:
        // * available interactions
        // * global (as opposed to per-column) non-interaction constraints
        // and display:
        // * number of rows and columns
        // whether all constraints are fulfilled

        Widget.call(this, '<div class="ductus_FlashcardDeckEditor">flashcard deck editor; coming soon</div>');
    }
    FlashcardDeckEditor.prototype = chain_clone(Widget.prototype);

    function FlashcardSide(fcs, column) {
        // a FlashcardSide widget. Visually, the cell in the flashcard deck
        // either empty or containing a ModelWidget in this.wrapped
        Widget.call(this, '<div class="ductus_FlashcardSide"></div>');
        this.set_from_json(fcs);
        this.column = column;
    }
    FlashcardSide.prototype = chain_clone(Widget.prototype);
    FlashcardSide.prototype.blueprint_repr = function () {
        if (this.wrapped) {
            return this.wrapped.blueprint_repr();
        } else {
            return {resource: null};
        }
    };
    FlashcardSide.prototype.get_outstanding_presave_steps = function () {
        return this.wrapped ? this.wrapped.get_outstanding_presave_steps() : [];
    };
    FlashcardSide.prototype.reset = function () {
        this.wrapped = null;
        this.elt.empty().html("&nbsp;");
    };
    FlashcardSide.prototype.ui_widget = function () {
        popup = $("#ductus_PopupWidget");
        if (popup.length) {
            popup.data('widget_object').show_popup(this);
        }
    };
    FlashcardSide.prototype.handle_double_click = function () {
        if (FlashcardSide._global_flashcard_side_editor)
            FlashcardSide._global_flashcard_side_editor.go_to_main_editor_tab();
    };
    FlashcardSide.prototype.set_from_json = function (fcs) {
        if (fcs && fcs.resource) {
            this._set_wrapped(new FlashcardSide.widgets_by_fqn[fcs.resource.fqn](fcs));
        } else {
            this.reset();
        }
    };
    FlashcardSide.prototype._set_wrapped = function (wrapped) {
        if (!wrapped) {
            this.reset();
            return;
        }
        this.wrapped = wrapped;
        this.elt.children().detach();
        this.elt.append(wrapped.elt);
    };
    FlashcardSide.prototype.ensure_last_row_empty = function () {
        // ensure there is always an empty row at the bottom of the deck
        if (this.elt.closest('tr').is(':last-child')) {
            var fcd = $(".ductus_FlashcardDeck").data('widget_object');
            fcd.add_row();
        }
    }
    // popup definition for an empty flashcard side
    FlashcardSide.prototype.popup_html = {
        'left': gettext('new phrase'),
        'right': gettext('new audio'),
        'top': gettext('new picture'),
        'bottom': gettext('paste')
    };
    // callbacks to handle clicks on an empty flashcard side
    FlashcardSide.prototype.popup_callback = {
        'left': function(caller) {
            caller.set_from_json({
                resource: {
                    phrase: { text: '' },
                    fqn: PhraseWidget.prototype.fqn
                }
            });
            caller.ensure_last_row_empty();
            caller.wrapped.input.focus();
        },
        'right': function(caller) {
            // show an audio creation widget in the deck
            if (!FlashcardSide._global_audio_creator) {
                FlashcardSide._global_audio_creator = AudioWidget.creation_ui_widget();
            } else {
                online_recorder.init();
            }
            caller._set_wrapped(FlashcardSide._global_audio_creator);
            FlashcardSide._global_audio_creator.elt.bind("ductus_element_selected", function (event, model_json_repr) {
                caller.set_from_json(model_json_repr);
            });
            caller.ensure_last_row_empty();
        },
        'top': function(caller) {
            // new picture: show an overlay with the pictureSearchWidget in it
            if (!FlashcardSide._global_picture_creator) {
                FlashcardSide._global_picture_creator = PictureModelWidget.creation_ui_widget();
            }
            $(FlashcardSide._global_picture_creator.elt).dialog({
                        height: ($(window).height() - parseInt($(document.body).css("padding-top")) - parseInt($(document.body).css("padding-top"))) * 0.8,
                        width: ($(window).width() - parseInt($(document.body).css("padding-left")) - parseInt($(document.body).css("padding-right"))) * 0.8 + "px",
                        title: gettext('Search flickr for pictures')
            });
            FlashcardSide._global_picture_creator.elt.bind("ductus_element_selected", function (event, model_json_repr) {
                caller.set_from_json(model_json_repr);
            });
            caller.ensure_last_row_empty();
        },
        'bottom': function(caller) {
            var bp = $.extend(true,
                    {
                        resource: {
                            fqn: AudioWidget.prototype.fqn
                                  }
                    },
                    window.global_copy_paste_buffer
            );
            caller.set_from_json(bp);
            caller.ensure_last_row_empty();
        }
    };
    FlashcardSide.widgets = [
        ['picture', PictureModelWidget],
        ['audio', AudioWidget],
        ['phrase', PhraseWidget]
    ];
    FlashcardSide.widgets_by_fqn = {};
    $.each(FlashcardSide.widgets, function (i, w) {
        FlashcardSide.widgets_by_fqn[w[1].prototype.fqn] = w[1];
    });

    function Flashcard(fc, columns) {
        // flashcard widget (a row visually)
        ModelWidget.call(this, fc, '<tr class="ductus_Flashcard"><td class="row_td"></td></tr>');

        var this_ = this;
        $.each(columns, function (i, column) {
            this_._append_new_cell(fc && fc.resource.sides.array[i], column);
        });

        this.elt.find(".row_td").ductus_selectable(function () {
            return this_.ui_widget();
        }, function () {
            return this_.elt.find("td");
        });

        this.record_initial_inner_blueprint();
    }
    Flashcard.prototype = chain_clone(ModelWidget.prototype);
    Flashcard.prototype.inner_blueprint_repr = function () {
        var sides = [];
        this.elt.find("td").children().each(function (i) {
            sides.push($(this).data("widget_object").blueprint_repr());
        });
        return this.add_inner_blueprint_constructor({ sides: { array: sides } });
    };
    Flashcard.prototype.get_outstanding_presave_steps = function () {
        var sides = [];
        this.elt.find("td").children().each(function (i) {
            sides.push($(this).data("widget_object"));
        });
        return ModelWidget.combine_presave_steps(sides);
    };
    Flashcard.prototype.fqn = '{http://wikiotics.org/ns/2011/flashcards}flashcard';
    Flashcard.prototype.ui_widget = function () {
        popup = $("#ductus_PopupWidget");
        if (popup.length) {
            popup.data('widget_object').show_popup(this);
        }
    };
    Flashcard.prototype._append_new_cell = function (fcs, column) {
        var fcsw = new FlashcardSide(fcs, column);
        var td = $('<td></td>').append(fcsw.elt);
        this.elt.append(td);
        td.ductus_selectable(function () {
            return fcsw.ui_widget();
        }, null, function () {
            fcsw.handle_double_click();
        });
    };
    // popup definition for a flashcard (a row)
    // FIXME: the width of the whole flashcard is used for positioning popup...
    Flashcard.prototype.popup_html = {
        'left': gettext('add row'),
        'bottom': gettext('delete row'),
        'top': gettext('insert row')
            // TODO: move row
    };
    // callbacks to handle clicks on an empty flashcard side
    Flashcard.prototype.popup_callback = {
        'left': function() {
            var fcd = $(".ductus_FlashcardDeck").data('widget_object');
            fcd.add_row();
        },
        'bottom': function(fc) {
            var fcd = $(".ductus_FlashcardDeck").data('widget_object');
            fcd.delete_row(fc);
        },
        'top': function(fc) {
            var fcd = $(".ductus_FlashcardDeck").data('widget_object');
            fcd.insert_row(fc.elt.index()-1);
        },
    };

    function ChoiceInteractionWidget(ci) {
        ModelWidget.call(this, ci, '<div class="ductus_ChoiceInteractionWidget"></div>');
        this.elt.append(gettext('Prompt:') + ' <input name="prompt" class="prompt"/> ' + gettext('Answer:') +' <input name="answer" class="answer"/>');
        this.prompt = this.elt.find('.prompt');
        this.answer = this.elt.find('.answer');
        if (ci) {
            this.prompt.val(ci.resource.prompt);
            this.answer.val(ci.resource.answer);
        }

        this.record_initial_inner_blueprint();
    }
    ChoiceInteractionWidget.prototype = chain_clone(ModelWidget.prototype);
    ChoiceInteractionWidget.prototype.inner_blueprint_repr = function () {
        return this.add_inner_blueprint_constructor({
            prompt: this.prompt.val(),
            answer: this.answer.val()
        });
    };
    ChoiceInteractionWidget.prototype.fqn = '{http://wikiotics.org/ns/2011/flashcards}choice_interaction';

    function AudioLessonInteractionWidget(ai) {
        ModelWidget.call(this, ai, '<div class="ductus_AudioLessonInteractionWidget"></div>');
        this.elt.append(gettext('Audio:') + ' <input name="audio" class="audio"/> ' + gettext('Transcript (optional):') + ' <input name="transcript" class="transcript"/>');
        this.audio = this.elt.find('.audio');
        this.transcript = this.elt.find('.transcript');
        if (ai) {
            this.audio.val(ai.resource.audio);
            this.transcript.val(ai.resource.transcript);
        }

        this.record_initial_inner_blueprint();
    }
    AudioLessonInteractionWidget.prototype = chain_clone(ModelWidget.prototype);
    AudioLessonInteractionWidget.prototype.inner_blueprint_repr = function () {
        return this.add_inner_blueprint_constructor({
            audio: this.audio.val(),
            transcript: this.transcript.val()
        });
    };
    AudioLessonInteractionWidget.prototype.fqn = '{http://wikiotics.org/ns/2011/flashcards}audio_lesson_interaction';

    function InteractionChooserWidget(ic) {
        Widget.call(this, '<div class="ductus_InteractionChooserWidget"></div>');
        this.interactions = $('<ul class="ductus_InteractionChooserWidget_interactions"></ul>').appendTo(this.elt);
        this.new_interaction_buttons = $('<ul class="ductus_InteractionChooserWidget_add_buttons"></ul>').appendTo(this.elt);
        var this_ = this;
        $('<a href="javascript:void(0)">' + gettext('Add a "choice" interaction') + '</a>').click(function () {
            this_.__add_interaction(new ChoiceInteractionWidget());
        }).appendTo($('<li></li>').appendTo(this.new_interaction_buttons));
        $('<a href="javascript:void(0)">' + gettext('Add an audio lesson interaction') + '</a>').click(function () {
            this_.__add_interaction(new AudioLessonInteractionWidget());
        }).appendTo($('<li></li>').appendTo(this.new_interaction_buttons));

        if (ic) {
            for (var i = 0; i < ic.array.length; ++i) {
                var interaction = ic.array[i];
                if (interaction.resource.fqn == ChoiceInteractionWidget.prototype.fqn) {
                    this.__add_interaction(new ChoiceInteractionWidget(interaction));
                } else if (interaction.resource.fqn == AudioLessonInteractionWidget.prototype.fqn) {
                    this.__add_interaction(new AudioLessonInteractionWidget(interaction));
                }
            }
        }
    }
    InteractionChooserWidget.prototype = chain_clone(ModelWidget.prototype);
    InteractionChooserWidget.prototype.blueprint_repr = function () {
        var interactions = [];
        this.interactions.children().each(function () {
            interactions.push($(this).children().first().data("widget_object").blueprint_repr());
        });
        return { array: interactions };
    };
    InteractionChooserWidget.prototype.__add_interaction = function (widget) {
        var li = $('<li></li>').append(widget.elt).appendTo(this.interactions);
        $('<span>' + gettext('delete interaction') + '</span>').button({text: false, icons: {primary: 'ui-icon-close'}}).click(function () {
            $(this).parent('li').remove();
        }).appendTo(li);
    };

    function FlashcardColumn(fcd) {
        // a simple widget to handle a column in the flash card deck
        // fcd is the parent flashcard deck
        // (this is mostly for "coherence" in related function calls, like popups...)
        Widget.call(this, '<th class="ductus_FlashcardDeck_column"></th>');
        this.th = this.elt;
        this.header = new FlashcardColumnEditor(fcd, this);
        this.th.append(this.header.elt);
        this.fcd = fcd;
    }
    FlashcardColumn.prototype = chain_clone(Widget.prototype);

    // define popup callbacks to handle clicks on a column header
    FlashcardColumn.prototype.popup_html = {
        'left': gettext('add column'),
        'bottom': gettext('delete column')
            // TODO: move column
    };
    FlashcardColumn.prototype.popup_callback = {
        'left': function(column) {
            column.fcd.add_column();
        },
        'bottom': function() {
            console.log('would delete column now');
        }
    };

    function FlashcardDeck(fcd) {
        // if new, create default nested json with one column and one row
        if (!fcd) {
            fcd = {
                resource: {
                    cards: {
                        array: [{
                            resource: {
                                "sides": {
                                    "array": [{"href": "", "resource": null}]
                                }
                            }
                        }]
                    },
                    headings: {
                        array: [{text: ''}]
                    }
                }
            };
        }

        ModelWidget.call(this, fcd, '<div class="ductus_FlashcardDeck"></div>');

        // create popup menu
        this.popup_menu = new PopupWidget(this);
        this.popup_menu.elt.appendTo(this.elt);

        this.rows = [];
        this.columns = [];
        this.table = $('<table border="1"></table>').appendTo(this.elt);
        this.header_elt = $('<tr><th class="topleft_th"></th></tr>');
        this.table.append(this.header_elt);

        var this_ = this;
        $.each(fcd.resource.headings.array, function (i, heading) {
            this_.add_column(heading.text);
        });
        $.each(fcd.resource.cards.array, function (i, card) {
            this_.add_row(card);
        });

        this.table.find(".topleft_th").ductus_selectable(null, function () {
            // fixme: this will do weird things if a widget itself contains a table; we should have a class that we use for all th and td's here
            return this_.table.find("th, td");
        });

        // when the widget first loads, select the first cell
        if (this.rows.length && this.columns.length) {
            this.rows[0].elt.find('td:not(.row_td)').first().click();
        }

        // a jQuery object to attach sidebar widgets to
        this.sidebar = $('<div id="ductus_Sidebar"></div>');

        this.interaction_chooser = new InteractionChooserWidget(fcd.resource.interactions);
        this.interaction_chooser.elt.make_sidebar_widget(gettext('Interactions'), this.sidebar);

        this.tagging_widget = new TaggingWidget(fcd.resource.tags);
        this.tagging_widget.elt.make_sidebar_widget(gettext('Tags'), this.sidebar);

        this.save_widget = new SaveWidget(this, 'the lesson');
        this.save_widget.elt.make_sidebar_widget(gettext('Save'), this.sidebar);

        this.record_initial_inner_blueprint();
    }
    FlashcardDeck.prototype = chain_clone(ModelWidget.prototype);
    FlashcardDeck.prototype.inner_blueprint_repr = function () {
        var cards = [];
        $.each(this.rows, function (i, row) {
            cards.push(row.blueprint_repr());
        });
        var headings = [];
        $.each(this.columns, function (i, column) {
            headings.push({text: column.heading});
        });
        var tags = [];
        $.each(this.tagging_widget.get_tag_list(), function (i, tag) {
            if (tag != '') {
                tags.push({value: tag});
            }
        });
        return this.add_inner_blueprint_constructor({
            cards: {array: cards},
            headings: {array: headings},
            tags: {array: tags},
            interactions: this.interaction_chooser.blueprint_repr()
        });
    };
    FlashcardDeck.prototype.get_outstanding_presave_steps = function () {
        return ModelWidget.combine_presave_steps(this.rows);
    };
    FlashcardDeck.prototype.fqn = '{http://wikiotics.org/ns/2011/flashcards}flashcard_deck';
    FlashcardDeck.prototype.add_row = function (fc) {
        var row = new Flashcard(fc, this.columns);
        this.rows.push(row);
        row.elt.find(".row_td").text(this.rows.length);
        this.table.append(row.elt);
    };
    FlashcardDeck.prototype.insert_row = function (row_index, fc) {
        // insert a row (flashcard) in the flashcard deck
        // row_index: the index at which to insert the row (and move every row below further down)
        // fc: a blueprint to initialise the inserted row with
        var row = new Flashcard(fc, this.columns);
        this.rows[row_index].elt.before(row.elt);
        this.rows.splice(row_index, 0, row);
        // reindex row headers
        $(this.rows).each(function (i, row) {
            row.elt.find('.row_td').text(i + 1);
        });
    }
    FlashcardDeck.prototype.delete_row = function (fc) {
        var row_index = fc.elt.index() - 1;
        // remove each FlashcardSide in the flashcard
        fc.elt.find("td").children().each(function (i) {
            $(this).data("widget_object").reset();
        });
        fc.elt.remove();
        this.rows.splice(row_index, 1);
        // reindex row headers
        $(this.rows).each(function (i, row) {
            row.elt.find('.row_td').text(i + 1);
        });
    }
    FlashcardDeck.prototype._set_column_heading = function (column, heading) {
        column.heading = heading;
        if (heading)
            column.header.set_heading(heading);
        else
            column.header.set_heading(gettext('Side') + ' ' + column.th.index());
    };
    FlashcardDeck.prototype.add_column = function (heading) {
        var this_ = this;
        var column = new FlashcardColumn(this);
        this.columns.push(column);
        column.th.appendTo(this.header_elt);
        this._set_column_heading(column, heading);
        column.th.ductus_selectable(function () {
            return this_.column_ui_widget(column);
        }, function () {
            var display_index = column.th.index() + 1;
            return this_.table.find("th:nth-child(" + display_index + "), td:nth-child(" + display_index + ")");
        });
        $.each(this.rows, function (i, row) {
            row._append_new_cell(null, column);
        });
        // ensure the minimal width of the deck so we can scroll over the whole thing
        this.ensure_min_width();
        return column;
    };
    FlashcardDeck.prototype.column_ui_widget = function (column) {
        popup = $("#ductus_PopupWidget");
        if (popup.length) {
            popup.data('widget_object').show_popup(column);
        }
    };
    FlashcardDeck.prototype.ensure_min_width = function() {
        this.elt.css('min-width', this.table.width() + $('#side_toolbar').width() + 50);
    }

    function PopupWidget(calling_widget) {
        // the widget holding the popup menu that shows up when clicking items on the flashcard deck
        Widget.call(this, '<div id="ductus_PopupWidget"></div>');
        this_ = this;
        $.each(['left', 'top', 'right', 'bottom'], function(i, side) {
            this_.elt.append('<div id="ductus_Popup' + side + '" class="ductus_Popup"></div>');
        });
    }
    PopupWidget.prototype = chain_clone(Widget.prototype);
    PopupWidget.prototype.hide_popup = function (calling_widget) {
        // hide the popup menu and all deactivate click event handlers.
        this_ = this;
        $.each(['left', 'top', 'right', 'bottom'], function(i, side) {
            var sub_popup = this_.elt.find('#ductus_Popup' + side).hide();
            sub_popup.unbind("click");
        });
        this.elt.hide();
    }
    PopupWidget.prototype.setup_popup = function (side, content, click_cb, click_cb_arg) {
        // setup a popup on one of the sides of the clicked element
        // content is the HTML that will fill the popup menu side
        // click_cb is the function to call when the user clicks the menu item
        // click_cb_arg is an argument passed to click_cb (defined at callback setup time, callback execution time!)
        // (except for objects ? http://api.jquery.com/bind/ )
        var sub_popup = this.elt.find('#ductus_Popup'+side);
        if (content) {
            sub_popup.html(content);
            sub_popup.bind("click",
                    {cb_arg: click_cb_arg},
                    function(e) {
                        click_cb(e.data.cb_arg);
                        // prevent flashcard from picking up click event when it has a wrapped widget
                        e.stopPropagation();
                    });
            sub_popup.show();
        }
    }
    PopupWidget.prototype.show_popup = function (calling_widget) {
        // show the popup menu according to context. calling_widget is the widget that was clicked.

        // don't do anything if it's the same widget we just clicked
        if (this.calling_widget === calling_widget)
            return;
        this.calling_widget = calling_widget;
        this_ = this;
        this.hide_popup();

        leftw = this.elt.find('#ductus_Popupleft');
        rightw = this.elt.find('#ductus_Popupright');
        topw = this.elt.find('#ductus_Popuptop');
        bottomw = this.elt.find('#ductus_Popupbottom');

        this.elt.show();
        // determine which widget was clicked
        var popup_caller = null;
        if (this_.calling_widget.wrapped) {
            // the flashcard side has some content: setup popup accordingly (content and callbacks)
            popup_caller = this_.calling_widget.wrapped;
        } else {
            // no wrapped widget
            popup_caller = this_.calling_widget;
        }

        // setup the popup menu content and callbacks
        if (popup_caller.popup_html) {
            $.each(popup_caller.popup_html, function(side, content) {
                this_.setup_popup(side,
                    content,
                    function(arg) {
                        // arg is a custom variable passed by the click event handler upon binding
                        popup_caller.popup_callback[side](arg);
                        this_.elt.hide();
                    },
                    popup_caller);
            });
        }

        // if a row was clicked, make the popup display around the row header
        // if a cell was clicked, make sure we do not hide any parts of it
        var positioning_elt = this.calling_widget.elt;
        if (this.calling_widget.elt.is('tr')) {
            positioning_elt = this.calling_widget.elt.children('td.row_td');
        } else if (!this.calling_widget.elt.is('th')) {
            positioning_elt = this.calling_widget.elt.closest('td');
        }
        // position popup buttons around the clicked widget
        leftw.position({
                    "my": "right center",
                    "at": "left center",
                    "of": positioning_elt
        });
        rightw.position({
                    "my": "left center",
                    "at": "right center",
                    "of": positioning_elt
        });
        topw.position({
                    "my": "center bottom",
                    "at": "center top",
                    "of": positioning_elt
        });
        bottomw.position({
                    "my": "center top",
                    "at": "center bottom",
                    "of": positioning_elt
        });
    };

    function TaggingWidget(tags) {
        // the widget used to edit tags applied to the whole flashcard deck
        ModelWidget.call(this, tags, '<div id="ductus_TaggingWidget"><label>' + gettext('Tags (space separated):') + '</label><input /></div>');
        this.input = this.elt.children('input');
        var tag_string = '';
        if (tags) {
            for (var i = 0; i < tags.array.length; ++i) {
                var tag = tags.array[i];
                tag_string += tag.value + ' ';
            }
        }
        this.input.val(tag_string);
    }
    TaggingWidget.prototype = chain_clone(Widget.prototype);
    TaggingWidget.prototype.inner_blueprint_repr = function () {
    }
    TaggingWidget.prototype.get_tag_list = function () {
        // return a list of all tags (for use in blueprint)
        var tag_list = [];
        if (this.input && this.input.val()) {
            tag_list = this.input.val().split(" ");
        }
        return tag_list;
    }

    var fcdw = new FlashcardDeck(resource_json);
    $('#side_toolbar').append(fcdw.sidebar);
    $("#flashcard_deck_editor").append(fcdw.elt);
    fcdw.ensure_min_width();

    $("#side_toolbar_spacer").appendTo("body");
});

