LFView Resources - Files
************************************************************************

.. image:: https://img.shields.io/pypi/v/lfview-resources-files.svg
    :target: https://pypi.org/project/lfview-resources-files
.. image:: https://readthedocs.org/projects/lfview-resources-files/badge/
    :target: http://lfview-resources-files.readthedocs.io/en/latest/
.. image:: https://travis-ci.com/seequent/lfview-resources-files.svg?branch=master
    :target: https://travis-ci.com/seequent/lfview-resources-files
.. image:: https://codecov.io/gh/seequent/lfview-resources-files/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/seequent/lfview-resources-files
.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://github.com/seequent/lfview-resources-files/blob/master/LICENSE

.. warning::

    The LF View API and all associated Python client libraries are in
    **pre-release**. They are subject to change at any time, and
    backwards compatibility is not guaranteed.

What is lfview-resources-files?
---------------------------------
This library defines fundamental file resources in the
`LF View <https://lfview.com>`_ API, such as images and arrays.

Scope
-----
This library simply includes declarative definitions of file resources.
It is built on `properties <https://propertiespy.readthedocs.io/en/latest/>`_ to
provide type-checking, validation, documentation, and serialization.
Very likely, these file resources will be used in conjunction with
the `LF View API Python client <https://lfview.readthedocs.io/en/latest/>`_.

Installation
------------

You may install this library using
`pip <https://pip.pypa.io/en/stable/installing/>`_  with

.. code::

    pip install lfview-resources-files

or from `Github <https://github.com/seequent/lfview-resources-files>`_

.. code::

    git clone https://github.com/seequent/lfview-resources-files.git
    cd lfview-resources-files
    pip install -e .

You may also just install the LF View API Python client with

.. code::

    pip install lfview-api-client

After installing, you may access these resources with

.. code:: python

    from lfview.resources import files

    arr = files.Array([1., 2., 3., 4., 5.])
    img = files.Image('photo.png')
