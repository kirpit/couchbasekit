#! /usr/bin/env python
import datetime
from couchbasekit import Document, Connection
from example.samples.book import Book

Connection.auth('couchbasekit_samples', 'couchbasekit')

class Publisher(Document):
    __bucket_name__ = 'couchbasekit_samples'
    __key_field__ = 'slug' # optional
    doc_type = 'publisher'
    structure = {
        'slug': unicode,
        'name': unicode,
        'phone': unicode,
        'address': unicode,
        'established_year': int,
        'created_at': datetime.datetime,
        'publishes': {
            datetime.date: [Book],
        }
    }
    # optional
    default_values = {
        # don't worry about the timezone info!
        # it's auto assigned as to UTC, so all you have to do is:
        'created_at': datetime.datetime.utcnow,
    }
    # optional
    required_fields = (
        'slug',
        'name',
    )