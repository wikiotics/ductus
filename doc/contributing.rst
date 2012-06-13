= Ductus Contributor Guide =

See also DuctusDevelopmentGuide for a high-level overview of the software; DuctusDevelopmentInstance for information on setting up a local (or public) development server.

== Interacting with the project team ==

#wikiotics on FreeNode.  Two google groups: [http://groups.google.com/group/ductus-developers ductus-developers] (for discussion of use/development of ductus itself) and [http://groups.google.com/group/wikiotics wikiotics] (for broader community aspects).  A semi-serious developer should be on both lists at this point.

== Coding style ==

 * [http://www.python.org/dev/peps/pep-0008/ PEP 8] describes the ideal style for Python programs.  All python developers should be familiar with this document, as most everyone follows this style.  We follow it with only a few exceptions.
 * It seems that we mostly follow Google's [http://google-styleguide.googlecode.com/svn/trunk/javascriptguide.xml JavaScript style guide].  Major differences: we currently use underscores instead of camelCase for variables, functions, and methods.  And we don't use jsdoc for anything at the moment.

Also, we generally don't commit to the repository any code that contains trailing whitespace after lines.  And a file should end with precisely one newline; there should be no extraneous newlines at the end of a file.

Indentation should be done with spaces, never with tabs.  [http://google.com/search?q=tabs+are+evil Tabs are evil.]  The only place we should have tabs is when we have copied and pasted code from another project and that project uses tabs.  In this case, we should use tabs only (and not mix spaces with them) when we modify that code. Getting indentation correct the first time is a Good Thing because it messes up the diff/blame history any time you change indentation. 

A useful resource for staying away from JavaScript pitfalls is the [http://bonsaiden.github.com/JavaScript-Garden/ Javascript Garden].  Douglas Crockford's book, Javascript: The Good Parts, can also be a useful reference.

See also Mozilla's [https://wiki.mozilla.org/WebAppSec/Secure_Coding_Guidelines Secure Coding Guidelines], which can be generally useful.  Another useful link is at http://jtaby.com/2012/04/23/modern-web-development-part-1.html

We are pretty serious about the [http://en.wikipedia.org/wiki/Don%27t_repeat_yourself DRY principle].  To avoid repeating ourselves, and to hide complexity in parts of the API, we make heavy use of python's metaprogramming features, particularly in the "ductmodels" layer.  In general, if you are copying and pasting code, there is probably a better way to do it.  That's fine for prototyping, but before submitting code for inclusion in the main development branch, it's generally best to make the code as maintainable as possible.

We try to [http://pragprog.com/the-pragmatic-programmer/extracts/software-entropy fix broken windows] as we go.

=== Some random notes ===

 * use [http://optipng.sourceforge.net/ optipng] on all PNG files before adding them to the repository

== Patch submission ==

Patches can either be uploaded to the corresponding ticket on trac, or a developer can tell us to pull a patch (or patch series) from a git repository.  The pull will only occur if the maintainer is satisfied with everything in the patch series.  [http://gitorious.org/ductus Ductus is registered on gitorious], which provides workflow mechanisms with which we can experiment.  Keep in mind, though, that garrison doesn't push code to gitorious as often as he pushes to git.garrison.cc, so it's best to pull from git.garrison.cc any time you want the latest code.

If using git, never ever ever commit unrelated changes in the same changeset.  Each commit should be one logical change.  And it should attempt to break nothing and to introduce no additional brokenness.  The same is true for patches submitted to trac.

== Documentation for software/specifications we use and depend on ==

 * [http://git-scm.com/documentation git documentation] - useful for development, and for understanding the inspiration behind Ductus' ResourceDatabase
 * Django ([http://docs.djangoproject.com/en/1.2/intro/tutorial01/ very good tutorials]; [http://docs.djangoproject.com/en/1.2/ API reference]) Keep in mind we don't use Django's Model system for much, but Ductus' model system is inspired by Django.
 * [http://dev.w3.org/html5/spec/Overview.html html5 spec]; [http://diveintohtml5.info/ dive into html5]
 * The [http://www.w3.org/TR/capture-api/ HTML media capture API] will allow users to submit audio, pictures, etc. directly from the web browser
 * [http://docs.jquery.com/ jQuery], and we use a few things from jQueryUI

== Other "required" reading ==

 * http://blog.wikiotics.net/