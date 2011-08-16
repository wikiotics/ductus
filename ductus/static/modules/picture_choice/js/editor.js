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
    function PictureChoiceElementWidget(pce) {
	// default nested json
	if (!pce) {
	    pce = {phrase: {text: ''}, picture: null};
	}

	Widget.call(this, '<li class="picture_choice_element_item"><input class="phrase" type="text"></input></li>');
	this.picture = new PictureModelWidget(pce.picture);
	this.elt.append(this.picture.elt);
	this.audio = new AudioWidget(pce.audio || null);
	this.elt.append("Audio: ").append(this.audio.elt);
        this.elt.find(".phrase").val(pce.phrase.text);
    }
    PictureChoiceElementWidget.prototype = chain_clone(Widget.prototype);
    PictureChoiceElementWidget.prototype.json_repr = function () {
	return {
	    phrase: {text: this.elt.find(".phrase").val()},
	    picture: ModelWidget.blueprint_repr(this.picture),
	    audio: this.audio.json_repr() // we don't use blueprint_repr here, since we are in direct control of the 'href' given
	};
    };

    function PictureChoiceGroupWidget(pcg) {
	// if new pcg, create default nested json
	if (!pcg) {
	    pcg = {resource: {group: {array: [null, null, null, null]}}};
	}

        ModelWidget.call(this, pcg, '<li class="picture_choice_group_item"><div><span class="handle">&mdash;&mdash;&mdash;</span></div><ul></ul></li>');
        var ul = this.elt.find('ul');
        var a = pcg.resource.group.array;
        for (var i = 0, l = a.length; i < l; ++i) {
	    var pcew = new PictureChoiceElementWidget(a[i]);
            ul.append(pcew.elt);
        }

	this.record_initial_json_repr();
    }
    PictureChoiceGroupWidget.prototype = chain_clone(ModelWidget.prototype);
    PictureChoiceGroupWidget.prototype.json_repr = function () {
	var array = [];
	this.elt.find(".picture_choice_element_item").each(function (i) {
	    array.push($(this).data('widget_object').json_repr());
	});
	return this.add_json_repr_constructor({group: { array: array }});
    };
    PictureChoiceGroupWidget.prototype.fqn = '{http://wikiotics.org/ns/2009/picture_choice}picture_choice_group';

    function PictureChoiceLessonWidget(pcl) {
	// if new pcl, create default nested json
	if (!pcl) {
	    pcl = {resource: {groups: {array: []}}};
	}

        ModelWidget.call(this, pcl, '<ul></ul>');
        this.elt.sortable({'handle': '.handle'});
        var a = pcl.resource.groups.array;
        for (var i = 0, l = a.length; i < l; ++i) {
	    var pcgw = new PictureChoiceGroupWidget(a[i]);
            this.elt.append(pcgw.elt);
        }

	this.record_initial_json_repr();
    }
    PictureChoiceLessonWidget.prototype = chain_clone(ModelWidget.prototype);
    PictureChoiceLessonWidget.prototype.append_new_pcg = function () {
	this.elt.append((new PictureChoiceGroupWidget).elt);
    };
    PictureChoiceLessonWidget.prototype.json_repr = function () {
	var groups = [];
        this.elt.find(".picture_choice_group_item").each(function (i) {
            groups.push(ModelWidget.blueprint_repr($(this).data('widget_object')));
        });
	return this.add_json_repr_constructor({groups: {array: groups}});
    };
    PictureChoiceLessonWidget.prototype.fqn = '{http://wikiotics.org/ns/2009/picture_choice}picture_choice_lesson';

    var pclw = new PictureChoiceLessonWidget(resource_json);
    var save_widget = new SaveWidget(pclw);
    $("#pcl_editor").append(pclw.elt).append($("#append_new_pcg_button")).append(save_widget.elt);
    $("#append_new_pcg_button").click(function () {
	pclw.append_new_pcg();
    });
});
