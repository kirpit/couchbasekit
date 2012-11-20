#! /usr/bin/env python
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
        'books': [Book], # 1-to-many
        'has_book': bool,
        'age': int,
        'birthday': datetime.date,
        'created_at': datetime.datetime,
    }
    # optional
    default_values = {
        'has_book': False,
        # don't worry about the timezone info!
        # it's auto assigned as to UTC, so all you have to do is:
        'created_at': datetime.datetime.utcnow,
    }
    # optional
    required_fields = (
        'slug',
        'first_name',
        'last_name',
        'email',
    )