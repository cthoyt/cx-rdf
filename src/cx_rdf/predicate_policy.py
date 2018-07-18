# -*- coding: utf-8 -*-

"""An export schema for CX to RDF that makes generating visualizations quickly.

In this schema, nodes' relationships are directly stored as triples.

- Network has NetworkAttribute
- Network has Edge
- Edge has EdgeAttribute
- Network has Node
- Node has NodeAttribute
- Node Edge Node

This makes it possible to quickly generate networks using a SPARQL query like:

.. code-block::

    SELECT ?source_label ?relation ?target_label
    WHERE {
        ?source ?relation ?target .
        ?source a ndex:node .
        ?source RDFS:label ?source_label .
        ?target a ndex:node .
        ?target RDFS:label ?target_label .
        ?relation a ndex:edge .
    }
"""

import itertools as itt
import logging
from typing import Dict, List

import rdflib
from rdflib import BNode, Literal, RDF

from nicecxModel.cx import known_aspects
from .abstract_policy import handle_aspects
from .constants import CX
from .exporter_base import Exporter
from .typing import CxType
from .utils import iterate_aspect_fragments

__all__ = [
    'export',
]

log = logging.getLogger(__name__)


def export(cx_json: CxType) -> rdflib.Graph:
    """Convert a CX JSON object to an RDFLib :class:`rdflib.Graph`.

    This policy uses CX standards for NDEx to make more meaningful RDF.

    :param cx_json: A CX JSON object
    """
    exporter = _ConciseEdgeExporter()
    return exporter.export(cx_json)


