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
        if (!selected) return;
        selected_wrapped_set.removeClass("ductus-selected");
    }
    function _select(elt, wrapped_set_func) {
        _unselect();
        selected = $(elt);
        selected_wrapped_set = wrapped_set_func ? wrapped_set_func() : $(elt);
        selected_wrapped_set.addClass("ductus-selected");
    }

    $.fn.ductus_selectable = function (ui_widget_func, wrapped_set_func, dblclick_handler) {
        if (dblclick_handler) {
            this.dblclick(dblclick_handler);
        }
        return this.each(function () {
            $(this).click(function () {
                _select($(this), wrapped_set_func);
                if (ui_widget_func) {
                    $("#bottom_toolbar").children().detach().end().append(ui_widget_func().elt);
                }
            });
        });
    };

    function PhraseWidget(phrase) {
        ModelWidget.call(this, phrase, '<div class="ductus_PhraseWidget"></div>');

        this.input = $('<input/>');
        if (phrase)
            this.input.val(phrase.resource.phrase.text);
        this.elt.append(this.input);

        this.record_initial_json_repr();
    }
    PhraseWidget.prototype = chain_clone(ModelWidget.prototype);
    PhraseWidget.prototype.json_repr = function () {
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
        Widget.call(this, '<div class="ductus_FlashcardSideEditor"><ul></ul></div>');

        var this_ = this;
        var ul = this.elt.find("ul");

        $.each(FlashcardSide.widgets, function (i, w) {
            var button = $('<li><a href="#new-' + i  + '">new ' + w[0] + '</a></li>');
            var creation_widget = w[1].creation_ui_widget();
            var tab_body = $('<div id="new-' + i + '"></div>').append(creation_widget.elt);
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

        var delete_tab_body = $('<div id="fcs-delete">Confirm deletion: <form><input type="submit" value="Delete"/></form></div>');
        delete_tab_body.find("form").submit(function () { this_.fcsw.reset(); return false; });
        ul.append('<li><a href="#fcs-delete" id="fcs-delete-tab" class="display-only-if-editable">delete</a></li>');
        this.elt.append(delete_tab_body);

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

        // bring up editor widget
        if (this.fcsw.wrapped) {
            this.editor_widget = this.fcsw.wrapped.edit_ui_widget();
            this.edit_tab_body.children().detach().end().append(this.editor_widget.elt);
        }
    };
    FlashcardSideEditor.prototype.go_to_main_editor_tab = function () {
        if (this.fcsw.wrapped) {
            this.elt.tabs("select", "fcs-edit");
            if (this.editor_widget && this.editor_widget.focus_on_editor)
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
        Widget.call(this, '<div class="ductus_FlashcardSide"></div>');
        this.set_from_json(fcs);
    }
    FlashcardSide.prototype = chain_clone(Widget.prototype);
    FlashcardSide.prototype.json_repr = function () {
        if (this.wrapped) {
            return ModelWidget.blueprint_repr(this.wrapped);
        } else {
            return {resource: null};
        }
    };
    FlashcardSide.prototype.reset = function () {
        this.wrapped = null;
        this.elt.empty().html("&nbsp;");
    };
    FlashcardSide.prototype.ui_widget = function () {
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
    FlashcardSide.widgets = [
        ['picture', PictureModelWidget],
        //['audio', AudioWidget], // fixme: AudioWidget's json_repr is all messed up.  see audio.json_repr()
        ['phrase', PhraseWidget]
    ];
    FlashcardSide.widgets_by_fqn = {};
    $.each(FlashcardSide.widgets, function (i, w) {
        FlashcardSide.widgets_by_fqn[w[1].prototype.fqn] = w[1];
    });

    function Flashcard(fc, columns) {
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

        this.record_initial_json_repr();
    }
    Flashcard.prototype = chain_clone(ModelWidget.prototype);
    Flashcard.prototype.json_repr = function () {
        var sides = [];
        this.elt.find("td").children().each(function (i) {
            sides.push($(this).data("widget_object").json_repr());
        });
        return this.add_json_repr_constructor({ sides: { array: sides } });
    };
    Flashcard.prototype.fqn = '{http://wikiotics.org/ns/2011/flashcards}flashcard';
    Flashcard.prototype.ui_widget = function () {
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

        ModelWidget.call(this, fcd, '<table border="1" class="ductus_FlashcardDeck"></table>');

        this.rows = [];
        this.columns = [];
        this.header_elt = $('<tr><th class="topleft_th"></th></tr>');
        this.elt.append(this.header_elt);

        var this_ = this;
        $.each(fcd.resource.headings.array, function (i, heading) {
            this_.add_column(heading.text);
        });
        $.each(fcd.resource.cards.array, function (i, card) {
            this_.add_row(card);
        });

        this.elt.find(".topleft_th").ductus_selectable(function () {
            return this_.ui_widget();
        }, function () {
            // fixme: this will do weird things if a widget itself contains a table; we should have a class that we use for all th and td's here
            return this_.elt.find("th, td");
        });

        // when the widget first loads, select the first cell
        if (this.rows && this.columns) {
            this.rows[0].elt.find('td:not(.row_td)').first().click();
        }

        this.record_initial_json_repr();
    }
    FlashcardDeck.prototype = chain_clone(ModelWidget.prototype);
    FlashcardDeck.prototype.json_repr = function () {
        var cards = [];
        $.each(this.rows, function (i, row) {
            cards.push(ModelWidget.blueprint_repr(row));
        });
        var headings = [];
        $.each(this.columns, function (i, column) {
            headings.push({text: column.heading});
        });
        return this.add_json_repr_constructor({cards: {array: cards}, headings: {array: headings}});
    };
    FlashcardDeck.prototype.fqn = '{http://wikiotics.org/ns/2011/flashcards}flashcard_deck';
    FlashcardDeck.prototype.add_row = function (fc) {
        var row = new Flashcard(fc, this.columns);
        this.rows.push(row);
        this.elt.append(row.elt);
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
        var column = {}; // will contain attributes `th` and `heading`
        this.columns.push(column);
        column.th = $('<th></th>').appendTo(this.header_elt);
        this._set_column_heading(column, heading);
        column.th.ductus_selectable(function () {
            return this_.column_ui_widget(column);
        }, function () {
            var display_index = column.th.index() + 1;
            return this_.elt.find("th:nth-child(" + display_index + "), td:nth-child(" + display_index + ")");
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
        if (!FlashcardDeck._global_flashcard_column_editor) {
            FlashcardDeck._global_flashcard_column_editor = new FlashcardColumnEditor(this, column);
        } else {
            FlashcardDeck._global_flashcard_column_editor.set(this, column);
        }
        return FlashcardDeck._global_flashcard_column_editor;
    };

    var fcdw = new FlashcardDeck(resource_json);
    var save_widget = new SaveWidget(fcdw);
    $("#flashcard_deck_editor").append(fcdw.elt).append($("#new_row_button").parent()).append($("#new_column_button").parent()).append(save_widget.elt);

    $("#new_row_button").click(function () {
	fcdw.add_row();
    });
    $("#new_column_button").click(function () {
	fcdw.add_column();
    });

    $("#bottom_toolbar_spacer").appendTo("body");
});

