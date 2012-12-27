Changelog
=========

Release v0.2.0-dev
--------------
* @register_view decorator to use CouchBase views easier
* EmailField.is_valid(email) is implemented and does work
* CustomField abstract class can hold any type of value including dictionary
* doc.delete() method that is equal to doc.bucket.delete(doc.doc_id, doc.cas_value)
* Fixed dependency errors on installation

Release v0.1.2
--------------
* Include *.rst files to prevent setup fail
* Fix None value skipping in retrieved documents
* Unicode encoding of CustomField values

Release v0.1.1
--------------
* Fix timezone aware datetime/time bug for free list fields
* Fix model document validation bugs
* Removed pragmatic document relations due to complexity
* Exception single/double quote swap
* ChoiceField.iteritems() now returns ChoiceField.CHOICES.iteritems()
* Respect lazy translations in ChoiceField
