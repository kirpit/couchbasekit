#! /usr/bin/env python
import datetime
from couchbasekit import Document, Connection

Connection.auth('couchbasekit_samples', 'couchbasekit')

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