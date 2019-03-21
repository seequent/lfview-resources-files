#!/usr/bin/env python

from collections import OrderedDict
from importlib import import_module
from jinja2 import Environment, FileSystemLoader
import properties

try:
    from properties_inheritance_graph import make_graph
    import nxpd
except ImportError:
    print('Graphs will not be rendered in docs')

# ----------------------------------------------------------------------
# You may specify alternative registry or registries defined within
# your package. Only resources in the registry will be documented.

# Ensure you import the module so classes are loaded to the registry
from lfview.resources import files

REGISTRIES = [
    files.base._BaseUIDModel._REGISTRY,
    files.base._BaseFile._REGISTRY,
]

# You may also specify an alternative base node for inheritance graphs
# in the docs.
GRAPH_BASE = properties.HasProperties
# ----------------------------------------------------------------------

# Organize module registries
modules = OrderedDict()
for registry in REGISTRIES:
    for resource in registry.values():
        if resource.__module__.startswith('properties'):
            continue
        if resource.__module__ not in modules:
            modules.update(
                {
                    resource.__module__: OrderedDict(
                        [(resource.__name__, resource)]
                    )
                }
            )
        else:
            modules[resource.__module__].update({resource.__name__: resource})

# Write index file
env = Environment(loader=FileSystemLoader('docs/templates'))
with open('docs/index.rst', 'w') as index:
    resources = {}
    for registry in REGISTRIES:
        resources.update(registry)
    try:
        graph_filename = 'images/index.png'
        graph, graph_registry = make_graph(
            registry=resources,
            ext_base=GRAPH_BASE,
        )
        nxpd.draw(
            graph,
            filename='docs/{}'.format(graph_filename),
            show=False,
        )
    except:
        print('Graphs will not be rendered in docs')
        graph_filename = None
        graph_registry = None
    template = env.get_template('index.tpl')
    index.write(template.render(
        modules=modules,
        graph=graph_filename,
    ))

# Write module files
for module in modules:
    resources = modules[module]
    try:
        if GRAPH_BASE.__name__ in resources:
            base = properties.HasProperties
        else:
            base = GRAPH_BASE
        graph_filename = 'images/{}.png'.format(module.replace('.', '_'))
        graph, graph_registry = make_graph(
            registry=resources,
            ext_base=base,
            expand_props='_props',
            only_new_props=False,
        )
        nxpd.draw(
            graph,
            filename='docs/{}'.format(graph_filename),
            show=False,
        )
    except:
        print('Graphs will not be rendered in docs')
        graph_filename = None
        graph_registry = None
    filename = 'docs/content/{}.rst'.format(module.replace('.', '_'))
    with open(filename, 'w') as doc:
        template = env.get_template('module.tpl')
        doc.write(
            template.render(
                module=module,
                module_doc=import_module(module).__doc__ or '',
                resources=modules[module],
                graph='../{}'.format(graph_filename)
                if graph_filename else None,
                registry=graph_registry,
            )
        )
