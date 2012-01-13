/*
 * This file is derived from wami-recorder
 * https://code.google.com/p/wami-recorder/
 * Copyright (C) 2011 Ian McGraw <mcgrawian@gmail.com>
 * Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
 */
var Wami = window.Wami || {};
var button_image = "/static/modules/audio/buttons.png"
Wami.Button = function(guiID, type) {
	var self = this;
	self.active = false;

	// Get the background button image position
	// Index: 1) normal 2) pressed 3) mouse-over
	function background(index) {
		if (index == 1)
			return "-56px 0px";
		if (index == 2)
			return "0px 0px";
		if (index == 3)
			return "-112px 0";
		alert("Background not found: " + index);
	}

	// Get the type of meter and its state
	// Index: 1) enabled 2) meter 3) disabled
	function meter(index, offset) {
		var top = 5;
		if (offset)
			top += offset;
		if (self.type == Wami.Button.RECORD) {
			if (index == 1)
				return "-169px " + top + "px";
			if (index == 2)
				return "-189px " + top + "px";
			if (index == 3)
				return "-249px " + top + "px";
		} else {
			if (index == 1)
				return "-269px " + top + "px";
			if (index == 2)
				return "-298px " + top + "px";
			if (index == 3)
				return "-327px " + top + "px";
		}
		alert("Meter not found: " + self.type + " " + index);
	}

	function silhouetteWidth() {
		if (self.type == Wami.Button.RECORD) {
			return "20px";
		} else {
			return "29px";
		}
	}

	function mouseHandler(e) {
		var rightclick;
		if (!e)
			var e = window.event;
		if (e.which)
			rightclick = (e.which == 3);
		else if (e.button)
			rightclick = (e.button == 2);

		if (!rightclick) {
			if (self.active && self.onstop) {
				self.active = false;
				self.onstop();
			} else if (!self.active && self.onstart) {
				self.active = true;
				self.onstart();
			}
		}
	}

	function init(guiID, type) {
		self.type = type;
		if (!self.type) {
			self.type = Wami.Button.record;
		}
		var jguiID = '#' + guiID;
		var elem = $(jguiID);
		var div = $('<div></div>').css( { position: 'relative' } );
		elem.append(div);

		self.guidiv = $('<div></div>').css( {
			width: '56px',
		    	height: '63px',
		    	cursor: 'pointer',
		    	background: "url("+button_image+") no-repeat",
		    	'background-position': background(1),
		    	'text-align': 'center'
		} );
		div.append(self.guidiv);

		// margin auto doesn't work in IE quirks mode
		// http://stackoverflow.com/questions/816343/why-will-this-div-img-not-center-in-ie8
		// text-align is a hack to force it to work even if you forget the
		// doctype.

		self.meterDiv = $('<div><div>').css( {
			width: silhouetteWidth(),
		    	height: '63px',
		    	margin: 'auto',
		    	cursor: 'pointer',
		    	position: 'relative',
		    	background: "url("+button_image+") no-repeat",
		    	'background-position': meter(2)
		} );
		self.guidiv.append(self.meterDiv);
		self.guidiv.click( mouseHandler );

		self.coverDiv = $('<div><div>').css( {
			width: silhouetteWidth(),
		    	height: '63px',
		    	margin: 'auto',
		    	cursor: 'pointer',
		    	position: 'relative',
		    	background: "url("+button_image+") no-repeat",
		    	'background-position': meter(1)
		} );
		self.meterDiv.append(self.coverDiv);

		self.active = false;
		//self.guidiv.onmousedown = mouseHandler;
	}
	
	self.isActive = function() {
		return self.active;
	}

	self.setActivity = function(level) {
		self.guidiv.onmouseout = function() {
		};
		self.guidiv.onmouseover = function() {
		};
		//self.guidiv.style.backgroundPosition = background(2);
		self.guidiv.css( { 'background-position': background(2) } );
		self.coverDiv.css( {'background-position': meter(1, 5) } );
		self.meterDiv.css( {'background-position': meter(2, 5) } );

		var totalHeight = 31;
		var maxHeight = 9;

		// When volume goes up, the black image loses height,
		// creating the perception of the colored one increasing.
		var height = (maxHeight + totalHeight - Math.floor(level / 100
				* totalHeight));
		self.coverDiv.css( { height: height + "px" } );
	}

	self.setEnabled = function(enable) {
		var guidiv = self.guidiv;
		self.active = false;
		if (enable) {
			self.coverDiv.css( { 'background-position': meter(1) } );
			self.meterDiv.css( { 'background-position': meter(1) } );
			guidiv.css( { 'background-position': background(1) } );
			guidiv.onmousedown = mouseHandler;
			guidiv.onmouseover = function() {
				guidiv.css({'background-position': background(3)});
			};
			guidiv.onmouseout = function() {
				guidiv.css( { 'background-position': background(1) });
			};
		} else {
			self.coverDiv.css( { 'background-position': meter(3) });
			self.meterDiv.css( {'background-position': meter(3) });
			guidiv.css( { 'background-position': background(1) });
			guidiv.onmousedown = null;
			guidiv.onmouseout = function() {
			};
			guidiv.onmouseover = function() {
			};
		}
	}

	init(guiID, type);
}
// The types of buttons we can show:
Wami.Button.RECORD = "record";
Wami.Button.PLAY = "play";
