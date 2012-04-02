/* Ductus
 * Copyright (C) 2012  Laurent Savaete <laurent@wikiotics.org>
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

$(function() {
    // this file requires widget.js to be included

    function FiveSecWidget(title, instructions, prompt, answer, controls) {
        // common stuff for 5 sec widgets
        var initial_html = '<div class="ductus_FiveSecWidget">' +
            '<div id="ductus_FSWTitle"></div>' +
            '<div id="ductus_FSWInstructions"></div>' +
            '<div id="ductus_FSWContent">' +
                '<div id="ductus_FSWPrompt"></div>' +
                '<div id="ductus_FSWAnswer"></div>' +
                '<div id="ductus_FSWControls"></div>' +
            '</div>' +
            '<div id="ductus_FSWFooter"></div>' +
            '</div>';
        ModelWidget.call(this, null, initial_html);
        if (title)
            this.set_title(title);
        if (instructions)
            this.set_instructions(instructions);
        if (prompt)
            this.set_prompt(prompt);
        if (answer)
            this.set_answer(answer);
        if (controls)
            this.set_controls(controls);
    }
    FiveSecWidget.prototype = chain_clone(ModelWidget.prototype);
    FiveSecWidget.prototype.set_title = function(title) {
        this.elt.find('#ductus_FSWTitle').html(title);
    };
    FiveSecWidget.prototype.set_instructions = function(instr) {
        this.elt.find('#ductus_FSWInstructions').html(instr);
    };
    FiveSecWidget.prototype.set_prompt = function(prompt) {
        this.elt.find('#ductus_FSWPrompt').html(prompt);
    };
    FiveSecWidget.prototype.set_answer = function(answer) {
        this.elt.find('#ductus_FSWAnswer').html(answer);
    };
    FiveSecWidget.prototype.set_footer = function(footer) {
        this.elt.find('#ductus_FSWFooter').html(footer);
    };
    FiveSecWidget.prototype.set_controls = function(controls) {
        // replace existing buttons with the ones provided in argument
        var ctrl = this.elt.find('#ductus_FSWControls');
        ctrl.empty();
        $.each(controls.buttons, function(i, button) {
            var btn = $('<div class="ductus_FSWButton">' + button.label + '</div>');
            btn.appendTo(ctrl);
            btn.button();
            btn.click(function() { button.callback(); });
        });
        if (typeof controls.links !== 'undefined') {
            $.each(controls.links, function(i, link) {
                var lnk = $('<a class="ductus_FSWlink" href="#">' + link.label + '</a>');
                lnk.appendTo(ctrl);
                lnk.click(function() { if (!lnk.hasClass('disabled')) { link.callback(); } });
            });
        }
    };

    /*
     * a simplified phrasewidget copied from flashcarddeck editor to avoid
     * importing the whole thing. Just here to allow easy blueprinting.
     */
    function PhraseWidget(phrase) {
        ModelWidget.call(this, phrase, '<div class="ductus_PhraseWidget"></div>');

        this.input = $('<textarea/>');
        if (phrase)
            this.input.val(phrase.resource.phrase.text);
        this.elt.append(this.input);

        this.record_initial_inner_blueprint();
    }
    PhraseWidget.prototype = chain_clone(ModelWidget.prototype);
    PhraseWidget.prototype.inner_blueprint_repr = function() {
        return {
            '@create': PhraseWidget.prototype.fqn,
            'phrase': {text: this.input.val()}
        };
    };
    PhraseWidget.prototype.fqn = '{http://wikiotics.org/ns/2011/phrase}phrase';

    /*
     * The subtitle widget proposes an audio bit to the user to be subtitled.
     * The user can listen to a recorded phrase for which we have no written transcription,
     * and type in what s/he hears.
     * The widget requests a prompt from the server (server side handling to be defined) by
     * accessing /five-sec-widget/get-audio-to-subtitle?params...
     * and receives a JSON like:
     * { flashcard: blueprint for a flashcard with an empty phrase + an audio,
     *   url: the url to the lesson from which it was taken, so the server knows what to update
     * }
     * (the url will be removed once indexing works on the server side.
     * It sends the same JSON back with the phrase filled in for the server to update the database.
     */
    function SubtitleFSWidget() {
        FiveSecWidget.call(this,
                'Got 5 seconds?',
                'Can you type in what you hear?'
                );
        this.language = 'fr';
        this.init_widget();
        this.get_audio();
    }
    SubtitleFSWidget.prototype = chain_clone(FiveSecWidget.prototype);
    SubtitleFSWidget.prototype.init_widget = function() {
        this.set_footer(
                '<select id="ductus_FSWLanguage" name="FSWLanguage">' +
                '<option value="de">Deutsch</option>' +
                '<option selected="selected" value="fr">Français</option>' +
                '<option value="zh">中文 - Mandarin Chinese</option>' +
                '</select>'
                );
        widget = this;
        this.elt.find('#ductus_FSWLanguage').change(function() {
            widget.language = $(this).find(':selected').attr('value');
            widget.get_audio();
        });
    };

    SubtitleFSWidget.prototype.init_from_blueprint = function(data) {
        // called when the audio prompt is received from AJAX to fill in the widget
        this_ = this;
        this.initial_href = data.href;
        this.fsi_url = data.fsi_url;
        this.fsi_index = data.fsi_index;
        this.tags = [];
        this.tags = data.resource.tags.array;
        this.card_sides = [];
        // TODO: use flashcard deck blueprint to decide where phrase and audio are, instead of hard coding them
        this.card_sides[0] = new PhraseWidget();
        this.set_answer(this.card_sides[0].elt);
        this.setup_audio_prompt(data);
        $.each(data.resource.sides.array, function(i, side) {
            if (i > 1) {
                this_.card_sides[i] = {'href': data.resource.sides.array[i].href};
            }
        });
        this.setup_controls(data);
        this.record_initial_inner_blueprint();
    };
    SubtitleFSWidget.prototype.setup_audio_prompt = function(data) {
        this.audio_widget = new AudioWidget(data.resource.sides.array[1]);
        this.card_sides[1] = this.audio_widget;
        this.set_prompt(this.audio_widget.elt);
    };
    SubtitleFSWidget.prototype.setup_controls = function(data) {
        // setup buttons to save or cancel, skip...
        fsw = this;
        $.each(data.resource.tags.array, function(i, tag) {
            if (tag.value.substring(0, 9) == 'language:') {
                fsw.language = tag.value.substring(9);
                return false;
            }
        });
        var fsw = this;
        var controls = {
            'buttons': [
                {'label': 'This is not ' + this.language,
                 'callback': function() { fsw.incorrect_language(); return false; }
                },
                {'label': 'Save',
                 'callback': function() { fsw.submit(); return false; }
                }
            ],
            'links': [
                {'label': 'skip',
                    'callback': function() { widget.get_audio(); }
                },
                {'label': 'flag',
                    'callback': function() {
                        widget.tags.push({value: 'flag:needs-review'});
                        widget.submit();
                    }
                }
            ]
        };
        this.set_controls(controls);
    };
    SubtitleFSWidget.prototype.disable_controls = function() {
        this.elt.find('#ductus_FSWControls > .ductus_FSWButton').button('option', 'disabled', true);
        this.elt.find('#ductus_FSWControls > .ductus_FSWlink').addClass('disabled');
    };

    SubtitleFSWidget.prototype.inner_blueprint_repr = function() {
        var sides = [];
        $.each(this.card_sides, function(i, side) {
            if (i < 2) {
                bp = side.blueprint_repr();
                sides.push(bp);
            } else {
                sides.push(side);
            }
        });
        return this.add_inner_blueprint_constructor({ sides: { array: sides }, tags: { array: this.tags }});
    }
    SubtitleFSWidget.prototype.thank_user = function() {
        // report success, and offer to take another quizz
        this.set_answer('<div>Thank you for your contribution!</div>');
        this_ = this;
        var controls = {
            'buttons': [
                {'label': 'One more!',
                 'callback': function() { this_.get_audio(); return false; }
                }
            ]};
        this.set_controls(controls);
    };
    SubtitleFSWidget.prototype.incorrect_language = function() {
        // report an incorrect language by removing the corresponding
        // "language:code" tag from the flashcard
        function getKey(data) {
              for (var prop in data)
                      return prop;
        }
        this.tags.splice(getKey('language:' + this.language), 1);
        // FSI specific: force a language tag as we know it's english from FSI design
        $.each(this.tags, function(i, tag) {
            if (tag.value == 'fsi') {
                this.tags.push({ value: 'language:en'});
            }
        });
        this.submit();
    };
    SubtitleFSWidget.prototype.submit = function() {
        // build a blueprint and send it to the server for processing
        // called when user clicks 'save'

        // remove language tag if it exists, and add the correct language one
        function getKey(data) {
              for (var prop in data)
                      return prop;
        }
        this.tags.splice(getKey('language:' + this.language), 1);
        this.tags.push({ value: 'language:' + this.language });

        blueprint = {'resource': this.inner_blueprint_repr()};
        this_ = this;
        $.ajax({
            url: window.location.pathname,
            data: {
                blueprint: JSON.stringify(blueprint),
                // temp hack for fsi upload
                fsi_url: this_.fsi_url,
                fsi_index: this_.fsi_index,
                log_message: '5sec-widget (subtitle)'
            },
            success: function(data) {
                this_.thank_user(data);
            },
            error: function(xhr, textStatus, errorThrown) {
                console.log(xhr.status + ' error. save failed.');
            },
            complete: function(xhr, textStatus) {
            },
            type: 'POST',
            dataType: 'json'
        });
    };
    SubtitleFSWidget.prototype.get_audio = function() {
        // get a JSON object to be passed to the audio element
        // response expected: {language: "langcode", blueprint: {the_blueprint}}
        this_ = this;
        this.set_prompt('Loading...');
        this.disable_controls();
        $.ajax({
            url: '/five-sec-widget/get-audio-to-subtitle',
            data: {
                language: this_.language
            },
            success: function(data) {
                         this_.init_from_blueprint(data);
                     },
            error: function(xhr, textStatus, errorThrown) {
                       this_.set_prompt('Error while loading audio content, sorry. Please contact the site administrator.');
                       this_.disable_controls();
                       console.log(xhr.status + ' error. Failed to get audio.');
                   },
            complete: function(xhr, textStatus) {
                          console.log('ajax complete');
                      },
            type: 'GET',
            dataType: 'json'
        });
    };

    var fsw = new SubtitleFSWidget();
    fsw.elt.appendTo('#ductus_five_sec_widget');
});

