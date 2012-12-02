#! /usr/bin/env python
"""
couchbasekit
~~~~~~~~~~~~

couchbasekit is a wrapper around couchbase driver for document validation
and more.

:website: http://github.com/kirpit/couchbasekit
:copyright: Copyright 2012, Roy Enjoy <kirpit *at* gmail.com>, see AUTHORS.txt.
:license: MIT, see LICENSE.txt for details.
"""
from couchbasekit.connection import Connection
from couchbasekit.document import Document

__version__ = '0.1.1'

__all__ = (
    Connection,
    Document,
)