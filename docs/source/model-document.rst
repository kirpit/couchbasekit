Model Document
==============

:class:`couchbasekit.document.Document` is the main class you will be extending
to define your own model documents. There are 3 attributes must be set within
your model:

* __bucket_name__
* doc_type
* structure

and the optional ones are:

* __key_field__
* default_values
* required_fields

__bucket_name__ (required)
--------------------------
The name of the couchbase bucket that the new records will be saved into and
retrieved back from. This bucket should be already created manually.

doc_type (required)
--------------------------
The type of the document that will be used in various places and usually
lowercase of your model name but not checked or forced.

The most important function of ``doc_type`` attribute is to create an auto-field
named ``doc_type`` in every document. That means you can use it in your
JavaScript views to check which type of documents you want to emit::

    function (doc, meta) {
      if (doc.doc_type=='author') {
        emit(doc.slug, {first_name: doc.first_name, last_name: doc.last_name});
      }
    }

Another function of ``doc_type`` is to prefix your document id, if you're
using ``__key_field__`` optional attribute in order to create meaningful
document IDs. Its format is; ``{doc_type}_{key_value.lower()}``. If you don't
choose to use ``__key_field__`` in your models, ``doc_type`` will not be used
to prefix your document IDs either.

structure (required)
--------------------------
Structure definition dictionary is a wide topic, therefore explained in
another section. See :ref:`model-document-structure`.

__key_field__ (optional)
--------------------------
Key field is kind of simulating primary key feature in relational databases
that gives you ability to retrieve a single document by its `key value`
without doing a map-reduce in your buckets. It should be set to one of your
root field in your structure and **it is your responsibility** to check
if a document exist with the same `key value` before over-writing it.

Assuming the ``username`` field is the ``__key_field__`` in your structure::

    userdata = {'username': u'kirpit', 'is_superuser': True}
    try:
        user = User(userdata['username'])
    except User.DoesNotExist:
        # good, username is not taken
        user = User(userdata)
        user.save()
    else:
        print 'Sorry, this username is already taken.'

If you don't provide a ``__key_field__`` in your structure, first 12
characters of the hash key of your initial document will be used without
prefixing with ``doc_type`` attribute. Hashing is done via :mod:`hashlib.sha1`.

default_values (optional)
--------------------------
As it explains itself, it sets the default values for specified fields before
saving a document. Practically, you may assign a static value, a custom
field, a model document to relate or any callable that gives a value for it.

It does NOT set the document value, if it was already provided (which
is not surprising, is it?).

Refer to :ref:`quick-start` for an example.

required_fields (optional)
--------------------------
Another self explanatory attribute that checks if its items was provided
at the time of validation. It should be a :func:`tuple` (:func:`list` is ok
too) and have all the names of the fields that are required.

Refer to :ref:`quick-start` for an example.

Bonus: @register_view decorator
-------------------------------
You may use this decorator to declare which design view your document
instances will be using. This feature is used by
:meth:`couchbasekit.document.Document.view` that lets you to query your
views::

    from couchbasekit import Document, register_view

    @register_view('dev_books')
    class Book(Document):
        __bucket_name__ = 'mybucket'
        doc_type = 'book'
        structure = {
            # snip snip
        }

Then it becomes easier to get your view queries. Please refer to CouchBase
views documentation for advanced query options::

    >>> by_title = Book().view('by_title').results({
    ...     'startkey': 'A',
    ...     'endkey': 'C',
    ...     'stale': 'ok',
    ...     'limit': 1000,
    ... })
    >>> for result in by_title.results:
    ...     print result['id'], result['key'], result['value']


An experimental tool :class:`couchbasekit.viewsync.ViewSync`
also uses this decorator to backup/restore your server-side map/reduce functions.

.. note::
    ``@register_view`` decorator automatically attaches ``'full_set': True``
    parameter to your development views by default, so you don't have do it
    programmatically. To disable it simply use as:
    ``@register_view('dev_books', full_set=False)``. This feature doesn't
    affect production views at all.