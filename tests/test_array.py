from __future__ import unicode_literals

import numpy as np
import pytest

import properties
import properties.extras
from lfview.resources import files


def test_empty_init():
    arr = files.Array()
    with pytest.raises(properties.ValidationError):
        arr.validate()


def test_object_without_array():
    arr = files.Array()
    arr.content_length = 64
    arr.dtype = 'Int8Array'
    arr.shape = [64]
    assert arr.validate()


@pytest.mark.parametrize(
    'input_arr', [
        [1, 2, 3],
        (1, 2, 3),
        np.array([1, 2, 3]),
    ]
)
def test_array_init(input_arr):
    arr = files.Array(input_arr)
    assert arr.validate()
    assert isinstance(arr.array, np.ndarray)
    assert np.array_equal(arr.array, np.array([1, 2, 3]))
    assert arr.dtype.startswith('Int')
    assert arr.shape == [3]
    assert arr.content_type == 'application/octet-stream'
    assert arr.content_length == np.dtype(arr.array.dtype).itemsize * 3
    assert arr.is_1d()


@pytest.mark.parametrize(
    'input_arr', [
        ['a', 'b', 'c'],
        ('a', 'b', 'c'),
        np.array(['a', 'b', 'c']),
    ]
)
def test_array_assignment(input_arr):
    arr = files.Array()
    with pytest.raises(ValueError):
        arr.array = input_arr


@pytest.mark.parametrize(
    'input_arr', [
        [[1., 2], [3, 4]],
        ((1., 2), (3, 4)),
        np.array([[1., 2], [3, 4]]),
    ]
)
def test_hasarray_assignment(input_arr):
    class HasArray(properties.extras.HasUID):
        arr = properties.extras.Pointer('array', files.Array)

    has_array = HasArray()
    has_array.arr = input_arr
    assert has_array.validate()
    assert isinstance(has_array.arr.array, np.ndarray)
    assert np.allclose(has_array.arr.array, np.array([[1., 2], [3, 4]]))
    assert has_array.arr.dtype.startswith('Float')
    assert has_array.arr.shape == [2, 2]
    assert has_array.arr.content_type == 'application/octet-stream'
    dtype = np.dtype(has_array.arr.array.dtype)
    assert has_array.arr.content_length == dtype.itemsize * 4
    assert not has_array.arr.is_1d()


def test_array_serialize():
    arr = files.Array([[1]])
    arr.validate()
    serial_arr = arr.serialize()
    assert serial_arr == {
        '__class__': 'Array',
        'content_length': np.dtype(arr.array.dtype).itemsize,
        'content_type': 'application/octet-stream',
        'dtype': 'Int32Array',
        'shape': [1, 1],
    }


def test_unsupported_array():
    with pytest.raises(ValueError):
        files.Array('bad array')
    int64array = np.array([100000000000])
    with pytest.raises(ValueError):
        files.Array(int64array)


def test_bad_input():
    with pytest.raises(properties.ValidationError):
        files.Array(dtype='bad')
    arr = files.Array(dtype='Int32Array', shape=[1])
    with pytest.raises(properties.ValidationError):
        arr.content_length = 100


@pytest.mark.parametrize(
    ('input', 'is_1d'),
    [(None, False), ([1, 2, 3], True), ([[1, 2], [3, 4]], False)]
)
def test_is_1d(input, is_1d):
    assert files.Array(input).is_1d() == is_1d


def test_types():
    assert files.Array.BASE_TYPE == 'files'
    assert files.Array.SUB_TYPE == 'array'


if __name__ == '__main__':
    pytest.main()
