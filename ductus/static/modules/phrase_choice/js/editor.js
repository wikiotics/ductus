/* Ductus
 * Copyright (C) 2010  Jim Garrison <jim@garrison.cc>
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
    function PhraseChoiceElementWidget(pce) {
	// default nested json
	if (!pce) {
	    pce = {prompt: {text: ''}, answer: {text: ''}};
	}

	Widget.call(this, '<li class="phrase_choice_element_item"> Prompt: <input class="prompt" type="text"></input> Answer: <input class="answer" type="text"></input></li>');
        this.elt.find(".prompt").val(pce.prompt.text);
        this.elt.find(".answer").val(pce.answer.text);
    }
    PhraseChoiceElementWidget.prototype = chain_clone(Widget.prototype);
    PhraseChoiceElementWidget.prototype.json_repr = function () {
	return {
	    prompt: {text: this.elt.find(".prompt").val()},
	    answer: {text: this.elt.find(".answer").val()}
	};
    };

    function PhraseChoiceGroupWidget(pcg) {
	// if new pcg, create default nested json
	if (!pcg) {
	    pcg = {resource: {group: {array: [null, null, null, null]}}};
	}

        ModelWidget.call(this, pcg, '<li class="phrase_choice_group_item"><div><span class="handle">&mdash;&mdash;&mdash;</span></div><ul></ul></li>');
        var ul = this.elt.find('ul');
        var a = pcg.resource.group.array;
        for (var i = 0, l = a.length; i < l; ++i) {
	    var pcew = new PhraseChoiceElementWidget(a[i]);
            ul.append(pcew.elt);
        }

	this.record_initial_json_repr();
    }
    PhraseChoiceGroupWidget.prototype = chain_clone(ModelWidget.prototype);
    PhraseChoiceGroupWidget.prototype.json_repr = function () {
	var array = [];
	this.elt.find(".phrase_choice_element_item").each(function (i) {
	    array.push($(this).data('widget_object').json_repr());
	});
	return this.add_json_repr_constructor({group: { array: array }});
    };
    PhraseChoiceGroupWidget.prototype.fqn = '{http://wikiotics.org/ns/2011/phrase_choice}phrase_choice_group';

    function PhraseChoiceLessonWidget(pcl) {
	// if new pcl, create default nested json
	if (!pcl) {
	    pcl = {resource: {groups: {array: []}}};
	}

        ModelWidget.call(this, pcl, '<ul></ul>');
        this.elt.sortable({'handle': '.handle'});
        var a = pcl.resource.groups.array;
        for (var i = 0, l = a.length; i < l; ++i) {
	    var pcgw = new PhraseChoiceGroupWidget(a[i]);
            this.elt.append(pcgw.elt);
        }

	this.record_initial_json_repr();
    }
    PhraseChoiceLessonWidget.prototype = chain_clone(ModelWidget.prototype);
    PhraseChoiceLessonWidget.prototype.append_new_pcg = function () {
	this.elt.append((new PhraseChoiceGroupWidget).elt);
    };
    PhraseChoiceLessonWidget.prototype.json_repr = function () {
	var groups = [];
        this.elt.find(".phrase_choice_group_item").each(function (i) {
            groups.push(ModelWidget.blueprint_repr($(this).data('widget_object')));
        });
	return this.add_json_repr_constructor({groups: {array: groups}});
    };
    PhraseChoiceLessonWidget.prototype.fqn = '{http://wikiotics.org/ns/2011/phrase_choice}phrase_choice_lesson';

    var pclw = new PhraseChoiceLessonWidget(resource_json);
    $("#pcl_editor").append(pclw.elt);
    $("#append_new_pcg_button").click(function () {
	pclw.append_new_pcg();
    });
    $(".save_form").submit(function (event) {
	var this_ = this;
	event.preventDefault(); // cancel normal submit event handling
	var blueprint = JSON.stringify(ModelWidget.blueprint_repr(pclw));
	$(".save_form").find("input:submit").attr("disabled", "disabled");
        $.ajax({
	    url: document.URL,
	    data: {
		blueprint: blueprint,
		log_message: $("#log_message").val()
	    },
	    success: function (data) {
		if (!data) {
		    // something failed, but jquery 1.4.2 gives "success"
		    // (see http://dev.jquery.com/ticket/6060)
		    alert("unknown error while saving; please try again");
		    return;
		}
		// go to the newly-saved page
		if (event.target.id === 'save_and_return') {
		    window.location = (data.page_url || resolve_urn(data.urn));
		} else {
		    $('<span class="ductus_save_notice">saved!</span>').appendTo(this_).delay(3000).fadeOut(400, function () { $(this).remove(); });
		}
	    },
	    error: function (xhr, textStatus, errorThrown) {
		alert(xhr.status + " error. save failed.");
	    },
	    complete: function (xhr, textStatus) {
		$(".save_form").find("input:submit").removeAttr("disabled");
	    },
	    type: 'POST',
	    dataType: 'json'
	});
    });
});
