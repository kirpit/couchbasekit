#! /usr/bin/env python
"""
couchbasekit.connection
~~~~~~~~~~~~~~~~~~~~~~~

:website: http://github.com/kirpit/couchbasekit
:copyright: Copyright 2012, Roy Enjoy <kirpit *at* gmail.com>, see AUTHORS.txt.
:license: MIT, see LICENSE.txt for details.
"""
from couchbase import Couchbase
from couchbasekit.errors import CredentialsNotSetError


class Connection(object):
    """This is the singleton pattern for handling couchbase connections
    application-wide.

    Simply set your authentication credentials at the beginning of your
    application (such as in "settings.py") by:

    >>> from couchbasekit import Connection
    >>> Connection.auth('theusername', 'p@ssword')

    or

    >>> Connection.auth(
    ...     username='theusername', password='p@ssword',
    ...     server='localhost', port='8091', # default already
    ... )

    .. note::
       This class is not intended to create instances, so don't try to do:

       >>> conn = Connection() # wrong

       or you will get a :exc:`RuntimeWarning`.
    """
    username = None
    password = None
    server = None
    connection = None

    def __new__(cls, *args, **kwargs):
        raise RuntimeWarning('Connection class is not intended to create instances.')

    @classmethod
    def auth(cls, username, password, server='localhost', port='8091'):
        """Sets the couchbase connection credentials, globally.

        :param username: bucket username (or "Administrator" for working with
            multi buckets).
        :type username: str
        :param password: bucket password (or Administrator's password for
            working with multi buckets).
        :type password: str
        :param server: couchbase server to connect, defaults to "localhost".
        :type server: str
        :param port: couchbase server port, defaults to "8091".
        :type port: str
        :returns: None
        """
        cls.username = username
        cls.password = password
        cls.server = ':'.join((server, port))

    @classmethod
    def bucket(cls, bucket):
        """Gives the bucket from couchbase server.

        :param bucket: Bucket name to fetch.
        :type bucket: str
        :returns: couchbase driver's Bucket object.
        :rtype: :class:`couchbase.client.Bucket`
        :raises: :exc:`couchbasekit.errors.CredentialsNotSetError` If the
            credentials wasn't set.
        """
        if cls.connection is None:
            if cls.username is None or cls.password is None:
                raise CredentialsNotSetError()
            cls.connection = Couchbase(cls.server, cls.username, cls.password)
        return cls.connection.bucket(bucket)

    @classmethod
    def close(cls):
        """Closes the current connection, which would be useful to ensure that
        no orphan couchbase processes are left. Use it in, for example one of
        your Django middleware's :meth:`process_response`.

        .. note::
           The class will open a new connection if a bucket is requested even
           though its connection was closed already.

        :returns: None
        """
        if cls.connection is not None:
            try: cls.connection.done()
            except AttributeError: pass
            cls.connection = None