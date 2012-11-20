#! /usr/bin/env python
from distutils.core import setup

setup(
    name = 'couchbasekit',
    version = '0.1.0',
    author = 'Roy Enjoy',
    author_email = 'kirpit@gmail.com',
    packages = ['couchbasekit', ],
    url = 'https://github.com/kirpit/couchbasekit',
    license = 'LICENSE.txt',
    description = 'A wrapper around couchbase driver for document validation and more.',
    long_description = open('README.txt').read(),
    install_requires = [
        'couchbase>=0.8.1',
        'jsonpickle>=0.4.0',
        'python-dateutil>=2.1',
        #'py-bcrypt>=0.2', # (optional for couchbasekit.fields.PasswordField)
    ],
)