# -*- coding: utf-8 -*-

"""Tests for exporting CX to RDF."""

import json
import unittest

from cx_rdf import export
from cx_rdf.export_abstract import export_abstract
from ndex2 import NiceCXNetwork
from rdflib import Graph


class TestExport(unittest.TestCase):
    """Tests for exporting CX to RDF."""

    def setUp(self):
        """Set up nice CX network and JSON."""
        ncx = NiceCXNetwork()
        ncx.set_name('Test Name')

        a, b, c, d, e = [
            ncx.create_node(letter)
            for letter in 'ABCDE'
        ]

        ncx.create_edge(
            edge_source=a,
            edge_target=b,
        )

        ncx.create_edge(
            edge_source=b,
            edge_target=c,
        )

        ncx.add_node_attribute(property_of=a, name='Color', values='Red')
        ncx.add_node_attribute(property_of=b, name='Color', values='Red')
        ncx.add_node_attribute(property_of=c, name='Color', values='Red')
        ncx.add_node_attribute(property_of=d, name='Color', values='Blue')
        ncx.add_node_attribute(property_of=e, name='Color', values='Blue')

        self.cx_json = json.loads(json.dumps(ncx.to_cx()))

    def test_export(self):
        """Test exporting CX to RDFlib."""
        # json_print(self.cx_json)

        graph = export(self.cx_json)
        self.assertIsInstance(graph, Graph)

        print(graph.serialize(format='turtle').decode('utf-8'))

    def test_export_abstract(self):
        """Test exporting CX to RDFlib."""
        # json_print(self.cx_json)

        graph = export_abstract(self.cx_json)
        self.assertIsInstance(graph, Graph)

        print(graph.serialize(format='turtle').decode('utf-8'))
