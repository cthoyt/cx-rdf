# -*- coding: utf-8 -*-

"""Functions for exporting CX to RDF."""

import logging
from typing import Dict, List, Optional

from rdflib import BNode, Graph, Literal, RDF, RDFS

from .constants import CX
from .typing import CxType
from .utils import bind_cx_namespace, iterate_aspect_fragments

__all__ = [
    'export',
]

log = logging.getLogger(__name__)


def export(cx_json: CxType, graph: Optional[Graph] = None) -> Graph:
    """Convert a CX JSON object to an RDFLib :class:`rdflib.Graph`.

    This policy for serializing CX to RDF is the most general, and only manages to encode the structure of a CX
    document in RDF. It has little semantic meaning.

    :param cx_json: A CX JSON object
    :param graph: An RDFLib graph (to append to)
    :return: An RDFLib graph
    """
    if graph is None:
        graph = Graph()

    bind_cx_namespace(graph)

    document = BNode()
    graph.add((document, RDF.type, CX.network))
    graph.add((document, CX.policy, CX.abstract_network))

    aspects = {}

    for aspect_name, elements in iterate_aspect_fragments(cx_json):
        _handle_aspects(graph, aspects, document, aspect_name, elements)

    return graph


def _handle_aspects(graph, aspects, document, aspect_name, elements):
    aspect_node = _get_aspect_node(graph, aspects, document, aspect_name)
    _handle_elements(graph, aspect_node, elements)


def _get_aspect_node(graph, aspects, document, aspect_name):
    aspect_node = aspects.get(aspect_name)

    if aspect_node is None:
        aspect_node = aspects[aspect_name] = BNode()
        graph.add((aspect_node, RDF.type, CX.aspect))
        graph.add((document, CX.has_aspect, aspect_node))
        graph.add((aspect_node, RDFS.label, Literal(aspect_name)))

    return aspect_node


def _handle_elements(graph: Graph, aspect_node: BNode, elements: List[Dict]):
    """Handle all attributes from a CX JSON aspect."""
    for element in elements:
        _handle_element(graph, aspect_node, element)


def _handle_element(graph: Graph, aspect_node: BNode, element: Dict):
    """Handle an attribute from a CX JSON aspect.

    Creates a blank node, registers it to the aspect as an entry, then adds its data.
    """
    element_node = BNode()
    graph.add((element_node, RDF.type, CX.attribute))
    graph.add((aspect_node, CX.has_element, element_node))

    for key, value in element.items():
        _handle_element_entries(graph, element_node, key, value)


def _handle_element_entries(graph: Graph, element_node: BNode, key, value):
    entry_node = BNode()
    graph.add((entry_node, RDF.type, CX.entry))
    graph.add((element_node, CX.has_entry, entry_node))

    graph.add((entry_node, CX.has_key, Literal(key)))
    # TODO need to handle different types here
    graph.add((entry_node, CX.has_value, Literal(value)))
