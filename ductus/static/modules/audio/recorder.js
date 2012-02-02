/*
 * Based on code from wami-recorder
 * https://code.google.com/p/wami-recorder/
 * Copyright (C) 2011 Ian McGraw <mcgrawian@gmail.com>
 * Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
 */
//var Wami = window.Wami || {};

function Wami(id, callback) {
    this.id = id;
    this.callback = callback;
    global_Wami = this;
}

Wami.prototype.setup = function() {
    /*if (Wami.startRecording) {
        // Wami's already defined
	    this.callback();
        return;
        NEW: it's now up to the user to ensure there is only one Wami??
    }*/
    
    if (this.supportsTransparency()) {
	this.params.wmode = "transparent";
    }
    
    if (console) {
	this.flashVars.console = true;
    }
    
    this.version = '10.0.0';
    this.noflash_warning = "WAMI requires Flash " +
        this.version + " or greater<br />https://get.adobe.com/flashplayer/";
    $(this.id).html(this.noflash_warning);
    
    // This is the minimum size due to the microphone security panel
    swfobject.embedSWF("/static/modules/audio/Wami.swf", this.id, 214, 137, this.version, null, this.flashVars,
		       this.params);
    
    // Without this line, Firefox has a dotted outline of the flash
    swfobject.createCSS("#" + this.id, "outline:none");
}   // setup()


    /**
     * Set up the Flash for WAMI
     */
Wami.prototype.supportsTransparency = function() {
	// Detecting the OS is a big no-no in Javascript programming, but
	// I can't think of a better way to know if wmode is supported or
	// not... since not supporting it (like Flash on Ubuntu) is a bug.
    return (navigator.platform.indexOf("Linux") == -1);
}
    
    /**
     * Attach all the audio methods to the Wami namespace in the callback.
     */
//Wami._callbacks = Wami._callbacks || {};
Wami.prototype.swfinit_callback = function() {
	// Delegate all the methods to the recorder.
    console.log('swfinit callback');
    this.recorder = document.getElementById(this.id);   // jQuery selector doesn't work

	this.delegate('startPlaying');
	this.delegate('stopPlaying');
	this.delegate('startRecording');
	this.delegate('stopRecording');
	this.delegate('startListening');
	this.delegate('stopListening');
	this.delegate('getRecordingLevel');
	this.delegate('getPlayingLevel');
	this.delegate('getSettings');
	this.delegate('showSecurity');
	this.delegate('getBase64AudioData');
	this.delegate('setCustomHeaders');
	this.delegate('uploadAudio');

	this.callback();
}

Wami.prototype.delegate = function(name) {
    wami = this;
    this[name] = function() {
        console.log('delegating ' + name);
        return wami.recorder[name].apply(wami.recorder, arguments);
    }
}

Wami.prototype.show = function() {
    if (!supportsTransparency()) {
        this.recorder.style.visibility = "visible";
    }
}

Wami.prototype.hide = function() {
    // Hiding flash correctly in all the browsers is tricky. Please read:
    // https://code.google.com/p/wami-recorder/wiki/HidingFlash

    if (!this.supportsTransparency()) {
        this.recorder.style.visibility = "hidden";
    }
}

Wami.prototype.flashVars = {
    visible : false,
    loadedCallback : "global_Wami.swfinit_callback",
    localMode : true
}

Wami.prototype.params = {
	allowScriptAccess : "always"
}
/*
 * Base64 encode/decode from http://ostermiller.org/calc/encode.html
 * Licensed under GPL version 2
 */
var END_OF_INPUT = -1;
var base64Chars = new Array(
		'A','B','C','D','E','F','G','H',
		'I','J','K','L','M','N','O','P',
		'Q','R','S','T','U','V','W','X',
		'Y','Z','a','b','c','d','e','f',
		'g','h','i','j','k','l','m','n',
		'o','p','q','r','s','t','u','v',
		'w','x','y','z','0','1','2','3',
		'4','5','6','7','8','9','+','/'
		);
var reverseBase64Chars = new Array();

for (var i=0; i < base64Chars.length; i++){
	reverseBase64Chars[base64Chars[i]] = i;
}

var base64Str;
var base64Count;