class _ConciseEdgeExporter(Exporter):
    """A class to mediate shared state in the export function."""

    policy = CX.concise

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #: keep track of aspects by name, since they're represented by a BNode
        self.aspects = {}

    def export(self, cx_json: CxType) -> rdflib.Graph:
        """Convert a CX JSON object to an RDFLib :class:`rdflib.Graph`.

        This policy uses CX standards for NDEx to make more meaningful RDF.

        :param cx_json: A CX JSON object
        """

        for name, elements in iterate_aspect_fragments(cx_json):
            self._extend_aspect(name, elements)

        return self.graph

    def _extend_aspect(self, name: str, elements: List[Dict]):
        """Extend an aspect.

        :param str name: The name of the aspect
        :param elements:
        """
        if name == 'numberVerification':
            n = elements[0]['longNumber']
            self.graph.add((self.document, CX.has_number_verification, Literal(n)))
        elif name == 'nodes':
            self._extend_node_elements(elements)
        elif name == 'edges':
            self._extend_edge_elements(elements)
        elif name == 'metaData':
            self._extend_metadata_aspect_values(elements)
        elif name == 'nodeAttributes':
            self._extend_node_attribute_elements(elements)
        elif name == 'edgeAttributes':
            self._extend_edge_attribute_elements(elements)
        elif name == 'networkAttributes':
            self._extend_network_attribute_elements(elements)
        elif name == 'citations':
            self._extend_citation_elements(elements)
        elif name == 'edgeCitations':
            self._extend_edge_citation_elements(elements)
        elif name == 'supports':
            self._extend_support_elements(elements)
        elif name == 'edgeSupports':
            self._extend_edge_support_elements(elements)
        # elif name == '@context':
        #    self._extend_context(elements)
        elif name in known_aspects:
            log.warning('unhandled known aspect: %s', name)
            self._abstract_handle_aspect(name, elements)
            # raise ValueError(f'unhandled known aspect: {name}')
        else:
            log.warning('unhandled unknown aspect: %s', name)
            # raise ValueError(f'unhandled unknown aspect: {name}')
            self._abstract_handle_aspect(name, elements)

    def _abstract_handle_aspect(self, aspect_name, elements):
        return handle_aspects(self.graph, self.aspects, self.document, aspect_name, elements)

    def _extend_metadata_aspect_values(self, attributes):
        for attribute in attributes:
            self._add_metadata_aspect_value(attribute)

    def _add_metadata_aspect_value(self, attribute) -> BNode:
        name = attribute['name']

        metadata = BNode()
        self.graph.add((metadata, RDF.type, CX.metadata))
        self.graph.add((self.document, CX.has_metadata, metadata))
        self._add_label(metadata, name)

        version = attribute.get('version')
        if version is not None:  # FIXME isn't this supposed to be required?
            self.graph.add((metadata, CX.aspect_version, Literal(version)))

        count = attribute['elementCount']
        self.graph.add((metadata, CX.aspect_elements_count, Literal(count)))

        group = attribute.get('consistencyGroup')
        if group is not None:  # FIXME isn't this supposed to be required?
            self.graph.add((metadata, CX.aspect_consistency_group, Literal(group)))

        counter = attribute.get('idCounter')
        if counter:
            self.graph.add((metadata, CX.aspect_id_counter, Literal(counter)))

        return metadata

    # def _extend_context(self, elements):

    def _extend_node_elements(self, elements):
        for element in elements:
            self._extend_node_element(element)

    def _extend_node_element(self, element) -> BNode:
        node_id = element['@id']
        node_label = element.get('n')

        node = self.ensure_node(node_id)
        if node_label is not None:
            self._add_label(node, node_label)

        return node

    def _extend_edge_elements(self, entries):
        for value in entries:
            self._extend_edge_entry(value)

    def _extend_edge_entry(self, entry) -> BNode:
        source_id = entry['s']
        source = self.ensure_node(source_id)

        edge_id = entry['@id']
        edge = self.ensure_edge(edge_id)

        target_id = entry['t']
        target = self.ensure_node(target_id)

        self.graph.add((source, edge, target))

        interaction = entry.get('i')
        if interaction is not None:
            self.graph.add((edge, CX.edge_has_interaction, Literal(interaction)))

        return edge

    def _extend_node_attribute_elements(self, entries):
        for entry in entries:
            self._extend_node_attribute_entry(entry)

    def _extend_node_attribute_entry(self, entry) -> BNode:
        node = self.ensure_node(entry['po'])

        node_attribute = BNode()
        self.graph.add((node_attribute, RDF.type, CX.node_attribute))
        self.graph.add((node, CX.node_has_attribute, node_attribute))

        name = entry['n']
        data_type = entry.get('d', 'string')

        self.graph.add((node_attribute, CX.attribute_has_name, Literal(name)))

        if data_type.startswith('list_of'):
            for value in entry['v']:
                self.graph.add((node_attribute, CX.attribute_has_value, Literal(value)))
        else:
            self.graph.add((node_attribute, CX.attribute_has_value, Literal(entry['v'])))

        return node_attribute

    def _extend_edge_attribute_elements(self, entries):
        for entry in entries:
            self._extend_edge_attribute_entry(entry)

    def _extend_edge_attribute_entry(self, entry) -> BNode:
        edge = self.ensure_node(entry['po'])
        edge_attribute = BNode()
        self.graph.add((edge_attribute, RDF.type, CX.edge_attribute))
        self.graph.add((edge, CX.edge_has_attribute, edge_attribute))

        self.graph.add((edge_attribute, CX.attribute_has_name, Literal(entry['n'])))
        self.graph.add((edge_attribute, CX.attribute_has_value, Literal(entry['v'])))

        return edge_attribute

    def _extend_network_attribute_elements(self, entries):
        for entry in entries:
            self._add_network_attribute_entry(entry)

    def _add_network_attribute_entry(self, entry) -> BNode:
        network_attribute = BNode()

        self.graph.add((self.document, CX.network_has_attribute, network_attribute))
        self.graph.add((network_attribute, RDF.type, CX.network_attribute))

        name = entry['n']
        self.graph.add((network_attribute, CX.network_attribute_has_key, Literal(name)))

        value = entry['v']
        data_type = entry.get('d')

        if data_type is None or data_type == 'string':
            self.graph.add((network_attribute, CX.network_attribute_has_key, Literal(value)))
        else:
            raise TypeError(f'unhandled data type: {data_type} {value}')

        return network_attribute

    def _extend_citation_elements(self, entries):
        for entry in entries:
            self._extend_citation_entry(entry)

    def _extend_citation_entry(self, entry) -> BNode:
        citation_id = entry['@id']
        citation = self.ensure_citation(citation_id)

        title = entry.get('dc:title')
        if title is not None:
            self.graph.add((citation, CX.citation_has_title, Literal(title)))

        # FIXME handle other possible keys in citation entry

        return citation

    def _extend_edge_citation_elements(self, entries):
        for entry in entries:
            self._extend_edge_citation_entry(entry)

    def _extend_edge_citation_entry(self, entry):
        edge_ids = entry['po']
        citation_ids = entry['citations']

        for edge_id, citation_id in itt.product(edge_ids, citation_ids):
            edge = self.ensure_edge(edge_id)
            citation = self.ensure_citation(citation_id)
            self.graph.add((edge, CX.edge_has_citation, citation))

    def _extend_support_elements(self, entries):
        for entry in entries:
            self._extend_support_entry(entry)

    def _extend_support_entry(self, entry) -> BNode:
        support_id = entry['@id']
        support = self.ensure_citation(support_id)

        text = entry.get('text')
        if text is not None:
            self.graph.add((support, CX.support_has_text, Literal(text)))

        # FIXME handle other possible keys in support entry

        return support

    def _extend_edge_support_elements(self, entries):
        for entry in entries:
            self._extend_edge_support_entry(entry)

    def _extend_edge_support_entry(self, entry):
        edge_ids = entry['po']
        support_ids = entry['supports']

        for edge_id, support_id in itt.product(edge_ids, support_ids):
            edge = self.ensure_edge(edge_id)
            support = self.ensure_support(support_id)
            self.graph.add((edge, CX.edge_has_support, support))
