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

function assert(condition_lambda) {
    if (!condition_lambda())
        throw { name: "assertion_error", message: condition_lambda.toString() };
}

// setup inheritance between prototypes
function chain_clone(obj) {
    function F() {}
    F.prototype = obj;
    return new F;
}

function compare_nested_objects (a, b) {
    // compare two nested objects (ie: blueprints)
    // return true if they are the same
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

window.__current_ductus_unique_id = 0;
function ductus_unique_dom_id () {
    return 'ductus_unique_dom_id' + (window.__current_ductus_unique_id++);
}

function Widget(initial_html_code) {
    // the base "class" for widgets
    // each widget has its DOM bits in this.elt that jQuery can manipulate
    this.elt = $(initial_html_code);
    this.elt.addClass("ductus_Widget");
    this.elt.data("widget_object", this);   // to access the widget from its DOM element
}

function ModelWidget(initial_data, initial_html_code) {
    // ModelWidgets also include a blueprint representation
    Widget.call(this, initial_html_code);
    this.elt.addClass("ductus_ModelWidget");
    this.initial_href = initial_data ? initial_data.href : null;
}
ModelWidget.prototype = chain_clone(Widget.prototype);
ModelWidget.prototype.record_initial_inner_blueprint = function () {
    // This function should be called at the end of initialization if we ever plan to call ModelWidget.blueprint_repr()
    // on the object (i.e. we do not plan to override blueprint_repr() in the subclass)
    //
    // the {} recorded in the default case evaluates to true, which allows us to assert below
    // that this function has actually been called
    this.initial_inner_blueprint = this.initial_href ? this.inner_blueprint_repr() : {};
};
ModelWidget.prototype.add_inner_blueprint_constructor = function (inner_blueprint_repr) {
    // yes, this modifies the dictionary in place
    if (this.initial_href) {
        inner_blueprint_repr['@patch'] = this.initial_href;
    } else {
        inner_blueprint_repr['@create'] = this.fqn;
    }
    return inner_blueprint_repr;
};
ModelWidget.prototype.blueprint_repr = function () {
    var inner_blueprint = this.inner_blueprint_repr();
    var initial_inner_blueprint = this.initial_inner_blueprint;
    // we shouldn't be calling this unless record_initial_inner_blueprint() has been called
    assert(function () { return !!initial_inner_blueprint; });

    // if blueprints are the same, just return a reference to the original version
    if (compare_nested_objects(initial_inner_blueprint, inner_blueprint)) {
        return {'href': this.initial_href};
    } else {
        return {'resource': inner_blueprint};
    }
};
ModelWidget.prototype.get_outstanding_presave_steps = function () {
    return [];
};
ModelWidget.combine_presave_steps = function (widgets, additional_steps) {
    var i, rv = [];
    for (i = 0; i < widgets.length; ++i) {
        $.merge(rv, widgets[i].get_outstanding_presave_steps());
    }
    if (additional_steps) {
        for (i = 0; i < additional_steps.length; ++i) {
            rv.push(additional_steps[i]);
        }
    }
    return rv;
};

function UrnPictureSource(urn) {
    this.urn = urn;
}
UrnPictureSource.prototype.get_images = function () {
    var resolved_urn = resolve_urn(this.urn);
    return {
        '250x250': resolved_urn + '?view=image&amp;max_size=250,250',
        '100x100': resolved_urn + '?view=image&amp;max_size=100,100',
        '50x50': resolved_urn + '?view=image&amp;max_size=50,50'
    };
};
UrnPictureSource.prototype.inner_blueprint_repr = function () {
    return {'@patch': this.urn};
};
UrnPictureSource.prototype.clone = function () {
    return this;
};

function FlickrPictureSource(flickr_photo) {
    this.flickr_photo = flickr_photo;
}
FlickrPictureSource.prototype.get_images = function () {
    return {
        '75x75': this.flickr_photo.small_url,
        '100x100': this.flickr_photo.thumbnail_url,
        '240x240': this.flickr_photo.small_url,
        '500x500': this.flickr_photo.medium_url,
        '1024x1024': this.flickr_photo.large_url
    };
};
FlickrPictureSource.prototype.inner_blueprint_repr = function () {
    return {
        '@create': PictureModelWidget.prototype.fqn,
        'flickr_photo_id': this.flickr_photo.id
    };
};
FlickrPictureSource.prototype.clone = function () {
    return this;
};

function PictureModelWidget(picture) {
    // the widget shown in a flashcard side cell for a picture
    // this one is blueprint-aware
    ModelWidget.call(this, picture, '<span class="ductus_PictureModelWidget"></span>');

    var picture_source = null;
    if (picture.href)
        picture_source = new UrnPictureSource(picture.href);
    else if (picture.resource && picture.resource._picture_source)
        picture_source = picture.resource._picture_source.clone();
    assert(function () { return !!picture_source; });

    this._picture_widget = new PictureWidget(picture_source);
    // show rotation controls next to picture
    this._picture_widget.elt.append(this._picture_widget.rotation_controls);

    if (picture && picture.resource && picture.resource.net_rotation)
        this._picture_widget.set_rotation(picture.resource.net_rotation);

    this.elt.append(this._picture_widget.elt);

    this.record_initial_inner_blueprint();
}
PictureModelWidget.prototype = chain_clone(ModelWidget.prototype);
PictureModelWidget.prototype.inner_blueprint_repr = function () {
    var repr = this._picture_widget._picture_source.inner_blueprint_repr();
    if (this._picture_widget.net_rotation)
        repr.net_rotation = this._picture_widget.net_rotation;
    return repr;
};
PictureModelWidget.prototype.fqn = '{http://wikiotics.org/ns/2009/picture}picture';
PictureModelWidget.creation_ui_widget = function () {
    return new PictureSearchWidget;
};
PictureModelWidget.prototype.edit_ui_widget = function () {
    return { elt: this._picture_widget.rotation_controls };
};
PictureModelWidget.prototype.popup_html = {
    'left': 'record (soon)',
    'right': 'upload (soon)',
    'top': 'search (soon)',
    'bottom': 'delete'
};
PictureModelWidget.prototype.popup_callback = {
    'left': function() {},
    'right': function() {},
    'top': function() {},
    'bottom': function(target) {
        target.elt.parent().data('widget_object').reset();
    }
};

function PictureWidget(picture_source, editable) {
    // a widget showing a picture
    // it is appended as a child to PictureModelWidget in flashcard decks
    // as it does not hold a blueprint itself
    var self = this;

    if (editable === undefined)
        // the user can rotate even if it is not editable, as that is useful for preview.
        // editable pictures will receive drop events, and will be swapped with another picture when dragged there.
        // fixme: we could probably just have a set_editable() method.
        // we should never allow a null picture source if it is not editable.
        editable = true;
    this._is_editable = editable;

    Widget.call(this, '<span class="ductus_PictureWidget"></span>');
    this.image_holder = $('<span style="display: inline-block">' + gettext('drag image here') + '</span>');
    this.elt.append(this.image_holder);

    // rotation controls
    var rotate_left_button = $('<img alt="' + gettext('rotate left') + '" title="' + gettext('rotate left') + '" src="' + ductus_media_prefix + 'modules/picture/img/object-rotate-left.png" class="ductus_rotate_button"/>');
    var rotate_right_button = $('<img alt="' + gettext('rotate right') + '" title="' + gettext('rotate right') + '" src="' + ductus_media_prefix + 'modules/picture/img/object-rotate-right.png" class="ductus_rotate_button"/>');
    rotate_left_button.click(function (e) { e.stopPropagation(); self.rotate_left(); });
    rotate_right_button.click(function (e) { e.stopPropagation(); self.rotate_right(); });
    this.rotation_controls = $('<span class="ductus_picture_controls"></span>').append(rotate_left_button).append(rotate_right_button);
    this.net_rotation = 0;

    // numerical rotation display, which acts as a fallback if canvas fails
    this.rotation_number_display = $("<span></span>");
    this.rotation_controls.append(this.rotation_number_display);

    // show the initial picture by setting the picture source
    this.set_picture_source(picture_source);

    // image_holder should receive drop events
    this.image_holder.droppable({
        accept: '.ductus_draggable_picture',
        tolerance: 'pointer',
        drop: function (event, ui) {
            var source_picture_widget = ui.draggable.data('widget_object');
            if (source_picture_widget && self._picture_source && source_picture_widget._is_editable) {
                // swap them, including rotation data
                var source_rotation = source_picture_widget.net_rotation;
                var source_picture_source = source_picture_widget._picture_source;
                source_picture_widget.set_picture_source(self._picture_source.clone());
                source_picture_widget.set_rotation(self.net_rotation);
                self.set_picture_source(source_picture_source.clone());
                self.set_rotation(source_rotation);
            } else {
                // clone the source and show an effect
                self.set_picture_source(source_picture_widget._picture_source.clone());
                self.set_rotation(source_picture_widget.net_rotation);
                ui.draggable.effect("transfer", {to: this}, 500);
            }
        }
    });
}
PictureWidget.prototype = chain_clone(Widget.prototype);
PictureWidget.prototype.set_picture_source = function (picture_source) {
    if (!picture_source) {
        // in the future we may also want to allow null as an argument, which would reset it to be uninitialized
        return;
    }

    this._picture_source = picture_source;

    var img_url = picture_source.get_images()['100x100'];
    this.img = $('<img src="" class="ductus_draggable_picture"/>');
    this.img.attr('src', img_url);
    this.img.data("widget_object", this); // so the drop event can find the widget
    this.img.draggable({helper: 'clone'});
    this.canvas = undefined;
    this.image_holder.empty().append(this.img);
    this.set_rotation(0);
};
PictureWidget.prototype.rotate_left = function () {
    this.set_rotation((this.net_rotation + 90) % 360);
};
PictureWidget.prototype.rotate_right = function () {
    this.set_rotation((this.net_rotation + 270) % 360);
};
PictureWidget.prototype.set_rotation = function (degrees) {
    assert(function () { return $.inArray(degrees, [0, 90, 180, 270]) !== -1; });
    if (this.net_rotation === degrees)
        return; // no-op
    this.net_rotation = degrees;
    this.rotation_number_display.text("");
    if (degrees === 0) {
        this.img.show();
        if (this.canvas)
            this.canvas.hide();
    } else {
        try {
            if (!this.canvas) {
                this.canvas = $('<canvas class="ductus_draggable_picture"></canvas>');
                this.canvas.data("widget_object", this); // so the drop event can find the widget
                this.canvas.draggable({
                    helper: function () {
                                // cloning a canvas doesn't clone its contents, so we do that here
                                var old_canvas = $(this);
                                var new_canvas = $('<canvas></canvas>');
                                var w = old_canvas.attr('width'), h = old_canvas.attr('height');
                                new_canvas.attr('width', w).attr('height', h);
                                var canvas_ctx = new_canvas[0].getContext('2d');
                                canvas_ctx.drawImage(this, 0, 0);
                                return new_canvas;
                            }
                });
                this.image_holder.append(this.canvas);
            }
            this.img.hide();
            this.canvas.show();
            if (this.img.attr('width') != 0) {
                this._draw_canvas();
            } else {
                // the image hasn't loaded yet
                var this_ = this;
                this.img.load(function () {
                    this_._draw_canvas();
                });
            }
        } catch (e) {
            this.rotation_number_display.text(degrees + "");
        }
    }
};
PictureWidget.prototype._draw_canvas = function () {
    var w = this.img[0].width, h = this.img[0].height;
    var dx = w / 2, dy = h / 2;
    var canvas_ctx = this.canvas[0].getContext('2d');
    if (this.net_rotation === 180) {
        this.canvas.attr({width: w, height: h});
        canvas_ctx.translate(dx, dy);
    } else {
        this.canvas.attr({width: h, height: w});
        canvas_ctx.translate(dy, dx);
    }
    canvas_ctx.rotate(-this.net_rotation * Math.PI / 180);
    canvas_ctx.translate(-dx, -dy);
    canvas_ctx.drawImage(this.img[0], 0, 0);
};

function PictureSearchWidget(initial_query_data) {
    // the widget used as a creation widget to search for a picture (from flickr)
    if (!initial_query_data) {
        initial_query_data = {};
    }

    Widget.call(this, '<div class="ductus_PictureSearchWidget"><form>' + gettext('What:') +' <input name="q" class="input-query"/><input type="submit" value="search"/><br/><input type="radio" name="sort" value="date-posted-desc"/>' + gettext('Recent') + ' <input type="radio" name="sort" value="interestingness-desc"/>' + gettext('Interesting') + ' <input type="radio" name="sort" value="relevance" checked/>' + gettext('Relevant | Search by') +' <input type="radio" name="search_by" value="text" checked/>' + gettext('Text') + ' <input type="radio" name="search_by" value="tags"/>' + gettext('Tags') + '</form></div>');
    if (DUCTUS_FLICKR_GROUP_ID) {
        $(this.elt).find("form").append('<div><input type="checkbox" name="group" value="' + DUCTUS_FLICKR_GROUP_ID + '"/> ' + gettext('Restrict to project\'s Flickr group') + '</div>');
    }
    var search_results_elt = $('<div class="search_results"></div>');
    var this_ = this;
    this.elt.find("form").submit(function () {
        $.ajax({
            url: "/new/picture",
            data: "view=flickr_search&" + $(this).serialize(),
            dataType: "json",
            success: function (data, textStatus) {
                search_results_elt.empty();
                if (data.place) {
                    search_results_elt.append($("<div></div>").text(data.place));
                }
                for (var i = 0; i < data.photos.length; ++i) {
                    var photo = data.photos[i];
                    var picture_source = new FlickrPictureSource(photo);
                    var picture_widget = new PictureWidget(picture_source, false);
                    // fixme: we really only want to trap clicks on the image itself, not anywhere on the widget.  this will affect the this.data(widgetobject) as well...
                    picture_widget.elt.find(".ductus_draggable_picture").click(function () { // fixme: we aren't using this for dragging here, so maybe we should give the class a more general name
                        var result = $(this).data('widget_object');
                        this_.elt.trigger("ductus_element_selected", [{
                            resource: {
                                fqn: PictureModelWidget.prototype.fqn,
                                _picture_source: result._picture_source,
                                net_rotation: result.net_rotation // FIXME (?)
                                      }
                        }]);
                    });
                    search_results_elt.append(picture_widget.elt);
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
PictureSearchWidget.prototype.do_focus = function () {
    this.elt.find(".input-query").focus();
};

function AudioWidget(audio) {
    ModelWidget.call(this, audio, '<span class="ductus_AudioWidget"><span class="control"></span><span class="status"></span></span>');

    this.control_elt = this.elt.find('.control');
    this.status_elt = this.elt.find('.status');
    if (audio.href) {
        this._set_state_remote_urn(audio.href);
    } else if (audio.resource && audio.resource._file) {
        this._set_state_localfile(audio.resource._file);
    }

    // we don't call this.record_initial_inner_blueprint() since we override blueprint_repr() directly (see below)
}
AudioWidget.prototype = chain_clone(ModelWidget.prototype);
AudioWidget.prototype.blueprint_repr = function () {
    if (!this._urn) {
        throw gettext('File has not been uploaded yet.');
    }
    return { href: this._urn };
};
AudioWidget.prototype.get_outstanding_presave_steps = function () {
    if (this.file) {
        var this_ = this;
        return [function (success_cb, error_cb) { return this_.attempt_upload(success_cb, error_cb); }];
    }
    return [];
};
AudioWidget.prototype.fqn = '{http://wikiotics.org/ns/2010/audio}audio';
AudioWidget.prototype._reset = function () {
    // don't call this; call _set_state_* instead, which will automatically call this
    this.control_elt.empty();
    this.status_elt.empty();
    this._urn = undefined;
    this.file = null;
};
AudioWidget.prototype._set_state_localfile = function (file) {
    // i.e. the user has selected a local file but has not yet uploaded it.
    // we'd like to preview it if possible.
    this._reset();
    this.file = file;
    if (file.type !== 'audio/ogg') {
        this.status_elt.append($('<span class="error"></span>').text(gettext('Warning: expected audio/ogg, but selected file is of type') + ' ' + file.type));
    }
    var reader = new FileReader();
    var _this = this;
    reader.onload = function (e) {
        _this._append_audio_control(e.target.result);
        var upload_button = $('<a href="javascript:void(0)">' + gettext('upload') + '</a>');
        upload_button.click(function () {
            _this.attempt_upload();
        });
        _this.control_elt.append(upload_button);
    };
    reader.readAsDataURL(file);
};
AudioWidget.prototype._set_state_remote_urn = function (urn) {
    this._reset();
    this._urn = urn;
    this._append_audio_control(resolve_urn(urn) + '?view=audio');
};
AudioWidget.prototype.attempt_upload = function (success_cb, error_cb) {
    var file = this.file;
    if (!file) {
        // no file selected, so this should not have been called
        if (error_cb) error_cb();
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
        _this._upload_in_progress = false;
        if (error_cb) error_cb(gettext('error uploading audio'));
    }
    $.ductusFileUpload({
        url: '/new/audio',
        onLoad: function (e, files, index, xhr) {
            if (xhr.status != 200) {
                handle_upload_errors(['http status ' + xhr.status]);
                return;
            }
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
    var html5_audio_element = $('<audio controls preload="none"></audio>');
    html5_audio_element.attr('src', src);
    this.control_elt.append(html5_audio_element);
};
// content of popup menu when clicking on an audio widget
// null will disable the corresponding submenu
AudioWidget.prototype.popup_html = {
    'left': gettext('record'),
    'right': gettext('copy'),
    'top': gettext('search'),
    'bottom': gettext('delete')
};
// callbacks to handle clicks on the menu for an audio widget
AudioWidget.prototype.popup_callback = {
    'left': function() {},
    'right': function() {
        // copy the blueprint for pasting in another cell
        window.global_copy_paste_buffer = this_.calling_widget.blueprint_repr();
    },
    'top': function() {},
    'bottom': function(target) {
        target.elt.parent().data('widget_object').reset();
    }
};
AudioWidget.creation_ui_widget = function () {
    if (typeof FileReader == 'undefined') {
        // File API is not supported, so don't provide file selection eleme
        return { elt: $('<div>' + gettext('Your browser does not support File API, so you will not be able to upload anything.') + '</div>') };
    }
    var upload_widget_elt = $('<div class="AudioWidget_creation_widget"></div>');
    var file_input = '<span class="ductus_file_upload_wrapper">' +
        '<input type="file" accept="audio/ogg" />' +
        '<span class="ductus_file_upload_button">' + gettext('Upload a file') + '</span>' +
        '</span>';
    var input = $(file_input).appendTo(upload_widget_elt).find('input');
    $(file_input).button();
    input.change(function () {
        var file = this.files[0];
        upload_widget_elt.trigger("ductus_element_selected", [{
            resource: { fqn: AudioWidget.prototype.fqn, _file: file }
        }]);
    });

    var recording_widget = new OnlineRecorder();
    recording_widget.elt.appendTo(upload_widget_elt);
    return { elt: upload_widget_elt };
};

function FullPagename (arg) {
    if (typeof arg === 'string') {
        this.__fqpagename = arg;
    } else if (arg.prefix && arg.pagename) {
        this.__fqpagename = '' + arg.prefix + ':' + arg.pagename;
    } else if (arg.directory && arg.remainder) {
        this.__fqpagename = '' + arg.directory + arg.remainder;
    } else if (arg.pathname && arg.pathname.charAt(0) == '/' && arg.pathname.length > 3) {
        this.__fqpagename = decodeURIComponent(arg.pathname.substring(1)).replace(/\//, ':');
    } else {
        throw gettext('invalid arguments given to FullPagename constructor');
    }

    this.__colon_index = this.__fqpagename.indexOf(':');
    if (this.__colon_index < 0) {
        throw gettext('invalid pagename; it contains no ":"');
    }
}
FullPagename.prototype.get_fqpagename = function () {
    return this.__fqpagename;
};
FullPagename.prototype.get_pathname = function () {
    return '/' + encodeURIComponent(this.__fqpagename.replace(/:/, '/'));
};
FullPagename.prototype.get_directory = function () {
    var prefix = this.get_prefix();
    if ($.inArray(prefix, ['user', 'group']) !== -1) {
        return prefix + ':' + this.get_pagename().split(/\//, 1) + '/';
    } else {
        return prefix + ':';
    }
};
FullPagename.prototype.get_remainder = function () {
    var fqpagename = this.get_fqpagename();
    var directory = this.get_directory();
    assert(function () { return directory.length <= fqpagename.length && fqpagename.substring(0, directory.length) === directory; });
    return fqpagename.substring(directory.length);
};
FullPagename.prototype.get_prefix = function () {
    return this.__fqpagename.substring(0, this.__colon_index);
};
FullPagename.prototype.get_pagename = function () {
    return this.__fqpagename.substring(this.__colon_index + 1);
};

function SaveDestinationChooserWidget (original_pagename, suggested_pagename, wikipage_type_shortname) {
    Widget.call(this, '<div class="ductus_SaveDestinationChooserWidget"></div>');

    this.form = $('<form style="display: inline"></form>').appendTo(this.elt);
    var this_ = this;

    var initial_pagename_selection = (original_pagename || suggested_pagename);
    var initial_directory_selection = initial_pagename_selection ? initial_pagename_selection.get_directory() : null;
    var pagetype = wikipage_type_shortname || gettext('the wiki page');

    // figure out directories
    var i, directories = {'user': [], 'group': [], 'language_namespace': []};
    for (i = 0; i < writable_directories.length; ++i) {
        var dir = writable_directories[i];
        if (dir[1] in directories) {
            directories[dir[1]].push(dir);
        }
    }

    // directory chooser
    $('<span>' + gettext('Save to:') + '</span>').appendTo(this.form);
    var ul = $('<ul class="radio_ul"></ul>').appendTo(this.form);
    for (i = 0; i < directories.user.length; ++i) {
        var dir = directories.user[i];
        var id = ductus_unique_dom_id();
        var div = $('<li></li>').appendTo(ul);
        div.append($('<input type="radio" name="grp" id="' + id + '"/>').attr('value', dir[0]));
        div.append($('<label for="' + id + '"></label>').text(gettext('my user directory') + ' (' + dir[2] + ') '));
        if (dir[0] === initial_directory_selection) {
            div.find("#" + id).attr("checked", true);
        }
        div.append('<span class="quiet">' + interpolate(gettext('Only you will be able to edit %(pagetype) in place, but others can make improvements and save them elsewhere.'), pagetype, true) + '</span>');
    }
    for (i = 0; i < directories.group.length; ++i) {
        var dir = directories.group[i];
        var id = ductus_unique_dom_id();
        var div = $('<li></li>').appendTo(ul);
        div.append($('<input type="radio" name="grp" id="' + id + '"/>').attr('value', dir[0]));
        div.append($('<label for="' + id + '"></label>').text(gettext('group: ') + dir[2]));
        if (dir[0] === initial_directory_selection) {
            div.find("#" + id).attr("checked", true);
        }
        div.append('<span class="quiet">' + interpolate(gettext('Only group members will be able to edit %(pagetype) in place.'), pagetype, true) + '</span>');
    }
    if (directories.language_namespace) {
        var select = $('<select></select>');
        var id = ductus_unique_dom_id();
        var lns_div = $('<li></li>').appendTo(ul);
        lns_div.append('<input type="radio" name="grp" id="' + id + '" value="///see_select///"/>');
        lns_div.append('<label for="' + id + '">' + gettext('community wiki for: ') + '</label>');
        lns_div.find("label").after(select);
        var directory_selected = false;
        for (i = 0; i < directories.language_namespace.length; ++i) {
            var dir = directories.language_namespace[i];
            var option = $('<option></option>').attr("value", dir[0]).text(dir[2]);
            if (dir[0] === initial_directory_selection) {
                option.attr("selected", true);
                lns_div.find("#" + id).attr("checked", true);
                directory_selected = true;
            }
            select.append(option);
        }
        if (!directory_selected) {
            select.prepend($('<option disabled selected></option>'));
        }
        select.bind('change keyup keypress', function () {
            lns_div.find("input").attr("checked", "checked");
            this_._destination_changed();
        });
        lns_div.append('<span class="quiet">' + interpolate(gettext('Choose the language to be taught.  Anyone will be able to edit %(pagetype) in place.'), pagetype, true) + '</span>');
    }
    this.elt.find("input[name='grp']").change(function () {
        this_._destination_changed();
    });

    // page name chooser
    this.elt.append('<span>' + gettext('Page title:') + '</span> ');
    this._page_name_input = $('<input name="page_name"/>').appendTo(this.elt);
    this._page_name_input.bind('change keyup keypress drop', function () {
        this_._destination_changed();
    });
    if (initial_pagename_selection) {
        this._page_name_input.val(initial_pagename_selection.get_remainder());
    }

    this._destination_display = $('<span class="destination_display"></span>').appendTo(this.elt);

    this._destination_changed();
}
SaveDestinationChooserWidget.prototype = chain_clone(Widget.prototype);
SaveDestinationChooserWidget.prototype._destination_changed = function () {
    var destination = this.get_destination();
    this._destination_display.text(destination ? destination.get_fqpagename() : "");
    this.elt.trigger("ductus_SaveDestinationChooserWidget_destination_changed", [destination]);
};
SaveDestinationChooserWidget.prototype.get_destination = function () {
    // figure out directory
    var checked = this.form.find("input[name=grp]:checked");
    var directory = checked.val();
    if (directory == '///see_select///') {
        directory = checked.parent().find("option:selected").val();
    }
    if (!directory)
        return null;

    // figure out remainder of page name
    var page_name_remainder = this._page_name_input.val();
    if (!page_name_remainder)
        return null;

    // split prefix, pagename
    var candidate = directory + page_name_remainder;
    var colon_index = candidate.indexOf(':');
    if (colon_index < 0)
        return null;
    var prefix = candidate.substring(0, colon_index);
    var pagename = candidate.substring(colon_index + 1);

    // normalize and validate, according to ductus.wiki.is_legal_wiki_pagename()
    // (as done in clean_target_pagename(), remove leading and trailing
    // underscores from each portion of path; remove extra slashes)
    pagename = pagename.replace(/[\s_]+/g, '_');
    var pagename_array = pagename.split(/\//);
    var new_pagename_array = [];
    for (var i = 0; i < pagename_array.length; ++i) {
        var x = pagename_array[i].replace(/^__*/, '').replace(/__*$/, '');
        if (x)
            new_pagename_array.push(x);
    }
    pagename = new_pagename_array.join('/');

    // (since the prefix is given by the directory list, we assume it is valid)

    return new FullPagename({prefix: prefix, pagename: pagename});
};

function SaveWidget (toplevel_blueprint_object, wikipage_type_shortname) {
    // the widget that defines page name, log message, uri, and actually saves the blueprint to the server
    // toplevel_blueprint_object is the root widget (typically the flashcard deck)
    this.toplevel_blueprint_object = toplevel_blueprint_object;
    Widget.call(this, '<div class="ductus_SaveWidget"></div>');
    var this_ = this;
    var original_pagename = resource_json && new FullPagename({pathname: location.pathname});
    var target_pagename = urlParams['target'] && new FullPagename(urlParams['target']);
    this.destination_chooser = new SaveDestinationChooserWidget(original_pagename, target_pagename, wikipage_type_shortname);
    this.elt.append(this.destination_chooser.elt);
    this.elt.append('<div>' + gettext('Log message: ') + '<input type="text" class="log_message" name="log_message" maxlength="400"/></div>');
    this.elt.append('<form class="save_form save_and_return" style="display: inline"><input type="submit" value="' + gettext('Save') + '"/></form>');
    //this.elt.append('<form class="save_form save_and_continue" style="display: inline"><input type="submit" value="Save and continue editing"/></form>');
    this.elt.find(".save_form").submit(function (event) {
        event.preventDefault(); // cancel normal submit event handling
        this_.perform_save($(event.target).hasClass('save_and_return'));
    });
    this.save_buttons = this.elt.find("input:submit");

    function handle_destination_changed(event, destination) {
        this_.save_buttons.attr("disabled", !destination);
    }
    this.destination_chooser.elt.bind("ductus_SaveDestinationChooserWidget_destination_changed", handle_destination_changed);
    handle_destination_changed(null, this.destination_chooser.get_destination());
}
SaveWidget.prototype = chain_clone(Widget.prototype);
SaveWidget.prototype.perform_save = function (save_and_return) {
    // the function called when the user clicks "save" in the editor.
    // upload files (audio...), put together the final blueprint
    // and finally send the blueprint to the server
    var this_ = this;
    var blocking_elements = this.elt.add(this.toplevel_blueprint_object.elt);
    blocking_elements.block({ message: gettext('saving ...') });
    // recursively list presave steps (eg: upload audio files)
    var presave_steps = this.toplevel_blueprint_object.get_outstanding_presave_steps();

    function perform_final_save () {
        var blueprint = JSON.stringify(this_.toplevel_blueprint_object.blueprint_repr());
        $.ajax({
            url: this_.destination_chooser.get_destination().get_pathname(),
            data: {
                blueprint: blueprint,
            log_message: this_.elt.find(".log_message").val()
            },
            success: function (data) {
                         // go to the newly-saved page
                         if (save_and_return) {
                             window.location = (data.page_url || resolve_urn(data.urn));
                         } else {
                             $('<span class="ductus_save_notice">' + gettext('saved!') + '</span>').appendTo(this_.elt).delay(3000).fadeOut(400, function () { $(this).remove(); });
                         }
                     },
            error: function (xhr, textStatus, errorThrown) {
                       alert(xhr.status + gettext(' error. save failed.'));
                   },
            complete: function (xhr, textStatus) {
                          blocking_elements.unblock();
                      },
            type: 'POST',
            dataType: 'json'
        });
    }
    var i = 0;
    function do_next_step () {
        if (i == presave_steps.length) {
            perform_final_save();
        } else {
            var next_step = presave_steps[i++];
            next_step(do_next_step, function (error) {
                alert(gettext('an error occurred: ') + error);
                blocking_elements.unblock();
            });
        }
    }
    do_next_step();
};

/*
 * Online recorder widget
 * makes use of wami recorder
 * this is the UI part of the recorder
 * the actual recording functionnality is in wami (recorder.js)
 */
var online_recorder;    // make this a global variable since this code is too messy. FIXME: clean this up
function OnlineRecorder() {
    var recorder_div =
        '<div id="ductus_OnlineRecorder" style="position: relative; width:414px">' +
            '<div id="record_online_button"></div>' +
            '<div id="rec_controls">' +
                '<button id="recordDiv"></button>' +
                '<button id="playDiv"></button>' +
                '<button id="uploadDiv"></button>' +
            '</div>' +
            '<div id="feedbackDiv" style="position: absolute; left: 30px; top: 95px"></div>' +
            '<div id="wami"></div>' +
        '</div>'
    Widget.call(this, recorder_div);
    online_recorder = this;     // set the global variable
    this.init();
}
OnlineRecorder.prototype = chain_clone(Widget.prototype);
OnlineRecorder.prototype.init = function() {
    // set or reset the widget to its initial status: upload or record buttons
    this.hideButtons();
    if (this.record_btn) {
        this.listen(false);
    }
    if (!this.record_online_btn) {
        this.record_online_btn = this.elt.find('#record_online_button');
        this.record_online_btn.button( { label: gettext('Record online') } );
    }
    this.record_online_btn.button().show();
    this.record_online_btn.click( function() {
        $(this).hide();
        online_recorder.setupRecorder();
    });
}
OnlineRecorder.prototype.setupRecorder = function() {
    if (!this.Wami) {
        this.Wami = new Wami('wami', function() {
            online_recorder.checkSecurity();
        });
        this.Wami.setup();
    } else {
        this.checkSecurity();
    }
}
OnlineRecorder.prototype.setupButtons = function() {
    this.elt.find('button').attr('visibility', 'hidden');
    this.elt.find('#rec_controls').hide();
    this.showRecordButton('start');
    this.showPlayButton('start');
    this.showUploadButton();
    this.elt.find('#rec_controls').buttonset();
    this.elt.find('#rec_controls').show();
    this.record_online_btn.hide();
}
OnlineRecorder.prototype.hideButtons = function() {
    this.elt.find('#rec_controls').hide();
}
OnlineRecorder.prototype.showRecordButton = function(start_stop) {
    this.record_btn = this.elt.find('#recordDiv');
    this.record_btn.unbind('click');
    if (start_stop == 'start') {
        this.record_btn.text(gettext('Start recording'));
        this.record_btn.button( {
            icons: { primary: "ui-icon-bullet" },
            text: false
        });
        this.record_btn.click( function(){ online_recorder.startRecording();} );
    } else {
        this.record_btn.text(gettext('Stop recording'));
        this.record_btn.button( {
            icons: { primary: "ui-icon-stop" },
            text: false
        });
        this.record_btn.click( function(){ online_recorder.stopRecording();} );
    }
}
OnlineRecorder.prototype.showPlayButton = function(start_stop) {
    this.play_btn = this.elt.find('#playDiv');
    this.play_btn.unbind('click');
    if (start_stop == 'start') {
        this.play_btn.text(gettext('Start playing'));
        this.play_btn.button( {
            icons: { primary: "ui-icon-play" },
            text: false
        });
        this.play_btn.click( function(){ online_recorder.startPlaying();} );
    } else {
        this.play_btn.text(gettext('Stop playing'));
        this.play_btn.button( {
            icons: { primary: "ui-icon-stop" },
            text: false
        });
        this.play_btn.click( function(){ online_recorder.stopPlaying();} );
    }
}
OnlineRecorder.prototype.showUploadButton = function() {
    this.upload_btn = this.elt.find('#uploadDiv');
    this.upload_btn.unbind('click');
    this.upload_btn.text(gettext('Upload recording'));
    this.upload_btn.button( {
        icons: { primary: "ui-icon-check" },
        text: false
    });
    this.upload_btn.click( function(){ online_recorder.uploadAudio();} );
}
OnlineRecorder.prototype.checkSecurity = function() {
    this.settings = this.Wami.getSettings();
    if (this.settings.microphone.granted) {
        this.listen(true);
        this.Wami.hide();
        this.setupButtons();
    } else {
        // Show any Flash settings panel you want using the string constants
        // defined here:
        // http://help.adobe.com/en_US/FlashPlatform/reference/actionscript/3/flash/system/SecurityPanel.html
        this.Wami.showSecurity("privacy", "online_recorder.Wami.show", "online_recorder.checkSecurity", "online_recorder.zoomError");
    }
}
OnlineRecorder.prototype.listen = function(active) {
    // activate (when recorder is used) or deactivate listening (when it is
    // unused because no recorder is used)
    if (active) {
        this.Wami.startListening();
        // Continually listening when the window is in focus allows us to
        // buffer a little audio before the users clicks, since sometimes
        // people talk too soon. Without "listening", the audio would record
        // exactly when startRecording() is called.
        window.onfocus = function () {
            online_recorder.Wami.startListening();
        };
        // Note that the use of onfocus and onblur should probably be replaced
        // with a more robust solution (e.g. jQuery's $(window).focus(...)
        window.onblur = function () {
            online_recorder.Wami.stopListening();
        };
    } else {
        //this.Wami.stopListening();
        window.onfocus = null;
        window.onblur = null;
    }
}
OnlineRecorder.prototype.zoomError = function() {
    // The minimum size for the flash content is 214x137. Browser's zoomed out
    // too far won't show the panel.
    // We could play the game of re-embedding the Flash in a larger DIV here,
    // but instead we just warn the user:
    alert(gettext('Your browser may be zoomed too far out to show the Flash security settings panel.  Zoom in, and refresh.'));
}
OnlineRecorder.prototype.uploadAudio = function() {
    this.Wami.uploadRecordedFile('/new/audio');
}
/**
 * These methods are called on clicks from the GUI.
 */
OnlineRecorder.prototype.startRecording = function() {
    this.showRecordButton('stop');
    this.Wami.startRecording("", "online_recorder.onRecordStart", "online_recorder.onRecordFinish", "online_recorder.onError");
}
OnlineRecorder.prototype.stopRecording = function() {
    this.showRecordButton('start');
    this.Wami.stopRecording();
}
OnlineRecorder.prototype.startPlaying = function() {
    this.showPlayButton('stop');
    this.Wami.startPlaying("", "online_recorder.onPlayStart", "online_recorder.onPlayFinish", "online_recorder.onError");
}
OnlineRecorder.prototype.stopPlaying = function() {
    this.showPlayButton('start');
    this.Wami.stopPlaying();
}
/**
 * Callbacks from the flash indicating certain events
 */
OnlineRecorder.prototype.onError = function(e) {
    console.log(e);
    this.elt.find('#feedbackDiv').html(e);
}
OnlineRecorder.prototype.onRecordStart = function() {
    console.log('OR onRecordStart');
}
OnlineRecorder.prototype.onRecordFinish = function() {
    console.log('OR onRecordFinish');
}
OnlineRecorder.prototype.onPlayStart = function() {
    console.log('OR onPlayStart');
}
OnlineRecorder.prototype.onPlayFinish = function() {
    console.log('OR onPlayFinish');
    this.showPlayButton('start');
}
