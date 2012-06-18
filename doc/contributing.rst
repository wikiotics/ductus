Ductus Contributor Guide
========================

See also DuctusDevelopmentGuide for a high-level overview of the software; DuctusDevelopmentInstance for information on setting up a local (or public) development server.

Interacting with the project team
---------------------------------

``#wikiotics`` on FreeNode.  Two google groups: ductus-developers_ (for discussion of use/development of ductus itself) and wikiotics_ (for broader community aspects).  A semi-serious developer should be on both lists at this point.

.. _ductus-developers: http://groups.google.com/group/ductus-developers
.. _wikiotics: http://groups.google.com/group/wikiotics

Coding style
------------

 * `PEP 8`_ describes the ideal style for Python programs.  All python developers should be familiar with this document, as most everyone follows this style.  We follow it with only a few exceptions.
 * It seems that we mostly follow Google's `JavaScript style guide`_.  Major differences: we currently use underscores instead of camelCase for variables, functions, and methods.  And we don't use jsdoc for anything at the moment.

.. _PEP 8: http://www.python.org/dev/peps/pep-0008/
.. _Javascript style guide: http://google-styleguide.googlecode.com/svn/trunk/javascriptguide.xml

Also, we generally don't commit to the repository any code that contains trailing whitespace after lines.  And a file should end with precisely one newline; there should be no extraneous newlines at the end of a file.

Indentation should be done with spaces, never with tabs. `Tabs are evil`_  The only place we should have tabs is when we have copied and pasted code from another project and that project uses tabs.  In this case, we should use tabs only (and not mix spaces with them) when we modify that code. Getting indentation correct the first time is a Good Thing because it messes up the diff/blame history any time you change indentation.

.. _Tabs are evil: http://google.com/search?q=tabs+are+evil

A useful resource for staying away from JavaScript pitfalls is the `Javascript Garden`_.  Douglas Crockford's book, Javascript: The Good Parts, can also be a useful reference.

.. _Javascript Garden: http://bonsaiden.github.com/JavaScript-Garden/

See also Mozilla's `Secure Coding Guidelines`_, which can be generally useful.  Another useful link_.

.. _Secure Coding Guidelines: https://wiki.mozilla.org/WebAppSec/Secure_Coding_Guidelines
.. _link: http://jtaby.com/2012/04/23/modern-web-development-part-1.html

We are pretty serious about the `DRY principle`_.  To avoid repeating ourselves, and to hide complexity in parts of the API, we make heavy use of python's metaprogramming features, particularly in the "ductmodels" layer.  In general, if you are copying and pasting code, there is probably a better way to do it.  That's fine for prototyping, but before submitting code for inclusion in the main development branch, it's generally best to make the code as maintainable as possible.

.. _DRY principle: http://en.wikipedia.org/wiki/Don%27t_repeat_yourself

We try to `fix broken windows`_ as we go.

.. _fix broken windows: http://pragprog.com/the-pragmatic-programmer/extracts/software-entropy

Some random notes
:::::::::::::::::

 * use optipng_ on all PNG files before adding them to the repository

.. _optipng: http://optipng.sourceforge.net/

Patch submission
----------------

Patches can either be uploaded to the corresponding ticket on trac, or a developer can tell us to pull a patch (or patch series) from a git repository.  The pull will only occur if the maintainer is satisfied with everything in the patch series. Ductus_ is registered on gitorious], which provides workflow mechanisms with which we can experiment.  Keep in mind, though, that garrison doesn't push code to gitorious as often as he pushes to git.garrison.cc, so it's best to pull from git.garrison.cc any time you want the latest code.

.. _Ductus: http://gitorious.org/ductus

If using git, never ever ever commit unrelated changes in the same changeset.  Each commit should be one logical change.  And it should attempt to break nothing and to introduce no additional brokenness.  The same is true for patches submitted to trac.

Documentation for software/specifications we use and depend on
--------------------------------------------------------------

 * `git documentation`_ - useful for development, and for understanding the inspiration behind Ductus' ResourceDatabase
 * Django (`very good tutorials`_, `API reference`_) Keep in mind we don't use Django's Model system for much, but Ductus' model system is inspired by Django.
 * `html5 spec`_, `dive into html5`_
 * The `HTML media capture API`_ will allow users to submit audio, pictures, etc. directly from the web browser
 * jQuery_, and we use a few things from jQueryUI

.. _git documentation: http://git-scm.com/documentation
.. _very good tutorials: http://docs.djangoproject.com/en/1.4/intro/tutorial01/
.. _API reference: http://docs.djangoproject.com/en/1.4/
.. _html5 spec: http://dev.w3.org/html5/spec/Overview.html
.. _dive into html5: http://diveintohtml5.info/
.. _HTML media capture API: http://www.w3.org/TR/capture-api/
.. _jQuery: http://docs.jquery.com/

Other "required" reading
------------------------

 * http://blog.wikiotics.net/
