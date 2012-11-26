#! /usr/bin/env python
"""
couchbasekit.schema
~~~~~~~~~~~~~~~~~~~

:website: http://github.com/kirpit/couchbasekit
:copyright: Copyright 2012, Roy Enjoy <kirpit *at* gmail.com>, see AUTHORS.txt.
:license: MIT, see LICENSE.txt for details.
"""
from abc import ABCMeta
import datetime
from dateutil.parser import parse
from couchbasekit.fields import CustomField
from couchbasekit.errors import StructureError


ALLOWED_TYPES = (
    bool,
    int,
    long,
    float,
    unicode,
    basestring,
    list,
    dict,
    datetime.datetime,
    datetime.date,
    datetime.time,
)

class SchemaDocument(dict):
    """Schema document class that handles validations and restoring raw
    couchbase documents into Python values as defined in model documents.

    Under normal circumstances, you don't use or inherit this class at all,
    because it is only being used by :class:`couchbasekit.document.Document`
    class.

    :param seq: Document data to store at initialization, defaults to None.
    :type seq: dict
    :raises: :exc:`couchbasekit.errors.StructureError` if the minimum
        structure requirements wasn't satisfied.
    """
    __metaclass__ = ABCMeta
    StructureError = StructureError
    __bucket_name__ = None
    __key_field__ = None
    doc_type = None
    structure = dict()
    default_values = dict()
    required_fields = tuple()
    is_new_record = True

    def __init__(self, seq=None, **kwargs):
        # check the required attributes
        if not isinstance(self.__bucket_name__, str) or \
           not isinstance(self.doc_type, str) or \
           not isinstance(self.structure, dict):
            raise self.StructureError(msg="Structure is not properly "
                                          "set for %s." % type(self).__name__)
        # check self.__key_field__ if correct
        if self.__key_field__ and self.__key_field__ not in self.structure:
            raise self.StructureError(
                msg="Document key field must be within the "
                    "structure, '%s' is given." % str(self.__key_field__)
            )
        # insert doc_type into the structure
        self.structure.update(doc_type=basestring)
        seq = seq if isinstance(seq, dict) else {}
        super(SchemaDocument, self).__init__(seq, **kwargs)

    def _convert_dict_item(self, structure, mapping):
        """Converts the given mapping against the given structure, recursively.
        This is quite code duplicate for :meth:`__getitem__` function.

        :type structure: dict
        :type mapping: dict
        :returns: Converted dictionary.
        :rtype: dict
        """
        new_map = dict()
        for skey, svalue in structure.iteritems():
            # this is a type:type structure
            if isinstance(skey, type) and isinstance(svalue, type):
                mkeys, mvalues = mapping.keys(), mapping.values()
                new_keys, new_values = mkeys, mvalues
                # convert keys if needed
                if skey not in (unicode, datetime.datetime,
                                datetime.date, datetime.time) and \
                   all((not isinstance(k, skey) for k in mkeys)):
                    new_keys = list()
                    map(lambda k: new_keys.append(k), [skey(k) for k in mkeys])
                elif skey is datetime.datetime and \
                     all((not isinstance(k, skey) for k in mkeys)):
                    new_keys = list()
                    map(lambda k: new_keys.append(k), [parse(k) for k in mkeys])
                elif skey is datetime.date and \
                     all((not isinstance(k, skey) for k in mkeys)):
                    new_keys = list()
                    map(lambda k: new_keys.append(k), [parse(k).date()
                                                       for k in mkeys])
                elif skey is datetime.time and \
                     all((not isinstance(k, skey) for k in mkeys)):
                    new_keys = list()
                    map(lambda k: new_keys.append(k), [parse(k).timetz()
                                                       for k in mkeys])
                # convert values if needed
                if svalue not in (unicode, datetime.datetime,
                                  datetime.date, datetime.time) and \
                   all((not isinstance(v, svalue) for v in mvalues)):
                    new_values = list()
                    map(lambda v: new_values.append(v), [svalue(v) for v in mvalues])
                elif svalue is datetime.datetime and \
                     all((not isinstance(v, svalue) for v in mvalues)):
                    new_values = list()
                    map(lambda v: new_values.append(v), [parse(v) for v in mvalues])
                elif svalue is datetime.date and \
                     all((not isinstance(v, svalue) for v in mvalues)):
                    new_values = list()
                    map(lambda v: new_values.append(v), [parse(v).date()
                                                         for v in mvalues])
                elif svalue is datetime.time and \
                     all((not isinstance(v, svalue) for v in mvalues)):
                    new_values = list()
                    map(lambda v: new_values.append(v), [parse(v).timetz()
                                                         for v in mvalues])
                # create the new_map
                if new_keys is not mkeys or new_values is not mvalues:
                    map(lambda (k,v): new_map.setdefault(k,v),
                        zip(new_keys, new_values))
                else:
                    new_map = mapping
                continue
            elif skey not in mapping:
                continue
            map_value = mapping[skey]
            # datetime
            if isinstance(svalue, datetime.datetime) and \
                 isinstance(map_value, unicode):
                # see: http://bugs.python.org/issue15873
                # see: http://bugs.python.org/issue6641
                new_value = parse(map_value)
                new_map[skey] = new_value
                continue
            # date
            elif isinstance(svalue, datetime.date) and \
                 isinstance(map_value, unicode):
                new_value = parse(map_value).date()
                new_map[skey] = new_value
                return new_value
            # time
            elif isinstance(svalue, datetime.time) and \
                 isinstance(map_value, unicode):
                # see: http://bugs.python.org/issue15873
                # see: http://bugs.python.org/issue6641
                new_value = parse(map_value).timetz()
                new_map[skey] = new_value
                return new_value
            # this is a tuple of Document options
            elif isinstance(svalue, tuple) and isinstance(map_value, unicode):
                # do smart guessing
                doc_type, key = map_value.split('_', 1)
                for sv in svalue:
                    if sv.doc_type!=doc_type:
                        continue
                        # found
                    new_value = sv(key)
                    new_map[skey] = new_value
                    break
                continue
            # this is a sub dictionary (recursive)
            elif isinstance(svalue, dict) and isinstance(map_value, dict):
                new_map[skey] = self._convert_dict_item(svalue, map_value)
                continue
            # this is an ordinary mapping dict, original type is fine
            new_map[skey] = svalue(map_value)
        return new_map

    def __getitem__(self, item, raw=False):
        """Converts the requested dictionary item into Python value if it was
        newly fetched from couchbase server and caches it.

        :type item: str
        :type raw: bool
        :returns: Mixed; converted Python value that is defined in main document
            structure.
        :raises KeyError:
        """
        # usual error if key not found
        if item not in self:
            raise KeyError(item)
        dict_value = super(SchemaDocument, self).__getitem__(item)
        # newly created, field not in structure or the exact value was needed
        if self.is_new_record is True or item not in self.structure or raw is True:
            return dict_value
        # HERE, THE THING STARTS
        svalue = self.structure[item]
        # no need to modify the item if one of these:
        ok_types = (bool, int, long, float, unicode, basestring, list, dict)
        if svalue in ok_types and isinstance(dict_value, ok_types):
            return dict_value
        # fix datetime string
        elif svalue is datetime.datetime and \
             not isinstance(dict_value, datetime.datetime):
            # see: http://bugs.python.org/issue15873
            # see: http://bugs.python.org/issue6641
            new_value = parse(dict_value)
            self[item] = new_value
            return new_value
        # fix date string
        elif svalue is datetime.date and \
             not isinstance(dict_value, datetime.date):
            new_value = parse(dict_value).date()
            self[item] = new_value
            return new_value
        # fix time string
        elif svalue is datetime.time and \
             not isinstance(dict_value, datetime.time):
            # see: http://bugs.python.org/issue15873
            # see: http://bugs.python.org/issue6641
            new_value = parse(dict_value).timetz()
            self[item] = new_value
            return new_value
        # fix CustomField
        elif isinstance(dict_value, unicode) and \
             isinstance(svalue, type) and \
             issubclass(svalue, CustomField):
            new_value = svalue(dict_value)
            self[item] = new_value
            return new_value
        # fix Document
        elif isinstance(dict_value, unicode) and \
             isinstance(svalue, type) and \
             issubclass(svalue, SchemaDocument):
            doc_type, key = dict_value.split('_', 1)
            new_value = svalue(key)
            self[item] = new_value
            return new_value
        # fix python list elements
        elif isinstance(dict_value, list) and \
             isinstance(svalue, list) and \
             all((not isinstance(dv, svalue[0]) for dv in dict_value)):
            new_value = list([type(svalue[0])(dv) for dv in dict_value])
            self[item] = new_value
            return new_value
        # the type is a tuple, value must be an either Document instance in it
        elif isinstance(svalue, tuple) and isinstance(dict_value, unicode):
            # do smart guessing
            doc_type, key = dict_value.split('_', 1)
            for sv in svalue:
                if sv.doc_type!=doc_type:
                    continue
                # found
                new_value = sv(key)
                self[item] = new_value
                return new_value
        # the type is dict instance, convert recursively
        elif isinstance(svalue, dict) and isinstance(dict_value, dict):
            new_value = self._convert_dict_item(svalue, dict_value)
            self[item] = new_value
            return new_value
        # perhaps already converted
        return dict_value

    def load(self):
        """Helper function to pre-load all the raw document values into Python
        ones, custom types and/or other document relations as they are defined in
        model document.

        This is only useful when you need the instance to convert all its raw
        values into Python types, custom fields and/or other document relations
        *before* sending that object to somewhere else. For example, sending a
        ``User`` document to your framework's ``login(request, user)`` function.

        If your code is the only one accessing its values such as;
        ``user.posts``, you don't have to ``.load()`` it as they're
        auto-converted and cached on-demand.

        Returns the instance itself so you can use it like:

        >>> book = Book('hhg2g').load()

        :returns: The Document instance itself on which was called from.
        """
        [self[k] for k in self.iterkeys()]
        return self

    def _validate(self, structure, mapping, root=False):
        """Recursive validation for the given structure against the given
        mapping dictionary.

        :param structure: The structure (or a sub-structure) to validate.
        :type structure: dict
        :param mapping: The values dictionary to be checked against.
        :type mapping: dict
        :param root: True if it was first called from :meth:`validate`.
        :type root: bool
        :returns: Always True, or raises
            :exc:`couchbasekit.errors.StructureError` exception.
        :raises: :exc:`couchbasekit.errors.StructureError` if any validation
            problem occurs.
        """
        # if root, check the required fields first
        if root is True:
            for rfield in self.required_fields:
                if (rfield not in mapping and rfield not in self.default_values) or \
                   (rfield in mapping and mapping[rfield] is None):
                    raise self.StructureError(
                        msg="Required field for '%s' is missing." % rfield
                    )
        # check the dict structure
        for skey, svalue in structure.iteritems():
            # STRUCTURE KEY (FIELD) IS A TYPE
            # i.e. {unicode: int}
            if skey in ALLOWED_TYPES:
                # if it's a type pair, must be the only item
                if not len(structure)==1:
                    raise self.StructureError(
                        msg="Type pairs must be the only item in a dictionary, "
                            "there are %d." % len(structure)
                    )
                # key instance must be hash()'able at this point
                # but we can't catch'em all as every instance is
                # not simply created by skey(), unfortunately
                try: hash(skey())
                except TypeError as why:
                    if 'unhashable type' in why.message:
                        raise self.StructureError(
                            msg="Structure keys must be hashable, "
                                "'%s' given." % skey.__name__
                        )
                    # yes, we ignore the rest of TypeErrors
                    pass
                # check all the key types in the dict
                for k in mapping.iterkeys():
                    if not isinstance(k, skey):
                        raise self.StructureError(k, skey, k)
                # structure value is a list [instance]
                if isinstance(svalue, list):
                    # and must have only 1 item
                    if not len(svalue)==1:
                        raise self.StructureError(
                            msg="List values must have only 1 item, "
                                "'%s' had %d." % (skey, len(svalue))
                        )
                    elif not (isinstance(svalue[0], type) and
                              (svalue[0] in ALLOWED_TYPES or
                               issubclass(svalue[0], (CustomField, SchemaDocument)))):
                        raise self.StructureError(
                            msg="A list has an invalid option in its "
                                "structure, '%s' is given." % svalue[0]
                        )
                    for k, v in mapping.iteritems():
                        if not isinstance(v, svalue[0]):
                            raise self.StructureError(k, svalue[0], v)
                # structure value is a tuple, all must be Document instances
                elif isinstance(svalue, tuple):
                    invalid = next([sv for sv in svalue
                                    if not (isinstance(sv, type) and
                                            issubclass(sv, SchemaDocument))],
                                    None)
                    if invalid is not None:
                        raise self.StructureError(
                            msg="A tuple defined field must have only model "
                                "documents as options, '%s' is given." % invalid
                        )
                    for k, v in mapping.iteritems():
                        if not isinstance(v, svalue): # within the tuple
                            raise self.StructureError(k, svalue, v)
                # structure value is an ALLOWED_TYPE or CustomField
                elif svalue in ALLOWED_TYPES or \
                     (isinstance(svalue, type) and
                      issubclass(svalue, (CustomField, SchemaDocument))):
                    for k, v in mapping.iteritems():
                        if not isinstance(v, svalue):
                            raise self.StructureError(k, svalue, v)
                continue
            # STRUCTURE KEY (FIELD) IS A STRING
            # field not set or None anyway
            if skey not in mapping or mapping[skey] is None:
                continue
            # is it in allowed types?
            elif svalue in ALLOWED_TYPES and isinstance(mapping[skey], svalue):
                continue
            # some custom type or document relation?
            elif isinstance(svalue, type) and \
                 issubclass(svalue, (CustomField, SchemaDocument)) and \
                 isinstance(mapping[skey], svalue):
                continue
            # structure value is a list [instance]
            elif isinstance(svalue, list):
                # and must have only 1 item
                if not len(svalue)==1:
                    raise self.StructureError(
                        msg="List values must have only 1 item, "
                            "'%s' had %d." % (skey, len(svalue))
                    )
                if isinstance(svalue[0], type) and \
                     (svalue[0] in ALLOWED_TYPES or
                      issubclass(svalue[0], (CustomField, SchemaDocument))) and \
                     isinstance(mapping[skey], list) and \
                     all([isinstance(v, svalue[0]) for v in mapping[skey]]):
                    continue
            # structure value is a tuple, all must be Document instances
            elif isinstance(svalue, tuple):
                if all([isinstance(sv, type) and
                        issubclass(sv, SchemaDocument) for sv in svalue]) and \
                   isinstance(mapping[skey], svalue): # within the tuple
                    continue
            # it's a dictionary instance, check recursively
            elif isinstance(svalue, dict) and \
                 isinstance(mapping[skey], dict) and \
                 len(mapping[skey]):
                if self._validate(svalue, mapping[skey]):
                    continue
            # houston, we got a problem!
            raise self.StructureError(skey, svalue, mapping[skey])
        return True

    def validate(self):
        """Validates the document object with current values, always called
        within :meth:`couchbasekit.document.Document.save` method.

        :returns: Always True, or raises
            :exc:`couchbasekit.errors.StructureError` exception.
        :raises: :exc:`couchbasekit.errors.StructureError` if
            any validation problem occurs.
        """
        # __key_field__ value must be provided if defined
        if self.__key_field__ and self.__key_field__ not in self:
            raise self.StructureError(msg="Key field '%s' is defined "
                                          "but not provided." % self.__key_field__)
        self.load()
        return self._validate(self.structure, self, root=True)