#! /usr/bin/env python
from distutils.core import setup


setup(
    name = 'couchbasekit',
    version = '0.2.3-dev',
    author = 'Roy Enjoy',
    author_email = 'kirpit@gmail.com',
    packages = ['couchbasekit'],
    url = 'https://github.com/kirpit/couchbasekit',
    license = 'LICENSE.txt',
    description = 'A wrapper around CouchBase Python driver for document validation and more.',
    keywords = ','.join(['couchbase', 'couchdb', 'nosql', 'validation']),
    long_description = open('README.rst').read(),
    install_requires = [
        'couchbase',
        'jsonpickle',
        'python-dateutil',
        #'py-bcrypt', # optional for couchbasekit.fields.PasswordField
    ],
)