function setBase64Str(str){
	base64Str = str;
	base64Count = 0;
}

function readReverseBase64(){
	if (!base64Str) return END_OF_INPUT;
	while (true){
		if (base64Count >= base64Str.length) return END_OF_INPUT;
		var nextCharacter = base64Str.charAt(base64Count);
		base64Count++;
		if (reverseBase64Chars[nextCharacter]){
			return reverseBase64Chars[nextCharacter];
		}
		if (nextCharacter == 'A') return 0;
	}
	return END_OF_INPUT;
}
function ntos(n){
	n=n.toString(16);
	if (n.length == 1) n="0"+n;
	n="%"+n;
	return unescape(n);
}
function decodeBase64(str){
	setBase64Str(str);
	var result = "";
	var inBuffer = new Array(4);
	var done = false;
	while (!done && (inBuffer[0] = readReverseBase64()) != END_OF_INPUT
			&& (inBuffer[1] = readReverseBase64()) != END_OF_INPUT){
		inBuffer[2] = readReverseBase64();
		inBuffer[3] = readReverseBase64();
		result += ntos((((inBuffer[0] << 2) & 0xff)| inBuffer[1] >> 4));
		if (inBuffer[2] != END_OF_INPUT){
			result += ntos((((inBuffer[1] << 4) & 0xff)| inBuffer[2] >> 2));
			if (inBuffer[3] != END_OF_INPUT){
				result += ntos((((inBuffer[2] << 6) & 0xff) | inBuffer[3]));
			} else {
				done = true;
			}
		} else {
			done = true;
		}
	}
	return result;
}

/*
 * Following code:
 * Copyright (c) 2012  Laurent Savaete <laurent@wikiotics.org>
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
Wami.prototype.handle_upload_errors = function(e) {
	online_recorder.onError(e);
}
Wami.prototype.handle_upload_success = function(data) {
    // feedback the urn to the recorded audio to the caller
    console.log('wami handle upload success');
    console.log(online_recorder.elt.parent());
    online_recorder.init();
    online_recorder.elt.parent().trigger('ductus_element_selected',
            { href: data.urn,
              resource: { fqn: AudioWidget.prototype.fqn }
            }
    );
}
Wami.prototype.uploadRecordedFile = function(url) {
	this.base64audioBytes = this.getBase64AudioData();
	var crlf = '\r\n';
	var body = '';
	this.audioBytes = decodeBase64(this.base64audioBytes);
	// create a file that looks like the DOM file structure but has file.content
	// so we can pass it to our customised jquery file upload function
	this.recordedFile = {
		name: "online-recording.wav",
		type: "audio/x-wav",
		size: this.audioBytes.length,
		recordedContent: this.audioBytes
	};
    wami = this;
	$.ductusFileUpload({
		url: '/new/audio',
		onLoad: function (e, files, index, xhr) {
			if (xhr.status != 200) {
				console.log('http status ' + xhr.status);
				return;
			}
			console.log(xhr);
			var data;
			try {
				data = $.parseJSON(xhr.responseText);
			} catch (error) {
				wami.handle_upload_errors(e);
				return;
			}
			if (data.errors) {
				console.log("onLoad error: ");
				console.log(data.errors);
				var key, errors = '';
				for (key in data.errors) {
					errors += data.errors[key];
				}
				wami.handle_upload_errors(errors);
				return;
			} else if (data.page_url) {
				//Wami.handle_upload_errors('<span>File saved successfully. </span><a href="'+data.page_url+'">View file</a>');
                wami.handle_upload_success(data);
				return;
			}
			console.log("ductusFileUpload onLoad complete");
		},
		onProgress: function (e, files, index, xhr) {
				    //var percent = parseInt(100 * e.loaded / e.total, 10);
				    //progress_elt.attr('value', percent).find('span').text(percent);
				    //console.log
		},
		onError: function (e, files, index, xhr) {
				 wami.handle_upload_errors(e);
				 console.log("ductus file upload error");
		},
		onAbort: function (e, files, index, xhr) {
				 wami.handle_upload_errors(e);
				 console.log("on abort in ductus file upload error");
		}
	}).handleFiles([this.recordedFile]);
}
