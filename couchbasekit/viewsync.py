#! /usr/bin/env python
"""
couchbasekit.viewsync
~~~~~~~~~~~~~~~~~~~~~

:website: http://github.com/kirpit/couchbasekit
:copyright: Copyright 2012, Roy Enjoy <kirpit *at* gmail.com>, see AUTHORS.txt.
:license: MIT, see LICENSE.txt for details.
"""
import os
import shutil
from couchbasekit import Document

class ViewSync(object):
    """This is an experimental helper to download, upload and synchronize your
    couchbase views (both map and reduce JavaScript functions) in an organized
    way.

    Unfortunately, it's quite impossible to synchronize these views since
    couchbase doesn't provide any information about when a specific view was
    created and modified. So we can't know if previously downloaded .js file or
    the current one at couchbase server should be replaced..

    This class also works in a singleton pattern so all its methods are
    ``@classmethod`` that you don't need to create an instance at all.

    In order to use this tool, you have to set its VIEW_PATH attribute to the
    directory wherever you want to keep downloaded JavaScript files. It is
    better to keep that directory under version controlled folder, as they can
    also become your view backups.
    """
    VIEWS_PATH = None
    _documents = set()

    @classmethod
    def register_document(cls, document):
        """Registers a model document within the synchronizer::

            from example.samples.book import Book
            ViewSync.register_document(Book)

        Finally, you should also set your
        :class:`couchbasekit.document.Document`'s ``__view_name__`` attribute
        to the design document name of your view, i.e. ``'dev_books'``

        :param document: The model document class to be registered.
        :type document: :class:`couchbasekit.document.Document`
        """
        if not issubclass(document, Document):
            raise TypeError('Class must be a couchbasekit "Document" subclass.')
        cls._documents.add(document)

    @classmethod
    def download(cls):
        """Downloads all the views from server for the registered model
        documents into the defined :attr:`VIEW_PATHS` directory.
        """
        if not isinstance(cls.VIEWS_PATH, basestring):
            raise RuntimeError('ViewSync.VIEWS_PATH must be set')
        if not os.path.isdir(cls.VIEWS_PATH):
            raise RuntimeError(
                'Directory must created before downloading; "%s"'
                % cls.VIEWS_PATH
            )
        os.chdir(cls.VIEWS_PATH)
        # remove everything first
        for item in os.listdir(cls.VIEWS_PATH):
            shutil.rmtree(item, ignore_errors=True)
        # iterate documents
        for doc in cls._documents:
            design_doc = doc().view()
            if design_doc is None:
                continue
            os.mkdir(design_doc.name)
            # iterate viewtypes (i.e. spatial and views)
            for view_type, views in design_doc.ddoc.iteritems():
                save_dir = '%s/%s' % (design_doc.name, view_type)
                os.mkdir(save_dir)
                for name, view in views.iteritems():
                    if 'map' in view:
                        map_file = '%s/%s-map.js' % (save_dir, name)
                        with open(map_file, 'w') as mapf:
                            mapf.write(view['map'])
                    if 'reduce' in view:
                        reduce_file = '%s/%s-reduce.js' % (save_dir, name)
                        with open(reduce_file, 'w') as reducef:
                            reducef.write(view['reduce'])
        pass

    @classmethod
    def upload(cls):
        """Not implemented yet."""
        raise NotImplementedError()

    @classmethod
    def sync(cls):
        """Not implemented yet."""
        raise NotImplementedError()
