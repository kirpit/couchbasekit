#! /usr/bin/env python
from distutils.core import setup
from couchbasekit import __version__


setup(
    name = 'couchbasekit',
    version = __version__,
    author = 'Roy Enjoy',
    author_email = 'kirpit@gmail.com',
    packages = ['couchbasekit'],
    url = 'https://github.com/kirpit/couchbasekit',
    license = 'LICENSE.txt',
    description = 'A wrapper around couchbase driver for document validation and more.',
    long_description = open('README.rst').read(),
    install_requires = [
        'couchbase>=0.8.1',
        'jsonpickle',
        'python-dateutil',
        #'py-bcrypt', # optional for couchbasekit.fields.PasswordField
    ],
)