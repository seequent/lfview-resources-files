"""File and Array resources for LF View API Python client"""
from . import base, files
from .files import Array, Image, Thumbnail

FILES_REGISTRY = base._BaseFile._REGISTRY

__version__ = '0.0.2'
