# -*- coding: utf-8 -*-

"""Functions for exporting CX to RDF."""

import itertools as itt
import logging
from typing import Dict, List, Optional

from ndex2.cx import known_aspects
from rdflib import BNode, Graph, Literal, RDF, RDFS

from .constants import CX
from .exporter_base import Exporter
from .typing import CxType
from .utils import iterate_aspect_fragments

__all__ = [
    'export',
]

log = logging.getLogger(__name__)


def export(cx_json: CxType, graph: Optional[Graph] = None) -> Graph:
    """Convert a CX JSON object to an RDFLib :class:`rdflib.Graph`.

    This policy uses CX standards for NDEx to make more meaningful RDF.

    :param cx_json: A CX JSON object
    :param graph: An optional RDFLib graph to fill. If not specified, creates one.
    :return: An RDFLib graph
    """
    exporter = _Exporter(graph=graph)
    return exporter.export(cx_json)


class _Exporter(Exporter):
    """A class to mediate shared state in the export function."""

    policy = CX.aspect

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #: keep track of aspects by name, since they're represented by a BNode
        self.aspects = {}

    def export(self, cx_json: CxType) -> Graph:
        """Convert a CX JSON object to an RDFLib :class:`rdflib.Graph`.

        This policy uses CX standards for NDEx to make more meaningful RDF.

        :param cx_json: A CX JSON object
        :return: An RDFLib graph
        """
        for name, attributes in iterate_aspect_fragments(cx_json):
            self._extend_aspect(name, attributes)

        return self.graph

    def get_aspect(self, aspect_name: str) -> BNode:
        """Get an aspect by name.

        :param aspect_name: The name of the aspect
        """
        aspect_node = self.aspects.get(aspect_name)
        if aspect_node is not None:
            return aspect_node

        aspect_node = self.aspects[aspect_name] = BNode()
        self.graph.add((aspect_node, RDF.type, CX.aspect))
        self.graph.add((aspect_node, RDFS.label, Literal(aspect_name)))
        self.graph.add((self.document, CX.has_aspect, aspect_node))

        return aspect_node

    def _extend_aspect(self, name: str, entries: List[Dict]):
        """Add a CX group to the graph.

        :param str name:
        :param list[dict] entries:
        """
        aspect = self.get_aspect(name)

        if name == 'numberVerification':
            n = entries[0]['longNumber']
            self.graph.add((self.document, CX.has_number_verification, Literal(n)))
        elif name == 'nodes':
            self._extend_node_entries(aspect, entries)
        elif name == 'edges':
            self._extend_edge_entries(aspect, entries)
        elif name == 'metaData':
            self._extend_metadata_entries(entries)
        elif name == 'nodeAttributes':
            self._extend_node_attribute_entries(aspect, entries)
        elif name == 'edgeAttributes':
            self._extend_edge_attributes_entries(aspect, entries)
        elif name == 'networkAttributes':
            self._extend_network_attribute_entries(aspect, entries)
        elif name == 'citations':
            self._extend_citation_entries(aspect, entries)
        elif name == 'edgeCitations':
            self._extend_edge_citation_entries(aspect, entries)
        elif name == 'supports':
            self._extend_support_entries(aspect, entries)
        elif name == 'edgeSupports':
            self._extend_edge_support_entries(aspect, entries)
        elif name in known_aspects:
            raise ValueError(f'unhandled known aspect: {name}')
        else:
            raise ValueError(f'unhandled unknown aspect: {name}')

    def _extend_metadata_entries(self, entries):
        for entry in entries:
            self._extend_metadata_entry(entry)

    def _extend_metadata_entry(self, entry: Dict):
        name = entry['name']
        aspect = self.get_aspect(name)

        version = entry['version']
        self.graph.add((aspect, CX.aspect_version, Literal(version)))

        count = entry['elementCount']
        self.graph.add((aspect, CX.aspect_elements_count, Literal(count)))

        group = entry['consistencyGroup']
        self.graph.add((aspect, CX.aspect_consistency_group, Literal(group)))

        counter = entry.get('idCounter')
        if counter:
            self.graph.add((aspect, CX.aspect_id_counter, Literal(counter)))

    def _extend_node_entries(self, aspect, entries):
        for entry in entries:
            node = self._extend_node_entry(entry)
            self.graph.add((aspect, CX.aspect_has_attribute, node))

    def _extend_node_entry(self, entry) -> BNode:
        node_id = entry['@id']
        node = self.ensure_node(node_id)

        node_label = entry.get('n')
        if node_label is not None:
            self.graph.add((node, RDFS.label, Literal(node_label)))

        return node

    def _extend_edge_entries(self, aspect, entries):
        for entry in entries:
            node = self._extend_edge_entry(entry)
            self.graph.add((aspect, CX.aspect_has_attribute, node))

    def _extend_edge_entry(self, entry) -> BNode:
        edge_id = entry['@id']
        edge = self.ensure_edge(edge_id)

        edge_source_id = entry['s']
        edge_target_id = entry['t']

        self.graph.add((edge, CX.edge_has_source, self.ensure_node(edge_source_id)))
        self.graph.add((edge, CX.edge_has_target, self.ensure_node(edge_target_id)))

        edge_interaction = entry.get('i')
        if edge_interaction is not None:
            self.graph.add((edge, CX.edge_has_interaction, Literal(edge_interaction)))

        return edge

    def _extend_node_attribute_entries(self, aspect, entries):
        for entry in entries:
            node = self._extend_node_attribute_entry(entry)
            self.graph.add((aspect, CX.aspect_has_attribute, node))

    def _extend_node_attribute_entry(self, entry) -> BNode:
        node = self.ensure_node(entry['po'])

        node_attribute = BNode()
        self.graph.add((node_attribute, RDF.type, CX.node_attribute))
        self.graph.add((node, CX.node_has_attribute, node_attribute))

        self.graph.add((node_attribute, CX.attribute_has_name, Literal(entry['n'])))
        self.graph.add((node_attribute, CX.attribute_has_value, Literal(entry['v'])))

        return node_attribute

    def _extend_network_attribute_entries(self, aspect, entries):
        for entry in entries:
            node = self._extend_network_attribute_entry(entry)
            self.graph.add((aspect, CX.aspect_has_attribute, node))

    def _extend_network_attribute_entry(self, entry) -> BNode:
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

    def _extend_edge_attributes_entries(self, aspect, entries):
        for entry in entries:
            node = self._extend_edge_attribute_entry(entry)
            self.graph.add((aspect, CX.aspect_has_attribute, node))

    def _extend_edge_attribute_entry(self, entry) -> BNode:
        edge = self.ensure_node(entry['po'])
        edge_attribute = BNode()
        self.graph.add((edge_attribute, RDF.type, CX.edge_attribute))
        self.graph.add((edge, CX.edge_has_attribute, edge_attribute))

        self.graph.add((edge_attribute, CX.attribute_has_name, Literal(entry['n'])))
        self.graph.add((edge_attribute, CX.attribute_has_value, Literal(entry['v'])))

        return edge_attribute

    def _extend_citation_entries(self, aspect, entries):
        for entry in entries:
            node = self._extend_citation_entry(entry)
            self.graph.add((aspect, CX.aspect_has_attribute, node))

    def _extend_citation_entry(self, entry) -> BNode:
        citation_id = entry['@id']
        citation = self.ensure_citation(citation_id)

        title = entry.get('dc:title')
        if title is not None:
            self.graph.add((citation, CX.citation_has_title, Literal(title)))

        # FIXME handle other possible keys in citation entry

        return citation

    def _extend_edge_citation_entries(self, aspect, entries):
        for entry in entries:
            self._extend_edge_citation_entry(aspect, entry)

    def _extend_edge_citation_entry(self, aspect, entry):
        edge_ids = entry['po']
        citation_ids = entry['citations']

        for edge_id, citation_id in itt.product(edge_ids, citation_ids):
            edge_citation = BNode()
            self.graph.add((aspect, CX.aspect_has_attribute, edge_citation))

            edge = self.ensure_edge(edge_id)
            citation = self.ensure_citation(citation_id)
            self.graph.add((edge_citation, CX.edge_citation_has_edge, edge))
            self.graph.add((edge_citation, CX.edge_citation_has_citation, citation))

    def _extend_support_entries(self, aspect, entries):
        for entry in entries:
            node = self._extend_support_entry(entry)
            self.graph.add((aspect, CX.aspect_has_attribute, node))

    def _extend_support_entry(self, entry) -> BNode:
        support_id = entry['@id']
        support = self.ensure_citation(support_id)

        text = entry.get('text')
        if text is not None:
            self.graph.add((support, CX.support_has_text, Literal(text)))

        # FIXME handle other possible keys in support entry

        return support

    def _extend_edge_support_entries(self, aspect, entries):
        for entry in entries:
            self._extend_edge_support_entry(aspect, entry)

    def _extend_edge_support_entry(self, aspect, entry):
        edge_ids = entry['po']
        support_ids = entry['supports']

        for edge_id, support_id in itt.product(edge_ids, support_ids):
            edge_support = BNode()
            self.graph.add((aspect, CX.aspect_has_attribute, edge_support))
            edge = self.ensure_edge(edge_id)
            support = self.ensure_support(support_id)
            self.graph.add((edge_support, CX.edge_support_has_edge, edge))
            self.graph.add((edge_support, CX.edge_support_has_support, support))
