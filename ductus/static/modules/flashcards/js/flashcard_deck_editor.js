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
        // mark the clicked widget as selected
        _unselect();
        selected = $(elt);
        selected_wrapped_set = wrapped_set_func ? wrapped_set_func() : $(elt);
        selected_wrapped_set.addClass("ductus-selected");
    }

    $.fn.ductus_selectable = function (ui_widget_func, wrapped_set_func, dblclick_handler) {
        // set click/dblclick handlers for a selectable element
        if (dblclick_handler) {
            this.dblclick(dblclick_handler);
        }
        return this.each(function () {
            $(this).click(function () {
                $('#ductus_PopupWidget').hide();
                _select($(this), wrapped_set_func);
                if (ui_widget_func) {
                    $("#side_item_editor").children().detach().end().append(ui_widget_func().elt);
                }
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
    PhraseWidget.prototype.edit_ui_widget = function () {
        var r = new Widget('<div>(see above)</div>');
        var this_ = this;
        r.focus_on_editor = function () {
            this_.input.focus();
        };
        return r;
    };
    // define popup menu content and callbacks
    PhraseWidget.prototype.popup_html = {
        'bottom': 'delete'
    };
    PhraseWidget.prototype.popup_callback = {
        // target is the phrase widget that generated the popup
        'bottom': function(target) {
            target.elt.parent().data('widget_object').reset();
        }
    };

    PhraseWidget.creation_ui_widget = function () {
        return new PhraseCreator;
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

        $.each(FlashcardSide.widgets, function (i, w) {
            var button = $('<li><a href="#fcs-new-' + i  + '">new ' + w[0] + '</a></li>');
            var creation_widget = w[1].creation_ui_widget();
            var tab_body = $('<div id="fcs-new-' + i + '"></div>').append(creation_widget.elt);
            creation_widget.elt.bind("ductus_element_selected", function (event, model_json_repr) {
                this_.fcsw.set_from_json(model_json_repr);
                this_.go_to_main_editor_tab();
            });
            this_.elt.append(tab_body);
            ul.append(button);
        });

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

        this.set_fcsw(fcsw);
    }
    FlashcardSideEditor.prototype = chain_clone(Widget.prototype);
    FlashcardSideEditor.prototype.set_fcsw = function (fcsw) {
        if (this.fcsw === fcsw)
            return;
        this.fcsw = fcsw;
        // show or hide edit/delete buttons as appropriate
        this.elt.find('.display-only-if-editable').toggle(!!this.fcsw.wrapped);

        // set editor widget
        this.editor_widget = (fcsw.wrapped && fcsw.wrapped.edit_ui_widget) ? fcsw.wrapped.edit_ui_widget() : null;
        this.elt.find('#fcs-edit-tab').parent().toggle(!!this.editor_widget);
        if (fcsw.wrapped && this.editor_widget)
            this.edit_tab_body.children().detach().end().append(this.editor_widget.elt);

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
        Widget.call(this, '<div class="ductus_FlashcardColumnEditor">Column header: <input/></div>');
        // allow user to edit heading
        // future: may allow superficial moving of column order
        // future: should also allow one to delete an entire column, after confirmation (but we will have undo soon)

        this.non_unique_warning = $('<div>Warning: each column name must be unique.</div>').appendTo(this.elt).hide();

        var this_ = this;
        this.input = this.elt.find('input');
        this.input.bind("change keyup keypress drop", function (event) {
            var heading = $.trim($(this).val());

            // do a linear search through all other columns to make sure the heading is unique
            var show_non_unique_warning = false;
            if (heading) {
                for (var i = 0; i < fcdw.columns.length; ++i) {
                    if (heading == fcdw.columns[i].heading && fcdw.columns[i] !== this_.column) {
                        heading = '';
                        show_non_unique_warning = true;
                        break;
                    }
                }
            }

            this_.non_unique_warning.toggle(show_non_unique_warning);
            this_.fcdw._set_column_heading(this_.column, heading);
        });

        this.set(fcdw, column);
    }
    FlashcardColumnEditor.prototype = chain_clone(Widget.prototype);
    FlashcardColumnEditor.prototype.set = function (fcdw, column) {
        this.column = column;
        this.fcdw = fcdw;
        this.input.val(this.column.heading || '');
    };

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
        // set the edit widget for this flashcard side
        if (!FlashcardSide._global_flashcard_side_editor) {
            FlashcardSide._global_flashcard_side_editor = new FlashcardSideEditor(this);
        } else {
            FlashcardSide._global_flashcard_side_editor.set_fcsw(this);
        }
        return FlashcardSide._global_flashcard_side_editor;
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
        this.elt.empty().append(wrapped.elt);
    };
    // popup definition for an empty flashcard side
    FlashcardSide.prototype.popup_html = {
        'left': 'new phrase',
        'right': 'new audio',
        'top': 'new picture'
    };
    // callbacks to handle clicks on an empty flashcard side
    FlashcardSide.prototype.popup_callback = {
        'left': function() {
            this_.calling_widget.set_from_json({
                resource: {
                    phrase: { text: '' },
                    fqn: PhraseWidget.prototype.fqn
                }
            });
            this_.calling_widget.wrapped.input.focus();
        },
        'right': function() {
            FlashcardSide._global_flashcard_side_editor.elt.tabs("select", "fcs-new-1");
            $('#side_item_editor').show();
        },
        'top': function() {
            FlashcardSide._global_flashcard_side_editor.elt.tabs("select", "fcs-new-0");
            $('#side_item_editor').show();
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
        if (!Flashcard._global_flashcard_editor) {
            Flashcard._global_flashcard_editor = new FlashcardEditor(this);
        } else {
            Flashcard._global_flashcard_editor.set_fcw(this);
        }
        return Flashcard._global_flashcard_editor;
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
        'left': 'add row'
            // TODO: move row
    };
    // callbacks to handle clicks on an empty flashcard side
    Flashcard.prototype.popup_callback = {
        'left': function() {
            var fcd = $(".ductus_FlashcardDeck").data('widget_object');
            fcd.add_row();
        }
    };

    function ChoiceInteractionWidget(ci) {
        ModelWidget.call(this, ci, '<div class="ductus_ChoiceInteractionWidget"></div>');
        this.elt.append('Prompt: <input name="prompt" class="prompt"/> Answer: <input name="answer" class="answer"/>');
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
        this.elt.append('Audio: <input name="audio" class="audio"/> Transcript (optional): <input name="transcript" class="transcript"/>');
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
        $('<a href="javascript:void(0)">Add a "choice" interaction</a>').click(function () {
            this_.__add_interaction(new ChoiceInteractionWidget());
        }).appendTo($('<li></li>').appendTo(this.new_interaction_buttons));
        $('<a href="javascript:void(0)">Add an audio lesson interaction</a>').click(function () {
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
        $('<span>delete interaction</span>').button({text: false, icons: {primary: 'ui-icon-close'}}).click(function () {
            $(this).parent('li').remove();
        }).appendTo(li);
    };

    function FlashcardColumn(fcd) {
        // a simple widget to handle a column in the flash card deck
        // fcd is the parent flashcard deck
        // (this is mostly for "coherence" in related function calls, like popups...)
        Widget.call(this, '<th class="ductus_FlashcardDeck_column"></th>');
        this.th = this.elt;
        this.fcd = fcd;
    }
    FlashcardColumn.prototype = chain_clone(Widget.prototype);

    // define popup callbacks to handle clicks on a column header
    FlashcardColumn.prototype.popup_html = {
        'left': 'add colummn',
        'bottom': 'delete column'
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

        this.table.find(".topleft_th").ductus_selectable(function () {
            return this_.ui_widget();
        }, function () {
            // fixme: this will do weird things if a widget itself contains a table; we should have a class that we use for all th and td's here
            return this_.table.find("th, td");
        });

        $('<a class="new_row_button" href="javascript:void(0)">add new row</a>').click(function () {
            this_.add_row();
        }).appendTo($('<div></div>').appendTo(this.elt));
        $('<a class="new_column_button" href="javascript:void(0)">add new column</a>').click(function () {
            this_.add_column();
        }).appendTo($('<div></div>').appendTo(this.elt));

        // when the widget first loads, select the first cell
        if (this.rows.length && this.columns.length) {
            this.rows[0].elt.find('td:not(.row_td)').first().click();
        }

        // a jQuery object to attach sidebar widgets to
        this.sidebar = $('<div id="ductus_Sidebar"></div>');

        this.interaction_chooser = new InteractionChooserWidget(fcd.resource.interactions);
        this.interaction_chooser.elt.make_sidebar_widget("Interactions", this.sidebar);

        this.tagging_widget = new TaggingWidget(fcd.resource.tags);
        this.tagging_widget.elt.make_sidebar_widget("Tags", this.sidebar);

        this.save_widget = new SaveWidget(this, 'the lesson');
        this.save_widget.elt.make_sidebar_widget("Save", this.sidebar);

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
    FlashcardDeck.prototype._set_column_heading = function (column, heading) {
        column.heading = heading;
        if (heading)
            column.th.text(heading);
        else
            column.th.html('<span class="ductus_FlashcardDeck_anonymous_column_name">Side ' + column.th.index() + '</span>');
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
        return column;
    };
    FlashcardDeck.prototype.ui_widget = function (column) {
        if (!FlashcardDeck._global_flashcard_deck_editor)
            FlashcardDeck._global_flashcard_deck_editor = new FlashcardDeckEditor(this);
        return FlashcardDeck._global_flashcard_deck_editor;
    };
    FlashcardDeck.prototype.column_ui_widget = function (column) {
        popup = $("#ductus_PopupWidget");
        if (popup.length) {
            popup.data('widget_object').show_popup(column);
        }
        if (!FlashcardDeck._global_flashcard_column_editor) {
            FlashcardDeck._global_flashcard_column_editor = new FlashcardColumnEditor(this, column);
        } else {
            FlashcardDeck._global_flashcard_column_editor.set(this, column);
        }
        return FlashcardDeck._global_flashcard_column_editor;
    };

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

        // position popup buttons around the clicked widget
        leftw.position({
                    "my": "right center",
                    "at": "left center",
                    "of": calling_widget.elt
        });
        rightw.position({
                    "my": "left center",
                    "at": "right center",
                    "of": calling_widget.elt
        });
        topw.position({
                    "my": "center bottom",
                    "at": "center top",
                    "of": calling_widget.elt
        });
        bottomw.position({
                    "my": "center top",
                    "at": "center bottom",
                    "of": calling_widget.elt
        });
    };

    function TaggingWidget(tags) {
        // the widget used to edit tags applied to the whole flashcard deck
        ModelWidget.call(this, tags, '<div id="ductus_TaggingWidget"><label>Tags (space seperated):</label><input /></div>');
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
    $("#side_item_editor").before(fcdw.sidebar);
    $("#side_item_editor").make_sidebar_widget("item editor", fcdw.sidebar);
    $("#flashcard_deck_editor").append(fcdw.elt);

    $("#side_toolbar_spacer").appendTo("body");
    $('#side_item_editor').show();
});

