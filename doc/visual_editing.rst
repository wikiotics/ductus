
Visual content editing
======================

Ductus uses visual editing for text-based pages to save users the trouble of learning any kind of markup.

Visual editing is based on the use of `Aloha editor`_

.. _Aloha editor: http://aloha-editor.org

For ductus developers: installing/upgrading aloha
-------------------------------------------------

Aloha Editor source code is included as a submodule of the git repository under ``DUCTUS_ROOT/submodules/Aloha-Editor``. See the `git book`_ for a primer on using git submodules.

When first cloning the git repository, you need to get the source code for aloha from github::

$ git submodule init
$ git submodule update

Follow the install steps in the `aloha documentation`_ to get the files needed to build aloha.

You can automatically build aloha for ductus by running::

$ cd DUCTUS_ROOT/submodules
$ ./build-aloha.sh

The above is equivalent to the following two sections.

.. _git book: http://git-scm.com/book/en/Git-Tools-Submodules
.. _aloha documentation: http://aloha-editor.org/guides/develop_aloha.html#building-aloha-building

Building a custom JS file
'''''''''''''''''''''''''

Ductus includes a custom build instructions file under ``ductus/static/modules/textwiki/build-aloha-for-ductus.js``.

Build with::

$ cd ductus/static/modules/textwiki
$ node ../../../../submodules/Aloha-Editor/build/r.js -o ./build-aloha-for-ductus.js

This will place the resulting files under `ductus/static/modules/textwiki/aloha/`, as Ductus expects them. Running the above command from elsewhere will most likely place the built files in the wrong place!
Note that if you have an existing `ductus/static/modules/textwiki/aloha` directory, it will be overwritten!

Building a custom CSS file
''''''''''''''''''''''''''

To build the corresponding CSS file, amend `ductus/static/modules/textwiki/aloha-css-for-ductus.css` and run::

$ cp aloha-css-for-ductus.css aloha/css
$ node ../../../../submodules/Aloha-Editor/build/r.js -o cssIn=aloha/css/aloha-css-for-ductus.css out=aloha/css/aloha.css optimizeCss=standard

Note that the javascript build process will overwrite the `aloha` directory, so you need to copy the css file again after (re)building JS.
