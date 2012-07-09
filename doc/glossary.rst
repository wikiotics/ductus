========
Glossary
========

.. todo::

    Obviously this section is very incomplete.

    Also, it would be nice to linkify a lot of things on this page to
    point to further information.

DAG: directed acyclic graph

Resource == hash == "URN": some saved object in the system.  Once a
resource is saved, it does not change.  (Other resources can be saved
that derive from the resource and contain it as a "parent", but that
is all.)

blob is a specific type of resource that contains arbitrary unstructed
data.  Maybe a text file, maybe audio or image binary data.  A blob is
always a terminal node (?) in the DAG; that is, it cannot directly
reference any other resource, but one or more resources may reference it.

XML Resource is the structured .

WikiPage: a page on the site, corresponding to a url.  For instance,
``en:main_page`` is a WikiPage.  The "prefix" is everything before the
first colon (i.e. the namespace).

WikiRevision: represents what resource (URN) is saved to a WikiPage at
a given time.  Must point to an XML resource (as it is unclear how to
display a bare blob).  Typically, when somebody navigates to a
WikiPage, the latest WikiRevision for the page will be displayed.

location history: the revision history of a WikiPage (i.e. the set of
all WikiRevision's).

document history: the revision history of the document itself.  As
each XML resource points to any parent revision(s), the revision
history consists of all such ancestors for a resource.  This is
distinct from the location history since we allow pages to move around
within the wiki yet still maintain full revision history.

ductmodels: a python convenience layer for dealing simply with XML resources and their schemata

blueprint: a JSON object that represents instructions for creating or
patching a ductmodel.  A blueprint is used e.g. when a resource is
saved through the web interface.  The browser sends a blueprint to the
server in a POST request, and the save is performed.

view

subview

lesson template

group

flashcard row == flashcard,
flashcard column == side

Responsive web design and Responsive CSS

chain_clone

document toolbar

indexing

mediacache
