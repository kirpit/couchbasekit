API Documentation
=================

.. toctree::
    :maxdepth: 2

.. automodule:: couchbasekit.connection
    :members:

.. automodule:: couchbasekit.document
    :members:

.. automodule:: couchbasekit.schema
    :members:

.. py:data:: ALLOWED_TYPES

This is the constant that will be used to check your model structure
definitions::

    ALLOWED_TYPES = (
        bool,
        int,
        long,
        float,
        unicode,
        basestring,
        list,
        dict,
        datetime.datetime,
        datetime.date,
        datetime.time,
    )

However, it doesn't include :class:`str` type intentionally because couchbase
will keep your values in :class:`unicode` and you will have trouble re-saving
a :class:`str` field right after you fetch it. If you really have to pass a
:class:`str` value while you first creating a document record, you can simply
define your field as :class:`basestring` and both types will be accepted at the
time of validation.

Besides these ones, you can also use :class:`couchbasekit.document.Document`
for document relations and :class:`couchbasekit.fields.CustomField` subclasses
for special field types. See :mod:`couchbasekit.fields`.


.. automodule:: couchbasekit.fields
    :members:

.. automodule:: couchbasekit.errors
    :members:

.. automodule:: couchbasekit.middlewares
    :members:

.. automodule:: couchbasekit.viewsync
    :members:
