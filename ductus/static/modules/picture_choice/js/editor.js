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
    function assert(condition_lambda) {
	if (!condition_lambda())
	    throw { name: "assertion_error", message: condition_lambda.toString() };
    }

    function chain_clone(obj) {
	function F() {}
	F.prototype = obj;
	return new F;
    }

    function compare_nested_objects (a, b) {
	// don't send this function any object with a circular reference
	var i, alen, prop, aprops, bprops;
	if (typeof(a) !== typeof(b)) return false;
	if (typeof(a) !== "object") return (a === b);
	if (a === null || b === null) return (a === b);

	if (a.constructor === Array) {
	    alen = a.length;
	    if (alen !== b.length) return false;
	    for (i = 0; i < alen; ++i) {
		if (!compare_nested_objects(a[i], b[i])) return false;
	    }
	    return true;
	} else {
	    // it's a dictionary-like object
	    aprops = [];
	    bprops = [];
	    for (prop in a) {
		if (a.hasOwnProperty(prop)) aprops.push(prop);
	    }
	    for (prop in b) {
		if (b.hasOwnProperty(prop)) bprops.push(prop);
	    }
	    aprops.sort();
	    bprops.sort();
	    if (!compare_nested_objects(aprops, bprops)) return false;
	    for (i = 0; i < aprops.length; ++i) {
		prop = aprops[i];
		if (!compare_nested_objects(a[prop], b[prop])) return false;
	    }
	    return true;
	}
    }

    function Widget(initial_html_code) {
	this.elt = $(initial_html_code);
	this.elt.data("widget_object", this);
	this.elt.addClass("ductus_pce_widget");
    }
    Widget.prototype.cleanup = function () {
	// call this function when we are done with the object to prevent
	// memory leaks in IE
	// fixme: make this function do more
	delete this.elt;
    };

    function ModelWidget(initial_data, initial_html_code) {
	Widget.call(this, initial_html_code);
	this.initial_href = initial_data ? initial_data.href : null;
    }
    ModelWidget.prototype = chain_clone(Widget.prototype);
    ModelWidget.prototype.record_initial_json_repr = function () {
	this.initial_json_repr = this.initial_href ? this.json_repr() : null;
    };
    ModelWidget.prototype.add_json_repr_constructor = function (json_repr) {
	// yes, this modifies the dictionary in place
	if (this.initial_href) {
	    json_repr['@patch'] = this.initial_href;
	} else {
	    json_repr['@create'] = this.fqn;
	}
	return json_repr;
    };
    ModelWidget.blueprint_repr = function (obj) {
	// fixme: we could save some bandwidth by doing a similar thing for
	// elements/attributes as well (right now we just do it for models)
	var json_repr = obj.json_repr();
	if (obj.initial_json_repr
	        && compare_nested_objects(obj.initial_json_repr, json_repr)) {
	    return {'href': obj.initial_href};
	} else {
	    return {'resource': json_repr};
	}
    };

    function UrnPictureDisplayWidget(picture) {
	Widget.call(this, '<img src="' + resolve_urn(picture.href) + '?view=image&amp;max_size=50,50"/>');
	this.picture_json = picture;

	this.elt.draggable({helper: 'clone'});
	this.elt.addClass('ductus_draggable_picture');
    }
    UrnPictureDisplayWidget.prototype = chain_clone(Widget.prototype);
    UrnPictureDisplayWidget.prototype.clone_display_widget = function () {
	return new UrnPictureDisplayWidget(this.picture_json);
    };
    UrnPictureDisplayWidget.prototype.do_json_repr = function () {
	return {'@patch': this.picture_json.href};
    };

    function FlickrPictureDisplayWidget(flickr_photo) {
	Widget.call(this, '<img/>');
	this.elt.attr("src", flickr_photo.square_url);
	this.elt.attr("title", '"' + flickr_photo.title + '" by [' + flickr_photo.owner + '] ' + flickr_photo.license);
	this.flickr_photo = flickr_photo;

	this.elt.draggable({helper: 'clone'});
	this.elt.addClass('ductus_draggable_picture');
    }
    FlickrPictureDisplayWidget.prototype = chain_clone(Widget.prototype);
    FlickrPictureDisplayWidget.prototype.clone_display_widget = function () {
	return new FlickrPictureDisplayWidget(this.flickr_photo);
    };
    FlickrPictureDisplayWidget.prototype.do_json_repr = function () {
	return {
	    '@create': PictureWidget.prototype.fqn,
	    'flickr_photo_id': this.flickr_photo.id
	};
    };

    function PictureWidget(picture) {
	var self = this;

	ModelWidget.call(this, picture, '<span></span>');
	this.image_holder = $('<span style="display: inline-block">drag image here</span>');
	this.rotation_controls = $('<span></span>');
	this.elt.append(this.image_holder).append(this.rotation_controls);

	// replace image control
	this.replace_image_button = $('<a>find new image</a>');
	this.replace_image_button.click(function () {
	    $(this).hide();
	    var search_box = new PictureSearchWidget(function (result) {
		self.replace_image_button.show();
		self.set_display_widget(result);
		search_box.destroy(); // we should just hide it, but that will store lots of memory if you work for a while... hmm
	    });
	    self.elt.append(search_box.elt.hide());
	    search_box.elt.slideDown();
	});
	this.elt.append(this.replace_image_button);

	// rotation controls
	var rotate_left_button = $('<img alt="rotate left" title="rotate left" src="' + ductus_media_prefix + '/modules/picture/img/object-rotate-left.png"/>');
	var rotate_right_button = $('<img alt="rotate right" title="rotate right" src="' + ductus_media_prefix + '/modules/picture/img/object-rotate-right.png"/>');
	rotate_left_button.click(function () { self.rotate_left(); });
	rotate_right_button.click(function () { self.rotate_right(); });
	this.rotation_controls.append(rotate_left_button).append(rotate_right_button).hide();
	this.net_rotation = 0;

	// rotation display, until we implement on-the-fly rotation w/ canvas
	this.rotation_number_display = $("<span></span>");
	this.rotation_controls.append(this.rotation_number_display);

	// set initial picture display widget
	if (picture) {
	    this.set_display_widget(new UrnPictureDisplayWidget(picture));
	}

	// image_holder should receive drop events
	this.image_holder.droppable({
	    accept: '.ductus_draggable_picture',
	    tolerance: 'pointer',
	    drop: function (event, ui) {
		var source_display_widget = ui.draggable.data('widget_object');
		var source_picture_widget = source_display_widget._picture_widget;
		if (source_picture_widget && self._display_widget) {
		    // swap them, including rotation data
		    var source_rotation = source_picture_widget.net_rotation;
		    var target_rotation = self.net_rotation;
		    source_picture_widget.set_display_widget(self._display_widget.clone_display_widget());
		    self.set_display_widget(source_display_widget.clone_display_widget());
		    self.set_rotation(source_rotation);
		    source_picture_widget.set_rotation(target_rotation);
		} else {
		    // clone the source and show an effect
		    self.set_display_widget(source_display_widget.clone_display_widget());
		    ui.draggable.effect("transfer", {to: this}, 500);
		}
	    }
	});

	this.record_initial_json_repr();
    }
    PictureWidget.prototype = chain_clone(ModelWidget.prototype);
    PictureWidget.prototype.set_display_widget = function (widget) { // fixme: This is a terrible function name!
	if (!widget) {
	    // in the future we may also want to allow null as an argument, which would reset the widget to uninitialized
	    return;
	}

	this._display_widget = widget;
	widget._picture_widget = this; // circular reference
	this.image_holder.empty().append(widget.elt);
	this.set_rotation(0);
	this.rotation_controls.show();
    };
    PictureWidget.prototype.json_repr = function () {
	if (!this._display_widget) {
	    throw {
		name: 'json_repr_error',
		message: 'Not all pictures are filled in'
	    };
	}
	var repr = this._display_widget.do_json_repr();
	if (this.net_rotation)
	    repr.net_rotation = this.net_rotation;
	return repr;
    };
    PictureWidget.prototype.rotate_left = function () {
	this.set_rotation((this.net_rotation + 90) % 360);
    };
    PictureWidget.prototype.rotate_right = function () {
	this.set_rotation((this.net_rotation + 270) % 360);
    };
    PictureWidget.prototype.set_rotation = function (degrees) {
	assert(function () { return $.inArray(degrees, [0, 90, 180, 270]) !== -1; });
	this.net_rotation = degrees;
	this.rotation_number_display.text(degrees ? (degrees + "") : "");
    };
    PictureWidget.prototype.fqn = '{http://wikiotics.org/ns/2009/picture}picture';

    function PictureSearchWidget(result_callback, initial_query_data) {
	this.result_callback = result_callback;
	if (!initial_query_data) {
	    initial_query_data = {};
	}

	Widget.call(this, '<div><form>What: <input name="q"/> Where: <input name="place"/><input type="submit" value="search"/><br/><input type="radio" name="sort" value="date-posted-desc" checked/>Recent <input type="radio" name="sort" value="interestingness-desc"/>Interesting <input type="radio" name="sort" value="relevance"/>Relevant | Search by <input type="radio" name="search_by" value="text" checked/>Text <input type="radio" name="search_by" value="tags"/>Tags</form></div>');
	if (DUCTUS_FLICKR_GROUP_ID) {
	    $(this.elt).find("form").append('<div><input type="checkbox" name="group" value="' + DUCTUS_FLICKR_GROUP_ID + '"/> Restrict to project\'s Flickr group</div>');
	}
	this.elt.addClass("ductus_PictureSearchWidget");
	var search_results_elt = $('<div class="search_results"></div>');
	this.elt.find("form").submit(function () {
	    $.ajax({
		url: "/new/picture",
		data: "view=flickr_search&" + $(this).serialize(),
		dataType: "json",
		success: function (data, textStatus) {
		    if (!data) {
			// something failed, but jquery 1.4.2 gives "success"
			// (see http://dev.jquery.com/ticket/6060)
			return;
		    }
		    search_results_elt.empty();
		    if (data.place) {
			search_results_elt.append($("<div></div>").text(data.place));
		    }
		    for (var i = 0; i < data.photos.length; ++i) {
			var photo = data.photos[i];
			var display_widget = new FlickrPictureDisplayWidget(photo);
			display_widget.elt.click(function () {
			    result_callback($(this).data('widget_object').clone_display_widget());
			});
			search_results_elt.append(display_widget.elt);
		    }
		},
		error: function (xhr, textStatus, errorThrown) {
		    alert("error: " + textStatus);

		}
	    });
	    return false;
	});
	this.elt.append(search_results_elt);
    }
    PictureSearchWidget.prototype = chain_clone(Widget.prototype);
    PictureSearchWidget.prototype.destroy = function () {
	this.elt.remove();
    };

    function PictureChoiceElementWidget(pce) {
	// default nested json
	if (!pce) {
	    pce = {phrase: {text: ''}, picture: null};
	}

	Widget.call(this, '<li class="picture_choice_element_item"><input class="phrase" type="text"></input></li>');
	this.picture = new PictureWidget(pce.picture);
	this.elt.append(this.picture.elt);
        this.elt.find(".phrase").val(pce.phrase.text);
    }
    PictureChoiceElementWidget.prototype = chain_clone(Widget.prototype);
    PictureChoiceElementWidget.prototype.json_repr = function () {
	return {
	    phrase: {text: this.elt.find(".phrase").val()},
	    picture: ModelWidget.blueprint_repr(this.picture)
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
    $("#pcl_editor").append(pclw.elt);
    $("#append_new_pcg_button").click(function () {
	pclw.append_new_pcg();
    });
    $("#save_form").submit(function (event) {
	event.preventDefault(); // cancel normal submit event handling
	var blueprint = JSON.stringify(ModelWidget.blueprint_repr(pclw));
	$(this).find("input:submit").attr("disabled", "disabled");
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
		window.location = (data.page_url || resolve_urn(data.urn));
	    },
	    error: function (xhr, textStatus, errorThrown) {
		alert(xhr.status + " error. save failed.");
	    },
	    complete: function (xhr, textStatus) {
		$("#save_form").find("input:submit").removeAttr("disabled");
	    },
	    type: 'POST',
	    dataType: 'json'
	});
    });
});
