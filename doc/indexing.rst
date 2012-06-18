Indexing plan
=============

(This is currently a bit out of date.)

A MongoDB collection will be created, which will be populated with a
MongoDB document for every URN that exists in the system.  A script will
exist that can populate/verify this collection with existing URNs, and
we will also update the collection on the fly any time a new URN comes
into existence.

The document will have the following fields:
 * urn - a string containing the URN of the resource
 * json - if the URN represents an XML resource, this will be set to the
data structure given by DuctModel.output_json_dict().  Otherwise (i.e.
for a blob), it will be null, and the following additional field will
not exist.
 * links - a list of all URNs that are linked from the current resource.
 URNs listed in resource.common.parents are *not* included here.  Both
direct links and links of any linked documents (recursively) will be
added to this list.  I think we'll put a boolean flag on each item of
the list to say whether it represents a direct link or not.
* current_wikipages - a list of pages on the site where the resource is
currently available (e.g. "en:English").  This will only be set on the
top-level resource, i.e. an image that is available within a lesson at
en:Introduction will have a blank current_wikipages list.
Of the above, "current_wikipages" is the only thing that will be
modified over time.

We can at some regular interval set "links" to null on any resource
where current_wikipages is empty *and* the urn is not contained in
"links" on any other resource.  That way we save a bit of memory on
outdated/old resources, and searches for "what contains image X or tag
Y" are less likely to return outdated results (we will filter such
results anyway, of course)  ... it is useful nonetheless to keep at
least the existence of these documents and their "parents" in memory, so
that we can always traverse the revision history...

We create MongoDB indexes on the following fields:
* urn
* json.common.parents
* json.tags
* links
* if MongoDB allows, an index on links that only includes documents
where current_wikipages is not empty

http://api.mongodb.org/python/current/tutorial.html

future: mapreduce http://cookbook.mongodb.org/patterns/unique_items_map_reduce/
