#! /usr/bin/env python
import datetime
from couchbasekit import Document
from couchbasekit.fields import EmailField, PasswordField

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