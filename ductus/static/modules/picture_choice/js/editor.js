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
		var source_picture_widget = source_display_widget.elt.data('_picture_widget');
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

	// using data() deals with circular reference memory leak problem on IE
	this._display_widget = widget;
	widget.elt.data('_picture_widget', this);

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

    function AudioWidget(audio) {
        // if new, create default nested json
        if (!audio) {
            audio = {href: ''};
        }

        ModelWidget.call(this, audio, '<span><span class="control"></span><span class="status"></span></span>');
        this.control_elt = this.elt.find('.control');
        this.status_elt = this.elt.find('.status');
        if (audio.href) {
            this._set_state_remote_urn(audio.href);
        } else {
            this._set_state_empty();
        }

        // we don't call this.record_initial_json_repr() since we never call blueprint_repr() on this object
    }
    AudioWidget.prototype = chain_clone(ModelWidget.prototype);
    AudioWidget.prototype.json_repr = function () {
        if (this.file) {
            alert('Please upload all audio before attempting to save');
            throw 'File has not been uploaded yet.';
        }
        return {href: (this._urn || '')};
    };
    AudioWidget.prototype.fqn = '{http://wikiotics.org/ns/2010/audio}audio';
    AudioWidget.prototype._reset = function () {
        // don't call this; call _set_state_* instead, which will automatically call this
        this.control_elt.empty();
        this.status_elt.empty();
        this._urn = undefined;
        this.file = null;
    };
    AudioWidget.prototype._set_state_empty = function () {
        // i.e. no audio file has been selected
        this._reset();
        if (typeof FileReader == 'undefined') {
            // File API is not supported, so don't provide file selection element
            return;
        }
        this.upload_widget = $('<input type="file" accept="audio/ogg">');
        var _this = this;
        this.upload_widget.change(function () {
            var file = this.files[0];
            _this._set_state_localfile(file);
        });
        this.control_elt.append(this.upload_widget);
    };
    AudioWidget.prototype._set_state_localfile = function (file) {
        // i.e. the user has selected a local file but has not yet uploaded it.
        // we'd like to preview it if possible.
        this._reset();
        this.file = file;
        if (file.type !== 'audio/ogg') {
            this.status_elt.append($('<span class="error"></span>').text('Warning: expected audio/ogg, but selected file is of type ' + file.type));
        }
        var reader = new FileReader();
        var _this = this;
        reader.onload = function (e) {
            _this._append_audio_control(e.target.result);
            var upload_button = $('<a>upload</a>');
            upload_button.click(function () {
                _this.attempt_upload();
            });
            _this.control_elt.append(upload_button);
            _this._append_trash_icon();
        };
        reader.readAsDataURL(file);
    };
    AudioWidget.prototype._set_state_remote_urn = function (urn) {
        this._reset();
        this._urn = urn;
        this._append_audio_control(resolve_urn(urn) + '?view=audio');
        this._append_trash_icon();
    };
    AudioWidget.prototype.attempt_upload = function (success_cb, error_cb) {
        var file = this.file;
        if (!file) {
            // no file selected, so this should not have been called
            error_cb();
            return;
        }
        if (this._upload_in_progress) {
            // note: no callback will be called... FIXME
            return;
        }
        var _this = this;
        this._upload_in_progress = true;
        var progress_elt = $('<progress max="100"><span>0</span>%</progress>');
        this.status_elt.empty().append(progress_elt);
        function handle_upload_errors(errors) {
            progress_elt.remove();
            for (var i = 0; i < errors.length; ++i) {
                _this.status_elt.append($('<span class="error"></span>').text(errors[i]));
            }
            this._upload_in_progress = false;
            if (error_cb) error_cb();
        }
        $.ductusFileUpload({
            url: '/new/audio',
            onLoad: function (e, files, index, xhr) {
                progress_elt.attr('value', 100).find('span').text(100);
                var data;
                try {
                    data = $.parseJSON(xhr.responseText);
                } catch (error) {
                    handle_upload_errors();
                    return;
                }
                if (data.errors) {
                    var key, errors = [];
                    for (key in data.errors) {
                        errors.push(data.errors[key]);
                    }
                    handle_upload_errors(errors);
                    return;
                }
                _this._set_state_remote_urn(data.urn);
                _this._upload_in_progress = false;
                if (success_cb) success_cb();
            },
            onProgress: function (e, files, index, xhr) {
                var percent = parseInt(100 * e.loaded / e.total, 10);
                progress_elt.attr('value', percent).find('span').text(percent);
            },
            onError: function (e, files, index, xhr) {
                handle_upload_errors();
            },
            onAbort: function (e, files, index, xhr) {
                handle_upload_errors();
            }
        }).handleFiles([file]);
    };
    AudioWidget.prototype._append_audio_control = function (src) {
        var html5_audio_element = $('<audio controls></audio>');
        html5_audio_element.attr('src', src);
        this.control_elt.append(html5_audio_element);
    };
    AudioWidget.prototype._append_trash_icon = function () {
        var trash_icon = $('<a>trash</a>');
        var that = this;
        trash_icon.click(function () { that._set_state_empty(); });
        this.control_elt.append(trash_icon);
    };

    function PictureChoiceElementWidget(pce) {
	// default nested json
	if (!pce) {
	    pce = {phrase: {text: ''}, picture: null};
	}

	Widget.call(this, '<li class="picture_choice_element_item"><input class="phrase" type="text"></input></li>');
	this.picture = new PictureWidget(pce.picture);
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
