"""File objects that hold structured file metadata"""
from collections import OrderedDict
import re

import numpy as np
import properties
from six import string_types

from .base import _BaseFile, UID_REGEX

NUMPY_DTYPES = {
    'f': [4, 8],
    'i': [1, 2, 4],
    'u': [1, 2, 4],
}
ARRAY_DTYPES = {
    'Float32Array': ['<f4', 'float32'],
    'Float64Array': ['<f8', 'float64'],
    'Int8Array': ['<i1', 'int8'],
    'Int16Array': ['<i2', 'int16'],
    'Int32Array': ['<i4', 'int32'],
    'Uint8Array': ['<u1', 'uint8'],
    'Uint16Array': ['<u2', 'uint16'],
    'Uint32Array': ['<u4', 'uint32'],
}


class Array(_BaseFile):
    """File resource for numeric array binary storage

    In addition to file metadata properties, Array instances have
    an :code:`array` attribute. This attribute can be set
    with a numeric list or a numpy array, and doing so will
    dynamically fill in the other properties.
    """

    SUB_TYPE = 'array'

    dtype = properties.StringChoice(
        'Data type of array',
        choices=ARRAY_DTYPES,
    )
    shape = properties.List(
        'Dimensions of the array',
        properties.Integer('', min=0),
        min_length=1,
    )
    content_type = properties.StringChoice(
        'Content type of the file',
        choices=['application/octet-stream'],
        default='application/octet-stream',
    )

    @property
    def array(self):
        """Reference to underlying numpy array

        This attribute does not need to be set; however, doing so will
        set the associated metadata.
        """
        return getattr(self, '_array', None)

    @array.setter
    def array(self, value):
        if not isinstance(value, (tuple, list, np.ndarray)):
            raise ValueError('Array must be numpy array, list, or tuple')
        self._array = np.array(value)
        kind = self._array.dtype.kind
        if kind not in NUMPY_DTYPES:
            raise ValueError('Invalid kind of array: {}'.format(kind))
        sizes = NUMPY_DTYPES[kind]
        itemsize = self._array.dtype.itemsize
        for size in sizes:
            if itemsize <= size:
                itemsize = size
                break
        else:
            itemsize = sizes[-1]
        dtype = '<{}{}'.format(kind, itemsize)
        if kind == 'f':
            mask = ~np.isnan(self._array)
            close = np.allclose(
                self._array[mask],
                self._array.astype(dtype)[mask]
            )
        else:
            close = (self._array == self._array.astype(dtype)).all()
        if not close:
            raise ValueError(
                'Converting array type {} to supported type {} failed'.format(
                    self._array.dtype, dtype
                )
            )
        self._array = self._array.astype(dtype)
        self.dtype = dtype
        self.shape = list(self._array.shape)
        self.content_length = self._array.nbytes

    def __init__(self, array=None, **kwargs):
        """Array initialization includes the optional argument array

        By including this argument, assigning a numeric array to
        a :class:`properties.Instance` property will coerce the numeric
        array into an Array resource.
        """
        super(Array, self).__init__(**kwargs)
        if array is not None:
            self.array = array

    @properties.validator('content_length')
    def _validate_content_length(self, change):
        """Ensure content_length matches specified shape and dtype

        content_length may be smaller than the size expected from
        shape/dtype, if the data is compressed. However, it cannot be
        larger.
        """
        if not self.dtype or not self.shape:
            return
        length = np.dtype(ARRAY_DTYPES[self.dtype][0]).itemsize
        for dim in self.shape:
            length *= dim
        if change['value'] > length:
            raise properties.ValidationError(
                message='content_length is too large for given shape/dtype',
                reason='invalid',
                prop='content_length',
                instance=self,
            )

    def is_1d(self):
        """Helper method to indicate if array is 1D"""
        if self.shape is None:
            return False
        return all([dim == 1 for dim in self.shape[1:]])


class Image(_BaseFile):
    """File resource for image storage

    Currently, only PNG images are supported.

    In addition to file metadata properties, Image instances have
    an :code:`image` attribute. This attribute can be set to a file,
    and doing so will dynamically fill in the other properties.
    """

    SUB_TYPE = 'image'

    content_type = properties.StringChoice(
        'Content type of the file',
        choices=[
            'image/png',
        ],
        default='image/png',
    )

    @property
    def image(self):
        """Reference to underlying image data

        This attribute does not need to be set; however, doing so will
        set the associated metadata.
        """
        return getattr(self, '_image', None)

    @image.setter
    def image(self, value):
        if isinstance(value, string_types):
            self._image = open(value, 'rb')
        elif hasattr(value, 'read'):
            self._image = value
        else:
            raise ValueError('image must be PNG file')
        self._image.seek(0, 2)
        self.content_length = self._image.tell()
        self._image.seek(0, 0)

    @image.deleter
    def image(self):
        self._image.close()

    def __init__(self, image=None, **kwargs):
        """Image initialization includes the optional argument image

        By including this argument, assigning an image file to a
        :class:`properties.Instance` property will coerce the
        image into an Image resource.
        """
        super(Image, self).__init__(**kwargs)
        if image is not None:
            self.image = image


class Thumbnail(Image):
    """File resource for thumbnail storage

    The Thumbnail class is identical to the Image class except it
    validates UID pointer differently, simply looking for the 'thumbnail'
    suffix attached to another standalone resource UID.
    """

    _REGISTRY = OrderedDict()

    pointer_regex = re.compile(
        r'{type_regex}{uid_regex}/thumbnail$'.format(
            type_regex=r'([a-zA-Z0-9]+/){1,2}',
            uid_regex=UID_REGEX,
        )
    )
