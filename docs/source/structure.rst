.. _model-document-structure:

Model Document Structure
========================
Structure definition dictionary is the most important part of your model
document. They are similar to table fields in relational SQL systems in a way.
You simply need to define them as key-value that corresponds to
field_name: field_type. Keep reading...

Allowed Types
-------------
To begin, you may simply define those field types as standard Python types, see
:const:`couchbasekit.schema.ALLOWED_TYPES` for the list of them.

Document Relations
------------------
You can define a field type as another model document (or even recursively)
within your structure. This simulates kind of foreign key scenario in the
relational systems but you must know that every related document will be
fetched separately from couchbase server as the nature of the non-relational
systems. The good news is, couchbasekit fetches these related documents
on-demand and caches them during the object's life time.

>>> lonely_galaxy = Publisher('lonely_galaxy')
>>> dna = Author('douglas_adams')
>>> dna.publisher = lonely_galaxy
>>> dna.save()
4535519295771
>>> dna = Author('douglas_adams') # retrieve the same doc
>>> dna.get('publisher')
u'publisher_lonely_galaxy'
>>> dna.load() # fetch and cache all of its items
... # output stripped out to keep here clean
>>> dna.get('publisher') # no more raw, already cached
{u'doc_type': u'publisher', u'created_at': u'2012-11-18 16:24:16.784474+00:00', 'slug': u'lonely_galaxy', u'name': u'Lonely Galaxy Press'}
>>>

Custom Fields
-------------
With couchbasekit, of course you can have your specific field types and a few
of them may be already defined in :mod:`couchbasekit.fields`. Creating your own
custom field is quite easy, please refer to
:class:`couchbasekit.fields.CustomField`.

As an example, the password fields are salted randomly and encrypted on the
fly, thus cannot be decrypted back:

>>> from couchbasekit.fields import PasswordField
>>> raw = '123456'
>>> PasswordField(raw)
'$2a$12$1nshsN7Nt8e3.dPd1ZcA7uJnesu2sg52nZl6CX1N0ETZwc2UYCGYS'
>>> PasswordField(raw)
'$2a$12$UyLdw0QwHJmONipuyQ3Mq.NA4YteHZ8NDwXFpaJP.xi9ZnUjmxvWa'
>>> hashed = PasswordField(raw)
>>> hashed.value
'$2a$12$r490Tn0zEaMYTf.dfjBNoe0I729Ej2Z18xTJLbwfqZyOXeabXZUky'
>>> hashed.check_password('incorrect')
False
>>> hashed.check_password('123456')
True
>>>

List (Multi Value) Fields
---------------------------------
You can also define a :func:`list` of values. For example::

    class Book(Document):
        __bucket_name__ = 'couchbasekit_samples'
        doc_type = 'book'
        structure = {
            'title': unicode,
            'published_at': datetime.date,
            'pictures': list,
            'tags': [unicode],
        }

Note that if you are sure what type of elements a `List Field` will have,
you should specify it explicitly **only once**. Otherwise just let it be
``list`` then it can have any combination of
:const:`couchbasekit.schema.ALLOWED_TYPES`, a model document or
a subclass of :class:`couchbasekit.fields.CustomField` as usual.


Schemaless Fields
-----------------
Some of your model documents may need complicated structure, such as
pre-defined item types of a dictionary, deeply nested dictionary or
totally schemaless sub-structures.

.. warning::
    One downside of such free dictionary models is that you can't use
    attribute access (a.k.a. dot notation), so you have to use
    dictionary-like item assignment and the same rule applies for retrieving
    of your data.

First and easiest example would be a total schemaless model document::

    class FreeModel(Document):
        __bucket_name__ = 'couchbasekit_samples'
        doc_type = 'free'
        structure = {}

    free = FreeModel()
    # that does NOT work because 'somefield' wasn't defined in the structure
    free.somefield = 'some value'
    # but that will work:
    free['somefield'] = 'some value'
    # and those also will work as the Document class is a dictionary itself!
    free = FreeModel(somefield='some value', listfield=['list', 'of', 'items'])
    # or that's ok too:
    data = {'somefield': 'some value', 'listfield': ['list', 'of', 'items']}
    free = FreeModel(data)


If you want a semi schemaless structure on a specific field that means you
know it will be dictionary and what type for its keys and values will be, you
may define only types for its key-value pair::

    class User(Document):
        __bucket_name__ = 'couchbasekit_samples'
        doc_type = 'user'
        structure = {
            'username': unicode,
            'email': EmailField,
            'password': PasswordField,
            'logins': {
                # datetime: ip
                datetime.datetime: unicode,
            },
        }

.. note::
    Please note that for the type specified free dictionaries, like the
    one above, the key of that dictionary must be :func:`hash`'able as
    it is required by Python dictionaries. This means you can't use a
    :func:`list` or a model document instance for such keys.


Finally, deeply nested dictionary fields::

    class Book(Document):
        __bucket_name__ = 'couchbasekit_samples'
        doc_type = 'book'
        structure = {
            'title': unicode,
            'published_at': datetime.date,
            'pictures': list,
            'tags': [unicode],
            'category': {
                u'History': bool,
                u'Sci-Fiction': bool,
                u'Cooking': {
                    u'Turkish': bool,
                    u'Italian': bool,
                    u'Fast Food': bool,
                    u'Dessert': bool,
                },
            },
        }

.. note::
    Please note that again; dot notation does **not** work for deeply nested
    dictionaries either. So you can't check or set of a book's `Dessert`
    category by dot notation:

    >>> book = Book('ad45556b3ba4')
    >>> book.category.Cooking.Dessert # wrong!
    >>> book.category.Cooking[u'Dessert'] # wrong!
    >>> book.category is None
    True
    >>> book.category['Cooking']['Dessert'] = False # wrong, as 'category' is not assigned yet
    >>> book.category = {u'Cooking': {u'Dessert': True}} # correct
    >>> book.category['Cooking']['Dessert'] = True # it was created, so it's ok now
    >>> book['category']['Cooking']['Dessert'] = True # correct, same as above
    >>> book.category['History'] # wrong, you'll get a KeyError
    >>> 'History' in book.category # that's the way
    False
    >>> book.category[u'History'] = True # correct, only assigns the u'History'
    >>> book['category'] = {u'History': True} # correct, but overwrites the 'category'
    >>>

