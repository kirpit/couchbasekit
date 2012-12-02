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
        self.structure.update(doc_type=unicode)
        seq = seq if isinstance(seq, dict) else {}
        super(SchemaDocument, self).__init__(seq, **kwargs)

    def _decode_dict(self, structure, mapping):
        for skey, svalue in structure.iteritems():
            map_keys = mapping.keys()
            # this is a type:type structure
            if isinstance(skey, type) and \
               any([not isinstance(k, skey) for k in map_keys]):
                new_keys = [self._decode_item(skey, k) for k in map_keys]
                new_values = [self._decode_item(svalue, v) for v in mapping.values()]
                return dict(zip(new_keys, new_values))
            # item is not within the mapping
            elif skey not in mapping:
                continue
            # decode only mapping value
            else:
                mapping[skey] = self._decode_item(svalue, mapping.get(skey))
        return mapping


    def _decode_item(self, stype, value):
        new_value = value
        safe_types = (bool, int, long, float, unicode, basestring, list, dict)
        # newly created or safe type
        if self.is_new_record or stype in safe_types:
            return value
        # fix datetime
        elif stype is datetime.datetime and \
             not isinstance(value, datetime.datetime):
            # see: http://bugs.python.org/issue15873
            # see: http://bugs.python.org/issue6641
            new_value = parse(value)
        # fix date
        elif stype is datetime.date and not isinstance(value, datetime.date):
            new_value = parse(value).date()
        # fix time
        elif stype is datetime.time and not isinstance(value, datetime.time):
            # see: http://bugs.python.org/issue15873
            # see: http://bugs.python.org/issue6641
            new_value = parse(value).timetz()
        # fix CustomField
        elif isinstance(stype, type) and issubclass(stype, CustomField) and \
             not isinstance(value, stype):
            new_value = stype(value)
        # fix document relation
        elif isinstance(stype, type) and issubclass(stype, SchemaDocument) and \
             not isinstance(value, stype):
            if getattr(stype, '__key_field__') is not None:
                doc_type, key = value.split('_', 1)
                new_value = stype(key)
            else:
                new_value = stype(value)
        # fix python list [instances]
        elif isinstance(stype, list) and isinstance(value, list) and \
             len(stype)==1 and any([not isinstance(v, stype[0]) for v in value]):
            new_value = [self._decode_item(stype[0], v) for v in value]
        # the type is a dict instance, decode recursively
        elif isinstance(stype, dict) and isinstance(value, dict):
            new_value = self._decode_dict(stype, value)

        return new_value

    def __getitem__(self, item):
        # usual error if key not found
        if item not in self:
            raise KeyError(item)
        value = self.get(item)
        # TODO: schemaless should be converted as well
        # schemaless or out of structure
        if item not in self.structure:
            return value
        # make sure the accessed value respects our structure
        try:
            new_value = self._decode_item(self.structure[item], value)
        except ValueError as why:
            raise ValueError(
                "Incorrect value for the field %s, '%s' was given." % (item, value)
            )
        # cache it
        if new_value is not value:
            self[item] = new_value
        return new_value

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

        Returns the instance itself (a.k.a. chaining) so you can do:

        >>> book = Book('hhg2g').load()

        :returns: The Document instance itself on which was called from.
        """
        [getattr(self, k) for k in self.iterkeys()]
        return self

    def _validate(self, structure, mapping, root=False):
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
                    for k, list_val in mapping.iteritems():
                        if not all([isinstance(v, svalue[0]) for v in list_val]):
                            raise self.StructureError(k, svalue, list_val)
                # structure value is an ALLOWED_TYPE, CustomField or Document
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
        return self._validate(self.structure, self, root=True)