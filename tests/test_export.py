# -*- coding: utf-8 -*-

"""Tests for exporting CX to RDF."""

import json
import unittest

from cx_rdf import cx_to_rdf_graph
from ndex2 import NiceCXNetwork
from ndex2.cx import CX_CONSTANTS
from ndex2.cx.aspects.CitationElement import CitationElement
from ndex2.cx.aspects.SupportElement import SupportElement
from rdflib import Graph


class TestExport(unittest.TestCase):
    """Tests for exporting CX to RDF."""

    @classmethod
    def setUpClass(cls):
        """Set up nice CX network and JSON."""
        cx_network = NiceCXNetwork()
        cx_network.set_name('Test Name')

        a, b, c, d, e = [
            cx_network.create_node(node_name=letter)
            for letter in 'ABCDE'
        ]

        e1 = cx_network.create_edge(
            edge_source=a,
            edge_target=b,
        )

        e2 = cx_network.create_edge(
            edge_source=b,
            edge_target=c,
            edge_interaction='increases',
        )

        c1 = CitationElement(id=0, title='Hi')
        cx_network.add_citation(c1)

        s1 = SupportElement(id=0, text='Hi')
        cx_network.add_support(s1)

        cx_network.add_node_attribute(property_of=a, name='Color', values='Red')
        cx_network.add_node_attribute(property_of=b, name='Color', values='Red')
        cx_network.add_node_attribute(property_of=c, name='Color', values='Red')
        cx_network.add_node_attribute(property_of=d, name='Color', values='Blue')
        cx_network.add_node_attribute(property_of=e, name='Color', values='Blue')

        cx_network.add_edge_attribute(property_of=e1, name='Color', values='Green')
        cx_network.add_edge_attribute(property_of=e2, name='Color', values='Purple')

        cx_network.add_edge_citations(edge_id=e1, citation_id=c1.get_id())

        edge_support_element_1 = {CX_CONSTANTS.PROPERTY_OF: [e1], CX_CONSTANTS.SUPPORTS: [c1.get_id()]}
        cx_network.add_edge_supports(edge_supports_element=edge_support_element_1)

        cls.cx_json = json.loads(json.dumps(cx_network.to_cx()))
        print(json.dumps(cls.cx_json, indent=2))

    def test_export_aspect_policy(self):
        """Test the aspect policy."""
        graph = cx_to_rdf_graph(self.cx_json, policy='aspect')
        self.assertIsInstance(graph, Graph)

        print(f'\nResulting ASPECT graph ({len(graph)} triplets):\n')
        print(graph.serialize(format='turtle').decode('utf-8'))

    def test_export_predicate_policy(self):
        """Test the predicate policy."""
        graph = cx_to_rdf_graph(self.cx_json, policy='predicate')
        self.assertIsInstance(graph, Graph)

        print(f'\nResulting PREDICATE graph ({len(graph)} triplets):\n')
        print(graph.serialize(format='turtle').decode('utf-8'))

    def test_export_abstract_policy(self):
        """Test the abstract policy."""
        graph = cx_to_rdf_graph(self.cx_json, policy='abstract')
        self.assertIsInstance(graph, Graph)

        print(f'\nResulting ABSRAC graph ({len(graph)} triplets):\n')
        print(graph.serialize(format='turtle').decode('utf-8'))
