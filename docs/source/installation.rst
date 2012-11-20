Installation and Configuration
==============================

It is strongly suggested that you should already know what is
`virtualenv <http://www.virtualenv.org/>`_, preferably
`virtualenvwrapper <http://www.doughellmann.com/projects/virtualenvwrapper/>`_
at this stage.

You can easily install couchbasekit via pip:

``$ pip install couchbasekit``

.. note::
    couchbasekit has dependencies on:

    * couchbase
    * jsonpickle
    * python-dateutil
    * py-bcrypt (optional for :class:`couchbasekit.fields.PasswordField`)

Then, the only configuration you have to do is couchbase authentication,
somewhere at the beginning of your application (such as `settings.py` if you're
using `Django Web Framework <https://www.djangoproject.com/>`_ for example)::

    from couchbasekit import Connection
    Connection.auth('theusername', 'p@ssword')

or::

    from couchbasekit import Connection
    Connection.auth(
        username='theusername', password='p@ssword',
        server='localhost', port='8091', # default already
    )

That's it. Now, you are ready for a crash course. See :ref:`quick-start`.
