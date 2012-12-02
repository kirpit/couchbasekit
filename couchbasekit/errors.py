#! /usr/bin/env python
"""
couchbasekit.errors
~~~~~~~~~~~~~~~~~~~

:website: http://github.com/kirpit/couchbasekit
:copyright: Copyright 2012, Roy Enjoy <kirpit *at* gmail.com>, see AUTHORS.txt.
:license: MIT, see LICENSE.txt for details.
"""

class CouchbasekitException(Exception):
    """Just to have some base exception class."""
    pass


class CredentialsNotSetError(CouchbasekitException):
    """Raised when your :class:`couchbasekit.connections.Connection`
    credentials are not set.
    """
    pass


class DoesNotExist(CouchbasekitException):
    """Raised when a model class passed with an id to be fetched, but not
    found within couchbase.

    You don't have to specifically import this error to check if does not exist
    because your model document has just the same error for convenience.
    For example::

        try:
            mrnobody = Author('someone_doesnt_exist')
        except Author.DoesNotExist:
            # some useful code here
            pass
    """
    def __init__(self, obj, key):
        msg = "{doc} document with the key '{key}' not found.".format(
            doc=type(obj).__name__,
            key=key,
        )
        super(DoesNotExist, self).__init__(msg)


class StructureError(CouchbasekitException):
    """Raised when things go wrong about your model class structure or instance
    values. For example, you pass an :class:`int` value to some field that
    should be :class:`str` or some required field wasn't provided etc..
    """
    def __init__(self, key=None, exp=None, given=None, msg=''):
        if key is not None and exp is not None and given is not None:
            # get "expected" type name
            if isinstance(exp, type):
                exp = exp.__name__
            elif isinstance(exp, list) and len(exp)==1:
                exp = 'list of %s' % exp[0].__name__
            else:
                exp = type(exp).__name__
            # get "given" type name
            if isinstance(given, type):
                given = given.__name__
            elif isinstance(given, (tuple, list)):
                given = ', '.join((type(g).__name__ for g in given))
            else:
                given = type(given).__name__
            msg = "'{key}' does not fit the required structure, " \
                  "expected {exp} but '{given}' is given.".format(
                key=key,
                exp=exp,
                given=given,
            )
        super(StructureError, self).__init__(msg)
