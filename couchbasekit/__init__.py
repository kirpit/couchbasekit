#! /usr/bin/env python
"""
couchbasekit
~~~~~~~~~~~~

A wrapper around CouchBase Python driver for document validation and more.

:website: http://github.com/kirpit/couchbasekit
:copyright: Copyright 2012, Roy Enjoy <kirpit *at* gmail.com>, see AUTHORS.txt.
:license: MIT, see LICENSE.txt for details.
"""
from couchbasekit.connection import Connection
from couchbasekit.document import Document
from couchbasekit.viewsync import register_view

__version__ = '0.2.1'

__all__ = (
    Connection,
    Document,
    register_view,
)