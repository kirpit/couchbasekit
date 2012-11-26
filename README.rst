**couchbasekit** is `a wrapper around couchbase driver for document validation
and more`. It was inspired by `MongoKit <http://namlook.github.com/mongokit/>`_
and was developed by *the project coming soon?*, which is also an open
source project.

You can get detailed information about couchbase itself from
http://www.couchbase.com/ and about its Python driver form
http://www.couchbase.com/develop/python/next.

Documentation: https://couchbasekit.readthedocs.org/en/latest/

Source code: https://github.com/kirpit/couchbasekit

Quick Start
===========

Less talk, more code. Set your authentication details first::

    from couchbasekit import Connection

    # you should do this somewhere beginning such as settings.py:
    Connection.auth('myusername', 'p@ssword')


Then define your model document.

**author.py**::

    import datetime
    from couchbasekit import Document
    from couchbasekit.fields import EmailField, ChoiceField
    from example.samples.publisher import Publisher
    from example.samples.book import Book

    class Gender(ChoiceField):
        CHOICES = {
            'M': 'Male',
            'F': 'Female',
        }


    class Author(Document):
        __bucket_name__ = 'couchbasekit_samples'
        __key_field__ = 'slug' # optional
        doc_type = 'author'
        structure = {
            'slug': unicode,
            'first_name': unicode,
            'last_name': unicode,
            'gender': Gender,
            'email': EmailField,
            'publisher': Publisher, # kind of foreign key
            'books': [Book], # 1-to-many, or many-to-many? some-to-some.. :)
            'has_book': bool,
            'age': int,
            'birthday': datetime.date,
            'created_at': datetime.datetime,
        }
        default_values = { # optional
            'has_book': False,
            # don't worry about the timezone info!
            # it's auto assigned as to UTC, so all you have to do is:
            'created_at': datetime.datetime.utcnow,
        }
        required_fields = ( # optional
            'slug',
            'first_name',
            'last_name',
            'email',
        )


Then use it as such;

>>> from example.samples.author import Author
>>> from couchbasekit.fields import EmailField
>>>
>>> douglas = Author()
>>> douglas.is_new_record
True
>>> try:
...     douglas.validate()
... except Author.StructureError as why:
...     print why
...
Key field "slug" is defined but not provided.
>>>
>>> douglas.slug = u'douglas_adams'
>>> try:
...     douglas.validate()
... except Author.StructureError as why:
...     print why
...
Required field for "first_name" is missing.
>>>
>>> isinstance(douglas, dict)
True
>>> douglas.update({
...     'first_name': u'Douglas',
...     'last_name': u'Adams',
...     'email': EmailField('dna@example.com'),
... })
...
>>> douglas.validate()
True
>>> douglas.save()
14379837794698
>>> douglas.cas_value # CAS value (version) of the couchbase document
14379837794698
>>> douglas.id
u'douglas_adams'
>>> douglas.doc_id
u'author_douglas_adams'
>>> douglas.birthday is None
True
>>> douglas.non_exist_field
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "couchbasekit/document.py", line 68, in __getattr__
    return super(Document, self).__getattribute__(item)
AttributeError: 'Author' object has no attribute 'non_exist_field'
>>>
>>> dna = Author('douglas_adams')
>>> dna.is_new_record
False
>>> douglas==dna
True
>>> douglas.has_book = True
>>> douglas==dna
False
>>> # nice!

