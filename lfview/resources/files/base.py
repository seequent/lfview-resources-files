"""Base classes to implement UID validation and shared file metadata"""
import re
from collections import OrderedDict

import properties

UID_REGEX = r'[a-z]{1}[a-z0-9]{0,31}'


class classproperty(object):  #pylint: disable=invalid-name
    """Class decorator to enable @property behavior on classes"""

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls=None):
        if cls is None:
            cls = type(obj)
        return self.func(cls)


class _BaseUIDModel(properties.HasProperties):
    """Base class with UID property and validation methods

    This class is used to enable pointer validation when used with
    :class:`properties.extras.Pointer`. When a :code:`_BaseUIDModel`
    subclass is specified as the instance class on a Pointer, the
    value assigned to that pointer can either be an instance of
    this class OR a validated UID value.

    For LF View API resources, the UID must end with slash-delimited
    type information (defined by :code:`BASE_TYPE` and :code:`SUB_TYPE`)
    and random identifier. Most commonly, these UIDs will
    be resource URLs; for example,

    https://example.com/api/v1/elements/surface/d7td9elq5k9ewdu557hk

    is a valid UID with base type 'elements' and subtype 'surface.'
    An equally valid UID is

    elements/surface/d7td9elq5k9ewdu557hk

    but without the full URL, the value may not be recognized by
    the LF View REST API.
    """

    _REGISTRY = OrderedDict()

    uid = properties.String(
        'Unique object identifier',
        required=False,
    )

    @classproperty
    def pointer_regex(cls):
        """Pointer regular expression generated on each class

        This regular expression requires strings to end in
        <base_type>/<sub_type>/<random_id> or simply
        <base_type>/<random_id> if no sub-type is defined
        """

        base = getattr(cls, 'BASE_TYPE', None)
        sub = getattr(cls, 'SUB_TYPE', None)
        if base is None:
            base_sub_regex = r'([a-zA-Z0-9]+/){1,2}'
            path_re = r'{}{}$'.format(base_sub_regex, UID_REGEX)
        elif sub is None and cls.__name__[0] != '_':
            path_re = r'{}/{}$'.format(base, UID_REGEX)
        else:
            sub_regex = sub or r'[a-zA-Z0-9]+'
            path_re = r'{}/{}/{}$'.format(base, sub_regex, UID_REGEX)
        return re.compile(path_re)

    @classmethod
    def validate_uid(cls, value):
        """Hook called on Pointer validation to verify regex

        When a :code:`_BaseUIDModel` is specified as the
        instance class on a :class:`properties.extras.Pointer`, a
        string pointer can be assigned as the value (in place of
        an instance of the class) if it passes this validation.
        """
        if not cls.pointer_regex.search(value):
            raise properties.ValidationError(
                'Pointer must contain string matching {}'.format(
                    cls.pointer_regex.pattern
                )
            )
        return True


class _BaseFile(_BaseUIDModel):
    """Base class for File resources

    The properties defined here apply to any generic file. Note that
    this file resource does not actually store the binary file itself,
    only its metadata.
    """

    BASE_TYPE = 'files'

    _REGISTRY = OrderedDict()

    content_type = properties.String('Content type of the file')
    content_length = properties.Integer(
        'Content length of the file',
        min=0,
    )
