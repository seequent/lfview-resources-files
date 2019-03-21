.. _{{ module.replace('.', '_') }}:

{{ module.split('.')[-1].title() }} Resources
************************************************************************
{{ module_doc }}
{% if graph %}
.. image:: {{ graph }}
{% endif %}
{% if registry %}
Doc links:
{%- for key in registry.keys() | sort %}
{%- if registry[key].__module__.startswith('properties') %}
:class:`{{ registry[key].__name__ }} <properties.{{ registry[key].__name__ }}>`
{%- else %}
:class:`{{ registry[key].__name__ }} <{{ registry[key].__module__ }}.{{ registry[key].__name__ }}>`
{%- endif %}
{%- endfor %}
{%- endif %}
{% for resource in resources %}
.. autoclass:: {{ module }}.{{ resource }}
{% endfor %}

