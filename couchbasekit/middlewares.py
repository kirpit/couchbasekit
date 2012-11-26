#! /usr/bin/env python
"""
couchbasekit.middlewares
~~~~~~~~~~~~~~~~~~~~~~~~

:website: http://github.com/kirpit/couchbasekit
:copyright: Copyright 2012, Roy Enjoy <kirpit *at* gmail.com>, see AUTHORS.txt.
:license: MIT, see LICENSE.txt for details.
"""
from couchbasekit import Connection

class CouchbasekitMiddleware(object):
    """A helper that can be used in Django Middlewares to close couchbase
    connection gracefully in order not leave any orphan subprocess behind.
    """
    def close_connection(self):
        Connection.close()

    def process_exception(self, request, exception):
        self.close_connection()
        return None

    def process_response(self, request, response):
        self.close_connection()
        return response