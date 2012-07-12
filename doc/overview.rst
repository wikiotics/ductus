.. _overview:

===============
Ductus Overview
===============

This page is a bit rough.  Please feel free to ask questions on the
ductus-developers list about anything that may be confusing.

Some things that are helpful to understand:

 * Some flavor of UNIX
 * Python
 * Django
 * XML and XML namespaces
 * Git (both for development and because Ductus' version control model is very similar to git)

Introduction
============

Data model
==========

We have a "ResourceDatabase", which is a database of static (that is, unchanging over time) objects that are each referenced by a URN that uniquely describes the content using a secure hash of the content.  We refer to these objects as "resources" or URNs.

Two main types of resources: blobs and XML.  A blob identifies itself as a blob and then contains some sequence of bytes.  Blobs are used to store image data, text data -- anything that does not need to reference other objects in the system, and generally for unstructured data.  XML resources, on the other hand, generally represent structured data in the system, and it can even reference other resources by a resource's URN.  An XML resource has a few bytes that identify it as XML, and then there is an XML data structure that can be parsed.  See source:ductus/resource/__init__.py for the main ResourceDatabase code.

The fully-qualified-name of the toplevel element in an XML resource describes what type of structured resource the resource represents.  Some fully-qualified-names currently in use in the system include:

 * textwiki content - {{{{http://wikiotics.org/ns/2009/wikitext}textwiki}}}
 * a picture - {{{{http://wikiotics.org/ns/2009/picture}picture}}}
 * a picture-choice group (four sentence+picture combinations) - {{{{http://wikiotics.org/ns/2009/picture_choice}picture_choice_group}}}
 * a picture-choice lesson (a series of picture-choice groups) - {{{{http://wikiotics.org/ns/2009/picture_choice}picture_choice_lesson}}}

By the way, you can view the XML representation of any resource on Wikiotics.org by clicking on "more views" and then "xml_as_html" (or by appending "?view=xml_as_html" to the URL).  This is probably worth doing, as just looking at a few resources in the database will give a much clearer idea of how things work.

Let's pause for a moment to think about what we've said so far and how it relates to the architecture of git.  One of the best ways to understand git is to read the [http://repo.or.cz/w/git.git/blob/e83c5163316f89bfbde7d9ab23ca2e25604af290:/README README from the very first commit] in which git bootstrapped itself.  Each object in a git database is referenced by a sha1 hash of the object.  In Ductus, we use a sha384 hash in URN form, instead.  There are three main types of objects in the git database: blobs (which are basically equivalent to blobs in Ductus), as well as trees and changesets.  (A tree represents the structure of a directory; a changeset represents a given commit in the system.)  Each of these objects exists in a special format that allows it to reference other objects in the git database.  In Ductus, instead of having a separate toplevel type for each possible structure of data that exists, we simply have a unified XML type of resource, which represents any type of structured data.  This unification allows us more flexibility in defining additional types of structured data, which is good because in Ductus we operate directly on lowlevel objects in the system (instead of using the filesystem as an intermediary).

We have a higher level "DuctModel" abstraction for XML resources (which can be found in the rather dense source file source:ductus/resource/ductmodels.py).  This system allows developers to declare the data structure for different classes of objects in the system (for instance, textwiki pages, picture-choice lessons, each of which is described in detail below).

The DuctModel system also supports "blueprints," which is a way of encoding json that represents changes that should be made to an object for its next revision in the system.  The picture-choice editor creates the json within the user's web browser, and it is sent to the server which then makes the requested changes.  In the future we may decouple the blueprint system slightly from the DuctModel system, which will allow us to more finely tune permissions.  (For instance, we may make it so only an "admin" on the site can edit the license of an object.  Right now the blueprint system does not support permissions, so nobody is allowed to change a license when patching a resource.)  Patching a resource creates a new resource with a new URN; the old resource exists in the system as before, and the new resource will have a reference to its parent so we can track revision history.

The DuctusCommonElement exists for each data model, and stores information about a revision.  This includes the author, timestamp, log message, license information, and the parent revisions of a resource.

Storage backends in source:ductus/resource/storage/ are used to store the objects in the ResourceDatabase.  The "remote" storage backend allows URNs to be gathered on demand from a remote server, such as wikiotics.org.  It would be nice in the future to have some smarter backends that can recognize similar objects and compress data, but right now we just store everything as flat files in the local storage backend.  This isn't ''too'' bad though, as since multiple lessons referencing the same image will each have references to the same "blob" URN, and the blob of the image itself will only be stored once in the database.

Generic wiki
============

Git has branches, each of which point to a tip (changeset) in the repository.  In Ductus, each wiki page is its own independent branch with revision history.  At a given moment in time, it will point to some URN that represents an XML resource (or if the urn is the empty string, it means that page has been "deleted").  A WikiPage in source:ductus/wiki/models.py represents a wiki page using Django's models system.  A WikiRevision refers to a specific revision at a given point in time.  (The most recent revision will generally be shown when somebody navigates to the URL that corresponds to a wiki page.)

source:ductus/wiki/views.py contains the generic wiki dispatch mechanism, as well as some views that are common to all wiki resources.  Indeed, a given wiki page or URN has multiple "views" depending on the type of content.  These "views" implement different ways of interacting with (or editing) a resource.  If somebody wants to create a game that works with picture-choice lesson cards, that would be implemented as a new view for picture-choice resources.

Wiki modules
============

Textwiki
--------

source:ductus/modules/textwiki/ductmodels.py

Flashcards
----------

source:ductus/modules/flashcards/ductmodels.py

Quirks involving Django
=======================

HttpRequest.escaped_full_path() (see ticket #32)

304 handling: source:ductus/wiki/views.py ; source:ductus/wiki/decorators.py ; source:ductus/middleware/unvarying.py ; ticket #20

Browser support
===============

A quick overview of how we deal with browser support is at https://code.ductus.us/wiki/DuctusBrowserSupport
