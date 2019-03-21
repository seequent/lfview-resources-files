.. _resources_files:

.. include:: ../README.rst

{%- if graph %}
.. image:: {{ graph }}
{%- endif %}

.. toctree::
   :maxdepth: 1
   :caption: Contents:
   {% for module in modules %}
   content/{{ '_'.join(module.split('.'))}}
   {%- endfor %}

* :ref:`genindex`
