Browser support in Ductus
=========================

We aim to support "legacy/old" browsers to the extent possible for viewing content. For editing content, supporting these would require too much hassle and would harm user experience.

We use a few tricks to simplify cross browser portability of code:
 * `jQuery <http://jquery.com>`_ ensures portability of javascript code.
 * `jQuery UI <http://jqueryui.com>`_ does the same for user interface javascript code.
 * `jPlayer <http://jplayer.org>`_ is used to enlarge browser support for playing media files (this is not perfect though).

Viewing content
---------------

The aim is to make content accessible to as many users as possible. So we include fallback solutions like flash to play audio where the browser doesn't handle it natively.

Editing content
---------------

The editing interface relies heavily on javascript, so this becomes an issue with older versions of IE (6 to 8). All other (fairly recent) browsers should play fine with the current editing interface.

We do not use jplayer for audio in the edit interface (yet?). Instead we rely on browsers' native audio support in html5.

Development
-----------
Most of the development is currently done in firefox or chrome/chromium, so these two browsers should have the best support.
