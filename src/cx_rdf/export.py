# -*- coding: utf-8 -*-

"""Functions for exporting CX to RDF."""

import logging

from rdflib import BNode, Graph, Literal, RDF, RDFS

from .constants import CX

__all__ = [
    'export',
]

log = logging.getLogger(__name__)


def export(cx_json):
    """Convert a CX JSON object to an RDFLib :class:`rdflib.Graph`.

    This policy uses CX standards for NDEx to make more meaningful RDF.

    :param list[dict] cx_json: A CX JSON object
    :return: An RDFLib graph
    :rtype: rdflib.Graph
    """
    exporter = _Exporter()
    return exporter.export(cx_json)


class _Exporter(object):
    """A class to mediate shared state in the export function."""

    def __init__(self):

        #: keep track of aspects by name, since they're represented by a BNode
        self.aspects = {}

        self.id_node = {}
        self.id_edge = {}

        self.graph = Graph()
        self.document = BNode()
        self.graph.add((self.document, RDF.type, CX.cx))

    def export(self, cx_json):
        """Convert a CX JSON object to an RDFLib :class:`rdflib.Graph`.

        This policy uses CX standards for NDEx to make more meaningful RDF.

        :param list[dict] cx_json: A CX JSON object
        :return: An RDFLib graph
        :rtype: rdflib.Graph
        """
        for aspect_dict in cx_json:
            for aspect_name, attributes in aspect_dict.items():
                self._add_element(aspect_name, attributes)

        return self.graph

    def get_aspect(self, aspect_name):
        """Get an aspect by name.

        :param str aspect_name: The name of the aspect
        :rtype: rdflib.BNode
        """
        aspect = self.aspects.get(aspect_name)

        if aspect is not None:
            return aspect

        aspect = self.aspects[aspect_name] = BNode()
        self.graph.add((aspect, RDF.type, CX.aspect))
        self.graph.add((aspect, RDFS.label, Literal(aspect_name)))
        self.graph.add((self.document, CX.has_aspect, aspect))

        return aspect

    def _add_element(self, aspect_name, attributes):
        """Add a CX group to the graph.

        :param str aspect_name:
        :param attributes:
        :param rdflib.Graph graph: An RDF graph.
        :param document: The RDF node representing the document
        """
        aspect = self.get_aspect(aspect_name)

        if aspect_name == 'numberVerification':
            n = attributes[0]['longNumber']
            self.graph.add((self.document, CX.has_number_verification, Literal(n)))
        elif aspect_name == 'nodes':
            self._add_node_aspect_value(aspect, attributes)
        elif aspect_name == 'edges':
            self._add_edge_aspect_value(aspect, attributes)
        elif aspect_name == 'metaData':
            self._add_metadata_aspect_values(attributes)
        elif aspect_name == 'nodeAttributes':
            self._add_node_attribute_aspect_value(attributes)
        elif aspect_name == 'networkAttributes':
            self._add_network_attribute_aspect_value(attributes)
        else:
            print('unhandled aspect: %s' % aspect_name)
            print('value: %s' % attributes)

    def _add_metadata_aspect_values(self, attributes):
        for attribute in attributes:
            name = attribute['name']
            aspect = self.get_aspect(name)

            version = attribute['version']
            self.graph.add((aspect, CX.aspect_version, Literal(version)))

            count = attribute['elementCount']
            self.graph.add((aspect, CX.aspect_elements_count, Literal(count)))

            group = attribute['consistencyGroup']
            self.graph.add((aspect, CX.aspect_consistency_group, Literal(group)))

            counter = attribute.get('idCounter')
            if counter:
                self.graph.add((aspect, CX.aspect_id_counter, Literal(counter)))

    def get_node(self, node_id):
        node = self.id_node.get(node_id)
        if node is not None:
            return node

        node = self.id_node[node_id] = BNode()  # represents the node
        self.graph.add((node, CX.has_id, Literal(node_id)))
        return node

    def _add_node_aspect_value(self, aspect, attributes):
        for value in attributes:
            node_id = value['@id']
            node = self.get_node(node_id)
            self.graph.add((aspect, CX.has_node, node))

            node_label = value.get('n')
            if node_label is not None:
                self.graph.add((node, RDFS.label, Literal(node_label)))

    def get_edge(self, edge_id):
        edge = self.id_edge.get(edge_id)
        if edge is not None:
            return edge

        edge = self.id_edge[edge_id] = BNode()
        self.graph.add((edge, CX.edge_has_id, Literal(edge_id)))
        return edge

    def _add_edge_aspect_value(self, aspect, attributes):
        for value in attributes:
            edge_id = value['@id']
            edge = self.get_edge(edge_id)
            self.graph.add((aspect, CX.has_edge, edge))

            edge_source_id = value['s']
            edge_target_id = value['t']

            self.graph.add((edge, CX.edge_has_source, self.get_node(edge_source_id)))
            self.graph.add((edge, CX.edge_has_target, self.get_node(edge_target_id)))

            edge_interaction = value.get('i')
            if edge_interaction is not None:
                self.graph.add((edge, CX.edge_has_interaction, Literal(edge_interaction)))

    def _add_node_attribute_aspect_value(self, attributes):
        for value in attributes:
            node = self.get_node(value['po'])

            node_attribute = BNode()
            self.graph.add((node_attribute, RDF.type, CX.node_attribute))
            self.graph.add((node, CX.node_has_attribute, node_attribute))

            self.graph.add((node_attribute, CX.attribute_has_name, Literal(value['n'])))
            self.graph.add((node_attribute, CX.attribute_has_value, Literal(value['v'])))

    def _add_network_attribute_aspect_value(self, attributes):
        for attribute in attributes:
            network_attribute = BNode()
            self.graph.add((self.document, CX.network_has_attribute, network_attribute))
            self.graph.add((network_attribute, RDF.type, CX.network_attribute))

            name = attribute['n']
            self.graph.add((network_attribute, CX.network_attribute_has_key, Literal(name)))

            value = attribute['v']
            data_type = attribute.get('d')

            if data_type is None or data_type == 'string':
                self.graph.add((network_attribute, CX.network_attribute_has_key, Literal(value)))
            else:
                raise TypeError('unhandled data type: {} {}'.format(data_type, value))
