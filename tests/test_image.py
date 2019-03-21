from __future__ import unicode_literals

import os

import png
import pytest

import properties
from lfview.resources import files


def test_empty_init():
    img = files.Image()
    with pytest.raises(properties.ValidationError):
        img.validate()


def test_image_init():
    img = files.Image(content_length=100)
    assert img.validate()
    assert img.content_type == 'image/png'
    assert img.content_length == 100


def test_actual_image():
    dirname, _ = os.path.split(os.path.abspath(__file__))
    png_file = os.path.sep.join(dirname.split(os.path.sep) + ['temp.png'])
    s = ['110010010011', '101011010100', '110010110101', '100010010011']
    s = [[int(v) for v in val] for val in s]
    f = open(png_file, 'wb')
    w = png.Writer(len(s[0]), len(s), greyscale=True, bitdepth=16)
    w.write(f, s)
    f.close()

    img = files.Image(png_file)
    assert img.image is img._image
    assert img.content_type == 'image/png'
    assert img.content_length == 88
    assert img.validate()

    del img.image
    assert img.validate()

    with open(png_file, 'rb') as fid:
        img = files.Image(fid)
        img.validate()

    with pytest.raises(ValueError):
        img = files.Image(5)

    os.remove(png_file)


def test_image_serialize():
    img = files.Image(content_length=10)
    img.validate()
    serial_img = img.serialize()
    assert serial_img == {
        '__class__': 'Image',
        'content_length': 10,
        'content_type': 'image/png',
    }


def test_types():
    assert files.Image.BASE_TYPE == 'files'
    assert files.Image.SUB_TYPE == 'image'


def test_thumbnail_pointer():
    with pytest.raises(properties.ValidationError):
        files.Thumbnail.validate_uid('files/image/abc123')
    assert files.Thumbnail.validate_uid('base/subtype/abc123/thumbnail')


if __name__ == '__main__':
    pytest.main()
