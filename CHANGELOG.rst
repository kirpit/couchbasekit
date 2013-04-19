Changelog
=========

Release v0.2.2
--------------------
* Caching bucket objects at Connection layer rather than Document layer
* Auto ``'full_set': True`` feature with ``@register_view`` decorator
* Implemented missing ``__ne__`` comparison magic function for Document and CustomField
* Minor email validation fix from Django 1.5.1

Release v0.2.1
--------------------
* Urgent CustomField and Document __eq__ fix (sorry for that)

Release v0.2.0
--------------------
* ``@register_view`` decorator (instead of __view_name__ document property) to use CouchBase views easier
* EmailField.is_valid(email) is implemented and does work
* ViewSync.download() now downloads within their bucket folder and supports spatial views too
* ViewSync.upload() is implemented and does work
* CustomField abstract class can hold any type of value including dictionary
* doc.delete() method that is equal to doc.bucket.delete(doc.doc_id, doc.cas_value)
* Removed CredentialsNotSetError and using RuntimeError instead on connection
* Fixed dependency errors on installation

Release v0.1.2
--------------------
* Include .rst files to prevent setup fail
* Fix None value skipping in retrieved documents
* Unicode encoding of CustomField values

Release v0.1.1
--------------------
* Fix timezone aware datetime/time bug for free list fields
* Fix model document validation bugs
* Removed pragmatic document relations due to complexity
* Exception single/double quote swap
* ChoiceField.iteritems() now returns ChoiceField.CHOICES.iteritems()
* Respect lazy translations in ChoiceField
