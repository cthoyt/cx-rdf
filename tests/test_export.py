# -*- coding: utf-8 -*-

"""Tests for exporting CX to RDF."""

import unittest

from cx_rdf import export
from ndex2 import NiceCXNetwork
from rdflib import Graph


class TestExport(unittest.TestCase):
    """Tests for exporting CX to RDF."""

    def test_export(self):
        """Test exporting CX to RDFlib."""
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

        cx_json = ncx.to_cx()

        graph = export(cx_json)
        self.assertIsInstance(graph, Graph)
