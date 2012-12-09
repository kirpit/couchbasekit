#! /usr/bin/env python
"""
couchbasekit.document
~~~~~~~~~~~~~~~~~~~~~

:website: http://github.com/kirpit/couchbasekit
:copyright: Copyright 2012, Roy Enjoy <kirpit *at* gmail.com>, see AUTHORS.txt.
:license: MIT, see LICENSE.txt for details.
"""
import datetime
import hashlib
import jsonpickle
from dateutil.tz import tzutc
from couchbase.exception import MemcachedError
from couchbasekit import Connection
from couchbasekit.schema import SchemaDocument
from couchbasekit.errors import DoesNotExist
from couchbasekit.fields import CustomField

class Document(SchemaDocument):
    """Couchbase document to be inherited by user-defined model documents that
    handles everything from validation to comparison with the help of
    :class:`couchbasekit.schema.SchemaDocument` parent class.

    :param key_or_map: Either the document id to be fetched or dictionary
        to initialize the first values of a new document.
    :type key_or_map: basestring or dict
    :param get_lock: True, if the document wanted to be locked for other
        processes, defaults to False.
    :type get_lock: bool
    :param kwargs: key=value arguments to be passed to the dictionary.
    :raises: :exc:`couchbasekit.errors.StructureError` or
        :exc:`couchbasekit.errors.DoesNotExist`
    """
    DoesNotExist = DoesNotExist
    __view_name__ = None
    _bucket = None
    _hashed_key = None
    _view_design_doc = None
    _view_cache = None
    cas_value = None

    def __init__(self, key_or_map=None, get_lock=False, **kwargs):
        # check document schema first
        super(Document, self).__init__(key_or_map, **kwargs)
        # fetch document by key?
        if isinstance(key_or_map, basestring):
            if self.__key_field__:
                self[self.__key_field__] = key_or_map
            else: # must be a hashed key then
                self._hashed_key = key_or_map
            # the document must be found if a key is given
            if self._fetch_data(get_lock) is False:
                raise self.DoesNotExist(self, self.doc_id)

    def __eq__(self, other):
        if type(self) is type(other) and \
           self.cas_value==other.cas_value and \
           self.keys()==other.keys() and \
           all([self[k]==other[k] for k in self.keys()]):
            return True
        return False

    def __getattr__(self, item):
        if item in self:
            return self[item]
        elif item in self.structure:
            return None
        # raise AttributeError eventually:
        return super(Document, self).__getattribute__(item)

    def __setattr__(self, key, value):
        if key in self.structure:
            self[unicode(key)] = value
        else:
            super(Document, self).__setattr__(key, value)

    @property
    def id(self):
        """Returns the document's key field value (sort of primary key if you
        defined it in your model, which is optional), object property.

        :returns: The document key if :attr:`__key_field__` was defined, or None.
        :rtype: unicode or None
        """
        return self.get(self.__key_field__) if self.__key_field__ else None

    @property
    def doc_id(self):
        """Returns the couchbase document's id, object property.

        :returns: The document id (that is created from :attr:`doc_type` and
            :attr:`__key_field__` value, or auto-hashed document id at first
            saving).
        :rtype: unicode
        """
        if self.id:
            return '%s_%s' % (self.doc_type, self.id.lower())
        return self._hashed_key

    @property
    def bucket(self):
        """Returns the couchbase Bucket object for this instance, object property.

        :returns: See: :class:`couchbase.client.Bucket`.
        :rtype: :class:`couchbase.client.Bucket`
        """
        if self._bucket is None:
            self._bucket = Connection.bucket(self.__bucket_name__)
        return self._bucket

    def _fetch_data(self, get_lock=False):
        try:
            if get_lock is True:
                (status, self.cas_value, data) = self.bucket.getl(self.doc_id)
            else:
                (status, self.cas_value, data) = self.bucket.get(self.doc_id)
        except MemcachedError as why:
            # raise if other than "not found"
            if why.status!=1:
                raise why
        else:
            # found within couchbase
            self.is_new_record = False
            data = jsonpickle.decode(data)
            self.update(data)
        # return is_fetched in other words:
        return not self.is_new_record

    def _encode_item(self, value):
        # Document instance
        if isinstance(value, Document):
            if value.doc_id is None:
                raise self.StructureError(
                    msg="Trying to relate an unsaved "
                        "document; '%s'" % type(value).__name__
                )
            return value.doc_id
        # CustomField instance
        elif isinstance(value, CustomField):
            return unicode(value)
        # datetime types
        elif isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
            if hasattr(value, 'tzinfo') and value.tzinfo is None:
                # always timezone "aware" datetime and time
                value = value.replace(tzinfo=tzutc())
            pickler = jsonpickle.Pickler(unpicklable=False)
            return pickler.flatten(value)
        # list
        elif isinstance(value, list):
            return [self._encode_item(v) for v in value]
        # dictionary, pass it to dict encoder
        elif isinstance(value, dict):
            return self._encode_dict(value)
        # no need to encode
        return value

    def _encode_dict(self, mapping):
        data = dict()
        for key, value in mapping.iteritems():
            # None values will be stripped out
            if value is None:
                continue
            # Document instance key issue
            if isinstance(key, Document):
                # document instances are not hashable!
                # should raise an error here
                pass
            key = self._encode_item(key)
            data[key] = self._encode_item(value)
        return data

    def save(self, expiry=0):
        """Saves the current instance after validating it.

        :param expiry: Expiration in seconds for the document to be removed by
            couchbase server, defaults to 0 - will never expire.
        :type expiry: int
        :returns: couchbase document CAS value
        :rtype: int
        :raises: :exc:`couchbasekit.errors.StructureError`,
            See :meth:`couchbasekit.schema.SchemaDocument.validate`.
        """
        # set the default values first
        for key, value in self.default_values.iteritems():
            if callable(value): value = value()
            self.setdefault(key, value)
        # validate
        self[u'doc_type'] = unicode(self.doc_type)
        self.validate()
        # json safe data
        json_safe = self._encode_dict(self)
        json_data = jsonpickle.encode(json_safe, unpicklable=False)
        # still no key identifier? create one..
        if self.doc_id is None:
            self._hashed_key = hashlib.sha1(json_data).hexdigest()[0:12]
        # finally
        self.cas_value = self.bucket.set(self.doc_id, expiry, 0, json_data)[1]
        return self.cas_value

    def view(self, view=None):
        """Returns the couchbase view(s) if :attr:`__view_name__` was provided
            within model class.

        :param view: If provided returns the asked couchbase view object or
            :attr:`__view_name__` design document.
        :type view: str
        :returns: couchbase design document, couchbase view or None
        :rtype: :class:`couchbase.client.DesignDoc` or
            :class:`couchbase.client.View` or None
        """
        if self.__view_name__ is None:
            return None
        # cache the design document
        if self._view_design_doc is None:
            self._view_design_doc = self.bucket['_design/%s' % self.__view_name__]
        # return the design doc
        if view is None:
            return self._view_design_doc
        # cache the views
        if self._view_cache is None:
            self._view_cache = self._view_design_doc.views()
        return next(iter([v for v in self._view_cache if v.name==view]), None)